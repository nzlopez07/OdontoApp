from app.models import Prestacion
from tests.factories.data import make_usuario, make_paciente, make_practica


def login(client, username, password):
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)


def test_listar_prestaciones_por_paciente(app, client, db_session):
    app.config['LOGIN_DISABLED'] = False
    user = make_usuario(username='odo9', rol='ODONTOLOGA', password='secret')
    login(client, 'odo9', 'secret')
    p = make_paciente(dni='11220033')

    resp = client.get(f'/pacientes/{p.id}/prestaciones')
    assert resp.status_code == 200


def test_nueva_prestacion_flow(app, client, db_session):
    app.config['LOGIN_DISABLED'] = False
    user = make_usuario(username='odo10', rol='ODONTOLOGA', password='secret')
    login(client, 'odo10', 'secret')
    p = make_paciente(dni='99887766')
    practica = make_practica(codigo='PR-100', descripcion='Consulta', monto=500)

    form_data = {
        'paciente_id': p.id,
        'descripcion': 'Prestación de prueba',
        'monto': '500.00',
        'descuento_porcentaje': '0',
        'descuento_fijo': '0',
        'observaciones': 'Observaciones',
        'practica_ids[]': [practica.id],
    }
    resp = client.post('/prestaciones/nueva', data=form_data, follow_redirects=False)
    assert resp.status_code in (302, 303)
    assert f'/pacientes/{p.id}' in resp.headers.get('Location', '')

    assert Prestacion.query.count() == 1
    pr = Prestacion.query.first()
    assert pr.paciente_id == p.id
    assert pr.descripcion == 'Prestación de prueba'
