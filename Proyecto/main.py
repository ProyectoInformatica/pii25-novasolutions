# --- USUARIOS EXISTENTES ---
# Director → usuario: director | contraseña: principal123
# Mantenimiento → usuario: maintenance | contraseña: 1234
# Estudiantes → sin login (botón “Entrar como estudiante”)

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTabWidget, QSlider, QProgressBar, QMessageBox, QCheckBox, QSizePolicy
)

# --- Datos simulados de sensores ---
sensors = {
    "fuego": {"estado": "Operativo", "bateria": 85, "humo": 10, "ultima_revision": "2025-10-01", "activo": True},
    "termostato": {"temp_actual": 23, "temp_objetivo": 22, "humedad": 40, "hvac": "Enfriando", "activo": True},
    "luz": {"nivel": 75, "consumo": 15, "encendido": True},
    "humedad": {"humedad": 45, "temperatura": 22, "aire": "Bueno", "deshumidificador": False}
}

# --- Usuarios de mantenimiento ---
maintenance_users = {"maintenance": "1234"}


# --- Ventana inicial ---
class Inicio(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Sensores Escolares")
        self.setGeometry(200, 150, 700, 400)
        self.setStyleSheet("background-color:#1E1E1E; color:white;")

        layout = QVBoxLayout()
        titulo = QLabel("Bienvenido al sistema escolar de sensores")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("font-size:20px; font-weight:bold; margin:20px; color:white;")
        layout.addWidget(titulo)

        btn_login = QPushButton("Iniciar sesión")
        btn_login.setStyleSheet("background-color:#4A90E2; color:white; font-size:18px; padding:20px; border-radius:15px;")
        btn_login.clicked.connect(self.ir_login)
        layout.addWidget(btn_login)

        btn_estudiante = QPushButton("Entrar como invitado")
        btn_estudiante.setStyleSheet("background-color:#F5A623; color:white; font-size:18px; padding:20px; border-radius:15px;")
        btn_estudiante.clicked.connect(self.ir_estudiante)
        layout.addWidget(btn_estudiante)

        self.setLayout(layout)

    def ir_login(self):
        self.login = Login()
        self.login.show()
        self.close()

    def ir_estudiante(self):
        self.main = VentanaPrincipal("estudiante")
        self.main.show()
        self.close()


# --- Login ---
class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inicio de sesión")
        self.setGeometry(200, 150, 400, 300)
        self.setStyleSheet("background-color:#1E1E1E; color:white;")

        layout = QVBoxLayout()
        lbl = QLabel("Ingrese sus credenciales")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-size:16px; margin-bottom:10px;")
        layout.addWidget(lbl)

        self.usuario = QLineEdit()
        self.usuario.setPlaceholderText("Usuario")
        layout.addWidget(self.usuario)

        self.clave = QLineEdit()
        self.clave.setPlaceholderText("Contraseña")
        self.clave.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.clave)

        btn_entrar = QPushButton("Entrar")
        btn_entrar.setStyleSheet("background-color:#4CAF50; color:white; font-size:16px; padding:10px; border-radius:10px;")
        btn_entrar.clicked.connect(self.verificar)
        layout.addWidget(btn_entrar)

        btn_volver = QPushButton("Volver")
        btn_volver.setStyleSheet("background-color:#E67E22; color:white; font-size:16px; padding:10px; border-radius:10px;")
        btn_volver.clicked.connect(self.volver_inicio)
        layout.addWidget(btn_volver)

        self.setLayout(layout)

    def verificar(self):
        user = self.usuario.text().lower()
        pw = self.clave.text()

        if user == "director" and pw == "principal123":
            self.menu_director = MenuDirector()
            self.menu_director.show()
            self.close()
        elif user in maintenance_users and maintenance_users[user] == pw:
            self.main = VentanaPrincipal("mantenimiento")
            self.main.show()
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Credenciales incorrectas o usuario no autorizado.")

    def volver_inicio(self):
        self.inicio = Inicio()
        self.inicio.show()
        self.close()


