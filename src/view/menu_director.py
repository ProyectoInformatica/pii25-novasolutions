from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QGroupBox, QGridLayout
)
from PySide6.QtCore import QTimer, Qt
from typing import List
from pathlib import Path

from src.model.sistema import Sistema
from src.model.sensor import Sensor, initialize_simulation_files
from src.model.actuador import Ventilador, Rociador, LuzExterior, LuzPasillo
from src.control.controlador_sistema import Controlador_Sistema
from src.control.controlador_sensores import Controlador_Sensores
from src.model.usuario import Usuario
from src.model.reporte import Reporteador
from src.view.gestion_usuarios import GestionUsuariosDirector
from src.view.reporte_view import ReporteHistorialView

RESOURCES_DIR = Path("resources")
ESCUELA_DATA_FILE = str(RESOURCES_DIR / "escuela_data.json")


class MenuDirector(QWidget):
    def __init__(self, usuario: Usuario):
        super().__init__()

        self.usuario = usuario
        self.sensor_data_file = ESCUELA_DATA_FILE

        self.setWindowTitle("Panel del Director")
        self.setGeometry(200, 150, 800, 600)
        self.setStyleSheet("background-color:#0e143b; color:white;")

        self.sensors: List[Sensor] = [
            Sensor(id="temp1", sensor_type="temperature", data_file=self.sensor_data_file),
            Sensor(id="smoke1", sensor_type="smoke", data_file=self.sensor_data_file),
            Sensor(id="light1", sensor_type="light", data_file=self.sensor_data_file),
            Sensor(id="dist1", sensor_type="distance", data_file=self.sensor_data_file),
            Sensor(id="airQ1", sensor_type="airQuality", data_file=self.sensor_data_file)
        ]

        self.actuators = [
            Ventilador(id="fan1"),
            Rociador(id="rociador1"),
            LuzExterior(id="luzext1"),
            LuzPasillo(id="luzpasillo1")
        ]

        self.sistema = Sistema(sensors=self.sensors, actuators=self.actuators)
        self.ctrl_sensores = Controlador_Sensores(self.sensors)
        self.ctrl_sistema = Controlador_Sistema(self.sistema)

        self.reporteador = Reporteador()
        self.update_count = 0


        for s in self.sensors:
            if s.type == "airQuality":
                s.air_quality_text_actualizada.connect(self.update_air_quality_text)
                break

        layout = QVBoxLayout()

        titulo = QLabel(f"Bienvenido Director General: {usuario.nombre_usuario}")
        titulo.setAlignment(Qt.AlignHCenter)
        titulo.setStyleSheet("font-size:20px; margin-bottom: 10px;")
        layout.addWidget(titulo)

        body_layout = QHBoxLayout()
        body_layout.setSpacing(12)

        gestion_group = QGroupBox("Opciones de Dirección")
        gestion_group.setStyleSheet("""
        QGroupBox {
            border: 1px solid #555;
            margin-top: 18px;
            padding-top: 6px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 6px;
            margin-left: 0px;
        }
        """)

        gestion_layout = QVBoxLayout()
        gestion_layout.setAlignment(Qt.AlignTop)

        btn_usuarios = QPushButton("Gestionar Usuarios")
        btn_usuarios.clicked.connect(self.abrir_gestion_usuarios)
        btn_usuarios.setStyleSheet("background-color:#3489e2; color:white;")
        gestion_layout.addWidget(btn_usuarios)

        btn_reportes = QPushButton("Ver Reportes Históricos")
        btn_reportes.clicked.connect(self.abrir_reportes)
        btn_reportes.setStyleSheet("background-color:#3489e2; color:white;")
        gestion_layout.addWidget(btn_reportes)

        gestion_layout.addStretch()
        gestion_group.setLayout(gestion_layout)
        gestion_group.setFixedWidth(260)

        status_group = QGroupBox("Estado del Sistema en Tiempo Real")
        status_group.setStyleSheet("""
        QGroupBox {
            border: 1px solid #555;
            margin-top: 18px;
            padding-top: 6px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 6px;
            margin-left: 0px;
        }
        """)
        status_layout = QGridLayout()

        status_layout.addWidget(QLabel("LECTURAS DE SENSORES"), 0, 0, 1, 2)

        self.lbl_temp = QLabel("Temperatura: -- °C")
        status_layout.addWidget(QLabel("Temp"), 1, 0)
        status_layout.addWidget(self.lbl_temp, 1, 1)

        self.lbl_humo = QLabel("Nivel de Humo: --")
        status_layout.addWidget(QLabel("Humo"), 2, 0)
        status_layout.addWidget(self.lbl_humo, 2, 1)

        self.lbl_luz = QLabel("Nivel de Luz: -- Lux")
        status_layout.addWidget(QLabel("Luz"), 3, 0)
        status_layout.addWidget(self.lbl_luz, 3, 1)

        self.lbl_distancia = QLabel("Distancia: -- cm")
        status_layout.addWidget(QLabel("Distancia"), 4, 0)
        status_layout.addWidget(self.lbl_distancia, 4, 1)

        self.lbl_airq = QLabel("Calidad del Aire: Esperando lectura...")
        status_layout.addWidget(QLabel("Calidad Aire"), 5, 0)
        status_layout.addWidget(self.lbl_airq, 5, 1)

        status_layout.addWidget(QLabel("ESTADO DE ACTUADORES"), 6, 0, 1, 2)

        self.actuator_labels = {}
        for i, actuator in enumerate(self.actuators):
            lbl_name = QLabel(f"{actuator.name}:")
            lbl_state = QLabel("🔴 OFF")
            self.actuator_labels[actuator.id] = lbl_state
            row = i + 7
            status_layout.addWidget(lbl_name, row, 0)
            status_layout.addWidget(lbl_state, row, 1)

        status_group.setLayout(status_layout)

        body_layout.addWidget(gestion_group, 0)
        body_layout.addWidget(status_group, 1)
        layout.addLayout(body_layout)

        btn_salir = QPushButton("Cerrar sesión")
        btn_salir.clicked.connect(self.cerrar_sesion)
        btn_salir.setStyleSheet("""QPushButton{background-color:#AA3333;color:white;padding:10px;border-radius:10px;font-size:14px;}QPushButton:hover{ background-color:#972d2d; }QPushButton:pressed{ background-color:#822727; }""")
        layout.addWidget(btn_salir)

        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.actualizar)
        self.timer.start()

    def update_air_quality_text(self, text_value: str, sensor_id: str):
        self.lbl_airq.setText(f"Calidad del Aire: {text_value}")

    def actualizar(self):
        self.ctrl_sistema.update()

        temp = self.sistema.get_sensor_reading("temperature")
        smoke = self.sistema.get_sensor_reading("smoke")
        light = self.sistema.get_sensor_reading("light")
        distance = self.sistema.get_sensor_reading("distance")

        self.lbl_temp.setText(f"Temperatura: {temp:.2f} °C" if temp is not None else "Temperatura: ⚠️ ERROR (JSON)")
        self.lbl_humo.setText(f"Nivel de Humo: {smoke:.2f}" if smoke is not None else "Nivel de Humo: ⚠️ ERROR (JSON)")
        self.lbl_luz.setText(f"Nivel de Luz: {light:.2f} Lux" if light is not None else "Nivel de Luz: ⚠️ ERROR (JSON)")
        self.lbl_distancia.setText(
            f"Distancia: {distance:.2f} cm" if distance is not None else "Distancia: ⚠️ ERROR (JSON)")

        for actuator in self.actuators:
            label = self.actuator_labels.get(actuator.id)
            if label:
                label.setText("🟢 ON" if actuator.state else "🔴 OFF")

        self.update_count += 1
        if self.update_count % 3600 == 0:
            self.reporteador.registrar_lectura_actual()

    def abrir_gestion_usuarios(self):
        self.gestion = GestionUsuariosDirector(usuario=self.usuario)
        self.gestion.show()

    def abrir_reportes(self):
        self.reporte_view = ReporteHistorialView()
        self.reporte_view.show()

    def cleanup(self):
        self.timer.stop()
        for sensor in self.sensors:
            sensor.stop_reading()

    def cerrar_sesion(self):
        from src.view.inicio import Inicio
        self.cleanup()
        self.inicio = Inicio()
        self.inicio.show()
        self.close()