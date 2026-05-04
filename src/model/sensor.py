from PySide6.QtCore import QObject, Signal
import logging
import math
from typing import Optional

logger = logging.getLogger("SensorModel")


class Sensor(QObject):
    # Señales para comunicar cambios a la Interfaz (View)
    lectura_actualizada = Signal(float)
    air_quality_text_actualizada = Signal(str, int)
    error_lectura = Signal(str)

    def __init__(self, id_bd: int, tipo: str, ubicacion: str, escuela: str):
        super().__init__()
        # Atributos según tu tabla 'sensor'
        self.id = id_bd
        self.sensor_type = tipo
        self.ubicacion = ubicacion
        self.escuela = escuela
        self.last_reading: Optional[float] = None

    def actualizar_valor(self, nuevo_valor: Optional[float]):
        if nuevo_valor is None:
            logger.debug("Sensor %s: valor None recibido, ignorando.", self.id)
            return

        # Solo emitimos si el valor realmente cambió para ahorrar recursos.
        # Usamos math.isclose para evitar falsos positivos por precisión flotante.
        if self.last_reading is None or not math.isclose(nuevo_valor, self.last_reading, rel_tol=1e-6):
            logger.debug("Sensor %s: valor actualizado %.4f -> %.4f", self.id, self.last_reading, nuevo_valor)
            self.last_reading = nuevo_valor

            if self.sensor_type == "airQuality":
                texto = self.map_air_quality_to_text(nuevo_valor)
                self.air_quality_text_actualizada.emit(texto, self.id)
            else:
                self.lectura_actualizada.emit(nuevo_valor)

    @staticmethod
    def map_air_quality_to_text(value: float) -> str:
        """Clasificación estándar de calidad de aire."""
        if value <= 10.0:
            return "Muy Buena"
        elif value <= 25.0:
            return "Buena"
        elif value <= 50.0:
            return "Aceptable"
        elif value <= 100.0:
            return "Mala"
        else:
            return "Muy Mala (Peligrosa)"