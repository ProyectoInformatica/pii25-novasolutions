# src/control/controlador_sistema.py
from typing import Optional
from src.model.sistema import Sistema

class Controlador_Sistema:

    def __init__(self, sistema: Sistema, deadband: float = 0.3):
        self.sistema = sistema
        self.deadband = deadband  # histéresis para evitar oscilaciones

    def update(self):
        """Llamar periódicamente para leer temperatura y aplicar control."""
        try:
            temp = self.sistema.get_temperature()
        except Exception as e:
            # No hay lecturas; se puede loggear o ignorar
            print(f"[Controlador] Error leyendo sensores: {e}")
            return

        if self.sistema.mode == "manual" and self.sistema.manual_enabled:
            target = self.sistema.manual_target
            # Lógica simple: si temp < target - deadband => encender calentador
            # si temp > target + deadband => apagar calentador
            if temp < (target - self.deadband):
                self._set_actuators(True)
            elif temp > (target + self.deadband):
                self._set_actuators(False)
            else:
                # Dentro de la banda muerta: no cambiar el estado.
                pass
        else:
            # Modo automático: por ahora no hacemos nada (placeholder).
            # Puedes implementar control automático aquí.
            pass

    def _set_actuators(self, on: bool):
        """Intenta activar/desactivar actuadores; si no existen métodos, hace print."""
        for a in self.sistema.actuators:
            try:
                if on:
                    if hasattr(a, "on"):
                        a.on()
                    elif hasattr(a, "set_state"):
                        a.set_state(True)
                    else:
                        print(f"[Actuador] {a} -> ON")
                else:
                    if hasattr(a, "off"):
                        a.off()
                    elif hasattr(a, "set_state"):
                        a.set_state(False)
                    else:
                        print(f"[Actuador] {a} -> OFF")
            except Exception as e:
                print(f"[Controlador] Error al cambiar actuador {a}: {e}")
