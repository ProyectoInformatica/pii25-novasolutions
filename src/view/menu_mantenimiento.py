from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QCheckBox, QDoubleSpinBox, QGroupBox, QGridLayout,
    QScrollArea, QLineEdit, QComboBox, QMessageBox
)
from PySide6.QtCore import QTimer, Qt
from typing import List, Dict

from src.model.usuario import Usuario
from src.model.basedatos import BaseDatos
from src.model.actuador import Ventilador, Rociador, LuzExterior, LuzPasillo
from src.control.controlador_sistema import Controlador_Sistema
from src.model.sistema import Sistema

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
        self.db = BaseDatos()

        # Referencias para actualización en tiempo real
        self.sensor_labels: Dict[int, QLabel] = {}

        # Actuadores (estos suelen ser fijos por hardware, pero los mantenemos)
        self.actuators = [
            Ventilador(id="fan1"),
            Rociador(id="rociador1"),
            LuzExterior(id="luzext1"),
            LuzPasillo(id="luzpasillo1")
        ]

        # Sistema mínimo para el controlador (ahora los sensores vendrán de la DB)
        self.sistema = Sistema(sensors=[], actuators=self.actuators)
        self.ctrl_sistema = Controlador_Sistema(self.sistema)

        self.setWindowTitle("Gestión de Infraestructura - Nova Solutions")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("background-color:#0e143b; color:white;")

        self.init_ui()

        # Timer de actualización (cada 1.5 segundos para no saturar la BDD)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_todo)
        self.timer.start(1500)

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Header
        titulo = QLabel(f"Panel Técnico: {self.usuario.nombre} {self.usuario.apellido}")
        titulo.setAlignment(Qt.AlignHCenter)
        titulo.setStyleSheet("font-size:20px; font-weight:700; margin-bottom:10px;")
        main_layout.addWidget(titulo)

        body_layout = QHBoxLayout()

        # --- COLUMNA IZQUIERDA: CONTROLES Y CREACIÓN ---
        left_column = QVBoxLayout()

        # 1. Grupo de Control de Actuadores (Tu lógica original)
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

        # 2. Grupo de Creación de Sensores (NUEVO)
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

        # --- COLUMNA DERECHA: LISTA DINÁMICA ---
        right_column = QVBoxLayout()

        status_group = QGroupBox("Sensores Activos y Actuadores")
        status_group.setStyleSheet(PANEL_STYLE)
        status_main_layout = QVBoxLayout()

        # Scroll para sensores
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none; background:transparent;")

        self.sensor_container = QWidget()
        self.sensor_layout = QVBoxLayout(self.sensor_container)
        self.sensor_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.sensor_container)

        status_main_layout.addWidget(QLabel("<b>LECTURAS EN TIEMPO REAL</b>"))
        status_main_layout.addWidget(scroll)

        # Actuadores (fijos al final)
        status_main_layout.addWidget(QLabel("<b>ESTADO ACTUADORES</b>"))
        self.actuator_labels = {}
        for a in self.actuators:
            l = QLabel(f"{a.name}: OFF")
            self.actuator_labels[a.id] = l
            status_main_layout.addWidget(l)

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
        self.cargar_sensores_ui()

    # --- LÓGICA DE BASE DE DATOS ---

    def cargar_sensores_ui(self):
        """Limpia y reconstruye la lista de sensores desde la BDD."""
        for i in reversed(range(self.sensor_layout.count())):
            self.sensor_layout.itemAt(i).widget().setParent(None)
        self.sensor_labels.clear()

        sensores = self.db.obtener_sensores()
        for s in sensores:
            item = QWidget()
            item_layout = QHBoxLayout(item)
            item.setStyleSheet("background: rgba(255,255,255,0.05); border-radius:5px; margin:2px;")

            info = QLabel(f"ID:{s['id']} | <b>{s['tipo_sensor'].upper()}</b>\n{s['ubicacion']}")
            val_lbl = QLabel("--")
            val_lbl.setStyleSheet("color: #00ff00; font-size:14px; font-weight:bold;")

            btn_del = QPushButton("✕")
            btn_del.setFixedSize(30, 30)
            btn_del.setStyleSheet("background:#883333; color:white; border-radius:15px;")
            btn_del.clicked.connect(lambda checked, id_s=s['id']: self.eliminar_sensor(id_s))

            item_layout.addWidget(info)
            item_layout.addStretch()
            item_layout.addWidget(val_lbl)
            item_layout.addWidget(btn_del)

            self.sensor_layout.addWidget(item)
            self.sensor_labels[s['id']] = val_lbl

    def crear_sensor(self):
        tipo = self.input_tipo.currentText()
        ubica = self.input_ubica.text()
        escuela = self.input_escuela.text()

        if not ubica or not escuela:
            QMessageBox.warning(self, "Error", "Completa todos los campos.")
            return

        id_nuevo = self.db.crear_sensor(tipo, ubica, escuela)
        if id_nuevo:
            self.input_ubica.clear()
            self.cargar_sensores_ui()
        else:
            QMessageBox.critical(self, "Error", "No se pudo conectar a la BDD.")

    def eliminar_sensor(self, id_s):
        reply = QMessageBox.question(self, 'Confirmar', f"¿Eliminar sensor ID {id_s}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.db.eliminar_sensor(id_s):
                self.cargar_sensores_ui()

    def actualizar_todo(self):
        """Actualiza lecturas de sensores y lógica de actuadores."""
        # 1. Actualizar valores de sensores desde registros
        for id_s, label in self.sensor_labels.items():
            valor = self.db.obtener_ultima_medida(id_s)
            if valor is not None:
                label.setText(f"{valor:.2f}")
            else:
                label.setText("N/A")

        # 2. Ejecutar lógica de control (opcional, si quieres que el controlador reaccione)
        self.ctrl_sistema.update()
        for a in self.actuators:
            self.actuator_labels[a.id].setText(f"{a.name}: {'ON' if a.state else 'OFF'}")

    # --- MANTENER TUS FUNCIONES ORIGINALES ---
    def cambiar_modo(self):
        # ... misma lógica que tenías para manual/auto ...
        pass

    def cerrar_sesion(self):
        from src.view.inicio import Inicio
        self.timer.stop()
        self.inicio = Inicio()
        self.inicio.show()
        self.close()