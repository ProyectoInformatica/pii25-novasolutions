from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QScrollArea, QGridLayout, QFrame
)
from PySide6.QtCore import Qt, QTimer

from src.control.controlador_sensores import ControladorSensores
from src.view.estilos import BTN_PRIMARY, BTN_DANGER

CARD_STYLE = """
QFrame#SensorCard {
    background-color: #1c224d;
    border-radius: 15px;
    border: 1px solid rgba(255,255,255,0.1);
}
QFrame#SensorCard:hover {
    background-color: #242b5e;
    border: 1px solid #3489e2;
}
QLabel#ValueLabel {
    font-size: 26px;
    font-weight: bold;
    color: #00ffcc;
}
QLabel#TypeLabel {
    font-size: 11px;
    color: #aaa;
    font-weight: 600;
}
"""


class MenuInvitado(QWidget):
    def __init__(self):
        super().__init__()
        self.ctrl_sensores = ControladorSensores()
        self.cards = {}

        self.setWindowTitle("Monitor Público - Nova Solutions")
        self.setGeometry(200, 150, 850, 600)
        self.setStyleSheet("background-color:#0e143b; color:white;")

        self.init_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_lecturas)
        self.timer.start(2000)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("Estado General de la Escuela")
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")

        container = QWidget()
        self.grid_layout = QGridLayout(container)
        self.grid_layout.setSpacing(15)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        button_layout = QHBoxLayout()

        btn_historial = QPushButton("Ver Historial de Datos")
        btn_historial.setCursor(Qt.PointingHandCursor)
        btn_historial.setStyleSheet(BTN_PRIMARY)
        btn_historial.clicked.connect(self.abrir_reportes)

        btn_volver = QPushButton("Volver al Inicio")
        btn_volver.setCursor(Qt.PointingHandCursor)
        btn_volver.setStyleSheet(BTN_DANGER)
        btn_volver.clicked.connect(self.volver_inicio)

        button_layout.addWidget(btn_historial)
        button_layout.addWidget(btn_volver)
        main_layout.addLayout(button_layout)

        self.cargar_tarjetas()

    def cargar_tarjetas(self):
        row, col = 0, 0

        for s in self.ctrl_sensores.get_all_sensors():
            card = QFrame()
            card.setObjectName("SensorCard")
            card.setFixedSize(240, 140)
            card.setStyleSheet(CARD_STYLE)

            layout_c = QVBoxLayout(card)

            lbl_tipo = QLabel(f"● {s.sensor_type.upper()}")
            lbl_tipo.setObjectName("TypeLabel")

            lbl_ubica = QLabel(s.ubicacion)
            lbl_ubica.setStyleSheet("font-size: 14px; font-weight: 500;")

            lbl_valor = QLabel("--")
            lbl_valor.setObjectName("ValueLabel")
            lbl_valor.setAlignment(Qt.AlignCenter)

            layout_c.addWidget(lbl_tipo)
            layout_c.addWidget(lbl_ubica)
            layout_c.addStretch()
            layout_c.addWidget(lbl_valor)

            self.grid_layout.addWidget(card, row, col)
            self.cards[s.id] = lbl_valor

            col += 1
            if col > 2:
                col = 0
                row += 1

    def actualizar_lecturas(self):
        for id_s, label in self.cards.items():
            valor = self.ctrl_sensores.get_ultima_medida(id_s)
            label.setText(f"{valor:.1f}" if valor is not None else "N/A")

    def abrir_reportes(self):
        from src.view.reporte_view import ReporteHistorialView
        self.rep_win = ReporteHistorialView()
        self.rep_win.show()

    def volver_inicio(self):
        from src.view.inicio import Inicio
        self.timer.stop()
        self.inicio_win = Inicio()
        self.inicio_win.show()
        self.close()
