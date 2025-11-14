from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QListWidget
)
from PySide6.QtCore import Qt
from src.control.controlador_usuarios import ControladorUsuarios
from src.model import usuario


class GestionUsuariosDirector(QWidget):
    def __init__(self, usuario=None):
        super().__init__()
        self.usuario_actual = usuario
        self.setWindowTitle("Gestión de Usuarios (Director)")
        self.setGeometry(250, 200, 500, 400)
        self.setStyleSheet("background-color:#252526; color:white;")

        self.ctrl_usuarios = ControladorUsuarios()

        layout = QVBoxLayout()

        titulo = QLabel("Registrar nuevo usuario de mantenimiento")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        # Campos de entrada
        self.nuevo_usuario = QLineEdit()
        self.nuevo_usuario.setPlaceholderText("Nombre de usuario")
        layout.addWidget(self.nuevo_usuario)

        self.nueva_clave = QLineEdit()
        self.nueva_clave.setPlaceholderText("Contraseña")
        self.nueva_clave.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.nueva_clave)

        # Botón para registrar
        btn_registrar = QPushButton("Registrar usuario de mantenimiento")
        btn_registrar.clicked.connect(self.registrar_usuario_mantenimiento)
        layout.addWidget(btn_registrar)

        # Botón de volver al menú del director
        #btn_volver = QPushButton("Volver al menú del director")
        #btn_volver.clicked.connect(self.volver_menu_director)
        #layout.addWidget(btn_volver)

        # Lista de usuarios actuales
        lbl_lista = QLabel("Usuarios registrados:")
        lbl_lista.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_lista)

        self.lista_usuarios = QListWidget()
        layout.addWidget(self.lista_usuarios)
        self.actualizar_lista_usuarios()



        self.setLayout(layout)

    def registrar_usuario_mantenimiento(self):
        nombre = self.nuevo_usuario.text().strip()
        clave = self.nueva_clave.text().strip()

        if not nombre or not clave:
            QMessageBox.warning(self, "Error", "Debe ingresar un nombre y una contraseña.")
            return

        exito = self.ctrl_usuarios.registrar_usuario(nombre, clave, "mantenimiento")

        if exito:
            QMessageBox.information(self, "Éxito", f"Usuario '{nombre}' registrado correctamente.")
            self.nuevo_usuario.clear()
            self.nueva_clave.clear()
            self.actualizar_lista_usuarios()
        else:
            QMessageBox.warning(self, "Error", f"El usuario '{nombre}' ya existe.")

    def actualizar_lista_usuarios(self):
        self.lista_usuarios.clear()
        for usuario in self.ctrl_usuarios.usuarios:
            self.lista_usuarios.addItem(f"{usuario.nombre_usuario} ({usuario.rol})")

    def volver_menu_director(self):
        """Vuelve al panel del director."""
        from src.view.menu_director import MenuDirector
        self.menu = MenuDirector(self.usuario_actual)
        self.menu.show()
        self.close()