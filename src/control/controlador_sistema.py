# src/control/controlador_sistema.py
from typing import Optional
# src/control/controlador_sistema.py

from src.model.sistema import Sistema
from src.model.actuador import Ventilador, Rociador, LuzExterior


class Controlador_Sistema:

    def __init__(self, sistema: Sistema, deadband: float = 0.3):
        self.sistema = sistema
        self.deadband = deadband
        # Umbrales para control (ajustar según sea necesario)
        self.UMBRAL_TEMP = 20.0  # <--- Temperatura mínima requerida en modo Auto
        self.UMBRAL_HUMO = 0.6
        self.UMBRAL_LUZ = 400.0

    def update(self):
        """Llamar periódicamente para leer sensores y aplicar control."""
        # 1. Leer temperatura
        temp = None
        try:
            temp = self.sistema.get_temperature()
        except RuntimeError as e:
            print(f"[Controlador] Error leyendo temperatura: {e}")
            return

        # 2. Controlar la temperatura (Manual o Auto)
        if self.sistema.mode == "manual" and self.sistema.manual_enabled:
            # Lógica de control manual (existente)
            if temp is not None:
                target = self.sistema.manual_target
                should_be_on = None

                # Lógica de Banda Muerta (Hysteresis)
                if temp < (target - self.deadband):
                    should_be_on = True  # Encender
                elif temp > (target + self.deadband):
                    should_be_on = False  # Apagar

                if should_be_on is not None:
                    self._set_actuators_by_type(Ventilador, should_be_on)

        elif self.sistema.mode == "auto":
            # Lógica de control automático (NUEVA)
            self._control_temperatura_auto(temp)

        # 3. Controlar Humo y Luz (se mantiene igual, ya que operan independientemente)
        self._control_humo()
        self._control_luz()

    def _control_temperatura_auto(self, current_temp: float):
        if current_temp is None:
            return

        target = self.UMBRAL_TEMP
        should_be_on = None

        if current_temp < (target - self.deadband):
            should_be_on = False

        elif current_temp > target:
            should_be_on = True


        if should_be_on is not None:
            self._set_actuators_by_type(Ventilador, should_be_on)


    def _set_actuators(self, on: bool):
        for a in self.sistema.actuators:
            try:
                # ... (Lógica de encendido/apagado usando a.on() / a.off() o set_state)
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

    def _control_luz(self):
        light_level = self.sistema.get_sensor_reading("light")
        if light_level is not None:
            if light_level < self.UMBRAL_LUZ:
                self._set_actuators_by_type(LuzExterior, True)
            elif light_level > (self.UMBRAL_LUZ + 50.0):
                self._set_actuators_by_type(LuzExterior, False)