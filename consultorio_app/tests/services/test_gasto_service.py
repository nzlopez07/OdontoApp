import pytest
from datetime import date

from app.services.gasto.crear_gasto_service import CrearGastoService
from app.services.gasto.listar_gastos_service import ListarGastosService
from app.services.common.exceptions import OdontoAppError
from tests.factories.data import make_usuario, make_gasto


def test_crear_gasto_valido(db_session):
    usuario = make_usuario(username="duena", rol="DUENA")
    gasto = CrearGastoService.crear(
        descripcion="Compra de insumos",
        monto=250.5,
        fecha=date(2025, 1, 10),
        categoria="INSUMO",
        creado_por_id=usuario.id,
        observaciones="Guantes y gasas"
    )

    assert gasto.id is not None
    assert gasto.descripcion == "Compra de insumos"
    assert float(gasto.monto) == 250.5
    assert gasto.categoria == "INSUMO"
    assert gasto.creado_por_id == usuario.id


def test_crear_gasto_categoria_invalida(db_session):
    usuario = make_usuario(username="duena2", rol="DUENA")
    with pytest.raises(OdontoAppError) as exc:
        CrearGastoService.crear(
            descripcion="Pago servicio",
            monto=100,
            fecha=date.today(),
            categoria="INVALIDA",
            creado_por_id=usuario.id,
        )
    assert exc.value.codigo == "CATEGORIA_INVALIDA"


def test_crear_gasto_monto_invalido(db_session):
    usuario = make_usuario(username="duena3", rol="DUENA")
    with pytest.raises(OdontoAppError) as exc:
        CrearGastoService.crear(
            descripcion="Pago",
            monto=0,
            fecha=date.today(),
            categoria="OPERATIVO",
            creado_por_id=usuario.id,
        )
    assert exc.value.codigo == "MONTO_INVALIDO"


def test_crear_gasto_usuario_inexistente(db_session):
    with pytest.raises(OdontoAppError) as exc:
        CrearGastoService.crear(
            descripcion="Pago",
            monto=100,
            fecha=date.today(),
            categoria="OPERATIVO",
            creado_por_id=9999,
        )
    assert exc.value.codigo == "USUARIO_NO_ENCONTRADO"


def test_listar_gastos_sin_filtros(db_session):
    usuario = make_usuario(username="duena4", rol="DUENA")
    make_gasto(descripcion="A", monto=50, fecha=date(2025, 1, 1), categoria="INSUMO", creado_por=usuario)
    make_gasto(descripcion="B", monto=150, fecha=date(2025, 1, 2), categoria="OPERATIVO", creado_por=usuario)

    gastos = ListarGastosService.listar()
    assert [g.descripcion for g in gastos] == ["B", "A"]


def test_listar_gastos_filtrando_por_fecha_y_categoria(db_session):
    usuario = make_usuario(username="duena5", rol="DUENA")
    make_gasto(descripcion="A", monto=50, fecha=date(2025, 1, 1), categoria="INSUMO", creado_por=usuario)
    make_gasto(descripcion="B", monto=150, fecha=date(2025, 1, 10), categoria="OPERATIVO", creado_por=usuario)
    make_gasto(descripcion="C", monto=75, fecha=date(2025, 1, 15), categoria="INSUMO", creado_por=usuario)

    gastos = ListarGastosService.listar(
        fecha_desde=date(2025, 1, 5),
        fecha_hasta=date(2025, 1, 31),
        categoria="INSUMO"
    )
    assert [g.descripcion for g in gastos] == ["C"]


def test_obtener_por_id(db_session):
    usuario = make_usuario(username="duena6", rol="DUENA")
    g = make_gasto(descripcion="X", monto=100, fecha=date(2025, 2, 1), categoria="OTRO", creado_por=usuario)

    encontrado = ListarGastosService.obtener_por_id(g.id)
    assert encontrado is not None
    assert encontrado.descripcion == "X"
    assert ListarGastosService.obtener_por_id(9999) is None
