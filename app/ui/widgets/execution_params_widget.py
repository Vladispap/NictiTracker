from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QTimeEdit, QPushButton, QFileDialog, QLineEdit, QDateTimeEdit
)
from PySide6.QtCore import QTime, QDateTime, QDate
import os

class ExecutionParamsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.export_folder = ""
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Minutos por frame
        mpf_layout = QHBoxLayout()
        mpf_layout.addWidget(QLabel("Minutos por frame:"))
        self.mpf_input = QSpinBox()
        self.mpf_input.setRange(1, 10000)
        self.mpf_input.setValue(1)
        mpf_layout.addWidget(self.mpf_input)
        layout.addLayout(mpf_layout)

        # Frames a saltar
        skip_layout = QHBoxLayout()
        skip_layout.addWidget(QLabel("Frames a saltar:"))
        self.skip_input = QSpinBox()
        self.skip_input.setRange(0, 10000)
        self.skip_input.setValue(10)
        skip_layout.addWidget(self.skip_input)
        layout.addLayout(skip_layout)

        # Hora inicial
        hora_layout = QHBoxLayout()
        hora_layout.addWidget(QLabel("Hora inicial (M/d/yyyy HH:mm):"))
        self.time_input = QDateTimeEdit()
        self.time_input.setDisplayFormat("M/d/yyyy HH:mm")
        self.time_input.setDateTime(QDateTime(QDate(2025, 1, 1), QTime(12, 0)))
        hora_layout.addWidget(self.time_input)
        layout.addLayout(hora_layout)

        # Selección de carpeta de exportación
        export_layout = QHBoxLayout()
        export_layout.addWidget(QLabel("Exportar en:"))
        self.export_path_display = QLineEdit()
        self.export_path_display.setReadOnly(True)
        export_layout.addWidget(self.export_path_display)

        self.btn_seleccionar_carpeta = QPushButton("Seleccionar carpeta")
        self.btn_seleccionar_carpeta.clicked.connect(self.seleccionar_carpeta)
        export_layout.addWidget(self.btn_seleccionar_carpeta)

        layout.addLayout(export_layout)
        self.setLayout(layout)

    def seleccionar_carpeta(self):
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de exportación")
        if carpeta:
            self.export_folder = carpeta
            self.export_path_display.setText(carpeta)

    def get_params(self):
        return {
            "min_per_frame": self.mpf_input.value(),
            "frame_skip": self.skip_input.value(),
            "init_time": self.time_input.dateTime().toString("M/d/yyyy HH:mm"),
            "output_dir": self.export_folder
        }
