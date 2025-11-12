from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from src.view.login import Login
from src.view.ventana_principal import VentanaPrincipal

class Inicio(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Sensores Escolares")
        self.setGeometry(200, 150, 700, 400)
        self.setStyleSheet("background-color:#1E1E1E; color:white;")

        layout = QVBoxLayout()
        titulo = QLabel("Bienvenido al sistema escolar de sensores")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("font-size:20px; font-weight:bold; margin:20px; color:white;")
        layout.addWidget(titulo)

        btn_login = QPushButton("Iniciar sesión")
        btn_login.setStyleSheet("background-color:#4A90E2; color:white; font-size:18px; padding:20px; border-radius:15px;")
        btn_login.clicked.connect(self.ir_login)
        layout.addWidget(btn_login)

        btn_estudiante = QPushButton("Entrar como invitado")
        btn_estudiante.setStyleSheet("background-color:#F5A623; color:white; font-size:18px; padding:20px; border-radius:15px;")
        btn_estudiante.clicked.connect(self.ir_estudiante)
        layout.addWidget(btn_estudiante)

        self.setLayout(layout)

    def ir_login(self):
        self.login = Login()
        self.login.show()
        self.close()

    def ir_estudiante(self):
        self.main = VentanaPrincipal()
        self.main.show()
        self.close()
