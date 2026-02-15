from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QGroupBox
)
from PySide6.QtCore import Qt, QTimer
from typing import List, Optional
from pathlib import Path

from src.model.sensor import Sensor
from src.model.sistema import Sistema
from src.control.controlador_sensores import Controlador_Sensores

# UBICACIONES DE ARCHIVOS JSON
RESOURCES_DIR = Path("resources")
MUNICIPIO_DATA_FILE = str(RESOURCES_DIR / "municipio_data.json")
ESCUELA_DATA_FILE = str(RESOURCES_DIR / "escuela_data.json")

TITLE_STYLE = "font-size:20px; font-weight:700; margin:8px 0 12px 0;"

PANEL_STYLE = """
QGroupBox {
    border: 1px solid rgba(255,255,255,0.14);
    margin-top: 18px;
    padding: 14px;
    border-radius: 12px;
    background: #141b44;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 10px;
    margin-left: 10px;
    color: white;
    font-weight: 700;
}
"""

BTN_PRIMARY = """
QPushButton{
    background-color:#3489e2;
    color:white;
    padding:12px;
    border-radius:12px;
    font-size:14px;
}
QPushButton:hover{ background-color:#2f7fd1; }
QPushButton:pressed{ background-color:#2a72ba; }
QPushButton:disabled{
    background-color: rgba(52,137,226,0.35);
    color: rgba(255,255,255,0.8);
}
"""

BTN_WARNING = """
QPushButton{
    background-color:#3489e2;
    color:white;
    padding:12px;
    border-radius:12px;
    font-size:14px;
}
QPushButton:hover{ background-color:#2f7fd1; }
QPushButton:pressed{ background-color:#2a72ba; }
QPushButton:disabled{
    background-color: rgba(52,137,226,0.35);
    color: rgba(255,255,255,0.8);
}
"""

BTN_DANGER = """
QPushButton{
    background-color:#AA3333;
    color:white;
    padding:12px;
    border-radius:12px;
    font-size:14px;
}
QPushButton:hover{ background-color:#972d2d; }
QPushButton:pressed{ background-color:#822727; }
"""

READING_STYLE = """
QLabel{
    padding: 10px 12px;
    border-radius: 10px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
    color: white;
}
"""


