from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from src.model.usuario import Usuario  # Importado


class VentanaPrincipal(QWidget):
    def __init__(self, usuario: Usuario = None):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("Panel Principal (Estándar)")
        self.setGeometry(200, 150, 400, 200)
        self.setStyleSheet("background-color:black; color:white;")

        layout = QVBoxLayout()
        if usuario:
            layout.addWidget(QLabel(f"Bienvenido {usuario.nombre_usuario} (rol: {usuario.rol})"))
        else:
            layout.addWidget(QLabel("Modo invitado"))

        layout.addWidget(QLabel("Esta es una vista genérica que se puede expandir si necesitas otros roles."))

        btn_salir = QPushButton("Cerrar sesión")
        btn_salir.clicked.connect(self.cerrar_sesion)
        layout.addWidget(btn_salir)

        self.setLayout(layout)

    def cerrar_sesion(self):
        from src.view.inicio import Inicio
        self.inicio = Inicio()
        self.inicio.show()
        self.close()