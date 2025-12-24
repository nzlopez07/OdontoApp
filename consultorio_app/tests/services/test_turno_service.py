import pytest
from datetime import date, time
from app.services.turno.agendar_turno_service import AgendarTurnoService
from app.services.common import TurnoSolapamientoError, PacienteNoEncontradoError
from tests.factories.data import make_paciente


def test_agendar_turno_ok(db_session):
    paciente = make_paciente(dni="55555555")
    turno = AgendarTurnoService.execute(
        paciente_id=paciente.id,
        fecha=date.today(),
        hora=time(10, 0),
        duracion=30,
    )
    assert turno.id is not None
    assert turno.estado == 'Confirmado'


def test_agendar_turno_solapado(db_session):
    paciente = make_paciente(dni="66666666")
    AgendarTurnoService.execute(
        paciente_id=paciente.id,
        fecha=date.today(),
        hora=time(9, 0),
        duracion=60,
    )
    with pytest.raises(TurnoSolapamientoError):
        AgendarTurnoService.execute(
            paciente_id=paciente.id,
            fecha=date.today(),
            hora=time(9, 30),
            duracion=30,
        )


def test_agendar_turno_paciente_inexistente(db_session):
    with pytest.raises(PacienteNoEncontradoError):
        AgendarTurnoService.execute(
            paciente_id=9999,
            fecha=date.today(),
            hora=time(11, 0),
            duracion=30,
        )
