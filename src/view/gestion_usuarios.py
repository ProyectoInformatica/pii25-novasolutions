from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt

from src.control.controlador_usuarios import ControladorUsuarios
from src.view.estilos import BTN_PRIMARY, BTN_DANGER, INPUT_STYLE, LIST_STYLE

TITLE_STYLE = "font-size:18px; font-weight:700; margin:8px 0 12px 0;"


class GestionUsuariosDirector(QWidget):
    def __init__(self, usuario=None):
        super().__init__()
        self.usuario_actual = usuario
        self.ctrl_usuarios = ControladorUsuarios()

        self.setWindowTitle("Gestión de Usuarios (Director)")
        self.setGeometry(250, 200, 560, 500)
        self.setStyleSheet("background-color:#0e143b; color:white;")

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(24, 18, 24, 18)

        titulo = QLabel("Registrar nuevo usuario de mantenimiento")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(TITLE_STYLE)
        layout.addWidget(titulo)

        self.nuevo_correo = QLineEdit()
        self.nuevo_correo.setPlaceholderText("Correo electrónico")
        self.nuevo_correo.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.nuevo_correo)

        self.nuevo_nombre = QLineEdit()
        self.nuevo_nombre.setPlaceholderText("Nombre")
        self.nuevo_nombre.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.nuevo_nombre)

        self.nuevo_apellido = QLineEdit()
        self.nuevo_apellido.setPlaceholderText("Apellido")
        self.nuevo_apellido.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.nuevo_apellido)

        self.nueva_clave = QLineEdit()
        self.nueva_clave.setPlaceholderText("Contraseña")
        self.nueva_clave.setEchoMode(QLineEdit.EchoMode.Password)
        self.nueva_clave.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.nueva_clave)

        btn_registrar = QPushButton("Registrar usuario de mantenimiento")
        btn_registrar.setStyleSheet(BTN_PRIMARY)
        btn_registrar.clicked.connect(self.registrar_usuario)
        layout.addWidget(btn_registrar)

        lbl_lista = QLabel("Usuarios registrados")
        lbl_lista.setAlignment(Qt.AlignCenter)
        lbl_lista.setStyleSheet("margin-top: 10px; font-weight:700;")
        layout.addWidget(lbl_lista)

        self.lista_usuarios = QListWidget()
        self.lista_usuarios.setStyleSheet(LIST_STYLE)
        layout.addWidget(self.lista_usuarios, 1)
        self.actualizar_lista()

        btn_eliminar = QPushButton("Eliminar usuario seleccionado")
        btn_eliminar.setStyleSheet(BTN_DANGER)
        btn_eliminar.clicked.connect(self.eliminar_usuario)
        layout.addWidget(btn_eliminar)

        self.setLayout(layout)

    def registrar_usuario(self):
        correo = self.nuevo_correo.text().strip().lower()
        nombre = self.nuevo_nombre.text().strip()
        apellido = self.nuevo_apellido.text().strip()
        clave = self.nueva_clave.text().strip()

        if not correo or not nombre or not apellido or not clave:
            QMessageBox.warning(self, "Error", "Debe completar todos los campos.")
            return

        if not correo.endswith("@escuela.com"):
            QMessageBox.warning(self, "Correo inválido", "El correo debe terminar en @escuela.com")
            return

        if not correo.split("@")[0]:
            QMessageBox.warning(self, "Correo inválido", "El correo debe tener un nombre antes de @escuela.com")
            return

        exito = self.ctrl_usuarios.registrar_usuario(
            email=correo, nombre=nombre, apellido=apellido,
            contrasena=clave, rol="mantenimiento"
        )

        if exito:
            QMessageBox.information(self, "Éxito", f"Usuario '{correo}' registrado correctamente.")
            self.nuevo_correo.clear()
            self.nuevo_nombre.clear()
            self.nuevo_apellido.clear()
            self.nueva_clave.clear()
            self.actualizar_lista()
        else:
            QMessageBox.warning(self, "Error", f"El correo '{correo}' ya está registrado.")

    def actualizar_lista(self):
        self.lista_usuarios.clear()
        for usuario in self.ctrl_usuarios.usuarios:
            texto = f"{usuario.nombre} {usuario.apellido} <{usuario.email}> ({usuario.rol})"
            item = QListWidgetItem(texto)
            item.setData(Qt.UserRole, usuario.email)
            self.lista_usuarios.addItem(item)

    def eliminar_usuario(self):
        item = self.lista_usuarios.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Seleccione un usuario para eliminar.")
            return

        email = item.data(Qt.UserRole)
        usuario = self.ctrl_usuarios.obtener_usuario_por_email(email)

        if usuario and usuario.es_director():
            QMessageBox.warning(self, "Error", "No se puede eliminar al usuario director.")
            return

        confirm = QMessageBox.question(
            self, "Confirmar",
            f"¿Está seguro de eliminar al usuario '{email}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            if self.ctrl_usuarios.eliminar_usuario(email):
                QMessageBox.information(self, "Éxito", f"Usuario '{email}' eliminado.")
                self.actualizar_lista()
            else:
                QMessageBox.warning(self, "Error", "No fue posible eliminar el usuario.")
