from PySide6.QtCore import QThread, Signal
import cv2
from datetime import datetime, timedelta
from app.utils.yolo_detect import detect_keypoints
from app.utils.angulos import get_leaf_angles
from app.utils.export import exportar_csv_por_planta
from app.utils.draw_detections import draw_detections

class VideoProcessingWorker(QThread):
    progress_changed = Signal(int)
    finished = Signal(str)
    cancelled = Signal()

    def __init__(self, video_paths, output_dir="output", frame_skip=1, init_time="1/1/2025 12:00", min_per_frame=1, visualization=False):
        super().__init__()
        self.video_paths = video_paths
        self.output_dir = output_dir
        self.frame_skip = frame_skip
        self.init_time = init_time
        self.min_per_frame = min_per_frame
        self.visualization = visualization
        self._is_running = True

    def run(self):
        data = []
        frame_id = 0
        frame_id_global = 0
        start_time = datetime.strptime(self.init_time, "%m/%d/%Y %H:%M")

        total_frames = self.estimate_total_frames()
        processed_frames = 0

        for video_path in self.video_paths:
            cap = cv2.VideoCapture(video_path)
            current_frame = 0

            while cap.isOpened() and self._is_running:
                ret = cap.grab()
                if not ret:
                    break

                if current_frame % self.frame_skip == 0:
                    ret, frame = cap.retrieve()
                    if not ret:
                        break

                    detections = detect_keypoints(frame)
                    
                    if self.visualization:
                        frame_with_detections = draw_detections(frame.copy(), detections)
                        height, width = frame_with_detections.shape[:2]
                        new_width = int(width * 0.5)
                        new_height = int(height * 0.5)
                        frame_with_detections = cv2.resize(frame_with_detections, (new_width, new_height))
                        cv2.imshow("Detections", frame_with_detections)
                        cv2.waitKey(1)

                    for plant_id, det in enumerate(detections):
                        angles = get_leaf_angles(det['keypoints'])
                        minutes_since_start = frame_id * self.min_per_frame * self.frame_skip
                        time_obj = start_time + timedelta(minutes=minutes_since_start)
                        time_str = time_obj.strftime("%m-%d-%Y %H:%M")
                        data.append([frame_id_global, time_str, plant_id, *angles])
                    
                    frame_id += 1
                    processed_frames += 1
                    percent_done = int((processed_frames / total_frames) * 100)
                    self.progress_changed.emit(percent_done)

                frame_id_global += 1
                current_frame += 1

            cap.release()

        if self._is_running:
            exportar_csv_por_planta(data, output_dir=self.output_dir)
            cv2.destroyAllWindows()
            self.finished.emit(self.output_dir)
        else:
            cv2.destroyAllWindows()
            self.cancelled.emit()

    def estimate_total_frames(self):
        total = 0
        for path in self.video_paths:
            cap = cv2.VideoCapture(path)
            total += int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) // self.frame_skip
            cap.release()
        return max(1, total)

    def stop(self):
        self._is_running = False
