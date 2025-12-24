def test_admin_logs_access_when_login_disabled(client):
    resp = client.get('/admin/logs')
    # Con LOGIN_DISABLED=1 en test, debe permitir acceso
    assert resp.status_code == 200
    assert b'Logs del Sistema' in resp.data
