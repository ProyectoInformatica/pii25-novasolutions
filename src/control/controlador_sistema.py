# src/control/controlador_sistema.py

from typing import Optional

from src.model.sistema import Sistema
# Importar el nuevo actuador
from src.model.actuador import Ventilador, Rociador, LuzExterior, LuzPasillo


class Controlador_Sistema:

    def __init__(self, sistema: Sistema, deadband: float = 0.3):
        self.sistema = sistema
        self.deadband = deadband
        # Umbrales para control (ajustar según sea necesario)
        self.UMBRAL_TEMP_MAX = 25.0  # <--- Temperatura MÁXIMA deseada (Auto)
        self.UMBRAL_HUMO = 0.6
        self.UMBRAL_LUZ = 400.0
        self.UMBRAL_DISTANCIA = 50.0  # cm. Distancia para detectar presencia

    def update(self):
        # 1. Leer temperatura
        temp = None
        try:
            temp = self.sistema.get_temperature()
        except RuntimeError as e:
            print(f"[Controlador] Error leyendo temperatura: {e}")
            return

        # 2. Controlar la temperatura (Manual o Auto)
        if self.sistema.mode == "manual" and self.sistema.manual_enabled:
            # Lógica de control manual: Si la temperatura es > Target, encender Ventilador. Si es < Target, apagarlo.
            if temp is not None:
                target = self.sistema.manual_target
                should_be_on = None

                # Si la temperatura sube por encima del target, encender ventilador (para enfriar)
                if temp > (target + self.deadband):
                    should_be_on = True
                    # Si la temperatura baja por debajo del target, apagar ventilador
                elif temp < (target - self.deadband):
                    should_be_on = False

                if should_be_on is not None:
                    self._set_actuators_by_type(Ventilador, should_be_on)

        elif self.sistema.mode == "auto":
            self._control_temperatura_auto(temp)

        # 3. Controlar Humo, Luz Ambiente y Luz de Pasillo
        self._control_humo()
        self._control_luz_exterior()
        self._control_luz_pasillo()  # <-- NUEVO CONTROL

    def _control_temperatura_auto(self, current_temp: float):
        if current_temp is None:
            return

        target = self.UMBRAL_TEMP_MAX
        should_be_on = None

        # Si la temperatura es demasiado ALTA (supera el umbral), encender el ventilador
        if current_temp > target:
            should_be_on = True

        # Si la temperatura baja por debajo del umbral menos la banda muerta, apagar el ventilador
        elif current_temp < (target - self.deadband):
            should_be_on = False

        if should_be_on is not None:
            self._set_actuators_by_type(Ventilador, should_be_on)

    def _set_actuators(self, on: bool):
        for a in self.sistema.actuators:
            try:
                a.set_state(on)
            except Exception as e:
                print(f"[Controlador] Error al cambiar actuador {a}: {e}")

    def _set_actuators_by_type(self, actuator_class: type, on: bool):
        for a in self.sistema.actuators:
            if isinstance(a, actuator_class):
                try:
                    a.set_state(on)
                except Exception as e:
                    print(f"[Controlador] Error al cambiar actuador {a}: {e}")

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
            # Si la distancia es menor (hay presencia)
            if distance < self.UMBRAL_DISTANCIA:
                self._set_actuators_by_type(LuzPasillo, True)
            # Si la distancia es mayor (no hay presencia)
            elif distance > (self.UMBRAL_DISTANCIA + 10.0):  # Histéresis de 10cm
                self._set_actuators_by_type(LuzPasillo, False)