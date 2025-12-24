from datetime import date

from app.models import Gasto
from tests.factories.data import make_usuario


def login(client, username, password):
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)


def test_dashboard_requires_duena_role(app, client, db_session):
    app.config['LOGIN_DISABLED'] = False

    # Usuario ODONTOLOGA no debe acceder
    odonto = make_usuario(username='odonto', rol='ODONTOLOGA', password='secret')
    resp_login = login(client, 'odonto', 'secret')
    assert resp_login.status_code in (200, 302, 303)

    resp = client.get('/finanzas/dashboard')
    # Redirige a index por falta de permisos
    assert resp.status_code in (302, 303)
    # La ubicación típicamente termina en '/'
    assert resp.headers.get('Location', '').endswith('/')

    # Usuario DUEÑA sí accede
    # Cerrar sesión del usuario anterior
    client.get('/logout')
    duena = make_usuario(username='duena', rol='DUEÑA', password='secret')
    resp_login2 = login(client, 'duena', 'secret')
    assert resp_login2.status_code in (200, 302, 303)

    resp2 = client.get('/finanzas/dashboard')
    assert resp2.status_code == 200


def test_api_resumen_returns_json(app, client, db_session):
    app.config['LOGIN_DISABLED'] = False
    duena = make_usuario(username='duena2', rol='DUEÑA', password='secret')
    login(client, 'duena2', 'secret')

    resp = client.get('/finanzas/api/resumen')
    assert resp.status_code == 200
    data = resp.get_json()
    assert set(data.keys()) >= {'ingresos', 'egresos', 'balance'}


def test_gastos_list_page(app, client, db_session):
    app.config['LOGIN_DISABLED'] = False
    duena = make_usuario(username='duena3', rol='DUEÑA', password='secret')
    login(client, 'duena3', 'secret')

    resp = client.get('/finanzas/gastos')
    assert resp.status_code == 200


def test_nuevo_gasto_creates_record(app, client, db_session):
    app.config['LOGIN_DISABLED'] = False
    duena = make_usuario(username='duena4', rol='DUEÑA', password='secret')
    login(client, 'duena4', 'secret')

    form_data = {
        'descripcion': 'Compra de insumos',
        'monto': '123.45',
        'fecha': date(2025, 1, 10).strftime('%Y-%m-%d'),
        'categoria': 'INSUMO',
        'observaciones': 'Guantes y gasas',
    }
    resp = client.post('/finanzas/gastos/nuevo', data=form_data, follow_redirects=False)

    # Debe redirigir a la lista de gastos
    assert resp.status_code in (302, 303)
    assert '/finanzas/gastos' in resp.headers.get('Location', '')

    # Verificar que el gasto fue creado
    assert Gasto.query.count() == 1
    g = Gasto.query.first()
    assert g.descripcion == 'Compra de insumos'
    assert g.categoria == 'INSUMO'


def test_reportes_page(app, client, db_session):
    app.config['LOGIN_DISABLED'] = False
    duena = make_usuario(username='duena5', rol='DUEÑA', password='secret')
    login(client, 'duena5', 'secret')

    resp = client.get('/finanzas/reportes?anio=2025')
    assert resp.status_code == 200
