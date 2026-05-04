from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QPixmap, QResizeEvent, QPainter, QPainterPath, QFont
)
from pathlib import Path

# UBICACIONES DE ARCHIVOS
RESOURCES_DIR = Path(__file__).parent.parent.parent / "resources"
LOGO_MADRID_PATH = str(RESOURCES_DIR / "cdm.png")
LOGO_NOVASOLUTIONS_PATH = str(RESOURCES_DIR / "novasolutions.jpg")

# La bandera de Madrid tiene una proporción de 11:7
MADRID_ASPECT_RATIO = 11 / 7

# Factores de escala
CDM_SCALE_FACTOR = 0.10
NOVASOLUTIONS_SCALE_FACTOR = 0.22
MIN_LOGO_SIZE = 60  # Tamaño mínimo de seguridad


class LogoLabel(QLabel):
    def __init__(self, path: str, name: str, default_size: int, scale_by_width=False, radius: int = 14):
        super().__init__()
        self.path = path
        self.name = name
        self.scale_by_width = scale_by_width
        self.radius = radius

        self.setAlignment(Qt.AlignCenter)
        self.setScaledContents(False)  # nosotros controlamos el escalado
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        # Borde suave tipo “card” (opcional pero queda bien)
        self.setStyleSheet("""
            QLabel{
                background: transparent;
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 14px;
            }
        """)

        self._load_logo_initial(default_size)

    def _rounded_pixmap(self, pixmap: QPixmap, radius: int) -> QPixmap:
        if pixmap.isNull():
            return pixmap

        rounded = QPixmap(pixmap.size())
        rounded.fill(Qt.transparent)

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing, True)

        path = QPainterPath()
        path.addRoundedRect(0, 0, pixmap.width(), pixmap.height(), radius, radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return rounded

    def _load_logo_initial(self, size: int):
        try:
            self.original_pixmap = QPixmap(self.path)
            if self.original_pixmap.isNull():
                print(f"⚠️ Error: No se pudo cargar la imagen: {self.path}.")
                self.setText(f"[{self.name}]")
                self.setStyleSheet(
                    "color: gray; font-size: 10px; border: 1px solid gray; padding: 5px; margin: 5px;"
                )
            else:
                pixmap_scaled = self.original_pixmap.scaled(
                    size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                pixmap_scaled = self._rounded_pixmap(pixmap_scaled, self.radius)
                self.setPixmap(pixmap_scaled)
                self.setFixedSize(pixmap_scaled.size())
        except Exception as e:
            print(f"Error cargando logo {self.name}: {e}")
            self.setText(f"[{self.name}]")

    def scale_logo(self, new_width: int, new_height: int = -1):
        if not hasattr(self, "original_pixmap") or self.original_pixmap.isNull():
            return

        if self.scale_by_width or new_height == -1:
            # NovaSolutions (rectangular): escalar por ancho
            scaled_pixmap = self.original_pixmap.scaledToWidth(new_width, Qt.SmoothTransformation)
        else:
            # Madrid: escalar por ancho y alto manteniendo proporción
            scaled_pixmap = self.original_pixmap.scaled(
                new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )

        scaled_pixmap = self._rounded_pixmap(scaled_pixmap, self.radius)
        self.setPixmap(scaled_pixmap)
        self.setFixedSize(scaled_pixmap.size())
        self.update()


class Inicio(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Sensores Escolares")
        self.setGeometry(200, 150, 700, 450)
        self.setStyleSheet("background-color:#0e143b; color:white;")

        # Fuente global (Windows): Calibri
        self.setFont(QFont("Calibri", 11))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        center = QVBoxLayout()
        center.setAlignment(Qt.AlignHCenter)
        center.setSpacing(14)
        center.setContentsMargins(0, 0, 0, 0)

        # Estiramientos para centrar verticalmente (ajusta si quieres)
        layout.addStretch(1)
        layout.addLayout(center)
        layout.addStretch(2)

        logo_container = QHBoxLayout()
        logo_container.setAlignment(Qt.AlignCenter)
        logo_container.setSpacing(24)

        self.lbl_madrid = LogoLabel(LOGO_MADRID_PATH, "Comunidad de Madrid", 80, scale_by_width=False, radius=14)
        logo_container.addWidget(self.lbl_madrid)

        self.lbl_novasolutions = LogoLabel(LOGO_NOVASOLUTIONS_PATH, "NovaSolutions", 120, scale_by_width=True, radius=14)
        logo_container.addWidget(self.lbl_novasolutions)

        center.addLayout(logo_container)

        titulo = QLabel("Bienvenido a CityMon")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size:22px; font-weight:700; margin:10px 0px; color:white;")
        center.addWidget(titulo)

        btn_login = QPushButton("Iniciar sesión")
        btn_login.setFixedWidth(460)
        btn_login.setStyleSheet("""
            QPushButton{
                background-color:#4A90E2;
                color:white;
                font-size:18px;
                padding:18px;
                border-radius:18px;
            }
            QPushButton:hover{ background-color:#3f86da; }
            QPushButton:pressed{ background-color:#3676c0; }
        """)
        btn_login.clicked.connect(self.ir_login)
        center.addWidget(btn_login, alignment=Qt.AlignHCenter)

        btn_estudiante = QPushButton("Entrar como invitado")
        btn_estudiante.setFixedWidth(460)
        btn_estudiante.setStyleSheet("""
            QPushButton{
                background-color:#4A90E2;
                color:white;
                font-size:18px;
                padding:18px;
                border-radius:18px;
            }
            QPushButton:hover{ background-color:#3f86da; }
            QPushButton:pressed{ background-color:#3676c0; }
        """)
        btn_estudiante.clicked.connect(self.ir_estudiante)
        center.addWidget(btn_estudiante, alignment=Qt.AlignHCenter)

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)

        new_width = self.width()

        # 1) Bandera de Madrid
        base_width_madrid = int(new_width * CDM_SCALE_FACTOR)
        base_width_madrid = max(base_width_madrid, MIN_LOGO_SIZE)

        # Mantener proporción
        height_madrid = int(base_width_madrid / MADRID_ASPECT_RATIO)

        # 2) Logo de NovaSolutions
        base_width_nova = int(new_width * NOVASOLUTIONS_SCALE_FACTOR)
        base_width_nova = max(base_width_nova, MIN_LOGO_SIZE + 30)

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
