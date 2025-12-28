"""
Servicio para eliminar turnos.

Replica la funcionalidad de eliminar_turno() del viejo turno_service.py.
"""

from typing import Dict, Any
from app.database.session import DatabaseSession
from app.models import Turno
from app.services.common import (
    TurnoNoEncontradoError,
    EstadoTurnoInvalidoError,
)


class EliminarTurnoService:
    """Servicio para eliminar turnos."""
    
    @staticmethod
    def execute(turno_id: int) -> Dict[str, Any]:
        """
        Elimina un turno.
        
        Solo permite eliminar turnos en estado 'Pendiente'.
        
        Args:
            turno_id: ID del turno a eliminar
            
        Returns:
            Dict con resultado:
            {
                'success': bool,
                'mensaje': str,
            }
            
        Raises:
            TurnoNoEncontradoError: Si turno no existe
            EstadoTurnoInvalidoError: Si estado != 'Pendiente'
        """
        session = DatabaseSession.get_instance().session
        
        # 1. Obtener turno
        turno = session.query(Turno).filter(
            Turno.id == turno_id
        ).first()
        if not turno:
            raise TurnoNoEncontradoError(turno_id)
        
        # 2. Validar estado
        estado_actual = turno.estado_nombre
        if estado_actual != 'Pendiente':
            raise EstadoTurnoInvalidoError(
                f'Solo se pueden eliminar turnos en estado "Pendiente". '
                f'Este turno está en estado "{estado_actual}"'
            )
        
        # 3. Eliminar
        session.delete(turno)
        session.commit()
        
        return {
            'success': True,
            'mensaje': f'Turno #{turno_id} eliminado correctamente',
        }
