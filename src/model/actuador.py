import logging

logger = logging.getLogger("Actuador")


class Actuador:
    def __init__(self, id: str, name: str = "actuator"):
        self.id = id
        self.name = name
        self._state: bool = False

    @property
    def state(self) -> bool:
        return self._state

    def on(self):
        if not self._state:
            self._state = True
            logger.debug(f"[{self.name}] -> ON")

    def off(self):
        if self._state:
            self._state = False
            logger.debug(f"[{self.name}] -> OFF")

    def set_state(self, on: bool):
        if on:
            self.on()
        else:
            self.off()

    def __repr__(self) -> str:
        return f"<Actuador id={self.id}, name={self.name}, state={'ON' if self.state else 'OFF'}>"


class Ventilador(Actuador):
    def __init__(self, id: str = "fan1"):
        super().__init__(id, name="Ventilador")


class Rociador(Actuador):
    def __init__(self, id: str = "sprinkler1"):
        super().__init__(id, name="Rociador")


class LuzExterior(Actuador):
    def __init__(self, id: str = "lightext1"):
        super().__init__(id, name="Luz Exterior")


class LuzPasillo(Actuador):
    def __init__(self, id: str = "lightpasillo1"):
        super().__init__(id, name="Luz de Pasillo")