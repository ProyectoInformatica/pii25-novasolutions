from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtCore import Qt
#si
class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inicio de sesión")
        self.setGeometry(200, 150, 400, 300)
        self.setStyleSheet("background-color:#1E1E1E; color:white;")

        layout = QVBoxLayout()
        lbl = QLabel("Ingrese sus credenciales")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-size:16px; margin-bottom:10px;")
        layout.addWidget(lbl)

        self.usuario = QLineEdit()
        self.usuario.setPlaceholderText("Usuario")
        layout.addWidget(self.usuario)

        self.clave = QLineEdit()
        self.clave.setPlaceholderText("Contraseña")
        self.clave.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.clave)

        btn_entrar = QPushButton("Entrar")
        btn_entrar.setStyleSheet("background-color:#4CAF50; color:white; font-size:16px; padding:10px; border-radius:10px;")
        btn_entrar.clicked.connect(self.intentar_login)
        layout.addWidget(btn_entrar)

        btn_volver = QPushButton("Volver")
        btn_volver.setStyleSheet("background-color:#E67E22; color:white; font-size:16px; padding:10px; border-radius:10px;")
        btn_volver.clicked.connect(self.volver_inicio)
        layout.addWidget(btn_volver)

        self.setLayout(layout)

    def intentar_login(self):
        # De momento no hay usuarios definidos
        QMessageBox.information(self, "Información", "El sistema de usuarios aún no está configurado.")

    def volver_inicio(self):
        # Importar aquí para evitar el ciclo circular
        from src.view.inicio import Inicio
        self.inicio = Inicio()
        self.inicio.show()
        self.close()
