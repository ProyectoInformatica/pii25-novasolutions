# src/view/menu_invitado.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QStackedLayout, QGroupBox, QGridLayout
)
from PySide6.QtCore import Qt, QTimer
from typing import List, Dict

from src.model.sensor import Sensor
from src.model.sistema import Sistema
from src.control.controlador_sensores import Controlador_Sensores


class MenuInvitado(QWidget):
    def __init__(self):
        super().__init__()

        # Ventana
        self.setWindowTitle("Modo Invitado – Solo Lectura")
        self.setGeometry(200, 150, 500, 450)
        self.setStyleSheet("background-color:#1E1E1E; color:white; font-size:18px;")

        # Archivo de datos base
        data_file = "simulation_data.json"

        # ======================================
        # 1. DEFINICIÓN Y CONFIGURACIÓN DE SENSORES
        # ======================================

        # Sensores del Municipio (Exterior/General)
        self.municipio_sensors: List[Sensor] = [
            Sensor(id="temp1", sensor_type="temperature", data_file=data_file),
            Sensor(id="airQ1", sensor_type="airQuality", data_file=data_file),
        ]

        # Sensores de la Escuela (Interior/Específico)
        self.escuela_sensors: List[Sensor] = [
            Sensor(id="light1", sensor_type="light", data_file=data_file),
        ]

        self.all_sensors = self.municipio_sensors + self.escuela_sensors

        # 🔔 Conexión de señales (airQuality → texto)
        for s in self.all_sensors:
            if s.type == "airQuality":
                s.air_quality_text_actualizada.connect(self.update_air_quality_text)

        # Sistema y controlador
        self.sistema = Sistema(sensors=self.all_sensors)
        self.ctrl = Controlador_Sensores(self.sistema.sensors)

        # ======================================
        # 2. LAYOUT PRINCIPAL
        # ======================================
        main_layout = QVBoxLayout()

        titulo = QLabel("Panel de Monitoreo - Invitado")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size:22px; font-weight:bold; margin-bottom:10px;")
        main_layout.addWidget(titulo)

        # Botones de selección de panel
        button_container = QHBoxLayout()

        self.btn_municipio = QPushButton("Sensores del Municipio")
        self.btn_municipio.clicked.connect(lambda: self.show_panel("municipio"))
        self.btn_municipio.setStyleSheet("background-color:#4A90E2; color:white; padding: 10px;")

        self.btn_escuela = QPushButton("Sensores de la Escuela")
        self.btn_escuela.clicked.connect(lambda: self.show_panel("escuela"))
        self.btn_escuela.setStyleSheet("background-color:#F5A623; color:white; padding: 10px;")

        button_container.addWidget(self.btn_municipio)
        button_container.addWidget(self.btn_escuela)
        main_layout.addLayout(button_container)

        # Paneles
        self.panel_municipio = self.create_municipio_panel()
        self.panel_escuela = self.create_escuela_panel()

        self.panel_container = QVBoxLayout()
        self.panel_container.addWidget(self.panel_municipio)
        self.panel_container.addWidget(self.panel_escuela)

        main_layout.addLayout(self.panel_container)

        # Botón cerrar sesión
        main_layout.addStretch()
        btn = QPushButton("Cerrar sesión")
        btn.clicked.connect(self.cerrar_sesion)
        btn.setStyleSheet("font-size:16px; margin-top:15px;")
        main_layout.addWidget(btn)

        self.setLayout(main_layout)

        # Mostrar panel inicial
        self.show_panel("municipio")

        # ======================================
        # 3. TIMER DE ACTUALIZACIÓN
        # ======================================
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar)
        self.timer.start(1000)

    # -----------------------------------
    #   PANELES
    # -----------------------------------

    def create_municipio_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)

        self.lbl_temp = QLabel("🌡️ Temperatura: -- °C")
        self.lbl_air = QLabel("🌬️ Calidad del aire: Esperando lectura...")

        self.lbl_temp.setAlignment(Qt.AlignCenter)
        self.lbl_air.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.lbl_temp)
        layout.addWidget(self.lbl_air)

        return panel

    def create_escuela_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)

        self.lbl_luz = QLabel("💡 Nivel de Luz: -- Lux")
        self.lbl_luz.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.lbl_luz)
        return panel

    # -----------------------------------
    #   CONTROL
    # -----------------------------------

    def show_panel(self, panel_name: str):
        if panel_name == "municipio":
            self.panel_municipio.show()
            self.panel_escuela.hide()
            self.btn_municipio.setEnabled(False)
            self.btn_escuela.setEnabled(True)

        elif panel_name == "escuela":
            self.panel_municipio.hide()
            self.panel_escuela.show()
            self.btn_municipio.setEnabled(True)
            self.btn_escuela.setEnabled(False)

    def get_reading(self, sensor_type: str):
        try:
            for s in self.all_sensors:
                if s.type == sensor_type:
                    return s.read()
            return None
        except RuntimeError:
            return None

    def update_air_quality_text(self, text_value: str):
        self.lbl_air.setText(f"🌬️ Calidad del aire: {text_value}")

    def actualizar(self):
        self.ctrl.read_all()

        temp = self.get_reading("temperature")
        self.lbl_temp.setText(
            f"🌡️ Temperatura: {temp:.1f} °C" if temp is not None else "🌡️ Temperatura: -- °C"
        )

        luz = self.get_reading("light")
        self.lbl_luz.setText(
            f"💡 Nivel de Luz: {luz:.1f} Lux" if luz is not None else "💡 Nivel de Luz: -- Lux"
        )

    def cerrar_sesion(self):
        from src.view.inicio import Inicio
        self.inicio = Inicio()
        self.inicio.show()
        self.close()
