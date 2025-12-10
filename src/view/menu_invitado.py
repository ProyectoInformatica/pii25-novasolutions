# src/view/menu_invitado.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QTimer

from src.model.sensor import Sensor
from src.model.sistema import Sistema
from src.control.controlador_sensores import Controlador_Sensores


class MenuInvitado(QWidget):
    def __init__(self):
        super().__init__()

        # Ventana
        self.setWindowTitle("Modo Invitado – Solo Lectura")
        self.setGeometry(200, 150, 500, 300)
        self.setStyleSheet("background-color:#1E1E1E; color:white; font-size:18px;")

        layout = QVBoxLayout()

        titulo = QLabel("Lectura de Sensores")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size:22px; font-weight:bold; margin-bottom:20px;")
        layout.addWidget(titulo)

        self.lbl_temp = QLabel("Temperatura: -- °C")
        self.lbl_temp.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_temp)

        self.lbl_air = QLabel("Calidad del aire: --")
        self.lbl_air.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_air)

        btn = QPushButton("Cerrar sesión")
        btn.clicked.connect(self.cerrar_sesion)
        btn.setStyleSheet("font-size:16px; margin-top:25px;")
        layout.addWidget(btn)

        self.setLayout(layout)

        # Sensores (MISMO que mantenimiento)
        data_file = "simulation_data.json"

        self.sensors = [
            Sensor(id="temperature1", sensor_type="temperature", data_file=data_file),
            Sensor(id="airQ1", sensor_type="airQuality", data_file=data_file),
        ]

        # --- Sistema y controlador ---
        self.sistema = Sistema(sensors=self.sensors)
        self.ctrl = Controlador_Sensores(self.sistema.sensors)

        # --- Timer de actualización ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar)
        self.timer.start(1000)

    def actualizar(self):
        lecturas = self.ctrl.read_all()

        temp = lecturas.get("temperature1")
        air = lecturas.get("airQ1")

        self.lbl_temp.setText(
            f"Temperatura: {temp:.1f} °C" if temp is not None else "Temperatura: -- °C"
        )

        self.lbl_air.setText(
            f"Calidad del aire: {air:.1f}" if air is not None else "Calidad del aire: -- "
        )

    def cerrar_sesion(self):
        from src.view.inicio import Inicio
        self.inicio = Inicio()
        self.inicio.show()
        self.close()
