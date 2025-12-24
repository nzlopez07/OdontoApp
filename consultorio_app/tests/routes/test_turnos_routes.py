from datetime import date, time, timedelta

from app.models import Turno, Paciente
from tests.factories.data import make_usuario, make_paciente


def login(client, username, password):
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)


def test_listar_turnos_agenda(app, client, db_session):
    app.config['LOGIN_DISABLED'] = False
    user = make_usuario(username='odo4', rol='ODONTOLOGA', password='secret')
    login(client, 'odo4', 'secret')

    resp = client.get('/turnos')
    assert resp.status_code == 200


def test_crear_turno_form_view(app, client, db_session):
    app.config['LOGIN_DISABLED'] = False
    user = make_usuario(username='odo5', rol='ODONTOLOGA', password='secret')
    login(client, 'odo5', 'secret')
    resp = client.get('/turnos/nuevo')
    assert resp.status_code == 200


def test_cambiar_estado_turno(app, client, db_session):
    app.config['LOGIN_DISABLED'] = False
    user = make_usuario(username='odo6', rol='ODONTOLOGA', password='secret')
    login(client, 'odo6', 'secret')
    p = make_paciente(dni='66778899')

    # Crear turno directamente en DB
    from app.database import db
    from app.models import Turno
    t = Turno(paciente_id=p.id, fecha=(date.today() + timedelta(days=2)), hora=time(9, 0), duracion=60, estado='Pendiente')
    db.session.add(t)
    db.session.commit()

    # Cambiar estado a Confirmado
    resp = client.post(f'/turnos/{t.id}/estado', data={'estado': 'Confirmado'}, follow_redirects=False)
    assert resp.status_code in (302, 303)
    t2 = Turno.query.get(t.id)
    assert t2.estado == 'Confirmado'
