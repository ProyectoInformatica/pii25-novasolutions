from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
)
from src.control.controlador_reportes import ControladorReportes


class ReporteHistorialView(QWidget):
    def __init__(self):
        super().__init__()
        self.ctrl_reportes = ControladorReportes()

        self.setWindowTitle("Historial de Datos")
        self.setGeometry(300, 200, 800, 500)
        self.setStyleSheet("background-color:#0e143b; color:white;")

        layout = QVBoxLayout(self)

        titulo = QLabel("Registro Histórico de Mediciones")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(titulo)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Fecha y Hora", "Sensor", "Ubicación", "Lectura"])
        self.tabla.setStyleSheet("background: #141b44; color: white;")

        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.tabla)
        self.cargar_datos()

    def cargar_datos(self):
        resultados = self.ctrl_reportes.obtener_historial(limit=100)
        self.tabla.setRowCount(len(resultados))

        for i, fila in enumerate(resultados):
            self.tabla.setItem(i, 0, QTableWidgetItem(str(fila['hora'])))
            self.tabla.setItem(i, 1, QTableWidgetItem(fila['tipo_sensor'].upper()))
            self.tabla.setItem(i, 2, QTableWidgetItem(fila['ubicacion']))
            self.tabla.setItem(i, 3, QTableWidgetItem(f"{fila['medida']:.2f}"))
