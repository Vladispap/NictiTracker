from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QProgressDialog, QMessageBox
from app.ui.widgets.video_selector_widget import VideoSelectorWidget
from app.ui.widgets.execution_params_widget import ExecutionParamsWidget
from app.ui.widgets.plant_viewer_qt import PlantViewerWidget
from app.main_controller import VideoProcessingWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NictiTracker")
        self.resize(1000, 600)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal horizontal
        layout = QHBoxLayout()
        central_widget.setLayout(layout)

        # Sidebar izquierda: selector de videos
        self.video_selector = VideoSelectorWidget()
        layout.addWidget(self.video_selector, stretch=1)

        # Área principal derecha
        right_area = QVBoxLayout()

        # Área principal de visualización (placeholder)
        self.main_area = QWidget()
        main_layout = QVBoxLayout()
        self.main_area.setLayout(main_layout)
        # main_layout.addWidget(QLabel("Aquí se mostrarán los resultados o visualizaciones"))
        self.planw_viewer = PlantViewerWidget()
        main_layout.addWidget(self.planw_viewer, stretch=3)

        right_area.addWidget(self.main_area, stretch=3)

        # Parámetros de ejecución abajo
        self.execution_params = ExecutionParamsWidget()
        right_area.addWidget(self.execution_params, stretch=1)

        # Botón de ejecución debajo de los parámetros
        self.btn_ejecutar = QPushButton("Ejecutar análisis")
        self.btn_ejecutar.clicked.connect(self.run_detection)
        right_area.addWidget(self.btn_ejecutar)

        # Agregar el área derecha completa
        container = QWidget()
        container.setLayout(right_area)
        layout.addWidget(container, stretch=3)

    def run_detection(self):
        video_paths = self.video_selector.obtener_videos_ordenados()
        params = self.execution_params.get_params()

        if not video_paths:
            QMessageBox.warning(self, "Error", "Por favor, seleccione al menos un video.")
            return

        if not params["output_dir"]:
            QMessageBox.warning(self, "Error", "Por favor, seleccione una carpeta de exportación.")
            return
        
        if params["min_per_frame"] <= 0:
            QMessageBox.warning(self, "Error", "Los minutos por frame deben ser mayores a 0.")
            return
        
        if params["frame_skip"] <= 0:
            QMessageBox.warning(self, "Error", "Los frames a saltar deben ser 1 o mayores.")
            return 
        
        if not params["init_time"]:
            QMessageBox.warning(self, "Error", "Por favor, seleccione una hora inicial válida.")
            return

        self.worker = VideoProcessingWorker(
            video_paths=video_paths,
            output_dir=params["output_dir"],
            frame_skip=params["frame_skip"],
            init_time=params["init_time"],
            min_per_frame=params["min_per_frame"]
        )

        self.progress_dialog = QProgressDialog("Procesando...", "Cancelar", 0, 100, self)
        self.progress_dialog.setWindowTitle("Progreso de Detección")
        self.progress_dialog.setValue(0)
        self.progress_dialog.canceled.connect(self.cancel_detection)
        self.progress_dialog.show()

        self.worker.progress_changed.connect(self.progress_dialog.setValue)
        self.worker.finished.connect(self.on_detection_finished)
        self.worker.cancelled.connect(self.on_detection_cancelled)
        # try:
        #     self.warmup_yolo_model()
        # except Exception as e:
        #     print(f"Error al calentar el modelo YOLO: {e}")
        self.worker.start()

    def cancel_detection(self):
        if hasattr(self, 'worker'):
            self.worker.stop()

    def on_detection_finished(self, output_dir):
        self.progress_dialog.close()
        QMessageBox.information(self, "Detección completada", f"Resultados exportados a: {output_dir}")
        # self.plant_viewer.load_output(output_dir) TODO

    def on_detection_cancelled(self):
        self.progress_dialog.close()
        QMessageBox.warning(self, "Cancelado", "La detección fue cancelada por el usuario.")


    # def warmup_yolo_model(self):
    #     from app.utils.yolo_detect import get_model
    #     import numpy as np
    #     model = get_model()
    #     dummy = np.zeros((480, 640, 3), dtype=np.uint8)
    #     _ = model(dummy, verbose=False)  # run once in main thread to avoid crash

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
