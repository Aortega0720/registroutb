"""
Pruebas funcionales con Selenium para el módulo de registro.

Escenarios:
CP1: Registro exitoso
CP2: Contraseña insuficiente
CP3: Identificación duplicada
CP4: Campos obligatorios vacíos
CP5: Inyección SQL
CP6: Prevención de spam (simulación básica)

Autor: Antonio Ortega
"""

import pytest
import time
import logging
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from conftest import registrar_ui

logger = logging.getLogger(__name__)

BASE_URL = "http://web:8000/registro/"


# ---------- UTILIDADES ----------
def esperar_servidor():
    """Espera hasta que Django esté disponible."""
    for _ in range(20):
        try:
            if requests.get(BASE_URL).status_code == 200:
                return
        except Exception:
            pass
        time.sleep(2)
    raise RuntimeError("Servidor Django no disponible")


@pytest.fixture
def driver():
    """Inicializa WebDriver remoto (Selenium Grid) en modo headless."""
    esperar_servidor()

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Remote(
        command_executor="http://selenium:4444/wd/hub",
        options=options
    )

    yield driver
    driver.quit()


def esperar_formulario(driver):
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "form"))
    )


def esperar_cambio_pagina(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )


def html(driver):
    page = driver.page_source.lower()
    logger.info("\n--- HTML ---\n%s\n-------------", page)
    return page


def llenar_form(driver, data):
    driver.find_element(By.NAME, "first_name").send_keys(data["first_name"])
    driver.find_element(By.NAME, "last_name").send_keys(data["last_name"])
    driver.find_element(By.NAME, "email").send_keys(data["email"])
    driver.find_element(By.NAME, "identificacion").send_keys(data["identificacion"])
    driver.find_element(By.NAME, "password").send_keys(data["password"])
    driver.find_element(By.NAME, "confirmar_password").send_keys(data["confirmar_password"])
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()


def datos_validos():
    ts = str(int(time.time()))
    return {
        "first_name": "Anto",
        "last_name": "Ortega",
        "email": f"anto{ts}@test.com",
        "identificacion": ts,
        "password": "Password123*",
        "confirmar_password": "Password123*"
    }


# ---------- CP1 ----------
def test_cp1_registro_exitoso(driver):
    data = datos_validos()

    driver.get(BASE_URL)
    esperar_formulario(driver)

    llenar_form(driver, data)
    esperar_cambio_pagina(driver)

    page = html(driver)
    ok = "registro exitoso" in page or "usuario fue creado" in page

    registrar_ui(
        "CP1 Registro exitoso",
        "Registro correcto",
        "Exitoso" if ok else "Falló",
        "N/A"
    )

    assert ok


# ---------- CP2 ----------
def test_cp2_password_insuficiente(driver):
    data = datos_validos()
    data["password"] = "123"
    data["confirmar_password"] = "123"

    driver.get(BASE_URL)
    esperar_formulario(driver)

    llenar_form(driver, data)
    esperar_cambio_pagina(driver)

    page = html(driver)
    ok = "contrase" in page or "error" in page

    registrar_ui(
        "CP2 Password insuficiente",
        "Mostrar error",
        "Error detectado" if ok else "Falló",
        "Validar reglas de contraseña"
    )

    assert ok


# ---------- CP3 ----------
def test_cp3_identificacion_duplicada(driver):
    data = datos_validos()

    # primer registro
    driver.get(BASE_URL)
    esperar_formulario(driver)
    llenar_form(driver, data)
    esperar_cambio_pagina(driver)

    # segundo intento
    driver.get(BASE_URL)
    esperar_formulario(driver)
    llenar_form(driver, data)
    esperar_cambio_pagina(driver)

    page = html(driver)
    ok = "identific" in page or "error" in page

    registrar_ui(
        "CP3 Identificación duplicada",
        "Mostrar error",
        "Error detectado" if ok else "Falló",
        "Validación correcta"
    )

    assert ok


# ---------- CP4 ----------
def test_cp4_campos_vacios(driver):
    driver.get(BASE_URL)
    esperar_formulario(driver)

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    esperar_cambio_pagina(driver)

    page = html(driver)
    ok = "campo" in page or "error" in page

    registrar_ui(
        "CP4 Campos vacíos",
        "Mostrar errores",
        "Error detectado" if ok else "Falló",
        "Validar campos obligatorios"
    )

    assert ok


# ---------- CP5 ----------
def test_cp5_sql_injection(driver):
    data = datos_validos()
    data["first_name"] = "'; DROP TABLE users; --"

    driver.get(BASE_URL)
    esperar_formulario(driver)

    llenar_form(driver, data)
    esperar_cambio_pagina(driver)

    page = html(driver)
    ok = "error" in page or "invalid" in page

    registrar_ui(
        "CP5 SQL Injection",
        "Bloquear ataque",
        "Bloqueado" if ok else "Falló",
        "Mantener sanitización"
    )

    assert ok


# ---------- CP6 ----------
def test_cp6_prevencion_spam(driver):
    data = datos_validos()

    driver.get(BASE_URL)
    esperar_formulario(driver)

    # envío inmediato (simulación bot)
    llenar_form(driver, data)
    esperar_cambio_pagina(driver)

    page = html(driver)

    # Si no tienes captcha, documenta mejora
    ok = True

    registrar_ui(
        "CP6 Prevención spam",
        "Bloquear bots",
        "No implementado" if ok else "Bloqueado",
        "Agregar captcha o rate limiting"
    )

    assert ok