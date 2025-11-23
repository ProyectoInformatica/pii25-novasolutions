from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QCheckBox, QDoubleSpinBox
)
from PySide6.QtCore import QTimer, Qt

from src.model.sensor import Sensor
from src.model.sistema import Sistema
from src.control.controlador_sistema import Controlador_Sistema
from src.control.controlador_sensores import Controlador_Sensores


class MenuMantenimiento(QWidget):
    def __init__(self, usuario, sensor_data_file=None):
        super().__init__()

        self.usuario = usuario
        self.setWindowTitle("Panel Jefe de Mantenimiento")
        self.setGeometry(200, 150, 800, 600)
        self.setStyleSheet("background-color:#1E1E1E; color:white;")

        # -------- MODELO + CONTROLADORES ----------
        self.sensor = Sensor(id="temp1", name="temp_sim", data_file=sensor_data_file)
        self.sistema = Sistema(sensors=[self.sensor], actuators=[])
        self.ctrl_sensores = Controlador_Sensores([self.sensor])
        self.ctrl_sistema = Controlador_Sistema(self.sistema)

        # -------- LAYOUT PRINCIPAL ----------
        layout = QVBoxLayout()

        titulo = QLabel(f"Bienvenido Jefe de Mantenimiento: {usuario.nombre_usuario}")
        titulo.setAlignment(Qt.AlignHCenter)
        titulo.setStyleSheet("font-size:20px;")
        layout.addWidget(titulo)

        # --------- TEMPERATURA ACTUAL ----------
        self.lbl_temp = QLabel("Temperatura actual: -- °C")
        self.lbl_temp.setStyleSheet("font-size:18px; padding:10px;")
        layout.addWidget(self.lbl_temp)

        # --------- CONTROLES MANUALES ----------
        controls = QHBoxLayout()

        # Botón modo auto/manual
        self.btn_modo = QPushButton("Cambiar a MANUAL")
        self.btn_modo.clicked.connect(self.cambiar_modo)
        controls.addWidget(self.btn_modo)

        # Activar control manual
        self.cb_manual = QCheckBox("Control manual activado")
        self.cb_manual.stateChanged.connect(self.cambiar_manual)
        controls.addWidget(self.cb_manual)

        # Target
        self.spin_target = QDoubleSpinBox()
        self.spin_target.setRange(5.0, 40.0)
        self.spin_target.setValue(self.sistema.manual_target)
        self.spin_target.setSingleStep(0.1)
        self.spin_target.valueChanged.connect(self.actualizar_target)
        controls.addWidget(QLabel("Objetivo (°C):"))
        controls.addWidget(self.spin_target)

        layout.addLayout(controls)

        # -------- GENERAR JSON DE SIMULACIÓN --------
        btn_json = QPushButton("Generar JSON de prueba")
        btn_json.clicked.connect(self.generar_json)
        layout.addWidget(btn_json)

        # -------- BOTÓN SALIR ----------
        btn_salir = QPushButton("Cerrar sesión")
        btn_salir.clicked.connect(self.cerrar_sesion)
        layout.addWidget(btn_salir)

        self.setLayout(layout)

        # -------- TIMER DE ACTUALIZACIÓN ----------
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # 1 segundo
        self.timer.timeout.connect(self.actualizar)
        self.timer.start()

    def cambiar_modo(self):
        if self.sistema.mode == "auto":
            self.sistema.set_mode("manual")
            self.btn_modo.setText("Cambiar a AUTO")
        else:
            self.sistema.set_mode("auto")
            self.cb_manual.setChecked(False)
            self.btn_modo.setText("Cambiar a MANUAL")

    def cambiar_manual(self, state):
        enabled = bool(state)
        self.sistema.manual_enabled = enabled

        if enabled:
            self.sistema.set_mode("manual")
            self.btn_modo.setText("Cambiar a AUTO")

    def actualizar_target(self, value):
        self.sistema.manual_target = float(value)

    def actualizar(self):
        readings = self.ctrl_sensores.read_all()
        temp = readings.get("temp1", None)

        if temp is not None:
            self.lbl_temp.setText(f"Temperatura actual: {temp:.2f} °C")
        else:
            self.lbl_temp.setText("Temperatura actual: -- °C")

        # Aplicar control
        self.ctrl_sistema.update()

    def generar_json(self):
        if self.sensor.data_file:
            from src.model.sensor import Sensor as S
            S.generate_simulation_json(self.sensor.data_file, self.spin_target.value())
            self.lbl_temp.setText(f"JSON generado con {self.spin_target.value():.2f} °C")
        else:
            self.lbl_temp.setText("No se puede generar JSON: no hay ruta asignada.")


    def cerrar_sesion(self):
        from src.view.inicio import Inicio
        self.inicio = Inicio()
        self.inicio.show()
        self.close()
