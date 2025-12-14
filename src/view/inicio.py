from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QResizeEvent
from pathlib import Path

# UBICACIONES DE ARCHIVOS
RESOURCES_DIR = Path("resources")
LOGO_MADRID_PATH = str(RESOURCES_DIR / "cdm.png")
LOGO_NOVASOLUTIONS_PATH = str(RESOURCES_DIR / "novasolutions.jpg")

# La bandera de Madrid tiene una proporción de 11:7
MADRID_ASPECT_RATIO = 11 / 7

# Factores de escala
CDM_SCALE_FACTOR = 0.10
NOVASOLUTIONS_SCALE_FACTOR = 0.22
MIN_LOGO_SIZE = 60  # Tamaño mínimo de seguridad


class LogoLabel(QLabel):

    def __init__(self, path: str, name: str, default_size: int, scale_by_width=False):
        super().__init__()
        self.path = path
        self.name = name
        self.scale_by_width = scale_by_width
        self.setAlignment(Qt.AlignCenter)
        self.setScaledContents(True)
        self._load_logo_initial(default_size)

    def _load_logo_initial(self, size: int):
        try:
            self.original_pixmap = QPixmap(self.path)
            if self.original_pixmap.isNull():
                print(f"⚠️ Error: No se pudo cargar la imagen: {self.path}.")
                self.setText(f"[{self.name}]")
                self.setStyleSheet("color: gray; font-size: 10px; border: 1px solid gray; padding: 5px; margin: 5px;")
            else:
                pixmap_scaled = self.original_pixmap.scaled(
                    size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.setPixmap(pixmap_scaled)
                self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        except Exception as e:
            print(f"Error cargando logo {self.name}: {e}")
            self.setText(f"[{self.name}]")

    def scale_logo(self, new_width: int, new_height: int = -1):
        if hasattr(self, 'original_pixmap') and not self.original_pixmap.isNull():

            if self.scale_by_width or new_height == -1:
                # Lógica para NovaSolutions (rectangular): escalar por ancho
                scaled_pixmap = self.original_pixmap.scaledToWidth(
                    new_width, Qt.SmoothTransformation
                )
                self.setFixedSize(scaled_pixmap.size())
            else:
                # Lógica
                scaled_pixmap = self.original_pixmap.scaled(
                    new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.setPixmap(scaled_pixmap)
                # Forzamos el tamaño del contenedor al tamaño REAL de la imagen escalada
                self.setFixedSize(scaled_pixmap.size())

            self.setPixmap(scaled_pixmap)
            self.update()


class Inicio(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Sensores Escolares")
        self.setGeometry(200, 150, 700, 450)
        self.setStyleSheet("background-color:#1E1E1E; color:white;")

        layout = QVBoxLayout()

        # CONTENEDOR DE LOGOS
        logo_container = QHBoxLayout()
        logo_container.setAlignment(Qt.AlignCenter)
        logo_container.setSpacing(20)

        # Logo de la Comunidad de Madrid
        self.lbl_madrid = LogoLabel(LOGO_MADRID_PATH, "Comunidad de Madrid", 80, scale_by_width=False)
        logo_container.addWidget(self.lbl_madrid)

        # Logo de NovaSolutions
        self.lbl_novasolutions = LogoLabel(LOGO_NOVASOLUTIONS_PATH, "NovaSolutions", 120, scale_by_width=True)
        logo_container.addWidget(self.lbl_novasolutions)

        layout.addLayout(logo_container)

        # TITULO PRINCIPAL
        titulo = QLabel("Bienvenido al sistema escolar de sensores")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("font-size:20px; font-weight:bold; margin:20px; color:white;")
        layout.addWidget(titulo)

        # BOTONES
        btn_login = QPushButton("Iniciar sesión")
        btn_login.setStyleSheet(
            "background-color:#4A90E2; color:white; font-size:18px; padding:20px; border-radius:15px;")
        btn_login.clicked.connect(self.ir_login)
        layout.addWidget(btn_login)

        btn_estudiante = QPushButton("Entrar como invitado")
        btn_estudiante.setStyleSheet(
            "background-color:#F5A623; color:white; font-size:18px; padding:20px; border-radius:15px;")
        btn_estudiante.clicked.connect(self.ir_estudiante)
        layout.addWidget(btn_estudiante)

        self.setLayout(layout)

    def resizeEvent(self, event: QResizeEvent):
        # Sobreescribe el evento para escalar los logos con el tamaño de la ventana.
        super().resizeEvent(event)

        new_width = self.width()

        # Bandera de Madrid
        base_width_madrid = int(new_width * CDM_SCALE_FACTOR)
        base_width_madrid = max(base_width_madrid, MIN_LOGO_SIZE)

        # Calcular la altura necesaria para mantener la proporcion
        height_madrid = int(base_width_madrid / MADRID_ASPECT_RATIO)

        # 2. Logo de NovaSolutions
        base_width_nova = int(new_width * NOVASOLUTIONS_SCALE_FACTOR)
        base_width_nova = max(base_width_nova, MIN_LOGO_SIZE + 30)

        # Redimensionar y actualizar los logos
        self.lbl_madrid.scale_logo(base_width_madrid, height_madrid)
        self.lbl_novasolutions.scale_logo(base_width_nova)

    def ir_login(self):
        from src.view.login import Login
        self.login = Login()
        self.login.show()
        self.close()

    def ir_estudiante(self):
        from src.view.menu_invitado import MenuInvitado
        self.main = MenuInvitado()
        self.main.show()
        self.close()