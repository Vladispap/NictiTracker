from ultralytics import YOLO
from pathlib import Path

_model = None  # cache model

def get_model():
    global _model
    if _model is None:
        model_path = Path(__file__).parent.parent / "model" / "model3.pt"
        _model = YOLO(str(model_path))
    return _model

def detect_keypoints(frame, conf=0.6):
    """
    Detecta las plantas detectadas en el frame y los keypoints de estas (punta1, peciolo1, punta2, peciolo2).
    Args:
        frame (numpy.ndarray): Frame de video en el que se detectarán los puntos clave.
    Returns:
        detections (list): Lista de detecciones, cada una conteniendo el bounding box y los keypoints detectados.
    """
    # results = model(source=frame, conf=conf)
    model = get_model()
    results = model(frame, conf=conf, verbose=False)
    detections = []

    for r in results:
        if r.keypoints is None:
            continue
        for box, keypoints in zip(r.boxes.xyxy, r.keypoints.xy):
            detections.append({
                'box': box.cpu().numpy(),
                'keypoints': keypoints.cpu().numpy()
            })
    detections.sort(key=lambda x: x['box'][0])
    return detections