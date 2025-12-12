from typing import List, Dict, Optional
from src.model.sensor import Sensor

class Controlador_Sensores:
    def __init__(self, sensors: List[Sensor]):
        self.sensors = sensors

    def read_all(self) -> Dict[str, Optional[float]]:
        readings = {}
        for s in self.sensors:
            # Llama a read() que internamente emite la señal
            try:
                # Guardamos el valor float retornado (None si falla)
                readings[s.id] = s.read()
            except Exception:
                readings[s.id] = None
        return readings