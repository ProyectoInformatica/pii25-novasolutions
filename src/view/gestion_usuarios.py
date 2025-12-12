from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QListWidget
)
from PySide6.QtCore import Qt
from src.control.controlador_usuarios import ControladorUsuarios
from src.model.usuario import Usuario


class GestionUsuariosDirector(QWidget):
    def __init__(self, usuario: Usuario = None):
        super().__init__()
        self.usuario_actual = usuario
        self.setWindowTitle("Gestión de Usuarios (Director)")
        self.setGeometry(250, 200, 500, 400)
        self.setStyleSheet("background-color:#252526; color:white;")

        self.ctrl_usuarios = ControladorUsuarios()

        layout = QVBoxLayout()

        titulo = QLabel("Registrar nuevo usuario de mantenimiento")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("font-size: 16px; margin-bottom: 10px;")
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
        btn_registrar.setStyleSheet("background-color:#3489e2; color:white;")
        btn_registrar.clicked.connect(self.registrar_usuario_mantenimiento)
        layout.addWidget(btn_registrar)

        # Lista de usuarios actuales
        lbl_lista = QLabel("Usuarios registrados:")
        lbl_lista.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_lista.setStyleSheet("margin-top: 15px;")
        layout.addWidget(lbl_lista)

        self.lista_usuarios = QListWidget()
        self.lista_usuarios.setStyleSheet("background-color:#1E1E1E; color:white;")
        layout.addWidget(self.lista_usuarios)
        self.actualizar_lista_usuarios()

        btn_eliminar = QPushButton("Eliminar usuario seleccionado")
        btn_eliminar.setStyleSheet("background-color:#AA3333; color:white;")
        btn_eliminar.clicked.connect(self.eliminar_usuario)
        layout.addWidget(btn_eliminar)

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

    def eliminar_usuario(self):
        """Elimina un usuario seleccionado de la lista."""
        item = self.lista_usuarios.currentItem()

        if not item:
            QMessageBox.warning(self, "Error", "Seleccione un usuario para eliminar.")
            return

        # Extraemos solo el nombre antes del rol
        nombre_usuario = item.text().split(" (")[0]

        # Evitar eliminar al director
        if nombre_usuario.lower() == "director":
            QMessageBox.warning(self, "Error", "No se puede eliminar al usuario director.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirmar",
            f"¿Está seguro de eliminar al usuario '{nombre_usuario}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            exito = self.ctrl_usuarios.eliminar_usuario(nombre_usuario)
            if exito:
                QMessageBox.information(self, "Éxito", f"Usuario '{nombre_usuario}' eliminado.")
                self.actualizar_lista_usuarios()
            else:
                QMessageBox.warning(self, "Error", "No fue posible eliminar el usuario.")