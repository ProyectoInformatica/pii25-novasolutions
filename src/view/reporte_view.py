from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PySide6.QtCore import Qt
from src.model.reporte import Reporteador


# ===== ESTILOS (armonía con el resto) =====
TITLE_STYLE = "font-size:20px; font-weight:700; margin:8px 0 12px 0;"
TABLE_STYLE = """
QTableWidget {
    background: #141b44;
    color: white;
    gridline-color: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 10px;
    padding: 6px;
    selection-background-color: rgba(52,137,226,0.45);
    selection-color: white;
}
QTableWidget::item {
    padding: 8px;
    border: none;
}
QTableWidget::item:selected {
    background: rgba(52,137,226,0.45);
}
QHeaderView::section {
    background-color: #1b214d;
    color: white;
    padding: 10px;
    border: none;
    font-weight: 700;
}
QTableCornerButton::section {
    background-color: #1b214d;
    border: none;
}
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 6px;
}
QScrollBar::handle:vertical {
    background: rgba(255,255,255,0.18);
    border-radius: 5px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background: transparent;
    height: 10px;
    margin: 6px;
}
QScrollBar::handle:horizontal {
    background: rgba(255,255,255,0.18);
    border-radius: 5px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
"""


class ReporteHistorialView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reportes Históricos de Sensores")
        self.setGeometry(300, 200, 900, 600)
        self.setStyleSheet("background-color:#0e143b; color:white;")

        self.reporteador = Reporteador()
        self.datos_historial = self.reporteador.get_historial_sensores()

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(24, 18, 24, 18)

        titulo = QLabel("Historial Completo de Lecturas de Sensores")
        titulo.setAlignment(Qt.AlignHCenter)
        titulo.setStyleSheet(TITLE_STYLE)
        layout.addWidget(titulo)

        if not self.datos_historial:
            vacio = QLabel("No se encontraron datos históricos para mostrar.")
            vacio.setAlignment(Qt.AlignCenter)
            vacio.setStyleSheet("color: rgba(255,255,255,0.75); padding: 18px;")
            layout.addWidget(vacio)
        else:
            self.tabla_reporte = QTableWidget()
            self.tabla_reporte.setStyleSheet(TABLE_STYLE)
            self.tabla_reporte.setAlternatingRowColors(True)
            self.tabla_reporte.setShowGrid(True)
            self.tabla_reporte.verticalHeader().setVisible(False)

            self.cargar_datos_en_tabla()
            layout.addWidget(self.tabla_reporte, 1)  # 1: que crezca y ocupe el espacio

        self.setLayout(layout)

    def cargar_datos_en_tabla(self):
        if not self.datos_historial:
            return

        columnas = list(self.datos_historial[0].keys())
        self.tabla_reporte.setColumnCount(len(columnas))
        self.tabla_reporte.setHorizontalHeaderLabels(columnas)
        self.tabla_reporte.setRowCount(len(self.datos_historial))

        for row_idx, data_row in enumerate(self.datos_historial):
            for col_idx, col_name in enumerate(columnas):
                valor = data_row.get(col_name, "N/A")

                if isinstance(valor, (float, int)):
                    item = QTableWidgetItem(f"{valor:.2f}")
                else:
                    item = QTableWidgetItem(str(valor))

                item.setTextAlignment(Qt.AlignCenter)
                self.tabla_reporte.setItem(row_idx, col_idx, item)

        # Ajustes de columnas
        header = self.tabla_reporte.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)

        # Mejor lectura
        self.tabla_reporte.setWordWrap(False)
        self.tabla_reporte.setSortingEnabled(True)
