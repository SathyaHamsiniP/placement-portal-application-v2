import pytest
from backend.main import create_app
from backend.database import db

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200


def test_register(client):
    response = client.post("/api/auth/register/student", json={
        "username": "student1",
        "email": "student@test.com",
        "password": "pass123",
        "full_name": "Test Student",
        "roll_number": "21f1001234",
        "cgpa": 8.5,
        "grad_year": 2025
    })
    assert response.status_code == 201


def test_short_password(client):
    response = client.post("/api/auth/register/student", json={
        "username": "student2",
        "email": "student2@test.com",
        "password": "123",
        "full_name": "Short Pass",
        "roll_number": "21f1001235",
        "cgpa": 7.0,
        "grad_year": 2025
    })
    assert response.status_code == 400


def test_login(client):
    # First register
    client.post("/api/auth/register/student", json={
        "username": "student3",
        "email": "student3@test.com",
        "password": "pass123",
        "full_name": "Login Student",
        "roll_number": "21f1001236",
        "cgpa": 8.0,
        "grad_year": 2025
    })

    # Then login
    response = client.post("/api/auth/login", json={
        "username": "student3",
        "password": "pass123"
    })

    assert response.status_code == 200
    assert "token" in response.get_json()   # key is 'token', not 'access_token'


def test_wrong_password(client):
    response = client.post("/api/auth/login", json={
        "username": "unknown",
        "password": "wrong"
    })
    assert response.status_code == 401


def test_dashboard_without_token(client):
    response = client.get("/api/student/dashboard")
    assert response.status_code == 401
