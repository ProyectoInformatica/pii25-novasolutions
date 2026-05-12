from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QListWidget, QListWidgetItem, QComboBox
)
from PySide6.QtCore import Qt

from src.control.controlador_usuarios import ControladorUsuarios
from src.view.estilos import BTN_PRIMARY, BTN_DANGER, INPUT_STYLE, LIST_STYLE

TITLE_STYLE = "font-size:18px; font-weight:700; margin:8px 0 12px 0;"

COMBO_STYLE = """
QComboBox{
    padding:10px;
    border-radius:10px;
    background:#1b214d;
    border:1px solid rgba(255,255,255,0.15);
    color:white;
    font-size:13px;
}
QComboBox::drop-down{ border:none; }
QComboBox QAbstractItemView{
    background:#1b214d;
    color:white;
    selection-background-color: rgba(52,137,226,0.55);
    border-radius:8px;
}
"""


class GestionUsuariosDirector(QWidget):
    def __init__(self, usuario=None):
        super().__init__()
        self.usuario_actual = usuario
        self.ctrl_usuarios = ControladorUsuarios()

        self.setWindowTitle("Gestión de Usuarios")
        self.setGeometry(250, 200, 560, 540)
        self.setStyleSheet("background-color:#0e143b; color:white;")

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(24, 18, 24, 18)

        titulo = QLabel("Registrar nuevo usuario")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(TITLE_STYLE)
        layout.addWidget(titulo)

        self.nuevo_correo = QLineEdit()
        self.nuevo_correo.setPlaceholderText("Correo electrónico (@escuela.com)")
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

        self.combo_rol = QComboBox()
        self.combo_rol.addItem("Mantenimiento", userData="mantenimiento")
        self.combo_rol.addItem("Administrador (Director)", userData="director")
        self.combo_rol.setStyleSheet(COMBO_STYLE)
        layout.addWidget(self.combo_rol)

        btn_registrar = QPushButton("Registrar usuario")
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
        rol = self.combo_rol.currentData()

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
            contrasena=clave, rol=rol
        )

        if exito:
            rol_str = "administrador" if rol == "director" else "de mantenimiento"
            QMessageBox.information(self, "Éxito", f"Usuario {rol_str} '{correo}' registrado correctamente.")
            self.nuevo_correo.clear()
            self.nuevo_nombre.clear()
            self.nuevo_apellido.clear()
            self.nueva_clave.clear()
            self.combo_rol.setCurrentIndex(0)
            self.actualizar_lista()
        else:
            QMessageBox.warning(self, "Error", f"El correo '{correo}' ya está registrado.")

    def actualizar_lista(self):
        self.lista_usuarios.clear()
        for usuario in self.ctrl_usuarios.usuarios:
            rol_etiqueta = "Administrador" if usuario.es_director() else "Mantenimiento"
            texto = f"{usuario.nombre} {usuario.apellido} <{usuario.email}> [{rol_etiqueta}]"
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

        if not usuario:
            QMessageBox.warning(self, "Error", "Usuario no encontrado.")
            return

        if self.usuario_actual and usuario.id_db == self.usuario_actual.id_db:
            QMessageBox.warning(self, "Operación no permitida",
                                "No puede eliminar su propio usuario mientras está conectado.")
            return

        confirm = QMessageBox.question(
            self, "Confirmar",
            f"¿Está seguro de dar de baja al usuario '{email}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            if self.ctrl_usuarios.eliminar_usuario(usuario.id_db):
                QMessageBox.information(self, "Éxito", f"Usuario '{email}' dado de baja.")
                self.actualizar_lista()
            else:
                QMessageBox.warning(self, "Error", "No fue posible eliminar el usuario.")
