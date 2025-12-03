# src/model/sistema.py

from typing import Optional, List, Dict
from src.model.sensor import Sensor # La clase Sensor ahora es un QObject
from src.model.actuador import Actuador


class Sistema:

    def __init__(self, sensors: Optional[List[Sensor]] = None, actuators: Optional[List[Actuador]] = None):
        self.sensors = sensors or []
        self.actuators = actuators or []
        self.mode = "auto"  # "auto" or "manual"
        self.manual_enabled = False
        self.manual_target = 22.0  # °C por defecto

    def get_temperature(self) -> float:
        temp_readings = [s.read() for s in self.sensors if s.type == "temperature"]
        valid_readings = [r for r in temp_readings if r is not None]

        if not valid_readings:
            raise RuntimeError("Los sensores de temperatura no devolvieron lecturas válidas.")
        return sum(valid_readings) / len(valid_readings)

    def get_sensor_reading(self, sensor_type: str) -> Optional[float]:
        """Obtiene la lectura de un sensor específico o el promedio si hay varios."""
        readings = [s.read() for s in self.sensors if s.type == sensor_type]
        valid_readings = [r for r in readings if r is not None]

        if not valid_readings:
            return None
        # Devuelve el promedio si hay varios, o el único valor
        return sum(valid_readings) / len(valid_readings)

    def set_manual(self, target: float, enabled: bool):
        self.manual_target = float(target)
        self.manual_enabled = bool(enabled)
        self.mode = "manual" if enabled else self.mode

    def set_mode(self, mode: str):
        if mode not in ("auto", "manual"):
            raise ValueError("mode debe ser 'auto' o 'manual'")
        self.mode = mode
        if mode == "auto":
            self.manual_enabled = False