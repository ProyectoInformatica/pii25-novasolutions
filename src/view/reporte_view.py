from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt
# Importar la clase del modelo
from src.model.reporte import Reporteador


class ReporteHistorialView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📈 Reportes Históricos de Sensores")
        self.setGeometry(300, 200, 900, 600)
        self.setStyleSheet("background-color:#1E1E1E; color:white;")

        self.reporteador = Reporteador()
        self.datos_historial = self.reporteador.get_historial_sensores()

        layout = QVBoxLayout()

        titulo = QLabel("Historial Completo de Lecturas de Sensores")
        titulo.setAlignment(Qt.AlignHCenter)
        titulo.setStyleSheet("font-size:20px; margin-bottom: 15px;")
        layout.addWidget(titulo)

        if not self.datos_historial:
            layout.addWidget(QLabel("No se encontraron datos históricos para mostrar."))
        else:
            self.tabla_reporte = QTableWidget()
            self.cargar_datos_en_tabla()
            layout.addWidget(self.tabla_reporte)

        self.setLayout(layout)

    def cargar_datos_en_tabla(self):

        if not self.datos_historial:
            return

        # Asumiendo que las claves son consistentes
        columnas = list(self.datos_historial[0].keys())
        self.tabla_reporte.setColumnCount(len(columnas))
        self.tabla_reporte.setHorizontalHeaderLabels(columnas)

        self.tabla_reporte.setRowCount(len(self.datos_historial))

        for row_idx, data_row in enumerate(self.datos_historial):
            for col_idx, col_name in enumerate(columnas):
                valor = data_row.get(col_name, "N/A")

                # Formato para valores float
                if isinstance(valor, (float, int)):
                    item = QTableWidgetItem(f"{valor:.2f}")
                else:
                    item = QTableWidgetItem(str(valor))

                # Centrar texto
                item.setTextAlignment(Qt.AlignCenter)
                self.tabla_reporte.setItem(row_idx, col_idx, item)

        # Ajustar el ancho de las columnas al contenido y estirar la última
        self.tabla_reporte.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.tabla_reporte.horizontalHeader().setStretchLastSection(True)
        # Colores
        self.tabla_reporte.setStyleSheet("""
            QTableWidget {
                gridline-color: #555;
                background-color: #2D2D30;
                color: white;
            }
            QHeaderView::section {
                background-color: #3C3C3C;
                color: white;
                padding: 4px;
                border: 1px solid #555;
            }
        """)