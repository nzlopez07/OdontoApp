"""
ListarPrestacionesService: Caso de uso para listar y consultar prestaciones.

Responsabilidades:
- Listar prestaciones de un paciente
- Obtener prestación específica
- Filtrar por descripción, monto, fecha
- Paginación
"""

from typing import List, Dict, Any, Optional
from datetime import date
from app.database.session import DatabaseSession
from app.models import Prestacion, Paciente


class ListarPrestacionesService:
    """Caso de uso: listar y consultar prestaciones."""
    
    @staticmethod
    def listar_por_paciente(
        paciente_id: int,
        pagina: int = 1,
        por_pagina: int = 10,
        descripcion: Optional[str] = None,
        monto_min: Optional[float] = None,
        monto_max: Optional[float] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
    ) -> Dict[str, Any]:
        """
        Lista prestaciones de un paciente paginadas con filtros opcionales.
        
        Args:
            paciente_id: ID del paciente
            pagina: Número de página (1-indexed)
            por_pagina: Elementos por página
            descripcion: Filtrar por descripción (búsqueda LIKE case-insensitive)
            monto_min: Monto mínimo (inclusive)
            monto_max: Monto máximo (inclusive)
            fecha_desde: Fecha desde (inclusive)
            fecha_hasta: Fecha hasta (inclusive)
        
        Returns:
            Dict con 'items', 'total', 'pagina_actual', 'total_paginas'
        
        Raises:
            Exception: Si paciente no existe
        """
        from app.services.common import PacienteNoEncontradoError
        
        # Validar paciente existe
        if not Paciente.query.get(paciente_id):
            raise PacienteNoEncontradoError(paciente_id)
        
        # Query base
        query = Prestacion.query.filter_by(paciente_id=paciente_id)
        
        # Aplicar filtros opcionales
        if descripcion:
            # Búsqueda case-insensitive con ILIKE
            query = query.filter(Prestacion.descripcion.ilike(f'%{descripcion}%'))
        
        if monto_min is not None:
            query = query.filter(Prestacion.monto >= monto_min)
        
        if monto_max is not None:
            query = query.filter(Prestacion.monto <= monto_max)
        
        if fecha_desde:
            query = query.filter(Prestacion.fecha >= fecha_desde)
        
        if fecha_hasta:
            query = query.filter(Prestacion.fecha <= fecha_hasta)
        
        # Ordenar por fecha de la prestación (más recientes primero)
        query = query.order_by(Prestacion.fecha.desc())
        
        # Paginación
        total = query.count()
        total_paginas = (total + por_pagina - 1) // por_pagina if total > 0 else 1
        pagina_actual = max(1, min(pagina, total_paginas))
        offset = (pagina_actual - 1) * por_pagina
        
        items = query.offset(offset).limit(por_pagina).all()
        
        return {
            'items': items,
            'total': total,
            'pagina_actual': pagina_actual,
            'total_paginas': total_paginas,
            'por_pagina': por_pagina,
            'filtros_aplicados': {
                'descripcion': descripcion,
                'monto_min': monto_min,
                'monto_max': monto_max,
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta,
            }
        }
    
    @staticmethod
    def obtener_por_id(prestacion_id: int) -> Prestacion:
        """
        Obtiene una prestación por ID.
        
        Args:
            prestacion_id: ID de la prestación
        
        Returns:
            Prestación encontrada
        
        Raises:
            PrestacionNoEncontradaError: Si no existe
        """
        from app.services.common import PrestacionNoEncontradaError
        
        prestacion = Prestacion.query.get(prestacion_id)
        if not prestacion:
            raise PrestacionNoEncontradaError(prestacion_id)
        return prestacion
    
    @staticmethod
    def listar_recientes_paciente(paciente_id: int, limite: int = 5) -> List[Prestacion]:
        """
        Lista las prestaciones más recientes de un paciente.
        
        Args:
            paciente_id: ID del paciente
            limite: Número máximo de prestaciones
        
        Returns:
            Lista de prestaciones recientes
        
        Raises:
            PacienteNoEncontradoError: Si paciente no existe
        """
        from app.services.common import PacienteNoEncontradoError
        
        if not Paciente.query.get(paciente_id):
            raise PacienteNoEncontradoError(paciente_id)
        
        return Prestacion.query.filter_by(paciente_id=paciente_id).order_by(
            Prestacion.fecha.desc()
        ).limit(limite).all()
