def test_login_page_loads(client):
    resp = client.get('/login')
    assert resp.status_code == 200
    assert b'Iniciar Sesi' in resp.data  # tolerante a acentos
