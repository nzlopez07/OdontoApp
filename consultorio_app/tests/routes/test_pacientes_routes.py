from datetime import date

from app.models import Paciente
from tests.factories.data import make_usuario


def login(client, username, password):
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)


def test_listar_pacientes_requires_login(app, client, db_session):
    app.config['LOGIN_DISABLED'] = False
    odonto = make_usuario(username='odo1', rol='ODONTOLOGA', password='secret')
    login(client, 'odo1', 'secret')

    resp = client.get('/pacientes')
    assert resp.status_code == 200


def test_crear_paciente_form_flow(app, client, db_session):
    app.config['LOGIN_DISABLED'] = False
    odonto = make_usuario(username='odo2', rol='ODONTOLOGA', password='secret')
    login(client, 'odo2', 'secret')

    form_data = {
        'nombre': 'Ana',
        'apellido': 'Perez',
        'dni': '12345678',
        'fecha_nac': date(1990, 1, 1).strftime('%Y-%m-%d'),
        'telefono': '1111-1111',
        'direccion': 'Calle Falsa 123',
        'barrio': '',
        'lugar_trabajo': '',
        'localidad_id': 0,
        'obra_social_id': 0,
        'nro_afiliado': '',
        'titular': '',
        'parentesco': '',
    }
    resp = client.post('/pacientes/nuevo', data=form_data, follow_redirects=False)
    assert resp.status_code in (302, 303)
    assert '/pacientes' in resp.headers.get('Location', '')

    assert Paciente.query.count() == 1
    p = Paciente.query.first()
    assert p.nombre == 'Ana'
    assert p.apellido == 'Perez'


def test_ver_paciente_detalle(app, client, db_session):
    app.config['LOGIN_DISABLED'] = False
    odonto = make_usuario(username='odo3', rol='ODONTOLOGA', password='secret')
    login(client, 'odo3', 'secret')

    # Crear paciente via servicio para tener ID
    form_data = {
        'nombre': 'Beto',
        'apellido': 'Garcia',
        'dni': '11112222',
        'fecha_nac': date(1985, 5, 10).strftime('%Y-%m-%d'),
        'localidad_id': 0,
        'obra_social_id': 0,
    }
    client.post('/pacientes/nuevo', data=form_data, follow_redirects=False)
    p = Paciente.query.first()

    resp = client.get(f'/pacientes/{p.id}')
    assert resp.status_code == 200
