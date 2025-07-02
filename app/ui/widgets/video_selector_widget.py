from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QFileDialog, QLabel
)
from PySide6.QtCore import Qt
import os

class VideoSelectorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.video_paths = []
        self.orden_personalizado = False

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Barra de botones
        btn_bar = QHBoxLayout()

        self.btn_cargar = QPushButton("Cargar videos")
        self.btn_carpeta = QPushButton("Seleccionar carpeta")
        self.btn_limpiar = QPushButton("Limpiar videos")
        self.btn_ordenar = QPushButton("Ordenar alfabéticamente")

        self.btn_cargar.clicked.connect(self.cargar_videos)
        self.btn_carpeta.clicked.connect(self.cargar_carpeta)
        self.btn_limpiar.clicked.connect(self.limpiar_videos)
        self.btn_ordenar.clicked.connect(self.ordenar_alfabeticamente)

        for btn in [self.btn_cargar, self.btn_carpeta, self.btn_limpiar, self.btn_ordenar]:
            btn_bar.addWidget(btn)

        layout.addLayout(btn_bar)

        # Lista de videos
        self.lista_videos = QListWidget()
        layout.addWidget(self.lista_videos)

        self.setLayout(layout)

    def cargar_videos(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Seleccionar videos", "", "Videos (*.mp4 *.avi *.mov)")
        if paths:
            self.video_paths.extend(paths)
            self.orden_personalizado = False
            self.actualizar_lista()

    def cargar_carpeta(self):
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")
        if carpeta:
            archivos = [os.path.join(carpeta, f) for f in os.listdir(carpeta)
                        if f.lower().endswith((".mp4", ".avi", ".mov"))]
            self.video_paths.extend(archivos)
            self.orden_personalizado = False
            self.actualizar_lista()
        print(self.video_paths)

    def limpiar_videos(self):
        self.video_paths = []
        self.lista_videos.clear()

    def ordenar_alfabeticamente(self):
        self.video_paths.sort()
        self.orden_personalizado = False
        self.actualizar_lista()

    def actualizar_lista(self):
        self.lista_videos.clear()
        for i, path in enumerate(self.video_paths):
            item = QListWidgetItem()
            widget = self.crear_widget_video(path, i)
            self.lista_videos.addItem(item)
            self.lista_videos.setItemWidget(item, widget)
            item.setSizeHint(widget.sizeHint())

    def crear_widget_video(self, path, index):
        widget = QWidget()
        layout = QHBoxLayout()
        label = QLabel(os.path.basename(path))

        layout.addWidget(label)
        layout.addStretch()

        if index > 0:
            btn_up = QPushButton("Arriba")
            btn_up.clicked.connect(lambda _, i=index: self.mover_video(i, -1))
            layout.addWidget(btn_up)

        if index < len(self.video_paths) - 1:
            btn_down = QPushButton("Abajo")
            btn_down.clicked.connect(lambda _, i=index: self.mover_video(i, 1))
            layout.addWidget(btn_down)

        widget.setLayout(layout)
        return widget

    def mover_video(self, index, delta):
        nuevo_index = index + delta
        if 0 <= nuevo_index < len(self.video_paths):
            self.video_paths[index], self.video_paths[nuevo_index] = self.video_paths[nuevo_index], self.video_paths[index]
            self.orden_personalizado = True
            self.actualizar_lista()

    def obtener_videos_ordenados(self):
        return self.video_paths.copy()
