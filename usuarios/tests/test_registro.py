"""
Pruebas unitarias del registro de usuarios.
"""

import pytest
import time
import logging
from django.contrib.auth.models import User
from usuarios.models import Perfil

from conftest import registrar_backend

logger = logging.getLogger(__name__)

PASSWORD_VALIDA = "Admin@123"


def generar_datos_validos():
    ts = str(int(time.time()))
    return {
        "first_name": "Juan",
        "last_name": "Perez",
        "email": f"user{ts}@test.com",
        "identificacion": ts,
        "password": PASSWORD_VALIDA,
        "confirmar_password": PASSWORD_VALIDA
    }

def limpiar_errores(form):
    """
    Convierte los errores del formulario en texto plano.
    """
    errores = []

    for campo, lista in form.errors.items():
        for error in lista:
            errores.append(f"{campo}: {error}")

    return " | ".join(errores)


@pytest.mark.django_db
def test_registro_usuario_valido(client):
    data = generar_datos_validos()
    response = client.post("/registro/", data)

    creado = User.objects.filter(email=data["email"]).exists()

    registrar_backend(
        "Registro válido",
        "Usuario creado",
        "Usuario creado" if creado else "Error",
        "N/A"
    )

    assert creado


@pytest.mark.django_db
def test_correo_duplicado(client):
    data = generar_datos_validos()

    User.objects.create_user(
        username=data["email"],
        email=data["email"],
        password=PASSWORD_VALIDA
    )

    response = client.post("/registro/", data)

    registrar_backend(
        "Correo duplicado",
        "Mostrar error",
        limpiar_errores(response.context["form"]),
        "Validación correcta"
    )

    assert response.context["form"].errors


@pytest.mark.django_db
def test_password_corta(client):
    data = generar_datos_validos()
    data["password"] = "123"
    data["confirmar_password"] = "123"

    response = client.post("/registro/", data)

    registrar_backend(
        "Password corta",
        "Error",
        limpiar_errores(response.context["form"]),
        "Mejorar pruebas"
    )

    assert response.context["form"].errors


@pytest.mark.django_db
def test_identificacion_duplicada(client):
    data = generar_datos_validos()

    user = User.objects.create_user(
        username="test@test.com",
        email="test@test.com",
        password=PASSWORD_VALIDA
    )

    Perfil.objects.create(user=user, identificacion=data["identificacion"])

    response = client.post("/registro/", data)

    registrar_backend(
        "Identificación duplicada",
        "Error",
        limpiar_errores(response.context["form"]),
        "Correcto"
    )

    assert response.context["form"].errors


@pytest.mark.django_db
def test_campos_vacios(client):
    response = client.post("/registro/", {})

    registrar_backend(
        "Campos vacíos",
        "Error",
        limpiar_errores(response.context["form"]),
        "Validar campos"
    )

    assert not response.context["form"].is_valid()


@pytest.mark.django_db
def test_sql_injection(client):
    data = generar_datos_validos()
    data["first_name"] = "'; DROP TABLE users; --"

    response = client.post("/registro/", data)

    creado = User.objects.filter(email=data["email"]).exists()

    registrar_backend(
        "SQL Injection",
        "Bloqueado",
        "Bloqueado" if not creado else "Falla",
        "Mantener validación"
    )

    assert not creado

