from datetime import datetime


class Mensaje:
    def __init__(
        self,
        id_mensaje: int,
        contenido: str,
        hora: datetime,
        estado: str,
        id_remitente: int,
        id_destinatario: int,
        nombre_remitente: str = "",
        apellido_remitente: str = "",
    ):
        self.id_mensaje = id_mensaje
        self.contenido = contenido
        self.hora = hora
        self.estado = estado
        self.id_remitente = id_remitente
        self.id_destinatario = id_destinatario
        self.nombre_remitente = nombre_remitente
        self.apellido_remitente = apellido_remitente

    @property
    def es_leido(self) -> bool:
        return self.estado == "1"

    @property
    def remitente_display(self) -> str:
        return f"{self.nombre_remitente} {self.apellido_remitente}".strip()

    @property
    def hora_display(self) -> str:
        if isinstance(self.hora, datetime):
            return self.hora.strftime("%d/%m %H:%M")
        return str(self.hora)
