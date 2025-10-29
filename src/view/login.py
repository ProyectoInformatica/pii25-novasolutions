from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pantalla de inicio de sesión (no funcional aún)")
        self.setGeometry(300, 200, 500, 300)
        self.setStyleSheet("background-color:#222; color:white;")

        layout = QVBoxLayout()
        label = QLabel("Aquí irá la ventana de login.\n(No funcional por ahora)")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)
