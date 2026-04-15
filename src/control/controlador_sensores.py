from typing import List, Optional
import logging
from src.model.sensor import Sensor
from src.model.basedatos import BaseDatos

logger = logging.getLogger("ControladorSensores")


class Controlador_Sensores:
    def __init__(self, db: BaseDatos):
        self.db = db
        self.sensors: List[Sensor] = []
        # Cargamos los sensores existentes al iniciar
        self.cargar_sensores_desde_bd()

    def cargar_sensores_desde_bd(self):
        """
        Consulta la tabla 'sensor' y crea los objetos en memoria.
        """
        self.sensors.clear()
        datos = self.db.obtener_sensores()  # Método que definimos en BaseDatos

        for d in datos:
            nuevo_sensor = Sensor(
                id_bd=d['id'],
                tipo=d['tipo_sensor'],
                ubicacion=d['ubicacion'],
                escuela=d['escuela']
            )
            self.sensors.append(nuevo_sensor)

        logger.info(f"Cargados {len(self.sensors)} sensores desde la base de datos.")

    def crear_nuevo_sensor(self, tipo: str, ubicacion: str, escuela: str) -> bool:
        """
        Crea un sensor en la BDD y, si tiene éxito, lo añade a la lista local.
        """
        nuevo_id = self.db.crear_sensor(tipo, ubicacion, escuela)

        if nuevo_id:
            nuevo_obj = Sensor(nuevo_id, tipo, ubicacion, escuela)
            self.sensors.append(nuevo_obj)
            logger.info(f"Sensor '{tipo}' en '{ubicacion}' creado con ID: {nuevo_id}")
            return True

        logger.error("No se pudo crear el sensor en la base de datos.")
        return False

    def actualizar_lecturas_en_tiempo_real(self):
        """
        Recorre los sensores actuales y busca su última medida en la tabla 'registros'.
        Este método debería ser llamado por un QTimer global.
        """
        for sensor in self.sensors:
            ultima_medida = self.db.obtener_ultima_medida(sensor.id)
            if ultima_medida is not None:
                sensor.actualizar_valor(ultima_medida)

    def get_all_sensors(self) -> List[Sensor]:
        return self.sensors