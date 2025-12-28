"""
CambiarEstadoTurnoService: Caso de uso para cambiar el estado de un turno.

Responsabilidades:
- Validar que el turno existe
- Validar transiciones de estado según matriz
- Persistir cambio y registrar historial
- Manejar reglas especiales (ej: turnos pasados, estados finales)
"""

from datetime import date, datetime
from app.database.session import DatabaseSession
from app.models import Turno, CambioEstado, Estado
from app.services.common import (
    TurnoNoEncontradoError,
    TurnoError,
    TransicionEstadoInvalidaError,
    EstadoFinalError,
)


class CambiarEstadoTurnoService:
    """Caso de uso: cambiar el estado de un turno."""
    
    # Matriz de transiciones válidas
    TRANSICIONES_VALIDAS = {
        'Pendiente': ['Confirmado', 'Cancelado', 'NoAtendido'],
        'Confirmado': ['Atendido', 'NoAtendido', 'Cancelado'],
        'Atendido': [],  # Estado final
        'NoAtendido': [],  # Estado final
        'Cancelado': []  # Estado final
    }
    
    @staticmethod
    def execute(turno_id: int, estado_nuevo: str, motivo: str = None) -> Turno:
        """
        Cambia el estado de un turno con validación completa.
        
        Args:
            turno_id: ID del turno (requerido)
            estado_nuevo: Nuevo estado deseado (requerido)
            motivo: Motivo del cambio (opcional)
        
        Returns:
            Turno con estado actualizado
        
        Raises:
            TurnoNoEncontradoError: Si turno no existe
            TransicionEstadoInvalidaError: Si transición no es válida
            EstadoFinalError: Si el turno está en estado final
            TurnoError: Para otros errores
        """
        session = DatabaseSession.get_instance().session
        
        try:
            # Obtener turno
            turno = Turno.query.get(turno_id)
            if not turno:
                raise TurnoNoEncontradoError(turno_id)
            
            estado_actual = turno.estado_nombre
            
            # Validar que no sea el mismo estado
            if estado_actual == estado_nuevo:
                raise TurnoError(f"El turno ya tiene el estado '{estado_nuevo}'")
            
            # Validar transición
            CambiarEstadoTurnoService._validar_transicion(estado_actual, estado_nuevo)
            
            # Validación especial: turnos pasados
            if turno.fecha < date.today():
                if estado_nuevo not in ['Atendido', 'NoAtendido']:
                    raise TurnoError(
                        f"Los turnos de fechas pasadas solo pueden marcarse como "
                        f"'Atendido' o 'NoAtendido', no como '{estado_nuevo}'"
                    )
            
            # Cambiar estado (string + FK a Estado)
            estado_nuevo_obj = Estado.query.filter_by(nombre=estado_nuevo).first()
            if not estado_nuevo_obj:
                raise TurnoError(f"Estado destino no encontrado en BD: '{estado_nuevo}'")

            turno.estado = estado_nuevo
            turno.estado_id = estado_nuevo_obj.id
            
            # Registrar cambio
            # Resolver id de estado anterior si existe
            estado_anterior_obj = Estado.query.filter_by(nombre=estado_actual).first()

            cambio = CambioEstado(
                turno_id=turno.id,
                estado_anterior=estado_actual,
                estado_nuevo=estado_nuevo,
                estado_anterior_id=estado_anterior_obj.id if estado_anterior_obj else None,
                estado_nuevo_id=estado_nuevo_obj.id,
                fecha_cambio=datetime.now(),
                motivo=motivo or f"Cambio a {estado_nuevo}"
            )
            
            session.add(cambio)
            session.commit()
            return turno
            
        except (TurnoNoEncontradoError, TransicionEstadoInvalidaError, EstadoFinalError, TurnoError):
            session.rollback()
            raise
        except Exception as exc:
            session.rollback()
            raise TurnoError(f"Error al cambiar estado del turno: {str(exc)}")
    
    @staticmethod
    def _validar_transicion(estado_actual: str, estado_nuevo: str) -> None:
        """
        Valida que la transición sea válida.
        
        Raises:
            TransicionEstadoInvalidaError: Si transición no es válida
            EstadoFinalError: Si estado actual es final
        """
        # Validar que estado actual exista
        if estado_actual not in CambiarEstadoTurnoService.TRANSICIONES_VALIDAS:
            raise TurnoError(f"Estado actual desconocido: '{estado_actual}'")
        
        # Verificar si es estado final
        transiciones_permitidas = CambiarEstadoTurnoService.TRANSICIONES_VALIDAS[estado_actual]
        if not transiciones_permitidas:
            raise EstadoFinalError(estado_actual)
        
        # Verificar si estado_nuevo es válido
        if estado_nuevo not in transiciones_permitidas:
            raise TransicionEstadoInvalidaError(
                estado_actual, estado_nuevo, transiciones_permitidas
            )
