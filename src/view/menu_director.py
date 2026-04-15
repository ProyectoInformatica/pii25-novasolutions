from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QGroupBox, QScrollArea, QFrame
)
from PySide6.QtCore import QTimer, Qt
from typing import Dict

from src.model.usuario import Usuario
from src.model.basedatos import BaseDatos
from src.view.gestion_usuarios import GestionUsuariosDirector
from src.view.reporte_view import ReporteHistorialView


class MenuDirector(QWidget):
    def __init__(self, usuario: Usuario):
        super().__init__()

        self.usuario = usuario
        self.db = BaseDatos()

        # Diccionarios para actualización dinámica
        self.sensor_widgets: Dict[int, QLabel] = {}
        self.actuador_widgets: Dict[int, QLabel] = {}

        self.setWindowTitle("Panel del Director - Nova Solutions")
        self.setGeometry(200, 150, 900, 700)
        self.setStyleSheet("background-color:#0e143b; color:white;")

        self.init_ui()

        # Timer para actualizar lecturas y estados cada 2 segundos
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_todo_desde_db)
        self.timer.start(2000)

    def init_ui(self):
        layout = QVBoxLayout()

        # Título
        titulo = QLabel(f"Bienvenido Director General: {self.usuario.nombre} {self.usuario.apellido}")
        titulo.setAlignment(Qt.AlignHCenter)
        titulo.setStyleSheet("font-size:20px; margin-bottom: 10px; font-weight: bold;")
        layout.addWidget(titulo)

        body_layout = QHBoxLayout()
        body_layout.setSpacing(12)

        # --- PANEL IZQUIERDO: OPCIONES ---
        gestion_group = QGroupBox("Opciones de Dirección")
        gestion_group.setStyleSheet(self.get_groupbox_style())
        gestion_layout = QVBoxLayout()

        btn_usuarios = QPushButton("Gestionar Usuarios")
        btn_usuarios.clicked.connect(self.abrir_gestion_usuarios)
        btn_usuarios.setStyleSheet("background-color:#3489e2; color:white; padding: 8px;")

        btn_reportes = QPushButton("Ver Reportes Históricos")
        btn_reportes.clicked.connect(self.abrir_reportes)
        btn_reportes.setStyleSheet("background-color:#3489e2; color:white; padding: 8px;")

        gestion_layout.addWidget(btn_usuarios)
        gestion_layout.addWidget(btn_reportes)
        gestion_layout.addStretch()
        gestion_group.setLayout(gestion_layout)
        gestion_group.setFixedWidth(240)

        # --- PANEL DERECHO: MONITOREO ---
        self.status_group = QGroupBox("Monitoreo de Infraestructura (BDD)")
        self.status_group.setStyleSheet(self.get_groupbox_style())

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

        # Botón Salir
        btn_salir = QPushButton("Cerrar sesión")
        btn_salir.clicked.connect(self.cerrar_sesion)
        btn_salir.setStyleSheet("background-color:#AA3333; color:white; padding:10px; border-radius:10px;")
        layout.addWidget(btn_salir)

        self.setLayout(layout)

        # Carga inicial
        self.cargar_elementos_desde_db()

    def cargar_elementos_desde_db(self):
        """Crea los widgets para sensores y actuadores basándose en la BDD."""
        # Limpiar widgets previos
        while self.layout_monitor.count():
            item = self.layout_monitor.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        self.sensor_widgets.clear()
        self.actuador_widgets.clear()

        # 1. SECCIÓN SENSORES
        lbl_sec_sens = QLabel("📡 SENSORES")
        lbl_sec_sens.setStyleSheet("font-weight: bold; color: #3489e2; margin-top: 10px;")
        self.layout_monitor.addWidget(lbl_sec_sens)

        sensores = self.db.obtener_sensores()
        for s in sensores:
            fila, valor_lbl = self.crear_fila_monitoreo(f"{s['tipo_sensor']} ({s['ubicacion']})")
            self.sensor_widgets[s['id']] = valor_lbl
            self.layout_monitor.addWidget(fila)

        # Separador
        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setStyleSheet("background-color: #555;")
        self.layout_monitor.addWidget(linea)

        # 2. SECCIÓN ACTUADORES
        lbl_sec_act = QLabel("⚙️ ACTUADORES")
        lbl_sec_act.setStyleSheet("font-weight: bold; color: #3489e2; margin-top: 10px;")
        self.layout_monitor.addWidget(lbl_sec_act)

        # Necesitas implementar 'obtener_actuadores' en basedatos.py
        actuadores = self.db.obtener_actuadores_con_sensor()
        for a in actuadores:
            fila, estado_lbl = self.crear_fila_monitoreo(f"{a['nombre']} - [{a['tipo']}]")
            self.actuador_widgets[a['id']] = estado_lbl
            self.layout_monitor.addWidget(fila)

    def crear_fila_monitoreo(self, nombre_texto):
        fila = QWidget()
        f_layout = QHBoxLayout(fila)
        nombre_lbl = QLabel(f"<b>{nombre_texto}</b>:")
        valor_lbl = QLabel("...")
        valor_lbl.setStyleSheet("color: #00ff00; font-family: monospace; font-size: 14px;")
        f_layout.addWidget(nombre_lbl)
        f_layout.addStretch()
        f_layout.addWidget(valor_lbl)
        return fila, valor_lbl

    def actualizar_todo_desde_db(self):
        """Actualiza valores de sensores y estados de actuadores."""
        # Actualizar Sensores
        for id_s, label in self.sensor_widgets.items():
            medida = self.db.obtener_ultima_medida(id_s)
            label.setText(f"{medida:.2f}" if medida is not None else "Sin datos")

        # Actualizar Actuadores
        actuadores = self.db.obtener_actuadores_con_sensor()
        for a in actuadores:
            if a['id'] in self.actuador_widgets:
                estado_txt = "ENCENDIDO" if a['estado_actual'] == 1 else "APAGADO"
                color = "#00ff00" if a['estado_actual'] == 1 else "#ff4444"
                self.actuador_widgets[a['id']].setText(estado_txt)
                self.actuador_widgets[a['id']].setStyleSheet(f"color: {color}; font-weight: bold;")

    def get_groupbox_style(self):
        return """
        QGroupBox { border: 1px solid #555; margin-top: 18px; padding-top: 10px; font-weight: bold; }
        QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 6px; }
        """

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