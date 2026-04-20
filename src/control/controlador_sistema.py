import logging
from src.model.sistema import Sistema
from src.model.basedatos import BaseDatos
from src.model.actuador import Ventilador, Rociador, LuzExterior, LuzPasillo

logger = logging.getLogger("ControladorSistema")
logger.setLevel(logging.INFO)


class ControladorSistema:
    UMBRAL_TEMP_MAX = 35.0
    UMBRAL_HUMO = 0.6
    UMBRAL_LUZ = 400.0
    UMBRAL_DISTANCIA = 50.0

    def __init__(self, sistema: Sistema, db: BaseDatos = None, deadband: float = 0.3):
        self.sistema = sistema
        self.db = db or BaseDatos()
        self.deadband = deadband

    def update(self):
        if self.sistema.mode == "manual":
            if self.sistema.manual_enabled:
                self._control_temperatura_manual()
            else:
                self._set_actuators_by_type(Ventilador, False)
        elif self.sistema.mode == "auto":
            self._control_temperatura_auto()

        self._control_humo()
        self._control_luz_exterior()
        self._control_luz_pasillo()

    def _evaluar_ventilador(self, a: Ventilador, umbral: float):
        temp = self.sistema.get_sensor_reading_by_id(a.id_sensor) if a.id_sensor is not None else None
        if temp is None:
            return
        if temp > (umbral + self.deadband):
            should_be_on = True
        elif temp < (umbral - self.deadband):
            should_be_on = False
        else:
            return
        try:
            a.set_state(should_be_on)
            self.db.actualizar_estado_actuador(a.id, should_be_on)
        except Exception as e:
            logger.error(f"Error al actualizar ventilador {a.id}: {e}")

    def _control_temperatura_manual(self):
        target = self.sistema.manual_target
        for a in self.sistema.actuators:
            if isinstance(a, Ventilador):
                self._evaluar_ventilador(a, target)

    def _control_temperatura_auto(self):
        for a in self.sistema.actuators:
            if isinstance(a, Ventilador):
                self._evaluar_ventilador(a, self.UMBRAL_TEMP_MAX)

    def _control_humo(self):
        smoke_level = self.sistema.get_sensor_reading("smoke")
        if smoke_level is not None:
            if smoke_level > self.UMBRAL_HUMO:
                self._set_actuators_by_type(Rociador, True)
            elif smoke_level < (self.UMBRAL_HUMO - 0.1):
                self._set_actuators_by_type(Rociador, False)

    def _control_luz_exterior(self):
        light_level = self.sistema.get_sensor_reading("light")
        if light_level is not None:
            if light_level < self.UMBRAL_LUZ:
                self._set_actuators_by_type(LuzExterior, True)
            elif light_level > (self.UMBRAL_LUZ + 50.0):
                self._set_actuators_by_type(LuzExterior, False)

    def _control_luz_pasillo(self):
        distance = self.sistema.get_sensor_reading("distance")
        if distance is not None:
            if distance < self.UMBRAL_DISTANCIA:
                self._set_actuators_by_type(LuzPasillo, True)
            elif distance > (self.UMBRAL_DISTANCIA + 10.0):
                self._set_actuators_by_type(LuzPasillo, False)

    def _set_actuators_by_type(self, actuator_class: type, on: bool):
        for a in self.sistema.actuators:
            if isinstance(a, actuator_class):
                try:
                    a.set_state(on)
                    self.db.actualizar_estado_actuador(a.id, on)
                except Exception as e:
                    logger.error(f"Error al actualizar actuador {a.id}: {e}")