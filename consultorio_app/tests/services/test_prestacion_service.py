import pytest
from app.services.prestacion.crear_prestacion_service import CrearPrestacionService
from app.services.common import DatosInvalidosError, PracticaNoEncontradaError
from tests.factories.data import make_paciente, make_practica


def test_crear_prestacion_con_descuentos(db_session):
    paciente = make_paciente(dni="77777777")
    p1 = make_practica(codigo="P001", monto=1000)
    p2 = make_practica(codigo="P002", monto=500)

    prestacion = CrearPrestacionService.execute({
        'paciente_id': paciente.id,
        'descripcion': 'Test prestacion',
        'practicas': [p1.id, p2.id],
        'descuento_porcentaje': 10,
        'descuento_fijo': 100,
    })

    # subtotal = 1000 + 500 = 1500
    # 10% desc -> 1350
    # -100 -> 1250
    assert abs(prestacion.monto - 1250) < 0.01
    assert len(prestacion.practicas) == 2


def test_crear_prestacion_falta_practicas(db_session):
    paciente = make_paciente(dni="88888888")
    with pytest.raises(DatosInvalidosError):
        CrearPrestacionService.execute({
            'paciente_id': paciente.id,
            'descripcion': 'Sin practicas',
            'practicas': [],
        })


def test_crear_prestacion_practica_no_encontrada(db_session):
    paciente = make_paciente(dni="99999999")
    with pytest.raises(PracticaNoEncontradaError):
        CrearPrestacionService.execute({
            'paciente_id': paciente.id,
            'descripcion': 'Practica missing',
            'practicas': [12345],
        })
