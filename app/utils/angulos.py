import numpy as np

def calculate_angleIzq(p1, p2):
    v = np.array(p2) - np.array(p1)
    angle = np.degrees(np.arctan2(v[1], v[0]))
    if angle <= -90:
        angle += 360
    return angle - 90

def calculate_angleDer(p1, p2):
    v = np.array(p2) - np.array(p1)
    angle = np.degrees(np.arctan2(+v[1], -v[0]))
    if angle <= -90:
        angle += 360
    return angle - 90

def get_leaf_angles(keypoints):
    """
    Calcula los ángulos de las hojas basándose en los keypoints detectados.
    Args:
        keypoints (list): Lista de keypoints detectados
    Returns:
        ang_izq (float): Ángulo de la hoja izquierda
        ang_der (float): Ángulo de la hoja derecha
    """

    punta1, peciolo1, punta2, peciolo2 = keypoints
    ang_izq = calculate_angleIzq(peciolo1, punta1)
    ang_der = calculate_angleDer(peciolo2, punta2)

    return ang_izq, ang_der
