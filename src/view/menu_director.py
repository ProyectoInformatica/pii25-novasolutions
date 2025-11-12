from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class MenuDirector(QWidget):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("Panel del Director")
        self.setGeometry(200, 150, 800, 500)
        self.setStyleSheet("background-color:#1E1E1E; color:white;")

        layout = QVBoxLayout()
        lbl = QLabel(f"Bienvenido Director: {usuario.nombre_usuario}")
        layout.addWidget(lbl)

        btn_usuarios = QPushButton("Gestionar usuarios")
        btn_usuarios.clicked.connect(self.abrir_gestion_usuarios)
        layout.addWidget(btn_usuarios)

        btn_reportes = QPushButton("Ver reportes de sensores")
        layout.addWidget(btn_reportes)

        btn_salir = QPushButton("Cerrar sesión")
        btn_salir.clicked.connect(self.cerrar_sesion)
        layout.addWidget(btn_salir)

        self.setLayout(layout)

    def abrir_gestion_usuarios(self):
        """Abre la ventana de gestión de usuarios sin cerrar el menú del director."""
        from src.view.gestion_usuarios import GestionUsuariosDirector
        self.gestion = GestionUsuariosDirector(parent=self)
        self.gestion.show()

    def cerrar_sesion(self):
        from src.view.inicio import Inicio
        self.inicio = Inicio()
        self.inicio.show()
        self.close()