import csv
import numpy as np
import os
from collections import defaultdict




def exportar_csv_por_planta(data, output_dir="resultados_por_planta"):
    """
    Exporta un CSV por cada planta, con columnas: frame, ang_izq, ang_der.

    Args:
        data (list): Lista de filas [frame_id, plant_id, ang_izq, ang_der]
        output_dir (str): Carpeta de salida
        modo (str): 'descartar' o 'rellenar'
    """

    plantas = defaultdict(list)
    for frame, time_str, plant_id, ang_izq, ang_der in data:
        plantas[plant_id].append([frame, time_str, ang_izq, ang_der])

    os.makedirs(output_dir, exist_ok=True)

    # Plantas con muy pocos datos se descartan
    longitudes = [len(filas) for filas in plantas.values()]
    if not longitudes:
        return
    promedio = np.mean(longitudes)
    umbral = promedio * 0.5

    for plant_id, filas in plantas.items():
        if len(filas) < umbral:
            continue  # descartar plantas con muy pocos datos
        file_path = os.path.join(output_dir, f"planta_{plant_id}.csv")
        with open(file_path, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["frame", "time", "ang_izq", "ang_der"])
            writer.writerows(filas)
