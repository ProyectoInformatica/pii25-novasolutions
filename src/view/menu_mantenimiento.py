from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QDoubleSpinBox, QGroupBox, QScrollArea, QLineEdit, QComboBox, QMessageBox
)
from PySide6.QtCore import QTimer, Qt
from typing import Dict

from src.model.usuario import Usuario
from src.model.actuador import Ventilador, Rociador, LuzExterior, LuzPasillo
from src.model.sistema import Sistema
from src.control.controlador_sensores import ControladorSensores
from src.control.controlador_actuadores import ControladorActuadores
from src.control.controlador_sistema import ControladorSistema
from src.view.estilos import BTN_PRIMARY, BTN_DANGER, PANEL_STYLE


class MenuMantenimiento(QWidget):
    def __init__(self, usuario: Usuario):
        super().__init__()
        self.usuario = usuario

        self.ctrl_sensores = ControladorSensores()
        self.ctrl_actuadores = ControladorActuadores()

        self.sensor_labels: Dict[int, QLabel] = {}
        self.actuador_labels: Dict[int, QLabel] = {}
        self.actuator_labels = {}

        self.actuators = [
            Ventilador(id="fan1"),
            Rociador(id="rociador1"),
            LuzExterior(id="luzext1"),
            LuzPasillo(id="luzpasillo1")
        ]

        self.sistema = Sistema(sensors=[], actuators=self.actuators)
        self.ctrl_sistema = ControladorSistema(self.sistema)

        self.setWindowTitle("Gestión de Infraestructura - Nova Solutions")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("background-color:#0e143b; color:white;")

        self.init_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_todo)
        self.timer.start(1500)

        self.cargar_sensores_ui()
        self.cargar_sensores_en_combo()
        self.cargar_actuadores_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        titulo = QLabel(f"Panel Técnico: {self.usuario.nombre} {self.usuario.apellido}")
        titulo.setAlignment(Qt.AlignHCenter)
        titulo.setStyleSheet("font-size:20px; font-weight:700; margin-bottom:10px;")
        main_layout.addWidget(titulo)

        body_layout = QHBoxLayout()

        left_column = QVBoxLayout()

        # Control de climatización
        control_group = QGroupBox("Control de Climatización")
        control_group.setStyleSheet(PANEL_STYLE)
        c_layout = QVBoxLayout()

        self.btn_modo = QPushButton("Modo: AUTO")
        self.btn_modo.setStyleSheet(BTN_PRIMARY)
        self.btn_modo.clicked.connect(self.cambiar_modo)

        self.spin_target = QDoubleSpinBox()
        self.spin_target.setRange(15, 35)
        self.spin_target.setValue(22.0)
        self.spin_target.setStyleSheet("padding:5px; background:#1b214d; color:white;")

        c_layout.addWidget(self.btn_modo)
        c_layout.addWidget(QLabel("Temp. Objetivo (Manual):"))
        c_layout.addWidget(self.spin_target)
        control_group.setLayout(c_layout)

        # Registrar nuevo sensor
        crear_group = QGroupBox("Registrar Nuevo Sensor")
        crear_group.setStyleSheet(PANEL_STYLE)
        f_layout = QVBoxLayout()

        self.input_tipo = QComboBox()
        self.input_tipo.addItems(["temperature", "smoke", "light", "distance", "airQuality"])

        self.input_ubica = QLineEdit()
        self.input_ubica.setPlaceholderText("Laboratorio")
        self.input_ubica.setStyleSheet("background: #1b214d; color:white; padding:5px;")

        self.input_escuela = QLineEdit()
        self.input_escuela.setPlaceholderText("Nombre de la Escuela")
        self.input_escuela.setStyleSheet("background: #1b214d; color:white; padding:5px;")

        btn_crear = QPushButton("Añadir a BDD")
        btn_crear.setStyleSheet(BTN_PRIMARY)
        btn_crear.clicked.connect(self.crear_sensor)

        f_layout.addWidget(QLabel("Tipo de Sensor:"))
        f_layout.addWidget(self.input_tipo)
        f_layout.addWidget(QLabel("Ubicación:"))
        f_layout.addWidget(self.input_ubica)
        f_layout.addWidget(QLabel("Escuela:"))
        f_layout.addWidget(self.input_escuela)
        f_layout.addWidget(btn_crear)
        crear_group.setLayout(f_layout)

        left_column.addWidget(control_group)
        left_column.addWidget(crear_group)
        left_column.addStretch()

        # Registrar actuador
        crear_act_group = QGroupBox("Registrar y Vincular Actuador")
        crear_act_group.setStyleSheet(PANEL_STYLE)
        act_layout = QVBoxLayout()

        self.input_nom_act = QLineEdit()
        self.input_nom_act.setPlaceholderText("Ej: Ventilador Norte")
        self.input_nom_act.setStyleSheet("background: #1b214d; color:white; padding:5px;")

        self.combo_tipo_act = QComboBox()
        self.combo_tipo_act.addItems(["Ventilador", "Rociador", "Luz Exterior", "Luz Pasillo"])

        self.combo_sensor_vinc = QComboBox()

        btn_vincular = QPushButton("Crear y Vincular")
        btn_vincular.setStyleSheet(BTN_PRIMARY)
        btn_vincular.clicked.connect(self.crear_actuador)

        act_layout.addWidget(QLabel("Nombre Actuador:"))
        act_layout.addWidget(self.input_nom_act)
        act_layout.addWidget(QLabel("Tipo de Actuador:"))
        act_layout.addWidget(self.combo_tipo_act)
        act_layout.addWidget(QLabel("Vincular a Sensor:"))
        act_layout.addWidget(self.combo_sensor_vinc)
        act_layout.addWidget(btn_vincular)
        crear_act_group.setLayout(act_layout)

        left_column.addWidget(crear_act_group)

        # Panel derecho: estado global
        right_column = QVBoxLayout()
        status_group = QGroupBox("Estado Global de Dispositivos")
        status_group.setStyleSheet(PANEL_STYLE)
        status_main_layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none; background:transparent;")

        container = QWidget()
        self.scroll_layout = QVBoxLayout(container)

        self.scroll_layout.addWidget(QLabel("<b>📡 SENSORES (LECTURAS)</b>"))
        self.sensor_layout = QVBoxLayout()
        self.scroll_layout.addLayout(self.sensor_layout)

        self.scroll_layout.addWidget(QLabel("<b>⚙️ ACTUADORES CONFIGURADOS</b>"))
        self.actuador_db_layout = QVBoxLayout()
        self.scroll_layout.addLayout(self.actuador_db_layout)

        scroll.setWidget(container)
        status_main_layout.addWidget(scroll)
        status_group.setLayout(status_main_layout)
        right_column.addWidget(status_group)

        body_layout.addLayout(left_column, 1)
        body_layout.addLayout(right_column, 2)
        main_layout.addLayout(body_layout)

        btn_salir = QPushButton("Cerrar Sesión")
        btn_salir.setStyleSheet(BTN_DANGER)
        btn_salir.clicked.connect(self.cerrar_sesion)
        main_layout.addWidget(btn_salir)

        self.setLayout(main_layout)

    def cargar_sensores_ui(self):
        for i in reversed(range(self.sensor_layout.count())):
            item = self.sensor_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
        self.sensor_labels.clear()

        self.ctrl_sensores.cargar_desde_bd()
        for s in self.ctrl_sensores.get_all_sensors():
            item = QWidget()
            item_layout = QHBoxLayout(item)
            item.setStyleSheet("background: rgba(255,255,255,0.05); border-radius:5px; margin:2px;")

            info = QLabel(f"ID:{s.id} | <b>{s.type.upper()}</b>\n{s.ubicacion}")
            val_lbl = QLabel("--")
            val_lbl.setStyleSheet("color: #00ff00; font-size:14px; font-weight:bold;")

            btn_del = QPushButton("✕")
            btn_del.setFixedSize(30, 30)
            btn_del.setStyleSheet("background:#883333; color:white; border-radius:15px;")
            btn_del.clicked.connect(lambda _, id_s=s.id: self.eliminar_sensor(id_s))

            item_layout.addWidget(info)
            item_layout.addStretch()
            item_layout.addWidget(val_lbl)
            item_layout.addWidget(btn_del)

            self.sensor_layout.addWidget(item)
            self.sensor_labels[s.id] = val_lbl

    def cargar_actuadores_ui(self):
        for i in reversed(range(self.actuador_db_layout.count())):
            item = self.actuador_db_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
        self.actuador_labels.clear()

        for a in self.ctrl_actuadores.get_all_con_sensor():
            item = QWidget()
            item_layout = QHBoxLayout(item)
            item.setStyleSheet("background: rgba(52, 137, 226, 0.1); border-radius:5px; margin:2px;")

            info = QLabel(f"<b>{a['nombre']}</b> ({a['tipo']})\nSensor: {a['tipo_sensor']}")
            est_lbl = QLabel("OFF")
            est_lbl.setStyleSheet("font-weight:bold; color: #ff4444;")

            item_layout.addWidget(info)
            item_layout.addStretch()
            item_layout.addWidget(est_lbl)

            self.actuador_db_layout.addWidget(item)
            self.actuador_labels[a['id']] = est_lbl

    def cargar_sensores_en_combo(self):
        self.combo_sensor_vinc.clear()
        self.ctrl_sensores.cargar_desde_bd()
        for s in self.ctrl_sensores.get_all_sensors():
            self.combo_sensor_vinc.addItem(
                f"ID:{s.id} - {s.type} ({s.ubicacion})",
                s.id
            )

    def crear_sensor(self):
        tipo = self.input_tipo.currentText()
        ubica = self.input_ubica.text()
        escuela = self.input_escuela.text()

        if not ubica or not escuela:
            QMessageBox.warning(self, "Error", "Completa todos los campos.")
            return

        if self.ctrl_sensores.crear_sensor(tipo, ubica, escuela):
            self.input_ubica.clear()
            self.input_escuela.clear()
            self.cargar_sensores_ui()
            self.cargar_sensores_en_combo()
        else:
            QMessageBox.critical(self, "Error", "No se pudo conectar a la BDD.")

    def eliminar_sensor(self, id_s: int):
        reply = QMessageBox.question(self, 'Confirmar', f"¿Eliminar sensor ID {id_s}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.ctrl_sensores.eliminar_sensor(id_s):
                self.cargar_sensores_ui()
                self.cargar_sensores_en_combo()

    def crear_actuador(self):
        nombre = self.input_nom_act.text()
        tipo_act = self.combo_tipo_act.currentText()
        id_sensor = self.combo_sensor_vinc.currentData()

        if not nombre or id_sensor is None:
            QMessageBox.warning(self, "Error", "Falta nombre o seleccionar sensor.")
            return

        reglas = {
            "Ventilador": "temperature",
            "Rociador": "smoke",
            "Luz Exterior": "light",
            "Luz Pasillo": "distance"
        }

        sensor = next((s for s in self.ctrl_sensores.get_all_sensors() if s.id == id_sensor), None)
        if sensor is None:
            QMessageBox.warning(self, "Error", "Sensor no encontrado.")
            return

        if reglas.get(tipo_act) != sensor.type:
            QMessageBox.warning(
                self, "Error",
                f"Un {tipo_act} solo se asigna a sensor de tipo '{reglas.get(tipo_act)}'."
            )
            return

        if self.ctrl_actuadores.crear_actuador(nombre, tipo_act, id_sensor):
            QMessageBox.information(self, "Éxito", "Actuador creado.")
            self.input_nom_act.clear()
            self.cargar_actuadores_ui()
        else:
            QMessageBox.critical(self, "Error", "Error al guardar en BDD.")

    def actualizar_todo(self):
        for id_s, label in self.sensor_labels.items():
            valor = self.ctrl_sensores.get_ultima_medida(id_s)
            label.setText(f"{valor:.2f}" if valor is not None else "N/A")

        for a in self.ctrl_actuadores.get_all_con_sensor():
            idx = a['id']
            if idx in self.actuador_labels:
                estado_txt = "ON" if a['estado_actual'] else "OFF"
                color = "#00ff00" if a['estado_actual'] else "#ff4444"
                self.actuador_labels[idx].setText(estado_txt)
                self.actuador_labels[idx].setStyleSheet(f"color: {color}; font-weight:bold;")

        self.ctrl_sistema.update()
        for a_hw in self.actuators:
            if a_hw.id in self.actuator_labels:
                self.actuator_labels[a_hw.id].setText(f"{a_hw.name}: {'ON' if a_hw.state else 'OFF'}")

    def cambiar_modo(self):
        pass

    def cerrar_sesion(self):
        from src.view.inicio import Inicio
        self.timer.stop()
        self.inicio = Inicio()
        self.inicio.show()
        self.close()