import cv2

def draw_detections(frame, detections):
    for det in detections:
        if 'box' in det:
            x1, y1, x2, y2 = map(int, det['box'])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        if 'keypoints' in det:
            for (x, y) in det['keypoints']:
                cv2.circle(frame, (int(x), int(y)), 3, (0, 0, 255), -1)

    return frame
