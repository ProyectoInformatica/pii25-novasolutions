from typing import List, Optional
import logging
from src.model.sensor import Sensor
from src.model.basedatos import BaseDatos

logger = logging.getLogger("ControladorSensores")


class ControladorSensores:
    def __init__(self):
        self.db = BaseDatos()
        self.sensors: List[Sensor] = []
        self.cargar_desde_bd()

    def cargar_desde_bd(self):
        self.sensors.clear()
        for d in self.db.obtener_sensores():
            self.sensors.append(Sensor(
                id_bd=d['id'],
                tipo=d['tipo_sensor'],
                ubicacion=d['ubicacion'],
                escuela=d['escuela']
            ))
        logger.info(f"Cargados {len(self.sensors)} sensores desde la base de datos.")

    def crear_sensor(self, tipo: str, ubicacion: str, id_escuela: int, nombre_escuela: str) -> bool:
        nuevo_id = self.db.crear_sensor(tipo, ubicacion, id_escuela)
        if nuevo_id:
            self.sensors.append(Sensor(nuevo_id, tipo, ubicacion, nombre_escuela))
            logger.info(f"Sensor '{tipo}' en '{ubicacion}' creado con ID: {nuevo_id}")
            return True
        logger.error("No se pudo crear el sensor en la base de datos.")
        return False

    def eliminar_sensor(self, id_sensor: int) -> bool:
        """Baja lógica: no borra la fila, solo la marca como inactiva."""
        if self.db.dar_baja_sensor(id_sensor):
            self.sensors = [s for s in self.sensors if s.id != id_sensor]
            return True
        return False

    def actualizar_lecturas(self):
        for sensor in self.sensors:
            medida = self.db.obtener_ultima_medida(sensor.id)
            if medida is not None:
                sensor.actualizar_valor(medida)

    def get_ultima_medida(self, id_sensor: int) -> Optional[float]:
        return self.db.obtener_ultima_medida(id_sensor)

    def get_all_sensors(self) -> List[Sensor]:
        return self.sensors
