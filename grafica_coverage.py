import json
import matplotlib.pyplot as plt

# Leer coverage
with open("coverage.json") as f:
    data = json.load(f)

files = data["files"]

labels = []
values = []

for file, info in files.items():
    labels.append(file.split("/")[-1])
    values.append(info["summary"]["percent_covered"])

# Crear gráfica
plt.figure()
plt.bar(labels, values)
plt.xticks(rotation=45)
plt.ylabel("Cobertura (%)")
plt.title("Cobertura por archivo")
plt.tight_layout()

# 👇 FORZAR GUARDADO ABSOLUTO
plt.savefig("/app/grafica_coverage.png")

print("✅ Imagen guardada en /app/grafica_coverage.png")