from app import app

def test_login_page():
    client = app.test_client()
    response = client.get('/login')
    assert response.status_code == 200

def test_register_page():
    client = app.test_client()
    response = client.get('/register')
    assert response.status_code == 200

def test_admin_krever_innlogging():
    client = app.test_client()
    response = client.get('/admin')
    assert response.status_code == 302
    