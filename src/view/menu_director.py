from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QGroupBox, QGridLayout, QScrollArea
)
from PySide6.QtCore import QTimer, Qt
from typing import List, Dict

from src.model.sistema import Sistema
from src.model.usuario import Usuario
from src.model.basedatos import BaseDatos  # Importamos tu clase de conexión
from src.view.gestion_usuarios import GestionUsuariosDirector
from src.view.reporte_view import ReporteHistorialView


class MenuDirector(QWidget):
    def __init__(self, usuario: Usuario):
        super().__init__()

        self.usuario = usuario
        self.db = BaseDatos()

        # Diccionario para guardar las etiquetas de los sensores dinámicos
        # Key: id_sensor (de la BDD), Value: QLabel (donde se muestra el valor)
        self.sensor_widgets: Dict[int, QLabel] = {}

        self.setWindowTitle("Panel del Director - Nova Solutions")
        self.setGeometry(200, 150, 800, 600)
        self.setStyleSheet("background-color:#0e143b; color:white;")

        self.init_ui()

        # Timer para actualizar lecturas desde la BDD cada 2 segundos
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_datos_desde_db)
        self.timer.start(2000)

    def init_ui(self):
        layout = QVBoxLayout()

        # Título
        titulo = QLabel(f"Bienvenido Director General: {self.usuario.nombre} {self.usuario.apellido}")
        titulo.setAlignment(Qt.AlignHCenter)
        titulo.setStyleSheet("font-size:20px; margin-bottom: 10px; font-weight: bold;")
        layout.addWidget(titulo)

        body_layout = QHBoxLayout()
        body_layout.setSpacing(12)

        # --- PANEL IZQUIERDO: OPCIONES ---
        gestion_group = QGroupBox("Opciones de Dirección")
        gestion_group.setStyleSheet(self.get_groupbox_style())
        gestion_layout = QVBoxLayout()

        btn_usuarios = QPushButton("Gestionar Usuarios")
        btn_usuarios.clicked.connect(self.abrir_gestion_usuarios)
        btn_usuarios.setStyleSheet("background-color:#3489e2; color:white; padding: 8px;")

        btn_reportes = QPushButton("Ver Reportes Históricos")
        btn_reportes.clicked.connect(self.abrir_reportes)
        btn_reportes.setStyleSheet("background-color:#3489e2; color:white; padding: 8px;")

        gestion_layout.addWidget(btn_usuarios)
        gestion_layout.addWidget(btn_reportes)
        gestion_layout.addStretch()
        gestion_group.setLayout(gestion_layout)
        gestion_group.setFixedWidth(240)

        # --- PANEL DERECHO: SENSORES DINÁMICOS ---
        self.status_group = QGroupBox("Monitoreo de Sensores (BDD)")
        self.status_group.setStyleSheet(self.get_groupbox_style())

        # Usamos un ScrollArea por si hay muchos sensores creados en la BDD
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")

        self.container_sensores = QWidget()
        self.layout_sensores = QVBoxLayout(self.container_sensores)
        self.layout_sensores.setAlignment(Qt.AlignTop)

        scroll.setWidget(self.container_sensores)

        # Layout principal del grupo de estatus
        status_main_layout = QVBoxLayout()
        status_main_layout.addWidget(scroll)
        self.status_group.setLayout(status_main_layout)

        body_layout.addWidget(gestion_group, 0)
        body_layout.addWidget(self.status_group, 1)

        layout.addLayout(body_layout)

        # Botón Salir
        btn_salir = QPushButton("Cerrar sesión")
        btn_salir.clicked.connect(self.cerrar_sesion)
        btn_salir.setStyleSheet("background-color:#AA3333; color:white; padding:10px; border-radius:10px;")
        layout.addWidget(btn_salir)

        self.setLayout(layout)

        # Carga inicial de sensores
        self.cargar_sensores_desde_db()

    def cargar_sensores_desde_db(self):
        """Consulta la BDD y crea un widget por cada sensor existente."""
        # Limpiar widgets previos si existen
        for i in reversed(range(self.layout_sensores.count())):
            self.layout_sensores.itemAt(i).widget().setParent(None)
        self.sensor_widgets.clear()

        conn = self.db.conectar()
        if not conn: return

        try:
            cursor = conn.cursor(dictionary=True)
            # Solo traemos los sensores (nombre, tipo, ubicacion)
            cursor.execute("SELECT id, tipo_sensor, ubicacion, escuela FROM sensor")
            sensores = cursor.fetchall()

            for s in sensores:
                # Creamos una fila para el sensor
                fila = QWidget()
                fila_layout = QHBoxLayout(fila)

                nombre_lbl = QLabel(f"<b>{s['tipo_sensor']}</b> ({s['ubicacion']}):")
                valor_lbl = QLabel("Cargando...")
                valor_lbl.setStyleSheet("color: #00ff00; font-family: monospace; font-size: 14px;")

                fila_layout.addWidget(nombre_lbl)
                fila_layout.addStretch()
                fila_layout.addWidget(valor_lbl)

                self.layout_sensores.addWidget(fila)
                # Guardamos la referencia para actualizar el valor_lbl luego
                self.sensor_widgets[s['id']] = valor_lbl

        except Exception as e:
            print(f"Error al cargar sensores: {e}")
        finally:
            conn.close()

    def actualizar_datos_desde_db(self):
        """Busca la última medida en la tabla 'registros' para cada sensor cargado."""
        conn = self.db.conectar()
        if not conn: return

        try:
            cursor = conn.cursor(dictionary=True)
            for id_sensor, label_widget in self.sensor_widgets.items():
                # Buscamos el último registro de este sensor
                query = "SELECT medida FROM registros WHERE id_sensor = %s ORDER BY hora DESC LIMIT 1"
                cursor.execute(query, (id_sensor,))
                resultado = cursor.fetchone()

                if resultado:
                    medida = resultado['medida']
                    label_widget.setText(f"{medida:.2f}")
                else:
                    label_widget.setText("Sin datos")

        except Exception as e:
            print(f"Error actualizando lecturas: {e}")
        finally:
            conn.close()

    def get_groupbox_style(self):
        return """
        QGroupBox {
            border: 1px solid #555;
            margin-top: 18px;
            padding-top: 10px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 6px;
        }
        """

    def abrir_gestion_usuarios(self):
        self.gestion = GestionUsuariosDirector(usuario=self.usuario)
        self.gestion.show()

    def abrir_reportes(self):
        self.reporte_view = ReporteHistorialView()
        self.reporte_view.show()

    def cerrar_sesion(self):
        from src.view.inicio import Inicio
        self.timer.stop()
        self.inicio = Inicio()
        self.inicio.show()
        self.close()