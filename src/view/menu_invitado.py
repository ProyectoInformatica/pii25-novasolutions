from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QGroupBox, QGridLayout
)
from PySide6.QtCore import Qt, QTimer
from typing import List, Optional
from pathlib import Path

from src.model.sensor import Sensor, initialize_simulation_files  # Importamos la función
from src.model.sistema import Sistema
from src.control.controlador_sensores import Controlador_Sensores

# UBICACIONES DE ARCHIVOS JSON
RESOURCES_DIR = Path("resources")
MUNICIPIO_DATA_FILE = str(RESOURCES_DIR / "municipio_data.json")
ESCUELA_DATA_FILE = str(RESOURCES_DIR / "escuela_data.json")




class MenuInvitado(QWidget):
    def __init__(self):
        super().__init__()

        # 1. Asegurar la existencia de los archivos JSON antes de crear los sensores
        initialize_simulation_files()

        # --- Ventana ---
        self.setWindowTitle("Modo Invitado – Solo Lectura")
        self.setGeometry(200, 150, 600, 550)  # Aumentamos el tamaño
        self.setStyleSheet("background-color:#1E1E1E; color:white; font-size:18px;")

        # Sensores del Municipio (temp y airQ con ID distinto)
        self.municipio_sensors: List[Sensor] = [
            Sensor(id="municipio_temp", sensor_type="temperature", data_file=MUNICIPIO_DATA_FILE, name="Temp. Ext."),
            Sensor(id="municipio_airQ", sensor_type="airQuality", data_file=MUNICIPIO_DATA_FILE, name="AirQ. Ext."),
        ]

        # Sensores de la Escuela (todos los internos)
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
                # La señal ahora es (text, id)
                s.air_quality_text_actualizada.connect(self.update_air_quality_text)

        # Sistema y controlador
        self.sistema = Sistema(sensors=self.all_sensors)
        self.ctrl = Controlador_Sensores(self.sistema.sensors)

        # LAYOUT PRINCIPAL Y CONTROLES
        main_layout = QVBoxLayout()

        titulo = QLabel("Panel de Monitoreo - Invitado")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size:22px; font-weight:bold; margin-bottom:10px;")
        main_layout.addWidget(titulo)

        # Contenedor de botones para alternar vistas
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

        # Contenedores de paneles
        self.panel_municipio = self.create_municipio_panel()
        self.panel_escuela = self.create_escuela_panel()

        self.panel_container = QVBoxLayout()
        self.panel_container.addWidget(self.panel_municipio)
        self.panel_container.addWidget(self.panel_escuela)

        main_layout.addLayout(self.panel_container)

        # Botón Cerrar Sesión
        main_layout.addStretch()
        btn = QPushButton("Cerrar sesión")
        btn.clicked.connect(self.cerrar_sesion)
        btn.setStyleSheet("font-size:16px; margin-top:15px;")
        main_layout.addWidget(btn)

        self.setLayout(main_layout)

        # Mostrar panel inicial
        self.show_panel("municipio")

        # Inicializar etiquetas al inicio
        self.actualizar()

        # TIMER DE ACTUALIZACIÓN
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar)
        self.timer.start(1000)

    #   CREACIÓN DE PANELES

    def create_municipio_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)

        self.lbl_temp_ext = QLabel("🌡️ Temperatura (Ext.): -- °C")
        self.lbl_air_ext = QLabel("🌬️ Calidad del aire (Ext.): Esperando lectura...")

        self.lbl_temp_ext.setAlignment(Qt.AlignCenter)
        self.lbl_air_ext.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.lbl_temp_ext)
        layout.addWidget(self.lbl_air_ext)

        return panel

    def create_escuela_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)

        self.lbl_temp_int = QLabel("🌡️ Temperatura (Int.): -- °C")
        self.lbl_air_int = QLabel("🌬️ Calidad del aire (Int.): Esperando lectura...")
        self.lbl_luz = QLabel("💡 Nivel de Luz: -- Lux")
        self.lbl_humo = QLabel("🔥 Concentración de Humo: -- PPM")
        self.lbl_distancia = QLabel("📏 Distancia (Presencia): -- cm")

        self.lbl_temp_int.setAlignment(Qt.AlignCenter)
        self.lbl_air_int.setAlignment(Qt.AlignCenter)
        self.lbl_luz.setAlignment(Qt.AlignCenter)
        self.lbl_humo.setAlignment(Qt.AlignCenter)
        self.lbl_distancia.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.lbl_temp_int)
        layout.addWidget(self.lbl_air_int)
        layout.addWidget(self.lbl_luz)
        layout.addWidget(self.lbl_humo)
        layout.addWidget(self.lbl_distancia)

        return panel

    #   FUNCIONES DE CONTROL

    def show_panel(self, panel_name: str):
        """Muestra el panel solicitado y oculta el otro."""
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
        """Intenta obtener la lectura de un sensor específico asociado a un archivo JSON."""
        for s in self.all_sensors:
            # Busca el sensor que coincida tanto en TIPO como en el ARCHIVO JSON
            if s.type == sensor_type and s.data_file == target_file:
                return s.read()  # Llama a read() para forzar la lectura del JSON
        return None

    def update_air_quality_text(self, text_value: str, sensor_id: str):
        if sensor_id == "municipio_airQ":
            # Sensor Municipal
            self.lbl_air_ext.setText(f"🌬️ Calidad del aire (Ext.): {text_value}")
        elif sensor_id == "escuela_airQ":
            # Sensor de la Escuela
            self.lbl_air_int.setText(f"🌬️ Calidad del aire (Int.): {text_value}")

    def actualizar(self):

        self.ctrl.read_all()  # Forzar la lectura de todos los sensores

        # Lecturas Municipales
        temp_ext = self.get_reading("temperature", target_file=MUNICIPIO_DATA_FILE)
        self.lbl_temp_ext.setText(
            f"🌡️ Temperatura (Ext.): {temp_ext:.1f} °C" if temp_ext is not None else "🌡️ Temperatura (Ext.): -- °C"
        )
        # La Calidad del Aire Ext. se actualiza con la señal

        # Lecturas de la Escuela
        temp_int = self.get_reading("temperature", target_file=ESCUELA_DATA_FILE)
        luz = self.get_reading("light", target_file=ESCUELA_DATA_FILE)
        humo = self.get_reading("smoke", target_file=ESCUELA_DATA_FILE)
        distancia = self.get_reading("distance", target_file=ESCUELA_DATA_FILE)

        self.lbl_temp_int.setText(
            f"🌡️ Temperatura (Int.): {temp_int:.1f} °C" if temp_int is not None else "🌡️ Temperatura (Int.): -- °C"
        )
        self.lbl_luz.setText(
            f"💡 Nivel de Luz: {luz:.1f} Lux" if luz is not None else "💡 Nivel de Luz: -- Lux"
        )
        self.lbl_humo.setText(
            f"🔥 Concentración de Humo: {humo:.1f} PPM" if humo is not None else "🔥 Concentración de Humo: -- PPM"
        )
        self.lbl_distancia.setText(
            f"📏 Distancia (Presencia): {distancia:.1f} cm" if distancia is not None else "📏 Distancia (Presencia): -- cm"
        )

    def cerrar_sesion(self):
        from src.view.inicio import Inicio
        self.inicio = Inicio()
        self.inicio.show()
        self.close()