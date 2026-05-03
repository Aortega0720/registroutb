"""
Configuración global de pytest para consolidar resultados.
"""

resultados_backend = []
resultados_ui = []


def registrar_backend(caso, esperado, obtenido, sugerencia):
    resultados_backend.append({
        "Caso": caso,
        "Esperado": esperado,
        "Obtenido": obtenido,
        "Sugerencia": sugerencia
    })


def registrar_ui(caso, esperado, obtenido, sugerencia):
    resultados_ui.append({
        "Caso": caso,
        "Esperado": esperado,
        "Obtenido": obtenido,
        "Sugerencia": sugerencia
    })


def pytest_sessionfinish(session, exitstatus):
    print("\n\n================ RESULTADOS BACKEND =================\n")

    print(f"{'Caso':<30} | {'Esperado':<25} | {'Obtenido':<25} | {'Sugerencia'}")
    print("-" * 110)

    for r in resultados_backend:
        print(f"{r['Caso']:<30} | {r['Esperado']:<25} | {r['Obtenido']:<25} | {r['Sugerencia']}")

    print("\n\n================ RESULTADOS UI =================\n")

    print(f"{'Caso':<30} | {'Esperado':<25} | {'Obtenido':<25} | {'Sugerencia'}")
    print("-" * 110)

    for r in resultados_ui:
        print(f"{r['Caso']:<30} | {r['Esperado']:<25} | {r['Obtenido']:<25} | {r['Sugerencia']}")