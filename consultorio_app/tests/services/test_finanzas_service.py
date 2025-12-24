from datetime import date
import pytest

from app.services.gasto.obtener_estadisticas_finanzas_service import ObtenerEstadisticasFinanzasService
from tests.factories.data import (
    make_gasto,
    make_obra_social,
    make_paciente,
    make_practica,
    make_prestacion,
    make_prestacion_practica,
)


def test_resumen_sin_datos(db_session):
    resumen = ObtenerEstadisticasFinanzasService.obtener_resumen()
    assert resumen['ingresos'] == 0.0
    assert resumen['egresos'] == 0.0
    assert resumen['balance'] == 0.0


def test_ingresos_por_tipo_vacio(db_session):
    data = ObtenerEstadisticasFinanzasService.obtener_ingresos_por_tipo()
    assert data == []


def test_resumen_con_prestacion(db_session):
    p = make_paciente(dni="11223344")
    make_prestacion(p, monto=2000)

    resumen = ObtenerEstadisticasFinanzasService.obtener_resumen()
    assert resumen['ingresos'] == 2000.0
    assert resumen['egresos'] == 0.0
    assert resumen['balance'] == 2000.0


def test_resumen_con_ingresos_y_gastos(db_session):
    p = make_paciente(dni="22334455")
    make_prestacion(p, monto=3000)
    make_gasto(monto=1200, categoria="OPERATIVO")
    make_gasto(monto=300, categoria="INSUMO")

    resumen = ObtenerEstadisticasFinanzasService.obtener_resumen()
    assert resumen['ingresos'] == 3000.0
    assert resumen['egresos'] == 1500.0
    assert resumen['balance'] == 1500.0


def test_ingresos_por_tipo_mixto(db_session):
    obra_social = make_obra_social(nombre="OSDE")

    paciente_particular = make_paciente(dni="30112233")
    paciente_os = make_paciente(dni="40112233", obra_social=obra_social)

    make_prestacion(paciente_particular, monto=1200)
    make_prestacion(paciente_os, monto=800)

    data = ObtenerEstadisticasFinanzasService.obtener_ingresos_por_tipo()
    data = sorted(data, key=lambda x: x['fuente'])

    assert data == [
        {'fuente': 'OSDE', 'total': 800.0, 'cantidad': 1},
        {'fuente': 'Particular', 'total': 1200.0, 'cantidad': 1},
    ]


def test_egresos_por_categoria(db_session):
    make_gasto(categoria="INSUMO", monto=200)
    make_gasto(categoria="INSUMO", monto=50)
    make_gasto(categoria="OPERATIVO", monto=100)

    data = ObtenerEstadisticasFinanzasService.obtener_egresos_por_categoria()
    data = sorted(data, key=lambda x: x['categoria'])

    assert data == [
        {'categoria': 'INSUMO', 'total': 250.0, 'cantidad': 2},
        {'categoria': 'OPERATIVO', 'total': 100.0, 'cantidad': 1},
    ]


def test_ingresos_por_practica_distribuye_por_cantidad(db_session):
    paciente = make_paciente(dni="55112233")
    prestacion = make_prestacion(paciente, monto=300)

    practica_1 = make_practica(codigo="PR-1", descripcion="Consulta", monto=100)
    practica_2 = make_practica(codigo="PR-2", descripcion="Radiografia", monto=200)

    make_prestacion_practica(prestacion, practica_1, cantidad=1)
    make_prestacion_practica(prestacion, practica_2, cantidad=2)

    data = ObtenerEstadisticasFinanzasService.obtener_ingresos_por_practica()

    assert len(data) == 2
    # Total 300 distribuido proporcionalmente (1 de 3 y 2 de 3)
    assert data[0]['codigo'] == 'PR-2'
    assert data[0]['cantidad'] == 2
    assert data[0]['total'] == pytest.approx(200.0)

    assert data[1]['codigo'] == 'PR-1'
    assert data[1]['cantidad'] == 1
    assert data[1]['total'] == pytest.approx(100.0)


def test_detalle_prestaciones_filtra_por_obra_social(db_session):
    obra_social = make_obra_social(nombre="IPSS")
    paciente_os = make_paciente(nombre="Beto", apellido="Garcia", dni="66112233", obra_social=obra_social)
    paciente_particular = make_paciente(nombre="Carla", apellido="Lopez", dni="77112233")

    prestacion_os = make_prestacion(paciente_os, monto=500)
    prestacion_particular = make_prestacion(paciente_particular, monto=400)

    practica_a = make_practica(codigo="DX01", descripcion="Diag", monto=100)
    practica_b = make_practica(codigo="DX02", descripcion="Diag 2", monto=200)

    make_prestacion_practica(prestacion_os, practica_a, cantidad=1)
    make_prestacion_practica(prestacion_os, practica_b, cantidad=2)

    # Otro registro que no debe aparecer por filtro de obra social
    make_prestacion_practica(prestacion_particular, practica_a, cantidad=1)

    data = ObtenerEstadisticasFinanzasService.obtener_detalle_prestaciones(obra_social="ipss")

    assert len(data) == 1
    detalle = data[0]
    assert detalle['paciente'] == 'Beto Garcia'
    assert detalle['obra_social'] == 'IPSS'
    assert detalle['monto'] == 500.0
    assert detalle['practicas'] == 'DX01 (1), DX02 (2)'


def test_evolucion_mensual_agrupa_por_mes(db_session):
    paciente = make_paciente(dni="88112233")

    # Ingresos
    make_prestacion(paciente, monto=500, fecha=date(2025, 1, 15))
    make_prestacion(paciente, monto=200, fecha=date(2025, 2, 10))

    # Egresos
    make_gasto(monto=100, fecha=date(2025, 1, 20))
    make_gasto(monto=50, fecha=date(2025, 2, 5))

    data = ObtenerEstadisticasFinanzasService.obtener_evolucion_mensual(2025)

    assert data['anio'] == 2025
    assert len(data['meses']) == 12

    enero = next(m for m in data['meses'] if m['mes'] == 1)
    febrero = next(m for m in data['meses'] if m['mes'] == 2)

    assert enero == {'mes': 1, 'nombre': 'Enero', 'ingresos': 500.0, 'egresos': 100.0, 'balance': 400.0}
    assert febrero == {'mes': 2, 'nombre': 'Febrero', 'ingresos': 200.0, 'egresos': 50.0, 'balance': 150.0}
