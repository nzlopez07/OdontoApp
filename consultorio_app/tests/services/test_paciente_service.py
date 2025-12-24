import pytest
from app.services.paciente.crear_paciente_service import CrearPacienteService
from app.services.common import PacienteDuplicadoError
from tests.factories.data import make_paciente


def test_crear_paciente_ok(db_session):
    paciente = CrearPacienteService.execute(
        nombre="Ana",
        apellido="Perez",
        dni="12345678",
        telefono="1111-1111",
    )
    assert paciente.id is not None
    assert paciente.dni == "12345678"


def test_crear_paciente_duplicado(db_session):
    make_paciente(dni="12345678")
    with pytest.raises(PacienteDuplicadoError):
        CrearPacienteService.execute(
            nombre="Ana",
            apellido="Perez",
            dni="12345678",
        )
