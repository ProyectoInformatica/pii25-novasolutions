# src/model/actuador.py

from typing import Optional

class Actuador:
    def __init__(self, id: str, name: str = "actuator"):
        self.id = id
        self.name = name
        self._state: bool = False  # False = OFF, True = ON

    @property
    def state(self) -> bool:
        return self._state

    def on(self):
        self._state = True
        # Lógica real de encendido (por ahora solo simulación)
        print(f"[Actuador] {self.name} -> ON")

    def off(self):
        self._state = False
        # Lógica real de apagado (por ahora solo simulación)
        print(f"[Actuador] {self.name} -> OFF")

    # Mantener set_state para compatibilidad con Controlador_Sistema
    def set_state(self, on: bool):
        if on:
            self.on()
        else:
            self.off()

    def __repr__(self):
        return f"<Actuador id={self.id}, name={self.name}, state={'ON' if self.state else 'OFF'}>"

class Ventilador(Actuador):
    def __init__(self, id: str = "heat1"):
        super().__init__(id, name="Ventilador")


class Rociador(Actuador):
    def __init__(self, id: str = "sprinkler1"):
        super().__init__(id, name="Rociador")


class LuzExterior(Actuador):
    def __init__(self, id: str = "light1"):
        super().__init__(id, name="Luz Exterior")