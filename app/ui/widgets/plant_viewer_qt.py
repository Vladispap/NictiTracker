import os
import pandas as pd
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QHBoxLayout, QComboBox
)
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
from PySide6.QtGui import QPainter
from PySide6.QtCore import QPointF, QDateTime, Qt
from scipy.signal import savgol_filter


class PlantViewerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

        # UI Elements
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

        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.layout().addWidget(self.chart_view)

        self.coord_label = QLabel("Posición: ")
        self.layout().addWidget(self.coord_label)

        self.csv_files = []

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

        if df.empty or not all(col in df.columns for col in ["time", "ang_izq", "ang_der"]):
            return

        df = df.dropna(subset=["time", "ang_izq", "ang_der"])
        if df.empty:
            return

        df["time"] = pd.to_datetime(df["time"], format="%m-%d-%Y %H:%M")
        df = df.sort_values("time")
        times = df["time"]
        izq = df["ang_izq"].to_numpy()
        der = df["ang_der"].to_numpy()

        if len(izq) >= 11:
            izq = savgol_filter(izq, 11, 3)
            der = savgol_filter(der, 11, 3)

        chart = QChart()
        chart.setTitle(os.path.basename(file_path))

        izq_series = QLineSeries()
        izq_series.setName("Ángulo Izquierdo")
        der_series = QLineSeries()
        der_series.setName("Ángulo Derecho")

        for time, y in zip(times, izq):
            dt = QDateTime(time.to_pydatetime())
            izq_series.append(dt.toMSecsSinceEpoch(), y)

        for time, y in zip(times, der):
            dt = QDateTime(time.to_pydatetime())
            der_series.append(dt.toMSecsSinceEpoch(), y)

        izq_series.hovered.connect(lambda point, state: self.show_coords(point, state, "Izquierdo"))
        der_series.hovered.connect(lambda point, state: self.show_coords(point, state, "Derecho"))

        chart.addSeries(izq_series)
        chart.addSeries(der_series)

        # Eje X como fechas reales con ticks cada 6 horas
        axis_x = QDateTimeAxis()
        axis_x.setTitleText("Fecha y hora")
        axis_x.setFormat("dd-MM HH:mm")
        # axis_x.setTickCount(10)
        min_time = QDateTime(times.min().to_pydatetime())
        max_time = QDateTime(times.max().to_pydatetime())
        axis_x.setRange(min_time, max_time)

        axis_y = QValueAxis()
        axis_y.setTitleText("Ángulo (grados)")
        axis_y.applyNiceNumbers()
        axis_y.setRange(min(izq.min(), der.min()), max(izq.max(), der.max()))

        chart.setAxisX(axis_x, izq_series)
        chart.setAxisX(axis_x, der_series)
        chart.setAxisY(axis_y, izq_series)
        chart.setAxisY(axis_y, der_series)

        chart.legend().setVisible(True)
        self.chart_view.setChart(chart)

    def show_coords(self, point, state, label):
        if state:
            dt = QDateTime.fromMSecsSinceEpoch(int(point.x()))
            time_str = dt.toString("dd-MM HH:mm")
            y = round(point.y(), 2)
            self.coord_label.setText(f"{label}: {time_str}, Ángulo {y}°")
