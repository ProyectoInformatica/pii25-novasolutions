# src/model/sistema.py
from typing import List, Optional
from src.model.sensor import Sensor

class Sistema:

    def __init__(self, sensors: Optional[List[Sensor]] = None, actuators: Optional[List[object]] = None):
        self.sensors = sensors or []
        self.actuators = actuators or []
        self.mode = "auto"           # "auto" or "manual"
        self.manual_enabled = False
        self.manual_target = 22.0    # °C por defecto

    def get_temperature(self) -> float:
        if not self.sensors:
            raise RuntimeError("No hay sensores configurados en el sistema.")
        readings = [s.read() for s in self.sensors]
        readings = [r for r in readings if r is not None]
        if not readings:
            raise RuntimeError("Los sensores no devolvieron lecturas válidas.")
        return sum(readings) / len(readings)

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
