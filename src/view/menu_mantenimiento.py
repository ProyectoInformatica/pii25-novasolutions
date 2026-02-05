# src/view/menu_mantenimiento.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QCheckBox, QDoubleSpinBox, QGroupBox, QGridLayout
)
from PySide6.QtCore import QTimer, Qt
from typing import List, Dict
from pathlib import Path

from src.model.sistema import Sistema
from src.model.sensor import Sensor
from src.model.actuador import Ventilador, Rociador, LuzExterior, LuzPasillo
from src.control.controlador_sistema import Controlador_Sistema
from src.control.controlador_sensores import Controlador_Sensores
from src.model.usuario import Usuario

# DEFINICIÓN DE RUTAS
RESOURCES_DIR = Path("resources")
ESCUELA_DATA_FILE = str(RESOURCES_DIR / "escuela_data.json")


class MenuMantenimiento(QWidget):
    def __init__(self, usuario: Usuario):
        super().__init__()

        self.usuario = usuario
        self.sensor_data_file = ESCUELA_DATA_FILE

        self.setWindowTitle("Panel Jefe de Mantenimiento")
        self.setGeometry(200, 150, 800, 600)
        self.setStyleSheet("background-color:#1E1E1E; color:white;")

        self.sensors: List[Sensor] = [
            Sensor(id="temp1", sensor_type="temperature", data_file=self.sensor_data_file),
            Sensor(id="smoke1", sensor_type="smoke", data_file=self.sensor_data_file),
            Sensor(id="light1", sensor_type="light", data_file=self.sensor_data_file),
            Sensor(id="dist1", sensor_type="distance", data_file=self.sensor_data_file),
            Sensor(id="airQ1", sensor_type="airQuality", data_file=self.sensor_data_file)
        ]

        # Actuadores
        self.actuators = [
            Ventilador(id="fan1"),
            Rociador(id="rociador1"),
            LuzExterior(id="luzext1"),
            LuzPasillo(id="luzpasillo1")
        ]

        self.sistema = Sistema(sensors=self.sensors, actuators=self.actuators)
        self.ctrl_sensores = Controlador_Sensores(self.sensors)
        self.ctrl_sistema = Controlador_Sistema(self.sistema)

        # 🔔 Señal para calidad del aire en texto
        for s in self.sensors:
            if s.type == "airQuality":
                s.air_quality_text_actualizada.connect(self.update_air_quality_text)
                break

        # ==========================
        #   LAYOUT PRINCIPAL
        # ==========================
        layout = QVBoxLayout()

        titulo = QLabel(f"Bienvenido Jefe de Mantenimiento: {usuario.nombre_usuario}")
        titulo.setAlignment(Qt.AlignHCenter)
        titulo.setStyleSheet("font-size:20px;")
        layout.addWidget(titulo)

        status_group = QGroupBox("Estado del Sistema")
        status_group.setStyleSheet(
            "QGroupBox { border: 1px solid #555; margin-top: 10px; padding-top: 10px; }"
        )
        status_layout = QGridLayout()

        sensores_left = QVBoxLayout()
        sensores_right = QVBoxLayout()

        self.lbl_temp = QLabel("Temperatura: -- °C")
        self.lbl_humo = QLabel("Nivel de Humo: --")
        self.lbl_luz = QLabel("Nivel de Luz: -- Lux")
        self.lbl_distancia = QLabel("Distancia: -- cm")
        self.lbl_airq = QLabel("Calidad del Aire: Esperando lectura...")

        for lbl in [self.lbl_temp, self.lbl_humo, self.lbl_luz, self.lbl_distancia, self.lbl_airq]:
            lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            lbl.setStyleSheet("padding: 4px;")

        sensores_left.addWidget(QLabel("🌡️ Temp"))
        sensores_left.addWidget(QLabel("💨 Humo"))
        sensores_left.addWidget(QLabel("💡 Luz"))
        sensores_left.addWidget(QLabel("📏 Distancia"))
        sensores_left.addWidget(QLabel("🌬️ Calidad Aire"))

        sensores_right.addWidget(self.lbl_temp)
        sensores_right.addWidget(self.lbl_humo)
        sensores_right.addWidget(self.lbl_luz)
        sensores_right.addWidget(self.lbl_distancia)
        sensores_right.addWidget(self.lbl_airq)

        status_layout.addLayout(sensores_left, 0, 0)
        status_layout.addLayout(sensores_right, 0, 1)

        # ACTUADORES
        actuadores_left = QVBoxLayout()
        actuadores_right = QVBoxLayout()

        self.actuator_labels: Dict[str, QLabel] = {}

        for actuator in self.actuators:
            name = QLabel(f"{actuator.name}:")
            estado = QLabel("🔴 OFF")

            actuadores_left.addWidget(name)
            actuadores_right.addWidget(estado)

            self.actuator_labels[actuator.id] = estado

        status_layout.addLayout(actuadores_left, 1, 0)
        status_layout.addLayout(actuadores_right, 1, 1)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # CONTROL MANUAL
        controls = QGroupBox("Control de Temperatura")
        controls_layout = QHBoxLayout()

        self.btn_modo = QPushButton("Cambiar a MANUAL")
        self.btn_modo.clicked.connect(self.cambiar_modo)
        controls_layout.addWidget(self.btn_modo)

        self.cb_manual = QCheckBox("Habilitar control manual (Ventilador)")
        self.cb_manual.setChecked(False)
        self.cb_manual.setEnabled(False)
        self.cb_manual.stateChanged.connect(self.cambiar_manual)
        controls_layout.addWidget(self.cb_manual)

        self.spin_target = QDoubleSpinBox()
        self.spin_target.setRange(5.0, 40.0)
        self.spin_target.setValue(self.sistema.manual_target)
        self.spin_target.setSingleStep(0.1)
        self.spin_target.setEnabled(False)
        self.spin_target.valueChanged.connect(self.actualizar_target)

        controls_layout.addWidget(QLabel("Objetivo (°C):"))
        controls_layout.addWidget(self.spin_target)

        controls.setLayout(controls_layout)
        layout.addWidget(controls)

        self._update_mode_ui(self.sistema.mode)

        btn_salir = QPushButton("Cerrar sesión")
        btn_salir.clicked.connect(self.cerrar_sesion)
        layout.addWidget(btn_salir)

        self.setLayout(layout)

        # Timer
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.actualizar)
        self.timer.start()

    def _update_mode_ui(self, mode: str):
        is_manual = mode == "manual"
        self.btn_modo.setText("Cambiar a AUTO" if is_manual else "Cambiar a MANUAL")
        self.cb_manual.setEnabled(is_manual)
        self.spin_target.setEnabled(is_manual and self.cb_manual.isChecked())

    def cambiar_modo(self):
        if self.sistema.mode == "auto":
            self.sistema.mode = "manual"
            self.sistema.manual_enabled = True
            self.cb_manual.setChecked(True)
        else:
            self.sistema.mode = "auto"
            self.sistema.manual_enabled = False
            self.cb_manual.setChecked(False)

        self._update_mode_ui(self.sistema.mode)

    def cambiar_manual(self, state):
        enabled = bool(state)
        self.sistema.manual_enabled = enabled
        self.spin_target.setEnabled(enabled and self.sistema.mode == "manual")

    def actualizar_target(self, value):
        self.sistema.manual_target = float(value)

    def update_air_quality_text(self, text_value: str):
        self.lbl_airq.setText(f"Calidad del Aire: {text_value}")

    def actualizar(self):
        self.ctrl_sistema.update()

        def safe_read(tipo):
            try:
                if tipo == "airQuality":
                    return None
                # Se lee directamente de la simulación.
                return self.sistema.get_sensor_reading(tipo)
            except RuntimeError:
                return None

        temp = safe_read("temperature")
        humo = safe_read("smoke")
        luz = safe_read("light")
        dist = safe_read("distance")

        # El mensaje de error ahora es más genérico, ya que la ruta debería estar corregida
        error_msg = "⚠️ No disponible"

        self.lbl_temp.setText(
            f"Temperatura: {temp:.2f} °C" if temp is not None else error_msg
        )
        self.lbl_humo.setText(
            f"Nivel de Humo: {humo:.2f}" if humo is not None else error_msg
        )
        self.lbl_luz.setText(
            f"Nivel de Luz: {luz:.2f} Lux" if luz is not None else error_msg
        )
        self.lbl_distancia.setText(
            f"Distancia: {dist:.2f} cm" if dist is not None else error_msg
        )

        for actuator in self.actuators:
            lbl = self.actuator_labels[actuator.id]
            lbl.setText("🟢 ON" if actuator.state else "🔴 OFF")

    def cleanup(self):
        # Detiene el timer de la ventana y los timers internos de todos los sensores.
        self.timer.stop()
        for sensor in self.sensors:
            sensor.stop_reading()

    def cerrar_sesion(self):
        from src.view.inicio import Inicio

        # Limpiar antes de cerrar
        self.cleanup()

        self.inicio = Inicio()
        self.inicio.show()
        self.close()