# --- Menú del Director ---
class MenuDirector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Panel del Director")
        self.setGeometry(100, 100, 800, 500)
        self.setStyleSheet("background-color:#1E1E1E; color:white;")

        # Layout principal (vertical)
        wrapper = QVBoxLayout()
        wrapper.setContentsMargins(0, 0, 0, 0)
        wrapper.setSpacing(0)

        # Barra superior con botón "Cerrar sesión"
        top = QHBoxLayout()
        top.setContentsMargins(10, 10, 10, 0)
        top.addStretch()
        btn_logout = QPushButton("Cerrar sesión ✖")
        btn_logout.setStyleSheet("background:none; color:#bbb; font-size:14px; border:none;")
        btn_logout.clicked.connect(self.cerrar_sesion)
        top.addWidget(btn_logout)
        wrapper.addLayout(top)

        # --- Contenedor horizontal para los dos rectángulos ---
        main = QHBoxLayout()
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # Botón: Ver Sensores
        btn_sensores = QPushButton("Ver Sensores")
        btn_sensores.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn_sensores.setStyleSheet("""
            QPushButton {
                background-color:#4A90E2;
                color:white;
                font-size:26px;
                font-weight:bold;
                border:none;
            }
            QPushButton:hover { background-color:#5AA0F2; }
        """)
        btn_sensores.clicked.connect(self.ver_sensores)

        # Botón: Gestionar Usuarios
        btn_gestion = QPushButton("Gestionar Usuarios")
        btn_gestion.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn_gestion.setStyleSheet("""
            QPushButton {
                background-color:#7ED321;
                color:white;
                font-size:26px;
                font-weight:bold;
                border:none;
            }
            QPushButton:hover { background-color:#8EE531; }
        """)
        btn_gestion.clicked.connect(self.ver_gestion)

        # Añadir botones al layout horizontal
        main.addWidget(btn_sensores)
        main.addWidget(btn_gestion)

        # Añadir el layout horizontal al principal (ocupa todo el espacio)
        wrapper.addLayout(main)
        wrapper.setStretch(1, 1)  # hace que los botones crezcan para llenar la ventana

        self.setLayout(wrapper)

    def ver_sensores(self):
        self.main = VentanaPrincipal("director")
        self.main.show()
        self.close()

    def ver_gestion(self):
        self.gestion = GestionUsuarios()
        self.gestion.show()
        self.close()

    def cerrar_sesion(self):
        self.inicio = Inicio()
        self.inicio.show()
        self.close()


# --- Ventana principal (Sensores) ---
class VentanaPrincipal(QWidget):
    def __init__(self, rol):
        super().__init__()
        self.rol = rol
        self.setWindowTitle(f"Panel de Sensores - {rol.title()}")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color:#1E1E1E; color:white;")

        main_layout = QVBoxLayout()

        # Cerrar sesión arriba
        top_bar = QHBoxLayout()
        btn_logout = QPushButton("Cerrar sesión ✖")
        btn_logout.setStyleSheet("background:none; color:#bbb; font-size:14px; border:none;")
        btn_logout.clicked.connect(self.cerrar_sesion)
        top_bar.addStretch()
        top_bar.addWidget(btn_logout)
        main_layout.addLayout(top_bar)

        # Pestañas
        self.tabs = QTabWidget()
        self.tabs.addTab(self.crear_tab_fuego(), "🔥 Humo")
        self.tabs.addTab(self.crear_tab_termostato(), "🌡️ Termostato")
        self.tabs.addTab(self.crear_tab_luz(), "💡 Luz")
        self.tabs.addTab(self.crear_tab_humedad(), "💧 Humedad")
        main_layout.addWidget(self.tabs)

        # Botón volver (solo director)
        if self.rol == "director":
            btn_volver = QPushButton("Volver")
            btn_volver.setStyleSheet("background-color:#E67E22; color:white; font-size:16px; padding:10px; border-radius:10px;")
            btn_volver.clicked.connect(self.volver_menu_director)
            main_layout.addWidget(btn_volver)

        self.setLayout(main_layout)

    # --- Fuego ---
    def crear_tab_fuego(self):
        tab = QWidget()
        l = QVBoxLayout()
        s = sensors["fuego"]
        l.addWidget(QLabel(f"Estado: {s['estado']}"))
        l.addWidget(QLabel(f"Batería: {s['bateria']}%"))
        l.addWidget(QLabel(f"Humo: {s['humo']}%"))
        l.addWidget(QLabel(f"Última revisión: {s['ultima_revision']}"))
        if self.rol != "estudiante":
            chk = QCheckBox("Sensor activo")
            chk.setChecked(s["activo"])
            chk.stateChanged.connect(lambda: self.toggle(chk, "fuego", "activo"))
            l.addWidget(chk)
        tab.setLayout(l)
        return tab

    # --- Termostato ---
    def crear_tab_termostato(self):
        tab = QWidget()
        l = QVBoxLayout()
        s = sensors["termostato"]
        self.lbl_temp = QLabel(f"Actual: {s['temp_actual']}°C | Objetivo: {s['temp_objetivo']}°C")
        self.lbl_temp.setStyleSheet("font-size:16px;")
        self.lbl_hvac = QLabel(f"Estado del HVAC: {s['hvac']}")
        self.lbl_humedad = QLabel(f"Humedad: {s['humedad']}%")
        l.addWidget(self.lbl_temp)
        l.addWidget(self.lbl_hvac)
        l.addWidget(self.lbl_humedad)

        if self.rol != "estudiante":
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(16, 30)
            slider.setValue(s["temp_objetivo"])
            slider.valueChanged.connect(lambda: self.cambiar_temp(slider.value()))
            l.addWidget(QLabel("Ajustar temperatura objetivo:"))
            l.addWidget(slider)

        tab.setLayout(l)
        return tab

    def cambiar_temp(self, valor):
        sensors["termostato"]["temp_objetivo"] = valor
        actual = sensors["termostato"]["temp_actual"]
        hvac = "Enfriando" if actual > valor else "Calentando" if actual < valor else "En espera"
        sensors["termostato"]["hvac"] = hvac
        self.lbl_temp.setText(f"Actual: {actual}°C | Objetivo: {valor}°C")
        self.lbl_hvac.setText(f"Estado del HVAC: {hvac}")

    # --- Luz ---
    def crear_tab_luz(self):
        tab = QWidget()
        l = QVBoxLayout()
        s = sensors["luz"]
        l.addWidget(QLabel(f"Nivel de luz: {s['nivel']}%"))
        l.addWidget(QLabel(f"Consumo: {s['consumo']}W"))
        barra = QProgressBar()
        barra.setValue(s["nivel"])
        l.addWidget(barra)
        if self.rol != "estudiante":
            chk = QCheckBox("Luces encendidas")
            chk.setChecked(s["encendido"])
            chk.stateChanged.connect(lambda: self.toggle(chk, "luz", "encendido"))
            l.addWidget(chk)
        tab.setLayout(l)
        return tab

    # --- Humedad ---
    def crear_tab_humedad(self):
        tab = QWidget()
        l = QVBoxLayout()
        s = sensors["humedad"]
        l.addWidget(QLabel(f"Humedad: {s['humedad']}%"))
        l.addWidget(QLabel(f"Temperatura: {s['temperatura']}°C"))
        l.addWidget(QLabel(f"Calidad del aire: {s['aire']}"))
        if self.rol != "estudiante":
            chk = QCheckBox("Deshumidificador encendido")
            chk.setChecked(s["deshumidificador"])
            chk.stateChanged.connect(lambda: self.toggle(chk, "humedad", "deshumidificador"))
            l.addWidget(chk)
        tab.setLayout(l)
        return tab

    # --- Acciones comunes ---
    def toggle(self, chk, sensor, key):
        sensors[sensor][key] = chk.isChecked()

    def cerrar_sesion(self):
        self.inicio = Inicio()
        self.inicio.show()
        self.close()

    def volver_menu_director(self):
        self.menu = MenuDirector()
        self.menu.show()
        self.close()


