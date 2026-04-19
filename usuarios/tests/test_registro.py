import pytest
from django.contrib.auth.models import User
from usuarios.models import Perfil


# contraseña válida según tus reglas
PASSWORD_VALIDA = "Admin@123"


@pytest.mark.django_db
def test_registro_usuario_valido(client):

    response = client.post("/registro/", {
        "first_name": "Juan",
        "last_name": "Perez",
        "email": "juan@test.com",
        "identificacion": "123456",
        "password": PASSWORD_VALIDA,
        "confirmar_password": PASSWORD_VALIDA
    })

    assert response.status_code == 200
    assert User.objects.filter(email="juan@test.com").exists()
    assert Perfil.objects.filter(identificacion="123456").exists()


@pytest.mark.django_db
def test_correo_duplicado(client):

    User.objects.create_user(
        username="test@test.com",
        email="test@test.com",
        password=PASSWORD_VALIDA
    )

    response = client.post("/registro/", {
        "first_name": "Pedro",
        "last_name": "Gomez",
        "email": "test@test.com",
        "identificacion": "999999",
        "password": PASSWORD_VALIDA,
        "confirmar_password": PASSWORD_VALIDA
    })

    assert b"correo ya est" in response.content.lower()


@pytest.mark.django_db
def test_password_corta(client):

    response = client.post("/registro/", {
        "first_name": "Ana",
        "last_name": "Lopez",
        "email": "ana@test.com",
        "identificacion": "888888",
        "password": "Ab1@",
        "confirmar_password": "Ab1@"
    })

    assert b"contrase" in response.content.lower()


@pytest.mark.django_db
def test_identificacion_duplicada(client):

    user = User.objects.create_user(
        username="test2@test.com",
        email="test2@test.com",
        password=PASSWORD_VALIDA
    )

    Perfil.objects.create(
        user=user,
        identificacion="111111"
    )

    response = client.post("/registro/", {
        "first_name": "Luis",
        "last_name": "Martinez",
        "email": "nuevo@test.com",
        "identificacion": "111111",
        "password": PASSWORD_VALIDA,
        "confirmar_password": PASSWORD_VALIDA
    })

    assert b"identificaci" in response.content.lower()


@pytest.mark.django_db
def test_password_no_coincide(client):

    response = client.post("/registro/", {
        "first_name": "Carlos",
        "last_name": "Ruiz",
        "email": "carlos@test.com",
        "identificacion": "555555",
        "password": PASSWORD_VALIDA,
        "confirmar_password": "OtraPass@123"
    })

    assert b"contrase" in response.content.lower()