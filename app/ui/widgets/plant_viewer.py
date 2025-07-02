import os
import pandas as pd
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QHBoxLayout, QComboBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.signal import savgol_filter
import matplotlib
matplotlib.use("Qt5Agg")


class PlantViewerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

        # Widgets
        self.label = QLabel("Cargar archivos CSV de plantas")
        self.layout().addWidget(self.label)

        self.load_button = QPushButton("Cargar CSV")
        self.load_button.clicked.connect(self.load_csv_files)
        self.layout().addWidget(self.load_button)

        self.file_selector = QComboBox()
        self.file_selector.currentIndexChanged.connect(self.plot_selected_plant)
        self.layout().addWidget(self.file_selector)

        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("Anterior")
        self.next_button = QPushButton("Siguiente")
        self.prev_button.clicked.connect(self.prev_file)
        self.next_button.clicked.connect(self.next_file)
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.next_button)
        self.layout().addLayout(nav_layout)

        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.layout().addWidget(self.canvas)

        self.csv_files = []  # List of file paths

    def load_csv_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Seleccionar archivos CSV", "", "CSV Files (*.csv)")
        if not files:
            return
        self.csv_files = files
        self.file_selector.clear()
        for file_path in self.csv_files:
            filename = os.path.basename(file_path)
            self.file_selector.addItem(filename)
        self.plot_selected_plant()

    def prev_file(self):
        index = self.file_selector.currentIndex()
        if index > 0:
            self.file_selector.setCurrentIndex(index - 1)

    def next_file(self):
        index = self.file_selector.currentIndex()
        if index < self.file_selector.count() - 1:
            self.file_selector.setCurrentIndex(index + 1)

    def plot_selected_plant(self):
        index = self.file_selector.currentIndex()
        if index < 0 or index >= len(self.csv_files):
            return

        file_path = self.csv_files[index]
        df = pd.read_csv(file_path)

        if df.empty or not all(col in df.columns for col in ["frame", "ang_izq", "ang_der"]):
            return

        df = df.sort_values("frame")
        frames = df["frame"].to_numpy()
        izq = df["ang_izq"].to_numpy()
        der = df["ang_der"].to_numpy()

        if len(izq) >= 11:
            izq = savgol_filter(izq, 11, 3)
            der = savgol_filter(der, 11, 3)

        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)
        ax.plot(frames, izq, label="Ángulo Izquierdo", color='blue')
        ax.plot(frames, der, label="Ángulo Derecho", color='orange')
        ax.set_title(f"{os.path.basename(file_path)}")
        ax.set_xlabel("Frame")
        ax.set_ylabel("Ángulo (grados)")
        ax.legend()
        ax.grid(True)
        self.canvas.draw()