# --- Gestión de usuarios ---
class GestionUsuarios(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Usuarios")
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet("background-color:#1E1E1E; color:white;")

        l = QVBoxLayout()
        top = QHBoxLayout()
        btn_logout = QPushButton("Cerrar sesión ✖")
        btn_logout.setStyleSheet("background:none; color:#bbb; font-size:14px; border:none;")
        btn_logout.clicked.connect(self.cerrar_sesion)
        top.addStretch()
        top.addWidget(btn_logout)
        l.addLayout(top)

        l.addWidget(QLabel("Usuarios autorizados de mantenimiento:"))
        self.lbl_users = QLabel(", ".join(maintenance_users.keys()))
        l.addWidget(self.lbl_users)

        self.txt_user = QLineEdit()
        self.txt_user.setPlaceholderText("Nombre de usuario")
        l.addWidget(self.txt_user)

        self.txt_pass = QLineEdit()
        self.txt_pass.setPlaceholderText("Contraseña")
        l.addWidget(self.txt_pass)

        btn_add = QPushButton("Añadir usuario")
        btn_add.setStyleSheet("background-color:#4A90E2; color:white;")
        btn_add.clicked.connect(self.add_user)

        btn_del = QPushButton("Eliminar usuario")
        btn_del.setStyleSheet("background-color:#E67E22; color:white;")
        btn_del.clicked.connect(self.del_user)

        btn_back = QPushButton("Volver")
        btn_back.setStyleSheet("background-color:#27AE60; color:white;")
        btn_back.clicked.connect(self.volver_menu)

        l.addWidget(btn_add)
        l.addWidget(btn_del)
        l.addWidget(btn_back)
        self.setLayout(l)

    def add_user(self):
        u, p = self.txt_user.text().strip().lower(), self.txt_pass.text().strip()
        if u and p:
            maintenance_users[u] = p
            self.lbl_users.setText(", ".join(maintenance_users.keys()))
            QMessageBox.information(self, "Usuario añadido", f"{u} ahora tiene acceso.")

    def del_user(self):
        u = self.txt_user.text().strip().lower()
        if u in maintenance_users:
            del maintenance_users[u]
            self.lbl_users.setText(", ".join(maintenance_users.keys()))
            QMessageBox.information(self, "Eliminado", f"{u} eliminado correctamente.")

    def volver_menu(self):
        self.menu = MenuDirector()
        self.menu.show()
        self.close()

    def cerrar_sesion(self):
        self.inicio = Inicio()
        self.inicio.show()
        self.close()


# --- Ejecutar programa ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    inicio = Inicio()
    inicio.show()
    sys.exit(app.exec())
