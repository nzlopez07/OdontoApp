"""
Servicio para crear prestaciones con cálculo de descuentos.

Replica la lógica compleja de crear_prestacion() del viejo prestacion_service.py,
incluyendo cálculo de descuentos porcentuales y fijos, y creación de
asociaciones PrestacionPractica.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from app.database.session import DatabaseSession
from app.models import Prestacion, Practica, PrestacionPractica, Paciente
from app.services.common import (
    PacienteNoEncontradoError,
    DatosInvalidosError,
    PracticaNoEncontradaError,
)


class CrearPrestacionService:
    """Servicio para crear prestaciones con descuentos."""
    
    @staticmethod
    def execute(data: Dict[str, Any]) -> Prestacion:
        """
        Crea una nueva prestación con cálculo automático de montos y descuentos.
        
        Lógica de cálculo:
        1. Obtener monto_unitario de cada practica
        2. Calcular subtotal = sum(practicas.monto_unitario)
        3. Aplicar descuento porcentaje: monto = subtotal * (1 - porcentaje/100)
        4. Aplicar descuento fijo: monto = monto - descuento_fijo
        5. Garantizar monto >= 0
        6. Crear PrestacionPractica para cada practica
        
        Args:
            data: Dict con estructura:
            {
                'paciente_id': int,                     # REQUERIDO
                'descripcion': str,                     # REQUERIDO
                'practicas': [int, int, ...],          # REQUERIDO - IDs de Practica
                'descuento_porcentaje': float,         # OPCIONAL (0-100), default 0
                'descuento_fijo': float,               # OPCIONAL, default 0
                'observaciones': str,                   # OPCIONAL
            }
            
        Returns:
            Objeto Prestacion creado con PrestacionPractica entries
            
        Raises:
            PacienteNoEncontradoError: Si paciente_id no existe
            PracticaNoEncontradaError: Si alguna practica no existe
            DatosInvalidosError: Si falta campo requerido o valor inválido
        """
        session = DatabaseSession.get_instance().session
        
        # 1. Validar y extraer datos requeridos
        paciente_id = data.get('paciente_id')
        if not paciente_id:
            raise DatosInvalidosError('paciente_id es requerido')
        
        descripcion = data.get('descripcion')
        if not descripcion or (isinstance(descripcion, str) and not descripcion.strip()):
            raise DatosInvalidosError('descripcion es requerida y no puede estar vacía')
        if isinstance(descripcion, str):
            descripcion = descripcion.strip()
        
        practicas_ids = data.get('practicas', [])
        if not practicas_ids:
            raise DatosInvalidosError('Debe seleccionar al menos una práctica')
        
        if not isinstance(practicas_ids, list):
            raise DatosInvalidosError('practicas debe ser una lista de IDs')
        
        descuento_porcentaje = float(data.get('descuento_porcentaje', 0))
        descuento_fijo = float(data.get('descuento_fijo', 0))
        observaciones = data.get('observaciones')
        if observaciones and isinstance(observaciones, str):
            observaciones = observaciones.strip() or None
        else:
            observaciones = None
        
        # 2. Validar rangos de descuentos
        if descuento_porcentaje < 0 or descuento_porcentaje > 100:
            raise DatosInvalidosError('descuento_porcentaje debe estar entre 0 y 100')
        
        if descuento_fijo < 0:
            raise DatosInvalidosError('descuento_fijo no puede ser negativo')
        
        # 3. Verificar que el paciente existe
        paciente = session.query(Paciente).filter(Paciente.id == paciente_id).first()
        if not paciente:
            raise PacienteNoEncontradoError(paciente_id)
        
        # 4. Query prácticas y calcular subtotal
        practicas = session.query(Practica).filter(
            Practica.id.in_(practicas_ids)
        ).all()
        
        # Validar que se encontraron todas las prácticas
        if len(practicas) != len(practicas_ids):
            encontradas = {p.id for p in practicas}
            no_encontradas = set(practicas_ids) - encontradas
            raise PracticaNoEncontradaError(
                f'Prácticas no encontradas: {", ".join(str(id) for id in no_encontradas)}'
            )
        
        # 5. Calcular subtotal
        subtotal = sum(p.monto_unitario for p in practicas)
        
        # 6. Aplicar descuento porcentaje (primero)
        monto = subtotal * (1 - descuento_porcentaje / 100)
        
        # 7. Aplicar descuento fijo (segundo)
        monto = monto - descuento_fijo
        
        # 8. Garantizar que monto nunca sea negativo
        monto = max(0, monto)
        
        # 9. Crear Prestacion
        prestacion = Prestacion(
            paciente_id=paciente_id,
            descripcion=descripcion,
            monto=monto,
            observaciones=observaciones or None,
            fecha=datetime.now(),
        )
        session.add(prestacion)
        session.flush()  # Para obtener el ID generado
        
        # 10. Crear PrestacionPractica entries para cada práctica
        for practica in practicas:
            pp = PrestacionPractica(
                prestacion_id=prestacion.id,
                practica_id=practica.id,
            )
            session.add(pp)
        
        # Commit de todo junto
        session.commit()
        
        return prestacion
    
    @staticmethod
    def calcular_monto_preview(
        practicas_ids: List[int],
        descuento_porcentaje: float = 0,
        descuento_fijo: float = 0,
    ) -> Dict[str, float]:
        """
        Calcula un preview del monto sin crear la prestación.
        
        Útil para mostrar al usuario el desglose antes de confirmar.
        
        Args:
            practicas_ids: Lista de IDs de prácticas
            descuento_porcentaje: Descuento porcentual (0-100)
            descuento_fijo: Descuento fijo en monto
            
        Returns:
            Dict con estructura:
            {
                'subtotal': float,
                'descuento_porcentaje_aplicado': float,
                'descuento_fijo_aplicado': float,
                'total': float,
            }
        """
        session = DatabaseSession.get_instance().session
        
        # Query prácticas
        practicas = session.query(Practica).filter(
            Practica.id.in_(practicas_ids)
        ).all()
        
        subtotal = sum(p.monto_unitario for p in practicas)
        descuento_porcentaje_monto = subtotal * (descuento_porcentaje / 100)
        monto_post_porcentaje = subtotal - descuento_porcentaje_monto
        total = max(0, monto_post_porcentaje - descuento_fijo)
        
        return {
            'subtotal': round(subtotal, 2),
            'descuento_porcentaje_aplicado': round(descuento_porcentaje_monto, 2),
            'descuento_fijo_aplicado': round(descuento_fijo, 2),
            'total': round(total, 2),
        }
