# src/view/login.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from src.control.controlador_usuarios import ControladorUsuarios

class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inicio de sesión")
        self.setGeometry(200, 150, 400, 300)
        self.setStyleSheet("background-color:#1E1E1E; color:white;")

        self.ctrl_usuarios = ControladorUsuarios()  # Usa JSON automáticamente

        layout = QVBoxLayout()
        lbl = QLabel("Ingrese sus credenciales")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)

        # Campo usuario
        self.usuario = QLineEdit()
        self.usuario.setPlaceholderText("Usuario")
        layout.addWidget(self.usuario)

        # Campo contraseña
        self.clave = QLineEdit()
        self.clave.setPlaceholderText("Contraseña")
        self.clave.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.clave)

        # Botones
        btn_entrar = QPushButton("Entrar")
        btn_entrar.clicked.connect(self.intentar_login)
        layout.addWidget(btn_entrar)

        btn_volver = QPushButton("Volver")
        btn_volver.clicked.connect(self.volver_inicio)
        layout.addWidget(btn_volver)

        self.setLayout(layout)

    def intentar_login(self):
        """Intenta autenticar el usuario."""
        usuario_texto = self.usuario.text().strip()
        clave_texto = self.clave.text().strip()
        usuario = self.ctrl_usuarios.autenticar(usuario_texto, clave_texto)

        if not usuario:
            QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos.")
            return

        # Abrir la ventana correspondiente según el rol
        if usuario.es_director():
            from src.view.menu_director import MenuDirector
            self.vista = MenuDirector(usuario)
        elif usuario.es_mantenimiento():
            from src.view.ventana_principal import VentanaPrincipal
            self.vista = VentanaPrincipal(usuario)
        else:
            from src.view.ventana_principal import VentanaPrincipal
            self.vista = VentanaPrincipal(usuario)

        self.vista.show()
        self.close()

    def volver_inicio(self):
        """Vuelve a la pantalla de inicio."""
        from src.view.inicio import Inicio
        self.inicio = Inicio()
        self.inicio.show()
        self.close()