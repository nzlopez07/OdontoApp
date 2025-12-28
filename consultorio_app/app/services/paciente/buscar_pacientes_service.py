"""
BuscarPacientesService: Caso de uso para buscar y listar pacientes.

Responsabilidades:
- Listar todos los pacientes
- Buscar pacientes por término (nombre, apellido, DNI)
- Aplicar paginación
- Obtener detalles de un paciente específico
"""

from typing import List, Dict, Any
from app.database.session import DatabaseSession
from app.models import Paciente, Turno, Prestacion
from app.services.common import PacienteNoEncontradoError


class BuscarPacientesService:
    """Caso de uso: buscar y listar pacientes."""
    
    @staticmethod
    def listar_todos() -> List[Paciente]:
        """Lista todos los pacientes ordenados por apellido y nombre."""
        return Paciente.query.order_by(Paciente.apellido, Paciente.nombre).all()
    
    @staticmethod
    def buscar(termino: str = None) -> List[Paciente]:
        """
        Busca pacientes por término (nombre, apellido o DNI).
        
        Args:
            termino: Término de búsqueda (parcial, case-insensitive, sin acentos)
        
        Returns:
            Lista de pacientes que coinciden
        """
        import unicodedata
        
        termino = (termino or "").strip()
        
        if not termino:
            return BuscarPacientesService.listar_todos()
        
        # Normalizar término: remover acentos y convertir a lowercase
        def normalizar(texto):
            """Elimina acentos y convierte a lowercase para búsqueda"""
            nfd = unicodedata.normalize('NFD', texto)
            sin_acentos = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
            return sin_acentos.lower()
        
        termino_normalizado = normalizar(termino)
        
        # Obtener todos los pacientes y filtrar en memoria (alternativa a búsqueda en BD)
        # Esto es necesario porque SQLite no maneja bien la normalización de acentos
        todos_pacientes = Paciente.query.all()
        
        resultados = []
        for paciente in todos_pacientes:
            nombre_norm = normalizar(paciente.nombre)
            apellido_norm = normalizar(paciente.apellido)
            dni_norm = normalizar(paciente.dni)
            
            if (termino_normalizado in nombre_norm or 
                termino_normalizado in apellido_norm or 
                termino_normalizado in dni_norm):
                resultados.append(paciente)
        
        # Ordenar resultados
        resultados.sort(key=lambda p: (p.apellido, p.nombre))
        return resultados
    
    @staticmethod
    def obtener_por_id(paciente_id: int) -> Paciente:
        """
        Obtiene un paciente por ID.
        
        Args:
            paciente_id: ID del paciente
        
        Returns:
            Paciente encontrado
        
        Raises:
            PacienteNoEncontradoError: Si no existe
        """
        paciente = Paciente.query.get(paciente_id)
        if not paciente:
            raise PacienteNoEncontradoError(paciente_id)
        return paciente
    
    @staticmethod
    def obtener_detalle_completo(paciente_id: int) -> Dict[str, Any]:
        """
        Obtiene detalles completos de un paciente (incluye turnos, prestaciones, estadísticas).
        
        Args:
            paciente_id: ID del paciente
        
        Returns:
            Dict con paciente, turnos, prestaciones, edad y estadísticas
        
        Raises:
            PacienteNoEncontradoError: Si no existe
        """
        from datetime import date
        from dateutil.relativedelta import relativedelta
        
        paciente = BuscarPacientesService.obtener_por_id(paciente_id)
        
        # Obtener turnos recientes
        turnos = Turno.query.filter_by(paciente_id=paciente_id).order_by(
            Turno.fecha.desc(), Turno.hora.desc()
        ).limit(5).all()
        
        # Obtener prestaciones recientes
        prestaciones = Prestacion.query.filter_by(paciente_id=paciente_id).order_by(
            Prestacion.fecha.desc()
        ).limit(5).all()
        
        # Calcular edad
        edad = None
        if paciente.fecha_nac:
            edad = relativedelta(date.today(), paciente.fecha_nac).years
        
        # Contar totales
        total_turnos = Turno.query.filter_by(paciente_id=paciente_id).count()
        total_prestaciones = Prestacion.query.filter_by(paciente_id=paciente_id).count()
        
        return {
            'paciente': paciente,
            'turnos': turnos,
            'prestaciones': prestaciones,
            'edad': edad,
            'total_turnos': total_turnos,
            'total_prestaciones': total_prestaciones,
        }