class MenuInvitado(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Modo Invitado – Solo Lectura")
        self.setGeometry(200, 150, 720, 560)
        self.setStyleSheet("background-color:#0e143b; color:white;")

        # Sensores del Municipio
        self.municipio_sensors: List[Sensor] = [
            Sensor(id="municipio_temp", sensor_type="temperature", data_file=MUNICIPIO_DATA_FILE, name="Temp. Ext."),
            Sensor(id="municipio_airQ", sensor_type="airQuality", data_file=MUNICIPIO_DATA_FILE, name="AirQ. Ext."),
        ]

        # Sensores de la Escuela
        self.escuela_sensors: List[Sensor] = [
            Sensor(id="escuela_temp", sensor_type="temperature", data_file=ESCUELA_DATA_FILE, name="Temp. Int."),
            Sensor(id="escuela_airQ", sensor_type="airQuality", data_file=ESCUELA_DATA_FILE, name="AirQ. Int."),
            Sensor(id="escuela_light", sensor_type="light", data_file=ESCUELA_DATA_FILE, name="Luz"),
            Sensor(id="escuela_smoke", sensor_type="smoke", data_file=ESCUELA_DATA_FILE, name="Humo"),
            Sensor(id="escuela_dist", sensor_type="distance", data_file=ESCUELA_DATA_FILE, name="Distancia"),
        ]

        self.all_sensors = self.municipio_sensors + self.escuela_sensors

        # CONEXIÓN DE SEÑALES ESPECÍFICAS
        for s in self.all_sensors:
            if s.type == "airQuality":
                s.air_quality_text_actualizada.connect(self.update_air_quality_text)

        # Sistema y controlador
        self.sistema = Sistema(sensors=self.all_sensors)
        self.ctrl = Controlador_Sensores(self.sistema.sensors)

        # ===== LAYOUT PRINCIPAL =====
        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(24, 18, 24, 18)

        titulo = QLabel("Panel de Monitoreo - Invitado")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(TITLE_STYLE)
        main_layout.addWidget(titulo)

        # ===== BOTONES (tabs) =====
        button_container = QHBoxLayout()
        button_container.setSpacing(10)

        self.btn_municipio = QPushButton("Sensores del Municipio")
        self.btn_municipio.clicked.connect(lambda: self.show_panel("municipio"))
        self.btn_municipio.setStyleSheet(BTN_PRIMARY)

        self.btn_escuela = QPushButton("Sensores de la Escuela")
        self.btn_escuela.clicked.connect(lambda: self.show_panel("escuela"))
        self.btn_escuela.setStyleSheet(BTN_WARNING)

        button_container.addWidget(self.btn_municipio)
        button_container.addWidget(self.btn_escuela)
        main_layout.addLayout(button_container)

        # ===== PANELES (cards) =====
        self.panel_municipio = self.create_municipio_panel()
        self.panel_escuela = self.create_escuela_panel()

        main_layout.addWidget(self.panel_municipio, 1)
        main_layout.addWidget(self.panel_escuela, 1)

        # ===== BOTÓN CERRAR SESIÓN =====
        btn = QPushButton("Cerrar sesión")
        btn.clicked.connect(self.cerrar_sesion)
        btn.setStyleSheet(BTN_DANGER)
        main_layout.addWidget(btn)

        self.setLayout(main_layout)

        # Mostrar panel inicial
        self.show_panel("municipio")

        # Inicializar etiquetas
        self.actualizar()

        # TIMER DE ACTUALIZACIÓN
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar)
        self.timer.start(1000)

    # ===== CREACIÓN DE PANELES =====
    def create_municipio_panel(self) -> QWidget:
        group = QGroupBox("Municipio – Lecturas Externas")
        group.setStyleSheet(PANEL_STYLE)

        layout = QVBoxLayout()
        layout.setSpacing(12)

        self.lbl_temp_ext = QLabel("Temperatura (Ext.): -- °C")
        self.lbl_air_ext = QLabel("Calidad del aire (Ext.): Esperando lectura...")

        for lab in (self.lbl_temp_ext, self.lbl_air_ext):
            lab.setAlignment(Qt.AlignCenter)
            lab.setStyleSheet(READING_STYLE)
            layout.addWidget(lab)

        group.setLayout(layout)
        return group

    def create_escuela_panel(self) -> QWidget:
        group = QGroupBox("Escuela – Lecturas Internas")
        group.setStyleSheet(PANEL_STYLE)

        layout = QVBoxLayout()
        layout.setSpacing(12)

        self.lbl_temp_int = QLabel("Temperatura (Int.): -- °C")
        self.lbl_air_int = QLabel("Calidad del aire (Int.): Esperando lectura...")
        self.lbl_luz = QLabel("Nivel de Luz: -- Lux")
        self.lbl_humo = QLabel("Concentración de Humo: -- PPM")
        self.lbl_distancia = QLabel("Distancia (Presencia): -- cm")

        for lab in (self.lbl_temp_int, self.lbl_air_int, self.lbl_luz, self.lbl_humo, self.lbl_distancia):
            lab.setAlignment(Qt.AlignCenter)
            lab.setStyleSheet(READING_STYLE)
            layout.addWidget(lab)

        group.setLayout(layout)
        return group

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

    def get_reading(self, sensor_type: str, target_file: str) -> Optional[float]:
        for s in self.all_sensors:
            if s.type == sensor_type and s.data_file == target_file:
                return s.read()
        return None

    def update_air_quality_text(self, text_value: str, sensor_id: str):
        if sensor_id == "municipio_airQ":
            self.lbl_air_ext.setText(f" Calidad del aire (Ext.): {text_value}")
        elif sensor_id == "escuela_airQ":
            self.lbl_air_int.setText(f" Calidad del aire (Int.): {text_value}")

    def actualizar(self):
        self.ctrl.read_all()

        # Lecturas Municipales
        temp_ext = self.get_reading("temperature", target_file=MUNICIPIO_DATA_FILE)
        self.lbl_temp_ext.setText(
            f"Temperatura (Ext.): {temp_ext:.1f} °C" if temp_ext is not None else "🌡️ Temperatura (Ext.): -- °C"
        )

        # Lecturas de la Escuela
        temp_int = self.get_reading("temperature", target_file=ESCUELA_DATA_FILE)
        luz = self.get_reading("light", target_file=ESCUELA_DATA_FILE)
        humo = self.get_reading("smoke", target_file=ESCUELA_DATA_FILE)
        distancia = self.get_reading("distance", target_file=ESCUELA_DATA_FILE)

        self.lbl_temp_int.setText(
            f"Temperatura (Int.): {temp_int:.1f} °C" if temp_int is not None else "🌡️ Temperatura (Int.): -- °C"
        )
        self.lbl_luz.setText(
            f"Nivel de Luz: {luz:.1f} Lux" if luz is not None else "💡 Nivel de Luz: -- Lux"
        )
        self.lbl_humo.setText(
            f"Concentración de Humo: {humo:.1f} PPM" if humo is not None else "🔥 Concentración de Humo: -- PPM"
        )
        self.lbl_distancia.setText(
            f"Distancia (Presencia): {distancia:.1f} cm" if distancia is not None else "📏 Distancia (Presencia): -- cm"
        )

    def cleanup(self):
        self.timer.stop()
        for sensor in self.all_sensors:
            sensor.stop_reading()

    def cerrar_sesion(self):
        from src.view.inicio import Inicio
        self.cleanup()
        self.inicio = Inicio()
        self.inicio.show()
        self.close()
