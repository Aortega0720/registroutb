import json
import os
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

# Guardar en el directorio donde se ejecuta el script
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grafica_coverage.png")
plt.savefig(output_path)

print(f"Imagen guardada en {output_path}")