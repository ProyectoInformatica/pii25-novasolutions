from typing import List, Optional
from src.model.sensor import Sensor
from src.model.actuador import Actuador
from PySide6.QtCore import QObject, Signal


class Sistema(QObject):
    mode_changed = Signal(str)
    manual_target_changed = Signal(float)
    manual_enabled_changed = Signal(bool)

    def __init__(self, sensors: List[Sensor], actuators: List[Actuador] = None):
        super().__init__()
        self.sensors = sensors
        self.actuators = actuators if actuators is not None else []

        self._mode: str = "auto"
        self._manual_target: float = 22.0
        self._manual_enabled: bool = False

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, new_mode: str):
        if new_mode in ("auto", "manual") and new_mode != self._mode:
            self._mode = new_mode
            self.mode_changed.emit(new_mode)

    @property
    def manual_target(self) -> float:
        return self._manual_target

    @manual_target.setter
    def manual_target(self, new_target: float):
        new_target = max(5.0, min(40.0, new_target))
        if new_target != self._manual_target:
            self._manual_target = new_target
            self.manual_target_changed.emit(new_target)

    @property
    def manual_enabled(self) -> bool:
        return self._manual_enabled

    @manual_enabled.setter
    def manual_enabled(self, enabled: bool):
        if enabled != self._manual_enabled:
            self._manual_enabled = enabled
            self.manual_enabled_changed.emit(enabled)

    def get_sensor_reading(self, sensor_type: str) -> Optional[float]:
        for s in self.sensors:
            if s.type == sensor_type:
                return s.last_reading
        return None

    def get_temperature(self) -> Optional[float]:
        return self.get_sensor_reading("temperature")

    def get_actuator_state(self, actuator_class: type) -> Optional[bool]:
        for a in self.actuators:
            if isinstance(a, actuator_class):
                return a.state
        return None