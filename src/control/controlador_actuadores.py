from typing import List
import logging
from src.model.basedatos import BaseDatos

logger = logging.getLogger("ControladorActuadores")


class ControladorActuadores:
    def __init__(self):
        self.db = BaseDatos()

    def get_all_con_sensor(self) -> List[dict]:
        return self.db.obtener_actuadores_con_sensor()

    def crear_actuador(self, nombre: str, tipo: str, id_sensor: int) -> bool:
        nuevo_id = self.db.crear_actuador(nombre, tipo, id_sensor)
        if nuevo_id:
            logger.info(f"Actuador '{nombre}' ({tipo}) creado con ID: {nuevo_id}")
            return True
        logger.error("No se pudo crear el actuador en la base de datos.")
        return False

    def actualizar_estado(self, id_actuador: int, estado: bool) -> bool:
        return self.db.actualizar_estado_actuador(id_actuador, estado)