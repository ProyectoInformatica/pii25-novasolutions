import threading
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QListWidget, QListWidgetItem, QScrollArea,
    QWidget, QGroupBox, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from typing import Optional

from src.model.usuario import Usuario
from src.model.lista_mensajes import ListaMensajes
from src.model.mensaje import Mensaje
from src.control.controlador_mensajes import ControladorMensajes
from src.view.estilos import BTN_PRIMARY, BTN_DANGER, PANEL_STYLE, INPUT_STYLE, LIST_STYLE

_INTERVALO_POLL_MS = 5000
_TICK_MS           = 100  # granularidad del sleep para detectar interrupción


class HiloPolling(QThread):
    """Hilo de fondo que refresca contactos y conversación cada 5 segundos."""

    sig_contactos = Signal(list)        # list[(Usuario, int)]
    sig_mensajes  = Signal(int, object) # (id_contacto, ListaMensajes)

    def __init__(self, ctrl: ControladorMensajes, id_yo: int, parent=None) -> None:
        super().__init__(parent)
        self._ctrl = ctrl
        self._id_yo = id_yo
        self._lock = threading.Lock()
        self._id_contacto: Optional[int] = None

    def set_contacto(self, id_contacto: Optional[int]) -> None:
        with self._lock:
            self._id_contacto = id_contacto

    def run(self) -> None:
        while not self.isInterruptionRequested():
            try:
                contactos = self._ctrl.obtener_contactos(self._id_yo)
                badges = [
                    (c, self._ctrl.contar_no_leidos_de(c.id_db, self._id_yo))
                    for c in contactos
                ]
                self.sig_contactos.emit(badges)

                with self._lock:
                    id_c = self._id_contacto
                if id_c is not None:
                    lista = self._ctrl.obtener_conversacion(self._id_yo, id_c)
                    self.sig_mensajes.emit(id_c, lista)
            except Exception:
                pass

            # Sleep en ticks cortos para poder interrumpir rápido al cerrar
            ticks = _INTERVALO_POLL_MS // _TICK_MS
            for _ in range(ticks):
                if self.isInterruptionRequested():
                    return
                self.msleep(_TICK_MS)


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
        self._cargar_contactos_inmediato()
        self._iniciar_hilo_polling()

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

        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setStyleSheet("background:#555; margin:2px 0;")
        d_layout.addWidget(linea)

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

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet(BTN_DANGER)
        btn_cerrar.clicked.connect(self.reject)
        layout.addWidget(btn_cerrar)

    # ── Hilo de polling ────────────────────────────────────────

    def _iniciar_hilo_polling(self):
        self._hilo = HiloPolling(self.ctrl, self.usuario.id_db, self)
        self._hilo.sig_contactos.connect(self._slot_contactos)
        self._hilo.sig_mensajes.connect(self._slot_mensajes)
        self._hilo.start()

    # ── Carga inmediata (hilo principal, acciones del usuario) ─

    def _cargar_contactos_inmediato(self):
        contactos = self.ctrl.obtener_contactos(self.usuario.id_db)
        self._contactos = contactos
        badges = [
            (c, self.ctrl.contar_no_leidos_de(c.id_db, self.usuario.id_db))
            for c in contactos
        ]
        self._slot_contactos(badges)

    def _cargar_conversacion_inmediato(self):
        if self.contacto_actual is None:
            return
        lista = self.ctrl.obtener_conversacion(
            self.usuario.id_db, self.contacto_actual.id_db
        )
        self._slot_mensajes(self.contacto_actual.id_db, lista)

    # ── Slots Qt (siempre ejecutan en hilo principal) ──────────

    def _slot_contactos(self, badges: list):
        """Recibe list[(Usuario, int)] y actualiza la lista de contactos."""
        contacto_id_previo = self.contacto_actual.id_db if self.contacto_actual else None

        self._contactos = [c for c, _ in badges]
        if contacto_id_previo is not None:
            self.contacto_actual = next(
                (c for c in self._contactos if c.id_db == contacto_id_previo), None
            )

        self.lista_contactos.blockSignals(True)
        self.lista_contactos.clear()
        for contacto, no_leidos in badges:
            texto = f"{contacto.nombre} {contacto.apellido}"
            if no_leidos > 0:
                texto += f"  [{no_leidos}]"
            item = QListWidgetItem(texto)
            item.setData(Qt.UserRole, contacto.id_db)
            if no_leidos > 0:
                item.setForeground(Qt.yellow)
            self.lista_contactos.addItem(item)
            if contacto.id_db == contacto_id_previo:
                self.lista_contactos.setCurrentItem(item)
        self.lista_contactos.blockSignals(False)

    def _slot_mensajes(self, id_contacto: int, lista: ListaMensajes):
        """Recibe (id_contacto, ListaMensajes) y renderiza burbujas si corresponde."""
        if self.contacto_actual is None or self.contacto_actual.id_db != id_contacto:
            return
        self._renderizar_mensajes(lista)

    # ── Renderizado ────────────────────────────────────────────

    def _renderizar_mensajes(self, lista: ListaMensajes):
        while self.layout_mensajes.count():
            item = self.layout_mensajes.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not lista:
            placeholder = QLabel("Sin mensajes aún. ¡Escribe el primero!")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("color:#888; font-style:italic; margin-top:20px;")
            self.layout_mensajes.addWidget(placeholder)
        else:
            for msg in lista:
                es_propio = (msg.id_remitente == self.usuario.id_db)
                self.layout_mensajes.addWidget(self._crear_burbuja(msg, es_propio))

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
        texto_completo = (
            f"<b>{remitente}</b><br>"
            f"{msg.contenido}<br>"
            f"<small style='color:#aaa;'>{msg.hora_display}</small>"
        )

        burbuja = QLabel(texto_completo)
        burbuja.setTextFormat(Qt.RichText)
        burbuja.setWordWrap(True)
        burbuja.setMaximumWidth(520)

        if es_propio:
            burbuja.setStyleSheet(
                "QLabel { background:#3489e2; color:white; border-radius:14px; padding:10px 14px; }"
            )
            h.addStretch()
            h.addWidget(burbuja)
        else:
            burbuja.setStyleSheet(
                "QLabel { background:#1b214d; color:white; border:1px solid rgba(255,255,255,0.12);"
                " border-radius:14px; padding:10px 14px; }"
            )
            h.addWidget(burbuja)
            h.addStretch()

        return contenedor

    # ── Eventos de usuario ─────────────────────────────────────

    def _on_contacto_seleccionado(self, item: QListWidgetItem, _prev):
        if item is None:
            return
        id_contacto = item.data(Qt.UserRole)
        self.contacto_actual = next(
            (c for c in self._contactos if c.id_db == id_contacto), None
        )
        if self.contacto_actual is None:
            return

        self._hilo.set_contacto(self.contacto_actual.id_db)
        self.ctrl.marcar_leidos(self.contacto_actual.id_db, self.usuario.id_db)
        self.lbl_contacto_activo.setText(
            f"Conversación con: {self.contacto_actual.nombre} {self.contacto_actual.apellido}"
        )
        self._cargar_conversacion_inmediato()
        self._cargar_contactos_inmediato()

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
            self._cargar_conversacion_inmediato()
        else:
            QMessageBox.critical(self, "Error", "No se pudo enviar el mensaje.")

    def _detener_hilo(self):
        if hasattr(self, '_hilo') and self._hilo.isRunning():
            self._hilo.requestInterruption()
            self._hilo.wait(2000)

    def reject(self):
        self._detener_hilo()
        super().reject()

    def closeEvent(self, event):
        self._detener_hilo()
        super().closeEvent(event)
