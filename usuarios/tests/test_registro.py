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
    client.post("/registro/", data)

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
def test_formulario_get(client):
    """GET al formulario retorna 200 y el contexto incluye el form."""
    response = client.get("/registro/")

    registrar_backend(
        "Formulario GET",
        "HTTP 200 con form",
        f"HTTP {response.status_code}",
        "N/A"
    )

    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_passwords_no_coinciden(client):
    """Contraseñas distintas generan error de validación."""
    data = generar_datos_validos()
    data["confirmar_password"] = "OtraPass@999"

    response = client.post("/registro/", data)

    registrar_backend(
        "Passwords no coinciden",
        "Error de validación",
        limpiar_errores(response.context["form"]),
        "Validar coincidencia"
    )

    assert response.context["form"].errors


@pytest.mark.django_db
def test_nombre_invalido(client):
    """Nombre con dígitos genera error de validación."""
    data = generar_datos_validos()
    data["first_name"] = "Juan123"

    response = client.post("/registro/", data)

    registrar_backend(
        "Nombre inválido",
        "Error en nombre",
        limpiar_errores(response.context["form"]),
        "Solo letras permitidas"
    )

    assert response.context["form"].errors


@pytest.mark.django_db
def test_apellido_invalido(client):
    """Apellido con caracteres especiales genera error de validación."""
    data = generar_datos_validos()
    data["last_name"] = "Perez!"

    response = client.post("/registro/", data)

    registrar_backend(
        "Apellido inválido",
        "Error en apellido",
        limpiar_errores(response.context["form"]),
        "Solo letras permitidas"
    )

    assert response.context["form"].errors


@pytest.mark.django_db
def test_registro_exitoso_renderiza_plantilla(client):
    """Registro válido renderiza la plantilla de confirmación."""
    data = generar_datos_validos()
    response = client.post("/registro/", data)

    plantilla = response.templates[0].name if response.templates else "Sin plantilla"

    registrar_backend(
        "Plantilla registro exitoso",
        "registro_exitoso.html",
        plantilla,
        "N/A"
    )

    assert response.status_code == 200
    assert any("registro_exitoso" in t.name for t in response.templates)


@pytest.mark.django_db
def test_sql_injection(client):
    data = generar_datos_validos()
    data["first_name"] = "'; DROP TABLE users; --"

    client.post("/registro/", data)

    creado = User.objects.filter(email=data["email"]).exists()

    registrar_backend(
        "SQL Injection",
        "Bloqueado",
        "Bloqueado" if not creado else "Falla",
        "Mantener validación"
    )

    assert not creado


@pytest.mark.django_db
def test_password_sin_mayuscula(client):
    """Contraseña sin mayúscula genera error de validación."""
    data = generar_datos_validos()
    data["password"] = "admin@123"
    data["confirmar_password"] = "admin@123"

    response = client.post("/registro/", data)

    registrar_backend(
        "Password sin mayúscula",
        "Error de contraseña",
        limpiar_errores(response.context["form"]),
        "Exigir al menos una mayúscula"
    )

    assert response.context["form"].errors


@pytest.mark.django_db
def test_password_sin_caracter_especial(client):
    """Contraseña sin carácter especial genera error de validación."""
    data = generar_datos_validos()
    data["password"] = "Admin1234"
    data["confirmar_password"] = "Admin1234"

    response = client.post("/registro/", data)

    registrar_backend(
        "Password sin carácter especial",
        "Error de contraseña",
        limpiar_errores(response.context["form"]),
        "Exigir al menos un carácter especial"
    )

    assert response.context["form"].errors


@pytest.mark.django_db
def test_password_sin_minuscula(client):
    """Contraseña sin letra minúscula genera error de validación."""
    data = generar_datos_validos()
    data["password"] = "ADMIN@123"
    data["confirmar_password"] = "ADMIN@123"

    response = client.post("/registro/", data)

    registrar_backend(
        "Password sin minúscula",
        "Error de contraseña",
        limpiar_errores(response.context["form"]),
        "Exigir al menos una minúscula"
    )

    assert response.context["form"].errors


@pytest.mark.django_db
def test_password_sin_numero(client):
    """Contraseña sin número genera error de validación."""
    data = generar_datos_validos()
    data["password"] = "Admin@abc"
    data["confirmar_password"] = "Admin@abc"

    response = client.post("/registro/", data)

    registrar_backend(
        "Password sin número",
        "Error de contraseña",
        limpiar_errores(response.context["form"]),
        "Exigir al menos un dígito"
    )

    assert response.context["form"].errors


@pytest.mark.django_db
def test_perfil_str():
    """El método __str__ de Perfil retorna el username del usuario."""
    user = User.objects.create_user(
        username="strtest@test.com",
        email="strtest@test.com",
        password=PASSWORD_VALIDA
    )
    perfil = Perfil.objects.create(user=user, identificacion="99999999")

    registrar_backend(
        "Perfil __str__",
        "strtest@test.com",
        str(perfil),
        "N/A"
    )

    assert str(perfil) == "strtest@test.com"

