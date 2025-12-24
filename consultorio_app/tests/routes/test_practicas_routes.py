from app.models import Practica, ObraSocial
from tests.factories.data import make_usuario, make_obra_social


def login(client, username, password):
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)


def test_listar_practicas(app, client, db_session):
    app.config['LOGIN_DISABLED'] = False
    user = make_usuario(username='odo7', rol='ODONTOLOGA', password='secret')
    login(client, 'odo7', 'secret')

    resp = client.get('/practicas')
    assert resp.status_code == 200


def test_crear_practica_con_obra_social(app, client, db_session):
    app.config['LOGIN_DISABLED'] = False
    user = make_usuario(username='odo8', rol='ODONTOLOGA', password='secret')
    login(client, 'odo8', 'secret')
    os = make_obra_social(nombre='IPSS')

    form_data = {
        'codigo': 'P001',
        'descripcion': 'Limpieza',
        'obra_social_id': os.id,
        'monto_unitario': '1500.00',
    }
    resp = client.post('/practicas/nueva', data=form_data, follow_redirects=False)
    assert resp.status_code in (302, 303)
    assert '/practicas' in resp.headers.get('Location', '')

    assert Practica.query.count() == 1
    pr = Practica.query.first()
    assert pr.codigo == 'P001'
    assert pr.obra_social_id == os.id
