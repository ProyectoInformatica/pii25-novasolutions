import threading
from typing import List
from src.model.basedatos import BaseDatos
from src.model.mensaje import Mensaje
from src.model.lista_mensajes import ListaMensajes
from src.model.usuario import Usuario


class ControladorMensajes:
    def __init__(self):
        self.db = BaseDatos()
        self._lock = threading.Lock()

    def obtener_contactos(self, id_usuario_actual: int) -> List[Usuario]:
        with self._lock:
            filas = self.db.obtener_usuarios_activos()
        contactos = []
        for row in filas:
            if row['id'] == id_usuario_actual:
                continue
            contactos.append(Usuario(
                email=row['mail'],
                contrasena='',
                rol=row['tipo'],
                nombre=row['nombre'],
                apellido=row['apellido'],
                id_db=row['id']
            ))
        return contactos

    def obtener_conversacion(self, id_yo: int, id_contacto: int) -> ListaMensajes:
        with self._lock:
            filas = self.db.obtener_conversacion(id_yo, id_contacto)
        lista = ListaMensajes()
        for row in filas:
            lista.agregar(Mensaje(
                id_mensaje=row['id_mensaje'],
                contenido=row['contenido'],
                hora=row['hora'],
                estado=row['estado'],
                id_remitente=row['id_remitente'],
                id_destinatario=row['id_destinatario'],
                nombre_remitente=row['nombre_remitente'],
                apellido_remitente=row['apellido_remitente'],
            ))
        return lista

    def enviar_mensaje(self, id_remitente: int, id_destinatario: int, texto: str) -> bool:
        if not texto.strip():
            return False
        with self._lock:
            return self.db.enviar_mensaje(id_remitente, id_destinatario, texto.strip())

    def contar_no_leidos(self, id_usuario: int) -> int:
        with self._lock:
            return self.db.contar_no_leidos(id_usuario)

    def contar_no_leidos_de(self, id_remitente: int, id_yo: int) -> int:
        with self._lock:
            return self.db.contar_no_leidos_de_contacto(id_remitente, id_yo)

    def marcar_leidos(self, id_remitente_contacto: int, id_yo: int) -> None:
        with self._lock:
            self.db.marcar_leidos(id_remitente_contacto, id_yo)
