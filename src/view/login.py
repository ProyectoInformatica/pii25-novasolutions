from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from src.control.controlador_usuarios import ControladorUsuarios

ICON_USER_PATH = "resources/img.png"


class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inicio de sesión")
        self.setGeometry(200, 150, 420, 340)
        self.setStyleSheet("background-color:#0e143b; color:white;")

        self.ctrl_usuarios = ControladorUsuarios()

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(30, 20, 30, 20)

        icon_lbl = QLabel()
        icon_lbl.setAlignment(Qt.AlignCenter)

        pix = QPixmap(ICON_USER_PATH)
        if not pix.isNull():
            pix = pix.scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_lbl.setPixmap(pix)

        layout.addWidget(icon_lbl)

        lbl = QLabel("Ingrese su correo y contraseña")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("font-size:16px; font-weight:700;")
        layout.addWidget(lbl)

        self.correo = QLineEdit()
        self.correo.setPlaceholderText("Correo electrónico")
        self.correo.setStyleSheet("""
            QLineEdit{
                padding:10px;
                border-radius:10px;
                background:#1b214d;
                border:1px solid rgba(255,255,255,0.15);
                color:white;
            }
        """)
        layout.addWidget(self.correo)

        self.clave = QLineEdit()
        self.clave.setPlaceholderText("Contraseña")
        self.clave.setEchoMode(QLineEdit.EchoMode.Password)
        self.clave.setStyleSheet("""
            QLineEdit{
                padding:10px;
                border-radius:10px;
                background:#1b214d;
                border:1px solid rgba(255,255,255,0.15);
                color:white;
            }
        """)
        layout.addWidget(self.clave)

        btn_entrar = QPushButton("Entrar")
        btn_entrar.clicked.connect(self.intentar_login)
        btn_entrar.setStyleSheet("""
            QPushButton{
                background-color:#3489e2;
                color:white;
                padding:10px;
                border-radius:10px;
                font-size:14px;
            }
            QPushButton:hover{ background-color:#2f7fd1; }
            QPushButton:pressed{ background-color:#2a72ba; }
        """)
        layout.addWidget(btn_entrar)

        btn_volver = QPushButton("Volver")
        btn_volver.clicked.connect(self.volver_inicio)
        btn_volver.setStyleSheet("""
            QPushButton{
                background-color:#AA3333;
                color:white;
                padding:10px;
                border-radius:10px;
                font-size:14px;
            }
            QPushButton:hover{ background-color:#972d2d; }
            QPushButton:pressed{ background-color:#822727; }
        """)
        layout.addWidget(btn_volver)

        self.setLayout(layout)

    def intentar_login(self):
        correo_texto = self.correo.text().strip()
        clave_texto = self.clave.text().strip()
        usuario = self.ctrl_usuarios.autenticar(correo_texto, clave_texto)

        if not usuario:
            QMessageBox.warning(self, "Error", "Correo o contraseña incorrectos.")
            return

        if usuario.es_director():
            from src.view.menu_director import MenuDirector
            self.vista = MenuDirector(usuario)
        elif usuario.es_mantenimiento():
            from src.view.menu_mantenimiento import MenuMantenimiento
            self.vista = MenuMantenimiento(usuario)
        else:
            QMessageBox.warning(self, "Acceso Denegado", "Rol de usuario no reconocido.")
            return

        self.vista.show()
        self.close()

    def volver_inicio(self):
        from src.view.inicio import Inicio
        self.inicio = Inicio()
        self.inicio.show()
        self.close()