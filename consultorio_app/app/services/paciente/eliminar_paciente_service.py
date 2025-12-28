"""
Servicio para eliminar pacientes y sus datos relacionados.

Reglas:
- Si el paciente no existe, dispara PacienteNoEncontradoError.
- Elimina en cascada turnos y odontogramas (según modelo Paciente).
"""
from typing import Dict, Any
from app.database.session import DatabaseSession
from app.models import Paciente
from app.services.common import PacienteNoEncontradoError


class EliminarPacienteService:
    """Caso de uso para eliminar un paciente."""

    @staticmethod
    def execute(paciente_id: int) -> Dict[str, Any]:
        """
        Elimina un paciente por ID.

        Args:
            paciente_id: ID del paciente a eliminar

        Returns:
            Dict con resultado {'success': bool, 'mensaje': str}

        Raises:
            PacienteNoEncontradoError: si no se encuentra el paciente
        """
        session = DatabaseSession.get_instance().session

        paciente = session.get(Paciente, paciente_id)
        if not paciente:
            raise PacienteNoEncontradoError(paciente_id)

        session.delete(paciente)
        session.commit()

        return {
            'success': True,
            'mensaje': f"Paciente #{paciente_id} eliminado correctamente",
        }
