from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
)
from src.model.basedatos import BaseDatos  # Usamos la base de datos directamente


class ReporteHistorialView(QWidget):
    def __init__(self):
        super().__init__()
        self.db = BaseDatos()
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

        # Estirar columnas
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.tabla)
        self.cargar_datos()

    def cargar_datos(self):
        # Consulta SQL para unir las tablas y mostrar nombres en lugar de IDs
        conexion = self.db.conectar()
        if not conexion: return

        try:
            cursor = conexion.cursor(dictionary=True)
            # Traemos los últimos 100 registros uniendo con la tabla sensor
            query = """
                SELECT r.hora, s.tipo_sensor, s.ubicacion, r.medida 
                FROM registros r
                JOIN sensor s ON r.id_sensor = s.id
                ORDER BY r.hora DESC
                LIMIT 100
            """
            cursor.execute(query)
            resultados = cursor.fetchall()

            self.tabla.setRowCount(len(resultados))

            for i, fila in enumerate(resultados):
                self.tabla.setItem(i, 0, QTableWidgetItem(str(fila['hora'])))
                self.tabla.setItem(i, 1, QTableWidgetItem(fila['tipo_sensor'].upper()))
                self.tabla.setItem(i, 2, QTableWidgetItem(fila['ubicacion']))
                self.tabla.setItem(i, 3, QTableWidgetItem(f"{fila['medida']:.2f}"))

        finally:
            conexion.close()