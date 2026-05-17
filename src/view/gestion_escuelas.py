from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QScrollArea, QGroupBox, QMessageBox, QFrame
)
from PySide6.QtCore import Qt

from src.model.basedatos import BaseDatos
from src.view.estilos import BTN_PRIMARY, BTN_DANGER, GROUPBOX_STYLE


class GestionEscuelas(QWidget):
    def __init__(self):
        super().__init__()
        self.db = BaseDatos()
        self.setWindowTitle("Gestión de Escuelas - Nova Solutions")
        self.setGeometry(250, 200, 700, 500)
        self.setStyleSheet("background-color:#0e143b; color:white;")
        self.init_ui()
        self.cargar_escuelas()

    def init_ui(self):
        main_layout = QVBoxLayout()

        titulo = QLabel("Gestión de Escuelas")
        titulo.setAlignment(Qt.AlignHCenter)
        titulo.setStyleSheet("font-size:18px; font-weight:bold; margin-bottom:10px;")
        main_layout.addWidget(titulo)

        body = QHBoxLayout()

        # Panel izquierdo: formulario de alta
        form_group = QGroupBox("Registrar Nueva Escuela")
        form_group.setStyleSheet(GROUPBOX_STYLE)
        form_layout = QVBoxLayout()

        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre de la escuela")
        self.input_nombre.setStyleSheet("background:#1b214d; color:white; padding:5px;")

        self.input_direccion = QLineEdit()
        self.input_direccion.setPlaceholderText("Dirección")
        self.input_direccion.setStyleSheet("background:#1b214d; color:white; padding:5px;")

        btn_crear = QPushButton("Registrar Escuela")
        btn_crear.setStyleSheet(BTN_PRIMARY)
        btn_crear.clicked.connect(self.crear_escuela)

        form_layout.addWidget(QLabel("Nombre:"))
        form_layout.addWidget(self.input_nombre)
        form_layout.addWidget(QLabel("Dirección:"))
        form_layout.addWidget(self.input_direccion)
        form_layout.addWidget(btn_crear)
        form_layout.addStretch()
        form_group.setLayout(form_layout)
        form_group.setFixedWidth(260)

        # Panel derecho: listado de escuelas
        lista_group = QGroupBox("Escuelas Registradas")
        lista_group.setStyleSheet(GROUPBOX_STYLE)
        lista_layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none; background:transparent;")

        self.container = QWidget()
        self.lista_layout = QVBoxLayout(self.container)
        self.lista_layout.setAlignment(Qt.AlignTop)

        scroll.setWidget(self.container)
        lista_layout.addWidget(scroll)
        lista_group.setLayout(lista_layout)

        body.addWidget(form_group)
        body.addWidget(lista_group, 1)
        main_layout.addLayout(body)
        self.setLayout(main_layout)

    def cargar_escuelas(self):
        while self.lista_layout.count():
            item = self.lista_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        escuelas = self.db.obtener_escuelas()
        if not escuelas:
            self.lista_layout.addWidget(QLabel("No hay escuelas registradas."))
            return

        for e in escuelas:
            fila = QWidget()
            fila.setStyleSheet("background:rgba(255,255,255,0.05); border-radius:5px; margin:2px;")
            fila_layout = QHBoxLayout(fila)

            info = QLabel(f"<b>{e['nombre']}</b><br><small>{e['direccion']}</small>")
            info.setTextFormat(Qt.RichText)

            btn_baja = QPushButton("Dar de baja")
            btn_baja.setFixedWidth(110)
            btn_baja.setStyleSheet(BTN_DANGER)
            btn_baja.clicked.connect(lambda _, id_e=e['id'], nom=e['nombre']: self.dar_baja(id_e, nom))

            fila_layout.addWidget(info, 1)
            fila_layout.addWidget(btn_baja)
            self.lista_layout.addWidget(fila)

        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setStyleSheet("background:#555; margin-top:4px;")
        self.lista_layout.addWidget(separador)

    def crear_escuela(self):
        nombre = self.input_nombre.text().strip()
        direccion = self.input_direccion.text().strip()

        if not nombre or not direccion:
            QMessageBox.warning(self, "Error", "Completa el nombre y la dirección.")
            return

        if self.db.crear_escuela(nombre, direccion):
            self.input_nombre.clear()
            self.input_direccion.clear()
            self.cargar_escuelas()
        else:
            QMessageBox.critical(self, "Error", "No se pudo registrar la escuela.")

    def dar_baja(self, id_escuela: int, nombre: str):
        reply = QMessageBox.question(
            self, "Confirmar baja",
            f"¿Dar de baja la escuela '{nombre}'?\nLos sensores asociados quedarán inactivos.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.db.dar_baja_escuela(id_escuela):
                self.cargar_escuelas()
            else:
                QMessageBox.critical(self, "Error", "No se pudo dar de baja la escuela.")
