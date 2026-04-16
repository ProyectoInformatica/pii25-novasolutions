from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QGroupBox, QScrollArea, QFrame
)
from PySide6.QtCore import QTimer, Qt
from typing import Dict

from src.model.usuario import Usuario
from src.control.controlador_sensores import ControladorSensores
from src.control.controlador_actuadores import ControladorActuadores
from src.view.gestion_usuarios import GestionUsuariosDirector
from src.view.reporte_view import ReporteHistorialView
from src.view.estilos import BTN_PRIMARY, BTN_DANGER, GROUPBOX_STYLE


class MenuDirector(QWidget):
    def __init__(self, usuario: Usuario):
        super().__init__()
        self.usuario = usuario
        self.ctrl_sensores = ControladorSensores()
        self.ctrl_actuadores = ControladorActuadores()

        self.sensor_widgets: Dict[int, QLabel] = {}
        self.actuador_widgets: Dict[int, QLabel] = {}

        self.setWindowTitle("Panel del Director - Nova Solutions")
        self.setGeometry(200, 150, 900, 700)
        self.setStyleSheet("background-color:#0e143b; color:white;")

        self.init_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_todo)
        self.timer.start(2000)

    def init_ui(self):
        layout = QVBoxLayout()

        titulo = QLabel(f"Bienvenido Director General: {self.usuario.nombre} {self.usuario.apellido}")
        titulo.setAlignment(Qt.AlignHCenter)
        titulo.setStyleSheet("font-size:20px; margin-bottom: 10px; font-weight: bold;")
        layout.addWidget(titulo)

        body_layout = QHBoxLayout()
        body_layout.setSpacing(12)

        # Panel izquierdo: opciones
        gestion_group = QGroupBox("Opciones de Dirección")
        gestion_group.setStyleSheet(GROUPBOX_STYLE)
        gestion_layout = QVBoxLayout()

        btn_usuarios = QPushButton("Gestionar Usuarios")
        btn_usuarios.clicked.connect(self.abrir_gestion_usuarios)
        btn_usuarios.setStyleSheet(BTN_PRIMARY)

        btn_reportes = QPushButton("Ver Reportes Históricos")
        btn_reportes.clicked.connect(self.abrir_reportes)
        btn_reportes.setStyleSheet(BTN_PRIMARY)

        gestion_layout.addWidget(btn_usuarios)
        gestion_layout.addWidget(btn_reportes)
        gestion_layout.addStretch()
        gestion_group.setLayout(gestion_layout)
        gestion_group.setFixedWidth(240)

        # Panel derecho: monitoreo
        self.status_group = QGroupBox("Monitoreo de Infraestructura (BDD)")
        self.status_group.setStyleSheet(GROUPBOX_STYLE)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")

        self.container_monitor = QWidget()
        self.layout_monitor = QVBoxLayout(self.container_monitor)
        self.layout_monitor.setAlignment(Qt.AlignTop)

        scroll.setWidget(self.container_monitor)

        status_main_layout = QVBoxLayout()
        status_main_layout.addWidget(scroll)
        self.status_group.setLayout(status_main_layout)

        body_layout.addWidget(gestion_group, 0)
        body_layout.addWidget(self.status_group, 1)
        layout.addLayout(body_layout)

        btn_salir = QPushButton("Cerrar sesión")
        btn_salir.clicked.connect(self.cerrar_sesion)
        btn_salir.setStyleSheet(BTN_DANGER)
        layout.addWidget(btn_salir)

        self.setLayout(layout)
        self.cargar_elementos()

    def cargar_elementos(self):
        while self.layout_monitor.count():
            item = self.layout_monitor.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.sensor_widgets.clear()
        self.actuador_widgets.clear()

        lbl_sensores = QLabel("📡 SENSORES")
        lbl_sensores.setStyleSheet("font-weight: bold; color: #3489e2; margin-top: 10px;")
        self.layout_monitor.addWidget(lbl_sensores)

        self.ctrl_sensores.cargar_desde_bd()
        for s in self.ctrl_sensores.get_all_sensors():
            fila, valor_lbl = self._crear_fila(f"{s.type} ({s.ubicacion})")
            self.sensor_widgets[s.id] = valor_lbl
            self.layout_monitor.addWidget(fila)

        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setStyleSheet("background-color: #555;")
        self.layout_monitor.addWidget(linea)

        lbl_actuadores = QLabel("⚙️ ACTUADORES")
        lbl_actuadores.setStyleSheet("font-weight: bold; color: #3489e2; margin-top: 10px;")
        self.layout_monitor.addWidget(lbl_actuadores)

        for a in self.ctrl_actuadores.get_all_con_sensor():
            fila, estado_lbl = self._crear_fila(f"{a['nombre']} - [{a['tipo']}]")
            self.actuador_widgets[a['id']] = estado_lbl
            self.layout_monitor.addWidget(fila)

    def _crear_fila(self, nombre_texto: str):
        fila = QWidget()
        f_layout = QHBoxLayout(fila)
        nombre_lbl = QLabel(f"<b>{nombre_texto}</b>:")
        valor_lbl = QLabel("...")
        valor_lbl.setStyleSheet("color: #00ff00; font-family: monospace; font-size: 14px;")
        f_layout.addWidget(nombre_lbl)
        f_layout.addStretch()
        f_layout.addWidget(valor_lbl)
        return fila, valor_lbl

    def actualizar_todo(self):
        for id_s, label in self.sensor_widgets.items():
            medida = self.ctrl_sensores.get_ultima_medida(id_s)
            label.setText(f"{medida:.2f}" if medida is not None else "Sin datos")

        for a in self.ctrl_actuadores.get_all_con_sensor():
            if a['id'] in self.actuador_widgets:
                estado_txt = "ENCENDIDO" if a['estado_actual'] == 1 else "APAGADO"
                color = "#00ff00" if a['estado_actual'] == 1 else "#ff4444"
                self.actuador_widgets[a['id']].setText(estado_txt)
                self.actuador_widgets[a['id']].setStyleSheet(f"color: {color}; font-weight: bold;")

    def abrir_gestion_usuarios(self):
        self.gestion = GestionUsuariosDirector(usuario=self.usuario)
        self.gestion.show()

    def abrir_reportes(self):
        self.reporte_view = ReporteHistorialView()
        self.reporte_view.show()

    def cerrar_sesion(self):
        from src.view.inicio import Inicio
        self.timer.stop()
        self.inicio = Inicio()
        self.inicio.show()
        self.close()