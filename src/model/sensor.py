# src/model/sensor.py

import os
import json
from typing import Optional, Dict, Any, Union


class Sensor:
    # Valores iniciales por defecto para la creación del JSON
    DEFAULT_SIM_DATA = {
        "temperature": 22.0,  # Temperatura segura
        "smoke": 0.0,  # Sin humo
        "light": 500.0  # Luz media
    }

    def __init__(self, id: str, sensor_type: str, name: str = "", data_file: Optional[str] = None):
        if sensor_type not in self.DEFAULT_SIM_DATA:
            raise ValueError(f"Tipo de sensor '{sensor_type}' no soportado.")

        self.id = id
        self.type = sensor_type
        self.name = name or f"{sensor_type}_sensor"
        self.data_file = data_file

        if self.data_file and not os.path.exists(self.data_file):
            print(
                f"[Sensor] Archivo de simulación '{self.data_file}' no encontrado. Creando con valores por defecto...")
            Sensor.generate_simulation_json(self.data_file, self.DEFAULT_SIM_DATA)

    def read(self) -> float:
        """
        Devuelve la lectura actual (float) leyendo exclusivamente desde el archivo JSON.
        """
        if not self.data_file or not os.path.exists(self.data_file):
            # Si se llega aquí, algo salió mal en la inicialización.
            raise RuntimeError(f"Archivo de datos de simulación no encontrado: {self.data_file}")

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data: Dict[str, Any] = json.load(f)

            # Intentar leer el valor correspondiente al tipo de sensor
            if self.type in data and isinstance(data[self.type], (int, float)):
                return float(data[self.type])
            else:
                raise KeyError(f"El JSON no contiene el campo '{self.type}' o el valor no es numérico.")

        except (IOError, json.JSONDecodeError, KeyError, Exception) as e:
            # Captura errores de archivo no encontrado, JSON inválido o clave faltante
            raise RuntimeError(f"Error leyendo sensor {self.type} desde JSON: {e}")

    @staticmethod
    def generate_simulation_json(path: str, data: Dict[str, Union[float, int]]):
        """Crea/reescribe un JSON con datos de simulación para pruebas."""
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        data_to_dump = {k: float(v) for k, v in data.items()}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data_to_dump, f, indent=4)