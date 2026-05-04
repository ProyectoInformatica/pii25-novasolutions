from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QListWidget, QListWidgetItem, QScrollArea,
    QWidget, QGroupBox, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QTimer
from typing import Optional

from src.model.usuario import Usuario
from src.model.mensaje import Mensaje
from src.control.controlador_mensajes import ControladorMensajes
from src.view.estilos import BTN_PRIMARY, BTN_DANGER, PANEL_STYLE, INPUT_STYLE, LIST_STYLE


class MensajeriaView(QDialog):
    def __init__(self, usuario: Usuario):
        super().__init__()
        self.usuario = usuario
        self.ctrl = ControladorMensajes()
        self.contacto_actual: Optional[Usuario] = None
        self._contactos: list[Usuario] = []

        self.setWindowTitle("Mensajería Interna - Nova Solutions")
        self.setGeometry(150, 100, 920, 640)
        self.setStyleSheet("background-color:#0e143b; color:white;")
        self.setModal(True)

        self.init_ui()
        self.cargar_contactos()
        self._iniciar_polling()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        titulo = QLabel("Mensajería Interna")
        titulo.setAlignment(Qt.AlignHCenter)
        titulo.setStyleSheet("font-size:18px; font-weight:bold; margin-bottom:6px;")
        layout.addWidget(titulo)

        body = QHBoxLayout()
        body.setSpacing(12)

        # ── Panel izquierdo: contactos ──────────────────────────
        contactos_group = QGroupBox("Contactos")
        contactos_group.setStyleSheet(PANEL_STYLE)
        contactos_group.setFixedWidth(220)
        c_layout = QVBoxLayout(contactos_group)

        self.lista_contactos = QListWidget()
        self.lista_contactos.setStyleSheet(LIST_STYLE)
        self.lista_contactos.currentItemChanged.connect(self._on_contacto_seleccionado)
        c_layout.addWidget(self.lista_contactos)

        # ── Panel derecho: conversación ─────────────────────────
        conv_group = QGroupBox("Conversación")
        conv_group.setStyleSheet(PANEL_STYLE)
        d_layout = QVBoxLayout(conv_group)
        d_layout.setSpacing(8)

        self.lbl_contacto_activo = QLabel("Selecciona un contacto")
        self.lbl_contacto_activo.setStyleSheet(
            "font-size:14px; font-weight:bold; color:#3489e2; margin-bottom:4px;"
        )
        d_layout.addWidget(self.lbl_contacto_activo)

        # Área de scroll con mensajes
        self.scroll_mensajes = QScrollArea()
        self.scroll_mensajes.setWidgetResizable(True)
        self.scroll_mensajes.setStyleSheet("border:none; background:#141b44; border-radius:8px;")

        self.container_mensajes = QWidget()
        self.container_mensajes.setStyleSheet("background:#141b44;")
        self.layout_mensajes = QVBoxLayout(self.container_mensajes)
        self.layout_mensajes.setAlignment(Qt.AlignTop)
        self.layout_mensajes.setSpacing(6)
        self.layout_mensajes.setContentsMargins(10, 10, 10, 10)

        self.scroll_mensajes.setWidget(self.container_mensajes)
        d_layout.addWidget(self.scroll_mensajes, 1)

        # Separador
        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setStyleSheet("background:#555; margin:2px 0;")
        d_layout.addWidget(linea)

        # Input + botón enviar
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)

        self.input_mensaje = QLineEdit()
        self.input_mensaje.setPlaceholderText("Escribe un mensaje...")
        self.input_mensaje.setStyleSheet(INPUT_STYLE)
        self.input_mensaje.returnPressed.connect(self._enviar_mensaje)

        btn_enviar = QPushButton("Enviar")
        btn_enviar.setStyleSheet(BTN_PRIMARY)
        btn_enviar.setFixedWidth(100)
        btn_enviar.clicked.connect(self._enviar_mensaje)

        input_layout.addWidget(self.input_mensaje, 1)
        input_layout.addWidget(btn_enviar)
        d_layout.addLayout(input_layout)

        body.addWidget(contactos_group)
        body.addWidget(conv_group, 1)
        layout.addLayout(body, 1)

        # Botón cerrar
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet(BTN_DANGER)
        btn_cerrar.clicked.connect(self.reject)
        layout.addWidget(btn_cerrar)

    # ── Contactos ──────────────────────────────────────────────

    def cargar_contactos(self):
        contacto_id_previo = (
            self.contacto_actual.id_db if self.contacto_actual else None
        )

        self._contactos = self.ctrl.obtener_contactos(self.usuario.id_db)

        self.lista_contactos.blockSignals(True)
        self.lista_contactos.clear()

        for contacto in self._contactos:
            no_leidos = self.ctrl.contar_no_leidos_de(contacto.id_db, self.usuario.id_db)
            texto = f"{contacto.nombre} {contacto.apellido}"
            if no_leidos > 0:
                texto += f"  [{no_leidos}]"
            item = QListWidgetItem(texto)
            item.setData(Qt.UserRole, contacto.id_db)
            if no_leidos > 0:
                item.setForeground(Qt.yellow)
            self.lista_contactos.addItem(item)

            # Reseleccionar el contacto activo tras recargar
            if contacto.id_db == contacto_id_previo:
                self.lista_contactos.setCurrentItem(item)

        self.lista_contactos.blockSignals(False)

    # ── Conversación ───────────────────────────────────────────

    def _on_contacto_seleccionado(self, item: QListWidgetItem, _prev):
        if item is None:
            return
        id_contacto = item.data(Qt.UserRole)
        self.contacto_actual = next(
            (c for c in self._contactos if c.id_db == id_contacto), None
        )
        if self.contacto_actual is None:
            return

        self.ctrl.marcar_leidos(self.contacto_actual.id_db, self.usuario.id_db)
        self.lbl_contacto_activo.setText(
            f"Conversación con: {self.contacto_actual.nombre} {self.contacto_actual.apellido}"
        )
        self._cargar_conversacion()
        self.cargar_contactos()  # actualiza badges tras marcar como leídos

    def _cargar_conversacion(self):
        if self.contacto_actual is None:
            return

        mensajes = self.ctrl.obtener_conversacion(
            self.usuario.id_db, self.contacto_actual.id_db
        )

        # Limpiar burbujas anteriores
        while self.layout_mensajes.count():
            item = self.layout_mensajes.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not mensajes:
            placeholder = QLabel("Sin mensajes aún. ¡Escribe el primero!")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("color:#888; font-style:italic; margin-top:20px;")
            self.layout_mensajes.addWidget(placeholder)
        else:
            for msg in mensajes:
                es_propio = (msg.id_remitente == self.usuario.id_db)
                burbuja = self._crear_burbuja(msg, es_propio)
                self.layout_mensajes.addWidget(burbuja)

        # Scroll al final
        QTimer.singleShot(
            50,
            lambda: self.scroll_mensajes.verticalScrollBar().setValue(
                self.scroll_mensajes.verticalScrollBar().maximum()
            )
        )

    def _crear_burbuja(self, msg: Mensaje, es_propio: bool) -> QWidget:
        contenedor = QWidget()
        h = QHBoxLayout(contenedor)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        remitente = "Yo" if es_propio else msg.remitente_display
        texto_completo = f"<b>{remitente}</b><br>{msg.contenido}<br><small style='color:#aaa;'>{msg.hora_display}</small>"

        burbuja = QLabel(texto_completo)
        burbuja.setTextFormat(Qt.RichText)
        burbuja.setWordWrap(True)
        burbuja.setMaximumWidth(520)

        if es_propio:
            burbuja.setStyleSheet("""
                QLabel {
                    background: #3489e2;
                    color: white;
                    border-radius: 14px;
                    padding: 10px 14px;
                }
            """)
            h.addStretch()
            h.addWidget(burbuja)
        else:
            burbuja.setStyleSheet("""
                QLabel {
                    background: #1b214d;
                    color: white;
                    border: 1px solid rgba(255,255,255,0.12);
                    border-radius: 14px;
                    padding: 10px 14px;
                }
            """)
            h.addWidget(burbuja)
            h.addStretch()

        return contenedor

    # ── Envío ──────────────────────────────────────────────────

    def _enviar_mensaje(self):
        if self.contacto_actual is None:
            QMessageBox.warning(self, "Aviso", "Selecciona un contacto primero.")
            return

        texto = self.input_mensaje.text().strip()
        if not texto:
            return

        ok = self.ctrl.enviar_mensaje(self.usuario.id_db, self.contacto_actual.id_db, texto)
        if ok:
            self.input_mensaje.clear()
            self._cargar_conversacion()
        else:
            QMessageBox.critical(self, "Error", "No se pudo enviar el mensaje.")

    # ── Polling ────────────────────────────────────────────────

    def _iniciar_polling(self):
        self.timer_chat = QTimer(self)
        self.timer_chat.timeout.connect(self._poll_chat)
        self.timer_chat.start(5000)

    def _poll_chat(self):
        self.cargar_contactos()
        if self.contacto_actual is not None:
            self._cargar_conversacion()

    def closeEvent(self, event):
        self.timer_chat.stop()
        super().closeEvent(event)
