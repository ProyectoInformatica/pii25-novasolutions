from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt

from src.control.controlador_usuarios import ControladorUsuarios
from src.view.estilos import BTN_PRIMARY, INPUT_STYLE

TITLE_STYLE = "font-size:20px; font-weight:700; margin:8px 0 4px 0;"
SUBTITLE_STYLE = "font-size:13px; color:rgba(255,255,255,0.65); margin-bottom:10px;"


class CrearPrimerAdmin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuración inicial — CityMon")
        self.setGeometry(200, 150, 440, 480)
        self.setStyleSheet("background-color:#0e143b; color:white;")

        self.ctrl_usuarios = ControladorUsuarios()

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(36, 28, 36, 28)

        titulo = QLabel("Bienvenido a CityMon")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(TITLE_STYLE)
        layout.addWidget(titulo)

        subtitulo = QLabel(
            "No hay ningún administrador registrado.\n"
            "Crea el primer usuario administrador para continuar."
        )
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setWordWrap(True)
        subtitulo.setStyleSheet(SUBTITLE_STYLE)
        layout.addWidget(subtitulo)

        self.correo = QLineEdit()
        self.correo.setPlaceholderText("Correo electrónico (@escuela.com)")
        self.correo.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.correo)

        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Nombre")
        self.nombre.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.nombre)

        self.apellido = QLineEdit()
        self.apellido.setPlaceholderText("Apellido")
        self.apellido.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.apellido)

        self.clave = QLineEdit()
        self.clave.setPlaceholderText("Contraseña")
        self.clave.setEchoMode(QLineEdit.EchoMode.Password)
        self.clave.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.clave)

        self.clave2 = QLineEdit()
        self.clave2.setPlaceholderText("Confirmar contraseña")
        self.clave2.setEchoMode(QLineEdit.EchoMode.Password)
        self.clave2.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.clave2)

        btn_crear = QPushButton("Crear administrador")
        btn_crear.setStyleSheet(BTN_PRIMARY)
        btn_crear.clicked.connect(self.crear_admin)
        layout.addWidget(btn_crear)

        self.setLayout(layout)

    def crear_admin(self):
        correo = self.correo.text().strip().lower()
        nombre = self.nombre.text().strip()
        apellido = self.apellido.text().strip()
        clave = self.clave.text().strip()
        clave2 = self.clave2.text().strip()

        if not correo or not nombre or not apellido or not clave or not clave2:
            QMessageBox.warning(self, "Error", "Debe completar todos los campos.")
            return

        if not correo.endswith("@escuela.com"):
            QMessageBox.warning(self, "Correo inválido", "El correo debe terminar en @escuela.com")
            return

        if not correo.split("@")[0]:
            QMessageBox.warning(self, "Correo inválido", "El correo debe tener un nombre antes de @escuela.com")
            return

        if clave != clave2:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden.")
            return

        exito = self.ctrl_usuarios.registrar_usuario(
            email=correo, nombre=nombre, apellido=apellido,
            contrasena=clave, rol="director"
        )

        if exito:
            QMessageBox.information(
                self, "Administrador creado",
                f"Usuario administrador '{correo}' creado correctamente.\n"
                "Ahora puede iniciar sesión."
            )
            from src.view.login import Login
            self.login = Login()
            self.login.show()
            self.close()
        else:
            QMessageBox.warning(self, "Error", f"El correo '{correo}' ya está registrado o hubo un error.")
