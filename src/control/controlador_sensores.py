# src/control/controlador_sensores.py
from typing import List, Dict
from src.model.sensor import Sensor

class Controlador_Sensores:
    def __init__(self, sensors: List[Sensor]):
        self.sensors = sensors

    def read_all(self) -> Dict[str, float]:
        readings = {}
        for s in self.sensors:
            try:
                readings[s.id] = s.read()
            except Exception as e:
                readings[s.id] = None
        return readings
