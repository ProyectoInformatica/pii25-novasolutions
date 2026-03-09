# src/view/menu_mantenimiento.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QCheckBox, QDoubleSpinBox, QGroupBox, QGridLayout
)
from PySide6.QtCore import QTimer, Qt
from typing import List, Dict

from src.model.sistema import Sistema
from src.model.sensor import Sensor
from src.model.actuador import Ventilador, Rociador, LuzExterior, LuzPasillo
from src.control.controlador_sistema import Controlador_Sistema
from src.control.controlador_sensores import Controlador_Sensores
from src.model.usuario import Usuario

ESCUELA_DATA_FILE = "resources/escuela_data.json"


PANEL_STYLE = """
QGroupBox {
    border: 1px solid #555;
    margin-top: 18px;
    padding-top: 10px;
    border-radius: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 8px;
    margin-left: 10px;
    color: white;
    font-weight: 600;
}
"""

BTN_PRIMARY = """
QPushButton{
    background-color:#3489e2;
    color:white;
    padding:10px;
    border-radius:10px;
    font-size:14px;
}
QPushButton:hover{ background-color:#2f7fd1; }
QPushButton:pressed{ background-color:#2a72ba; }
"""

BTN_DANGER = """
QPushButton{
    background-color:#AA3333;
    color:white;
    padding:10px;
    border-radius:10px;
    font-size:14px;
}
QPushButton:hover{ background-color:#972d2d; }
QPushButton:pressed{ background-color:#822727; }
"""

BTN_NEUTRAL = """
QPushButton{
    background-color:#2b2f36;
    color:white;
    padding:10px;
    border-radius:10px;
    font-size:14px;
    border: 1px solid rgba(255,255,255,0.10);
}
QPushButton:hover{ background-color:#333844; }
QPushButton:pressed{ background-color:#2a2e38; }
"""


