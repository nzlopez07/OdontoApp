"""
Servicio para crear gastos.
"""
from datetime import date
from decimal import Decimal
from typing import Optional

from app.database import db
from app.models import Gasto, Usuario
from app.services.common.exceptions import OdontoAppError


class CrearGastoService:
    """Servicio para crear gastos."""
    
    @staticmethod
    def crear(
        descripcion: str,
        monto: float,
        fecha: date,
        categoria: str,
        creado_por_id: int,
        observaciones: Optional[str] = None,
        comprobante: Optional[str] = None
    ) -> Gasto:
        """
        Crea un nuevo gasto.
        
        Args:
            descripcion: Descripción del gasto
            monto: Monto del gasto
            fecha: Fecha del gasto
            categoria: Categoría (MATERIAL, INSUMO, MATRICULA, CURSO, OPERATIVO, OTRO)
            creado_por_id: ID del usuario que crea el gasto
            observaciones: Observaciones adicionales (opcional)
            comprobante: Ruta del comprobante (opcional)
            
        Returns:
            Gasto creado
            
        Raises:
            OdontoAppError: Si los datos son inválidos
        """
        # Validar datos
        if not descripcion or descripcion.strip() == '':
            raise OdontoAppError('La descripción es requerida', codigo='DESCRIPCION_REQUERIDA')
        
        if monto <= 0:
            raise OdontoAppError('El monto debe ser mayor a 0', codigo='MONTO_INVALIDO')
        
        categorias_validas = ['MATERIAL', 'INSUMO', 'MATRICULA', 'CURSO', 'OPERATIVO', 'OTRO']
        if categoria not in categorias_validas:
            raise OdontoAppError(
                f'Categoría inválida. Debe ser una de: {", ".join(categorias_validas)}',
                codigo='CATEGORIA_INVALIDA'
            )
        
        # Verificar que el usuario existe
        usuario = db.session.get(Usuario, creado_por_id)
        if not usuario:
            raise OdontoAppError('Usuario no encontrado', codigo='USUARIO_NO_ENCONTRADO')
        
        # Crear el gasto
        gasto = Gasto(
            descripcion=descripcion.strip(),
            monto=Decimal(str(monto)),
            fecha=fecha,
            categoria=categoria,
            observaciones=observaciones.strip() if observaciones else None,
            comprobante=comprobante,
            creado_por_id=creado_por_id
        )
        
        db.session.add(gasto)
        db.session.commit()
        
        return gasto
