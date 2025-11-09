from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class MenuDirector(QWidget):
    def __init__(self, usuario):
        super().__init__()
        self.setWindowTitle("Panel del Director")
        self.setGeometry(200, 150, 800, 500)
        self.setStyleSheet("background-color:#1E1E1E; color:white;")

        layout = QVBoxLayout()
        lbl = QLabel(f"Bienvenido Director: {usuario.nombre_usuario}")
        layout.addWidget(lbl)

        btn_usuarios = QPushButton("Gestionar usuarios")
        layout.addWidget(btn_usuarios)

        btn_reportes = QPushButton("Ver reportes de sensores")
        layout.addWidget(btn_reportes)

        btn_salir = QPushButton("Cerrar sesión")
        btn_salir.clicked.connect(self.cerrar_sesion)
        layout.addWidget(btn_salir)

        self.setLayout(layout)

    def cerrar_sesion(self):
        from src.view.inicio import Inicio
        self.inicio = Inicio()
        self.inicio.show()
        self.close()
