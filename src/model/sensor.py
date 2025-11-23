# src/model/sensor.py
import json
import random
import os
from typing import Optional

class Sensor:

    def __init__(self, id: str, name: str = "temp_sensor", data_file: Optional[str] = None):
        self.id = id
        self.name = name
        self.data_file = data_file

    def read(self) -> float:
        """Devuelve la temperatura actual (float)."""
        # Intentar leer JSON de simulación si existe
        if self.data_file and os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Permitimos varias estructuras; priorizamos key "temperature"
                if isinstance(data, dict) and "temperature" in data:
                    return float(data["temperature"])
            except Exception:
                # Caeremos a la simulación aleatoria
                pass

        # Simulación por defecto: 20 +/- 4 °C
        return round(20.0 + random.uniform(-4.0, 4.0), 2)

    @staticmethod
    def generate_simulation_json(path: str, temperature: float):
        """Crea/reescribe un JSON simple { "temperature": temp } para pruebas."""
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"temperature": float(temperature)}, f)
