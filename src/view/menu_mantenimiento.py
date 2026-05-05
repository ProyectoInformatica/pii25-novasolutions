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
from src.control.controlador_mensajes import ControladorMensajes
from src.view.estilos import BTN_PRIMARY, BTN_DANGER, PANEL_STYLE


class MenuMantenimiento(QWidget):
    def __init__(self, usuario: Usuario):
        super().__init__()
        self.usuario = usuario

        self.ctrl_sensores = ControladorSensores()
        self.ctrl_actuadores = ControladorActuadores()
        self.ctrl_mensajes = ControladorMensajes()

        self.sensor_labels: Dict[int, QLabel] = {}
        self.actuador_labels: Dict[int, QLabel] = {}
        self.sistema = Sistema(sensors=[], actuators=[])
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
        self.cargar_escuelas_en_combo()

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

        self.btn_modo = QPushButton("Modo de operacion: AUTOMATICO")
        self.btn_modo.setStyleSheet(BTN_PRIMARY)
        self.btn_modo.clicked.connect(self.cambiar_modo)

        self.spin_target = QDoubleSpinBox()
        self.spin_target.setRange(15, 40)
        self.spin_target.setValue(35.0)
        self.spin_target.setEnabled(False)
        self.spin_target.setStyleSheet("padding:5px; background:#1b214d; color:white;")
        self.spin_target.valueChanged.connect(
            lambda v: setattr(self.sistema, 'manual_target', v)
        )

        c_layout.addWidget(self.btn_modo)
        c_layout.addWidget(QLabel("Temperatura objetivo (grados C):"))
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

        self.combo_escuela = QComboBox()
        self.combo_escuela.setStyleSheet("background: #1b214d; color:white; padding:5px;")

        btn_crear = QPushButton("Registrar Sensor")
        btn_crear.setStyleSheet(BTN_PRIMARY)
        btn_crear.clicked.connect(self.crear_sensor)

        f_layout.addWidget(QLabel("Tipo de Sensor:"))
        f_layout.addWidget(self.input_tipo)
        f_layout.addWidget(QLabel("Ubicación:"))
        f_layout.addWidget(self.input_ubica)
        f_layout.addWidget(QLabel("Escuela:"))
        f_layout.addWidget(self.combo_escuela)
        f_layout.addWidget(btn_crear)
        crear_group.setLayout(f_layout)

        left_column.addWidget(control_group)
        left_column.addWidget(crear_group)
        left_column.addStretch()

        # Registrar actuador
        crear_act_group = QGroupBox("Registrar Nuevo Actuador")
        crear_act_group.setStyleSheet(PANEL_STYLE)
        act_layout = QVBoxLayout()

        self.input_nom_act = QLineEdit()
        self.input_nom_act.setPlaceholderText("Ej: Ventilador Norte")
        self.input_nom_act.setStyleSheet("background: #1b214d; color:white; padding:5px;")

        self.combo_tipo_act = QComboBox()
        self.combo_tipo_act.addItems(["Ventilador", "Rociador", "Luz Exterior", "Luz Pasillo"])

        self.combo_sensor_vinc = QComboBox()

        btn_vincular = QPushButton("Registrar Actuador")
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

        # Mensajería interna
        msg_group = QGroupBox("Comunicación")
        msg_group.setStyleSheet(PANEL_STYLE)
        msg_layout = QVBoxLayout(msg_group)

        self.btn_mensajes = QPushButton("Mensajes")
        self.btn_mensajes.setStyleSheet(BTN_PRIMARY)
        self.btn_mensajes.clicked.connect(self.abrir_mensajeria)

        msg_layout.addWidget(self.btn_mensajes)
        left_column.addWidget(msg_group)

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

        self.scroll_layout.addWidget(QLabel("<b>SENSORES — LECTURAS EN TIEMPO REAL</b>"))
        self.sensor_layout = QVBoxLayout()
        self.scroll_layout.addLayout(self.sensor_layout)

        self.scroll_layout.addWidget(QLabel("<b>ACTUADORES REGISTRADOS</b>"))
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

            # CORRECCIÓN: s.sensor_type en lugar de s.type
            info = QLabel(f"ID:{s.id} | <b>{s.sensor_type.upper()}</b>\n{s.ubicacion}")
            val_lbl = QLabel("--")
            val_lbl.setStyleSheet("color: #00ff00; font-size:14px; font-weight:bold;")

            btn_del = QPushButton("X")
            btn_del.setFixedSize(30, 30)
            btn_del.setStyleSheet("background:#883333; color:white; border-radius:15px; font-weight:bold;")
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

        tipo_map = {
            "Ventilador": Ventilador,
            "Rociador": Rociador,
            "Luz Exterior": LuzExterior,
            "Luz Pasillo": LuzPasillo,
        }
        self.sistema.actuators = []
        for a in self.ctrl_actuadores.get_all_con_sensor():
            cls = tipo_map.get(a['tipo'])
            if cls:
                self.sistema.actuators.append(
                    cls(id=str(a['id']), id_sensor=a['id_sensor_vinculado'])
                )

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

    def cargar_escuelas_en_combo(self):
        self.combo_escuela.clear()
        escuelas = self.ctrl_sensores.db.obtener_escuelas()
        if not escuelas:
            self.combo_escuela.addItem("Sin escuelas disponibles", None)
        for e in escuelas:
            self.combo_escuela.addItem(e['nombre'], e['id'])

    def cargar_sensores_en_combo(self):
        self.combo_sensor_vinc.clear()
        self.ctrl_sensores.cargar_desde_bd()
        for s in self.ctrl_sensores.get_all_sensors():
            # CORRECCIÓN: s.sensor_type en lugar de s.type
            self.combo_sensor_vinc.addItem(
                f"ID:{s.id} - {s.sensor_type} ({s.ubicacion})",
                s.id
            )

    def crear_sensor(self):
        tipo = self.input_tipo.currentText()
        ubica = self.input_ubica.text().strip()
        id_escuela = self.combo_escuela.currentData()
        nombre_escuela = self.combo_escuela.currentText()

        if not ubica or id_escuela is None:
            QMessageBox.warning(self, "Error", "Completa la ubicación y selecciona una escuela.")
            return

        if self.ctrl_sensores.crear_sensor(tipo, ubica, id_escuela, nombre_escuela):
            self.input_ubica.clear()
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

        # CORRECCIÓN: sensor.sensor_type en lugar de sensor.type
        if reglas.get(tipo_act) != sensor.sensor_type:
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

    def _actualizar_badge_mensajes(self):
        cantidad = self.ctrl_mensajes.contar_no_leidos(self.usuario.id_db)
        if cantidad > 0:
            self.btn_mensajes.setText(f"Mensajes  [{cantidad}]")
        else:
            self.btn_mensajes.setText("Mensajes")

    def abrir_mensajeria(self):
        from src.view.mensajeria_view import MensajeriaView
        ventana_chat = MensajeriaView(self.usuario)
        ventana_chat.exec()

    def actualizar_todo(self):
        self.ctrl_sensores.actualizar_lecturas()
        self.sistema.sensors = self.ctrl_sensores.get_all_sensors()

        for id_s, label in self.sensor_labels.items():
            valor = self.ctrl_sensores.get_ultima_medida(id_s)
            label.setText(f"{valor:.2f}" if valor is not None else "N/A")

        self.ctrl_sistema.update()

        for a in self.ctrl_actuadores.get_all_con_sensor():
            idx = a['id']
            if idx in self.actuador_labels:
                estado_txt = "ON" if a['estado_actual'] else "OFF"
                color = "#00ff00" if a['estado_actual'] else "#ff4444"
                self.actuador_labels[idx].setText(estado_txt)
                self.actuador_labels[idx].setStyleSheet(f"color: {color}; font-weight:bold;")

        self._actualizar_badge_mensajes()

    def cambiar_modo(self):
        nuevo_modo = "manual" if self.sistema.mode == "auto" else "auto"
        self.sistema.mode = nuevo_modo
        self.sistema.manual_enabled = (nuevo_modo == "manual")
        etiqueta = "MANUAL" if nuevo_modo == "manual" else "AUTOMATICO"
        self.btn_modo.setText(f"Modo de operacion: {etiqueta}")
        self.spin_target.setEnabled(nuevo_modo == "manual")
        self.actualizar_todo()

    def cerrar_sesion(self):
        from src.view.inicio import Inicio
        self.timer.stop()
        self.inicio = Inicio()
        self.inicio.show()
        self.close()