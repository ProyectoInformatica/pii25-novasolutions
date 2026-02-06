from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QListWidget
)
from PySide6.QtCore import Qt
from src.control.controlador_usuarios import ControladorUsuarios
from src.model.usuario import Usuario


BTN_PRIMARY = """
QPushButton{
    background-color:#3489e2;
    color:white;
    padding:10px;
    border-radius:10px;
    font-size:14px;
}
QPushButton:hover{ background-color:#2f7fd1; }
QPushButton:pressed{ background-color:#2a72ba; }
"""

BTN_DANGER = """
QPushButton{
    background-color:#AA3333;
    color:white;
    padding:10px;
    border-radius:10px;
    font-size:14px;
}
QPushButton:hover{ background-color:#972d2d; }
QPushButton:pressed{ background-color:#822727; }
"""

INPUT_STYLE = """
QLineEdit{
    padding:10px;
    border-radius:10px;
    background:#1b214d;
    border:1px solid rgba(255,255,255,0.15);
    color:white;
}
QLineEdit:focus{
    border:1px solid rgba(52,137,226,0.85);
}
"""

LIST_STYLE = """
QListWidget{
    background:#141b44;
    color:white;
    border:1px solid rgba(255,255,255,0.12);
    border-radius:10px;
    padding:6px;
}
QListWidget::item{
    padding:8px;
    border-radius:8px;
}
QListWidget::item:selected{
    background: rgba(52,137,226,0.45);
    border: 1px solid rgba(52,137,226,0.75);
}
QListWidget::item:hover{
    background: rgba(255,255,255,0.06);
}
"""

TITLE_STYLE = "font-size:18px; font-weight:700; margin:8px 0 12px 0;"


class GestionUsuariosDirector(QWidget):
    def __init__(self, usuario: Usuario = None):
        super().__init__()
        self.usuario_actual = usuario

        self.setWindowTitle("Gestión de Usuarios (Director)")
        self.setGeometry(250, 200, 560, 460)
        self.setStyleSheet("background-color:#0e143b; color:white;")

        self.ctrl_usuarios = ControladorUsuarios()

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(24, 18, 24, 18)

        titulo = QLabel("Registrar nuevo usuario de mantenimiento")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(TITLE_STYLE)
        layout.addWidget(titulo)

        self.nuevo_usuario = QLineEdit()
        self.nuevo_usuario.setPlaceholderText("Nombre de usuario")
        self.nuevo_usuario.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.nuevo_usuario)

        self.nueva_clave = QLineEdit()
        self.nueva_clave.setPlaceholderText("Contraseña")
        self.nueva_clave.setEchoMode(QLineEdit.EchoMode.Password)
        self.nueva_clave.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.nueva_clave)

        btn_registrar = QPushButton("Registrar usuario de mantenimiento")
        btn_registrar.setStyleSheet(BTN_PRIMARY)
        btn_registrar.clicked.connect(self.registrar_usuario_mantenimiento)
        layout.addWidget(btn_registrar)

        lbl_lista = QLabel("Usuarios registrados")
        lbl_lista.setAlignment(Qt.AlignCenter)
        lbl_lista.setStyleSheet("margin-top: 10px; font-weight:700;")
        layout.addWidget(lbl_lista)

        self.lista_usuarios = QListWidget()
        self.lista_usuarios.setStyleSheet(LIST_STYLE)
        layout.addWidget(self.lista_usuarios, 1)  # 1: que crezca y ocupe espacio
        self.actualizar_lista_usuarios()

        btn_eliminar = QPushButton("Eliminar usuario seleccionado")
        btn_eliminar.setStyleSheet(BTN_DANGER)
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
        item = self.lista_usuarios.currentItem()

        if not item:
            QMessageBox.warning(self, "Error", "Seleccione un usuario para eliminar.")
            return

        nombre_usuario = item.text().split(" (")[0]

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
