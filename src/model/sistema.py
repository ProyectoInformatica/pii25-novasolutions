# src/model/sistema.py

from typing import List, Optional, Dict
from src.model.sensor import Sensor
from src.model.actuador import Actuador
from PySide6.QtCore import QObject, Signal


class Sistema(QObject):
    # Señales para notificar cambios de estado (útil para la interfaz)
    mode_changed = Signal(str)
    manual_target_changed = Signal(float)
    manual_enabled_changed = Signal(bool)

    def __init__(self, sensors: List[Sensor], actuators: List[Actuador] = None):
        super().__init__()
        self.sensors = sensors
        self.actuators = actuators if actuators is not None else []

        # Estado de control
        self._mode: str = "auto"
        self._manual_target: float = 22.0  # Temperatura de referencia manual
        self._manual_enabled: bool = False  # Control manual desactivado por defecto en modo AUTO

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, new_mode: str):
        if new_mode in ["auto", "manual"] and new_mode != self._mode:
            self._mode = new_mode
            self.mode_changed.emit(new_mode)
            # print(f"[Sistema] Modo de control cambiado a: {new_mode}")

    @property
    def manual_target(self) -> float:
        return self._manual_target

    @manual_target.setter
    def manual_target(self, new_target: float):
        new_target = max(5.0, min(40.0, new_target))  # Limitar rango
        if new_target != self._manual_target:
            self._manual_target = new_target
            self.manual_target_changed.emit(new_target)
            # print(f"[Sistema] Target manual cambiado a: {new_target}°C")

    @property
    def manual_enabled(self) -> bool:
        return self._manual_enabled

    @manual_enabled.setter
    def manual_enabled(self, enabled: bool):
        if enabled != self._manual_enabled:
            self._manual_enabled = enabled
            self.manual_enabled_changed.emit(enabled)
            # print(f"[Sistema] Control manual (Ventilador) establecido a: {enabled}")

    def get_sensor_reading(self, sensor_type: str) -> Optional[float]:
        """Busca el primer sensor de un tipo dado y devuelve su última lectura (forzando la lectura del JSON)."""

        for s in self.sensors:
            if s.type == sensor_type:
                # Llama a .read() para forzar la lectura del JSON (simulación)
                return s.read()

        raise RuntimeError(f"Sensor de tipo '{sensor_type}' no encontrado en el sistema.")

    def get_temperature(self) -> Optional[float]:
        """Método directo para el controlador."""
        # Note: Esta versión llama a get_sensor_reading, que a su vez llama a .read() del sensor.
        return self.get_sensor_reading("temperature")

    def get_actuator_state(self, actuator_class: type) -> Optional[bool]:
        """Devuelve el estado (ON/OFF) del primer actuador de la clase dada."""
        for a in self.actuators:
            if isinstance(a, actuator_class):
                return a.state
        return None