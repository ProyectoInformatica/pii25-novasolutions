from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt

class VentanaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ventana Principal - Invitado")
        self.setGeometry(200, 150, 800, 600)
        self.setStyleSheet("background-color:black;")