class MenuMantenimiento(QWidget):
    def __init__(self, usuario: Usuario):
        super().__init__()

        self.usuario = usuario
        self.sensor_data_file = ESCUELA_DATA_FILE

        self.setWindowTitle("Panel Jefe de Mantenimiento")
        self.setGeometry(200, 150, 900, 600)
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

        for s in self.sensors:
            if s.type == "airQuality":
                s.air_quality_text_actualizada.connect(self.update_air_quality_text)
                break

        layout = QVBoxLayout()

        titulo = QLabel(f"Bienvenido Jefe de Mantenimiento: {usuario.nombre} {usuario.apellido}")
        titulo.setAlignment(Qt.AlignHCenter)
        titulo.setStyleSheet("font-size:20px; margin-bottom: 10px; font-weight:700;")
        layout.addWidget(titulo)

        body_layout = QHBoxLayout()
        body_layout.setSpacing(12)

        opciones_group = QGroupBox("Opciones de Mantenimiento")
        opciones_group.setStyleSheet(PANEL_STYLE)
        opciones_group.setFixedWidth(300)

        opciones_layout = QVBoxLayout()
        opciones_layout.setAlignment(Qt.AlignTop)

        self.btn_modo = QPushButton("Cambiar a MANUAL")
        self.btn_modo.setStyleSheet(BTN_PRIMARY)
        self.btn_modo.clicked.connect(self.cambiar_modo)
        opciones_layout.addWidget(self.btn_modo)

        self.cb_manual = QCheckBox("Habilitar control manual (Ventilador)")
        self.cb_manual.setChecked(False)
        self.cb_manual.setEnabled(False)
        self.cb_manual.stateChanged.connect(self.cambiar_manual)
        self.cb_manual.setStyleSheet("padding:6px;")
        opciones_layout.addWidget(self.cb_manual)

        opciones_layout.addWidget(QLabel("Objetivo de temperatura (°C):"))

        self.spin_target = QDoubleSpinBox()
        self.spin_target.setRange(5.0, 40.0)
        self.spin_target.setValue(self.sistema.manual_target)
        self.spin_target.setSingleStep(1)
        self.spin_target.setEnabled(False)
        self.spin_target.valueChanged.connect(self.actualizar_target)
        self.spin_target.setStyleSheet("""
            QDoubleSpinBox{
                padding: 8px;
                border-radius: 8px;
                background: #1b214d;
                border: 1px solid rgba(255,255,255,0.12);
                color: white;
            }
        """)
        opciones_layout.addWidget(self.spin_target)

        hint = QLabel("En MANUAL puedes forzar el ventilador con el objetivo.")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: rgba(255,255,255,0.75); padding-top: 8px;")
        opciones_layout.addWidget(hint)

        opciones_layout.addStretch()
        opciones_group.setLayout(opciones_layout)

        status_group = QGroupBox("Estado del Sistema en Tiempo Real")
        status_group.setStyleSheet(PANEL_STYLE)
        status_layout = QGridLayout()
        status_layout.setHorizontalSpacing(16)
        status_layout.setVerticalSpacing(10)

        lbl_header_sens = QLabel("LECTURAS DE SENSORES")
        lbl_header_sens.setStyleSheet("font-weight:700; padding:6px 0;")
        status_layout.addWidget(lbl_header_sens, 0, 0, 1, 2)

        self.lbl_temp = QLabel("Temperatura: -- °C")
        self.lbl_humo = QLabel("Nivel de Humo: --")
        self.lbl_luz = QLabel("Nivel de Luz: -- Lux")
        self.lbl_distancia = QLabel("Distancia: -- cm")
        self.lbl_airq = QLabel("Calidad del Aire: Esperando lectura...")

        status_layout.addWidget(QLabel("Temp"), 1, 0)
        status_layout.addWidget(self.lbl_temp, 1, 1)

        status_layout.addWidget(QLabel("Humo"), 2, 0)
        status_layout.addWidget(self.lbl_humo, 2, 1)

        status_layout.addWidget(QLabel("Luz"), 3, 0)
        status_layout.addWidget(self.lbl_luz, 3, 1)

        status_layout.addWidget(QLabel("Distancia"), 4, 0)
        status_layout.addWidget(self.lbl_distancia, 4, 1)

        status_layout.addWidget(QLabel("Calidad Aire"), 5, 0)
        status_layout.addWidget(self.lbl_airq, 5, 1)

        for lbl in [self.lbl_temp, self.lbl_humo, self.lbl_luz, self.lbl_distancia, self.lbl_airq]:
            lbl.setStyleSheet("padding: 4px; color: rgba(255,255,255,0.92);")

        lbl_header_act = QLabel("ESTADO DE ACTUADORES")
        lbl_header_act.setStyleSheet("font-weight:700; padding:10px 0 6px 0;")
        status_layout.addWidget(lbl_header_act, 6, 0, 1, 2)

        self.actuator_labels: Dict[str, QLabel] = {}
        row = 7
        for actuator in self.actuators:
            lbl_name = QLabel(f"{actuator.name}:")
            lbl_state = QLabel("OFF")
            lbl_name.setStyleSheet("padding:4px;")
            lbl_state.setStyleSheet("padding:4px; font-weight:600;")
            self.actuator_labels[actuator.id] = lbl_state

            status_layout.addWidget(lbl_name, row, 0)
            status_layout.addWidget(lbl_state, row, 1)
            row += 1

        status_group.setLayout(status_layout)

        body_layout.addWidget(opciones_group, 0)
        body_layout.addWidget(status_group, 1)

        layout.addLayout(body_layout)

        btn_salir = QPushButton("Cerrar sesión")
        btn_salir.clicked.connect(self.cerrar_sesion)
        btn_salir.setStyleSheet(BTN_DANGER)
        layout.addWidget(btn_salir)

        self.setLayout(layout)

        self._update_mode_ui(self.sistema.mode)

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.actualizar)
        self.timer.start()

    def _update_mode_ui(self, mode: str):
        is_manual = mode == "manual"
        self.btn_modo.setText("Cambiar a AUTO" if is_manual else "Cambiar a MANUAL")
        self.cb_manual.setEnabled(is_manual)
        self.spin_target.setEnabled(is_manual and self.cb_manual.isChecked())

        self.btn_modo.setStyleSheet(BTN_NEUTRAL if is_manual else BTN_PRIMARY)

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
                return self.sistema.get_sensor_reading(tipo)
            except RuntimeError:
                return None

        temp = safe_read("temperature")
        humo = safe_read("smoke")
        luz = safe_read("light")
        dist = safe_read("distance")

        error_msg = "No disponible"

        self.lbl_temp.setText(f"Temperatura: {temp:.2f} °C" if temp is not None else error_msg)
        self.lbl_humo.setText(f"Nivel de Humo: {humo:.2f}" if humo is not None else error_msg)
        self.lbl_luz.setText(f"Nivel de Luz: {luz:.2f} Lux" if luz is not None else error_msg)
        self.lbl_distancia.setText(f"Distancia: {dist:.2f} cm" if dist is not None else error_msg)

        for actuator in self.actuators:
            lbl = self.actuator_labels[actuator.id]
            lbl.setText("ON" if actuator.state else "OFF")

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
