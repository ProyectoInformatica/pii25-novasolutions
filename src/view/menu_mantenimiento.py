# src/view/menu_mantenimiento.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QCheckBox, QDoubleSpinBox, QGroupBox, QGridLayout
)
from PySide6.QtCore import QTimer, Qt

# Importar las clases necesarias
from src.model.sensor import Sensor
from src.model.actuador import Ventilador, Rociador, LuzExterior, Actuador
from src.model.sistema import Sistema
from src.control.controlador_sistema import Controlador_Sistema
from src.control.controlador_sensores import Controlador_Sensores


class MenuMantenimiento(QWidget):
    def __init__(self, usuario, sensor_data_file="simulation_data.json"):
        super().__init__()

        self.usuario = usuario
        self.sensor_data_file = sensor_data_file

        self.setWindowTitle("Panel Jefe de Mantenimiento")
        self.setGeometry(200, 150, 800, 600)
        self.setStyleSheet("background-color:#1E1E1E; color:white;")

        # MODELO + CONTROLADORES
        # Mantener la inicialización de sensores y actuadores igual
        self.sensors = [
            Sensor(id="temp1", sensor_type="temperature", data_file=self.sensor_data_file),
            Sensor(id="smoke1", sensor_type="smoke", data_file=self.sensor_data_file),
            Sensor(id="light1", sensor_type="light", data_file=self.sensor_data_file)
        ]
        self.actuators = [
            Ventilador(id="calentador1"),
            Rociador(id="rociador1"),
            LuzExterior(id="luzext1")
        ]

        self.sistema = Sistema(sensors=self.sensors, actuators=self.actuators)
        self.ctrl_sensores = Controlador_Sensores(self.sensors)
        self.ctrl_sistema = Controlador_Sistema(self.sistema)

        # LAYOUT PRINCIPAL
        layout = QVBoxLayout()

        titulo = QLabel(f"Bienvenido Jefe de Mantenimiento: {usuario.nombre_usuario}")
        titulo.setAlignment(Qt.AlignHCenter)
        titulo.setStyleSheet("font-size:20px;")
        layout.addWidget(titulo)

        # SENSORES y ACTUADORES
        status_group = QGroupBox("Estado del Sistema")
        status_layout = QGridLayout()
        status_group.setStyleSheet("QGroupBox { border: 1px solid #555; margin-top: 10px; }")

        # Lecturas de Sensores
        status_layout.addWidget(QLabel("--- SENSORES ---"), 0, 0, 1, 2)

        self.lbl_temp = QLabel("Temperatura: -- °C")
        self.lbl_temp.setStyleSheet("font-weight: bold; padding: 5px;")
        status_layout.addWidget(QLabel("🌡️ Temp"), 1, 0)
        status_layout.addWidget(self.lbl_temp, 1, 1)

        self.lbl_humo = QLabel("Nivel de Humo: --")
        status_layout.addWidget(QLabel("💨 Humo"), 2, 0)
        status_layout.addWidget(self.lbl_humo, 2, 1)

        self.lbl_luz = QLabel("Nivel de Luz: -- Lux")
        status_layout.addWidget(QLabel("💡 Luz"), 3, 0)
        status_layout.addWidget(self.lbl_luz, 3, 1)

        # 2. Estado de Actuadores
        status_layout.addWidget(QLabel("--- ACTUADORES ---"), 4, 0, 1, 2)

        self.actuator_labels = {}
        for i, actuator in enumerate(self.actuators):
            lbl_name = QLabel(f"{actuator.name}:")
            lbl_state = QLabel("🔴 OFF")
            self.actuator_labels[actuator.id] = lbl_state

            row = i + 5
            status_layout.addWidget(lbl_name, row, 0)
            status_layout.addWidget(lbl_state, row, 1)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # CONTROLES MANUALES
        controls = QGroupBox("Control Manual de Temperatura")
        controls_layout = QHBoxLayout()

        # Botón modo auto/manual
        self.btn_modo = QPushButton("Cambiar a MANUAL")
        self.btn_modo.clicked.connect(self.cambiar_modo)
        controls_layout.addWidget(self.btn_modo)

        # Activar control manual
        self.cb_manual = QCheckBox("Control manual activado")
        self.cb_manual.stateChanged.connect(self.cambiar_manual)
        controls_layout.addWidget(self.cb_manual)

        # Target
        self.spin_target = QDoubleSpinBox()
        self.spin_target.setRange(5.0, 40.0)
        self.spin_target.setValue(self.sistema.manual_target)
        self.spin_target.setSingleStep(0.1)
        self.spin_target.valueChanged.connect(self.actualizar_target)

        controls_layout.addWidget(QLabel("Objetivo (°C):"))
        controls_layout.addWidget(self.spin_target)

        controls.setLayout(controls_layout)
        layout.addWidget(controls)

        # BOTÓN SALIR
        btn_salir = QPushButton("Cerrar sesión")
        btn_salir.clicked.connect(self.cerrar_sesion)
        layout.addWidget(btn_salir)

        self.setLayout(layout)

        # TIMER DE ACTUALIZACIÓN
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # 1 segundo
        self.timer.timeout.connect(self.actualizar)
        self.timer.start()

    def cambiar_modo(self):
        """Alterna entre modo automático y manual."""
        if self.sistema.mode == "auto":
            self.sistema.set_mode("manual")
            self.btn_modo.setText("Cambiar a AUTO")
        else:
            self.sistema.set_mode("auto")
            self.cb_manual.setChecked(False)
            self.btn_modo.setText("Cambiar a MANUAL")

    def cambiar_manual(self, state):
        """Activa/Desactiva el control manual de temperatura."""
        enabled = bool(state)
        self.sistema.manual_enabled = enabled

        if enabled:
            self.sistema.set_mode("manual")
            self.btn_modo.setText("Cambiar a AUTO")

    def actualizar_target(self, value):
        """Actualiza el valor objetivo de temperatura en el sistema."""
        self.sistema.manual_target = float(value)

    def actualizar(self):
        """Lee sensores, aplica control y actualiza la UI cada segundo."""

        def safe_read(sensor_type):
            try:
                return self.sistema.get_sensor_reading(sensor_type)
            except RuntimeError:
                return None  # Devolvemos None si falla la lectura del JSON

        temp = safe_read("temperature")
        smoke = safe_read("smoke")
        light = safe_read("light")

        # Actualización de etiquetas
        self.lbl_temp.setText(f"Temperatura: {temp:.2f} °C" if temp is not None else "Temperatura: ⚠️ ERROR (JSON)")
        self.lbl_humo.setText(f"Nivel de Humo: {smoke:.2f}" if smoke is not None else "Nivel de Humo: ⚠️ ERROR (JSON)")
        self.lbl_luz.setText(f"Nivel de Luz: {light:.2f} Lux" if light is not None else "Nivel de Luz: ⚠️ ERROR (JSON)")

        # 2. Aplicar control
        self.ctrl_sistema.update()

        # 3. Actualizar el estado de los actuadores en la UI
        for actuator in self.actuators:
            label = self.actuator_labels.get(actuator.id)
            if label:
                state_text = "🟢 ON" if actuator.state else "🔴 OFF"
                label.setText(state_text)

    def cerrar_sesion(self):
        from src.view.inicio import Inicio

        self.inicio = Inicio()
        self.inicio.show()

        self.close()