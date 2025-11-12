from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class VentanaPrincipal(QWidget):
    def __init__(self, usuario=None):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("Panel Principal")
        self.setGeometry(200, 150, 800, 600)
        self.setStyleSheet("background-color:black; color:white;")

        layout = QVBoxLayout()
        if usuario:
            layout.addWidget(QLabel(f"Bienvenido {usuario.nombre_usuario} (rol: {usuario.rol})"))
        else:
            layout.addWidget(QLabel("Modo invitado"))

        btn_salir = QPushButton("Cerrar sesión")
        btn_salir.clicked.connect(self.cerrar_sesion)
        layout.addWidget(btn_salir)

        self.setLayout(layout)

    def cerrar_sesion(self):
        from src.view.inicio import Inicio
        self.inicio = Inicio()
        self.inicio.show()
        self.close()
