# src/view/menu_director.py (Sustituye a la implementación anterior del MenuDirector)

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QGroupBox, QGridLayout
)
from PySide6.QtCore import QTimer, Qt

# Importar las clases necesarias del modelo y control
# ASUME que estas rutas son correctas y accesibles desde este archivo
from src.model.sistema import Sistema
from src.model.sensor import Sensor
from src.model.actuador import Ventilador, Rociador, LuzExterior, LuzPasillo, Actuador
from src.control.controlador_sistema import Controlador_Sistema
from src.control.controlador_sensores import Controlador_Sensores

# from src.view.gestion_usuarios import GestionUsuariosDirector # Necesario para el botón de gestión
# from src.view.inicio import Inicio # Necesario para cerrar sesión

class MenuDirector(QWidget):
    def __init__(self, usuario, sensor_data_file="simulation_data.json"):
        super().__init__()

        self.usuario = usuario
        self.sensor_data_file = sensor_data_file

        self.setWindowTitle("Panel del Director")
        # Ajustamos el tamaño para el contenido de monitoreo + gestión
        self.setGeometry(200, 150, 800, 600)
        self.setStyleSheet("background-color:#1E1E1E; color:white;")

        # Sensores
        self.sensors = [
            Sensor(id="temp1", sensor_type="temperature", data_file=self.sensor_data_file),
            Sensor(id="smoke1", sensor_type="smoke", data_file=self.sensor_data_file),
            Sensor(id="light1", sensor_type="light", data_file=self.sensor_data_file),
            Sensor(id="dist1", sensor_type="distance", data_file=self.sensor_data_file)
        ]

        # Actuadores
        self.actuators = [
            Ventilador(id="fan1"),
            Rociador(id="rociador1"),
            LuzExterior(id="luzext1"),
            LuzPasillo(id="luzpasillo1")
        ]

        self.sistema = Sistema(sensors=self.sensors, actuators=self.actuators)
        self.ctrl_sensores = Controlador_Sensores(self.sensors)
        self.ctrl_sistema = Controlador_Sistema(self.sistema)

        # LAYOUT PRINCIPAL
        layout = QVBoxLayout()

        titulo = QLabel(f"Bienvenido Director General: {usuario.nombre_usuario}")
        titulo.setAlignment(Qt.AlignHCenter)
        titulo.setStyleSheet("font-size:20px; margin-bottom: 10px;")
        layout.addWidget(titulo)

        # BOTONES DE GESTIÓN
        gestion_group = QGroupBox("Opciones de Dirección")
        gestion_layout = QHBoxLayout()
        gestion_group.setStyleSheet("QGroupBox { border: 1px solid #555; margin-top: 10px; }")

        btn_usuarios = QPushButton("👥 Gestionar Usuarios")
        btn_usuarios.clicked.connect(self.abrir_gestion_usuarios)
        gestion_layout.addWidget(btn_usuarios)

        btn_reportes = QPushButton("📈 Ver Reportes Históricos")
        gestion_layout.addWidget(btn_reportes)

        gestion_group.setLayout(gestion_layout)
        layout.addWidget(gestion_group)


        # SECCIÓN DE MONITOREO
        status_group = QGroupBox("Estado del Sistema en Tiempo Real")
        status_layout = QGridLayout()
        status_group.setStyleSheet("QGroupBox { border: 1px solid #555; margin-top: 10px; }")

        # Lecturas de Sensores
        status_layout.addWidget(QLabel("### 📡 LECTURAS DE SENSORES"), 0, 0, 1, 2)

        self.lbl_temp = QLabel("Temperatura: -- °C")
        self.lbl_temp.setStyleSheet("font-weight: bold; padding: 5px;")
        status_layout.addWidget(QLabel("🌡️ Temp"), 1, 0)
        status_layout.addWidget(self.lbl_temp, 1, 1)

        self.lbl_humo = QLabel("Nivel de Humo: --")
        status_layout.addWidget(QLabel("💨 Humo"), 2, 0)
        status_layout.addWidget(self.lbl_humo, 2, 1)

        self.lbl_luz = QLabel("Nivel de Luz: -- Lux")
        status_layout.addWidget(QLabel("💡 Luz"), 3, 0)
        status_layout.addWidget(self.lbl_luz, 3, 1)

        self.lbl_distancia = QLabel("Distancia: -- cm")
        status_layout.addWidget(QLabel("📏 Distancia"), 4, 0)
        status_layout.addWidget(self.lbl_distancia, 4, 1)

        # Estado de Actuadores
        status_layout.addWidget(QLabel("### ⚙️ ESTADO DE ACTUADORES"), 5, 0, 1, 2)

        self.actuator_labels = {}
        for i, actuator in enumerate(self.actuators):
            lbl_name = QLabel(f"{actuator.name}:")
            lbl_state = QLabel("🔴 OFF")
            self.actuator_labels[actuator.id] = lbl_state

            row = i + 6
            status_layout.addWidget(lbl_name, row, 0)
            status_layout.addWidget(lbl_state, row, 1)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # BOTÓN SALIR
        btn_salir = QPushButton("Cerrar sesión")
        btn_salir.clicked.connect(self.cerrar_sesion)
        layout.addWidget(btn_salir)

        self.setLayout(layout)


        # TIMER DE ACTUALIZACIÓN
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # 1 segundo
        self.timer.timeout.connect(self.actualizar)
        self.timer.start()


    # METODOS
    def actualizar(self):

        # El Director solo monitorea; el sistema sigue en modo automatico
        self.ctrl_sistema.update()

        def safe_read(sensor_type):
            try:
                return self.sistema.get_sensor_reading(sensor_type)
            except RuntimeError:
                return None

        temp = safe_read("temperature")
        smoke = safe_read("smoke")
        light = safe_read("light")
        distance = safe_read("distance")

        # 1. Actualizacion de etiquetas de sensores
        self.lbl_temp.setText(f"Temperatura: {temp:.2f} °C" if temp is not None else "Temperatura: ⚠️ ERROR (JSON)")
        self.lbl_humo.setText(f"Nivel de Humo: {smoke:.2f}" if smoke is not None else "Nivel de Humo: ⚠️ ERROR (JSON)")
        self.lbl_luz.setText(f"Nivel de Luz: {light:.2f} Lux" if light is not None else "Nivel de Luz: ⚠️ ERROR (JSON)")
        self.lbl_distancia.setText(
            f"Distancia: {distance:.2f} cm" if distance is not None else "Distancia: ⚠️ ERROR (JSON)")

        # 2. Actualizar el estado de los actuadores en la UI
        for actuator in self.actuators:
            label = self.actuator_labels.get(actuator.id)
            if label:
                state_text = "🟢 ON" if actuator.state else "🔴 OFF"
                label.setText(state_text)

    def abrir_gestion_usuarios(self):
        # Se necesita importar la clase 'GestionUsuariosDirector'
        from src.view.gestion_usuarios import GestionUsuariosDirector
        self.gestion = GestionUsuariosDirector(usuario=self.usuario)
        self.gestion.show()

    def cerrar_sesion(self):
        # Se necesita importar la clase 'Inicio'
        from src.view.inicio import Inicio
        self.inicio = Inicio()
        self.inicio.show()
        self.close()