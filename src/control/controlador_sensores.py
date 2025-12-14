from typing import List, Dict, Optional
import json
from src.model.sensor import Sensor
from pathlib import Path


class Controlador_Sensores:
    def __init__(self, sensors: List[Sensor]):
        self.sensors = sensors

    def read_all(self) -> Dict[str, Optional[float]]:
        readings = {}
        for s in self.sensors:
            # Llama a read() que internamente emite la señal
            try:
                # Guardamos el valor float retornado (None si falla)
                readings[s.id] = s.read()
            except Exception:
                readings[s.id] = None
        return readings

    def write_data(self, sensor_type: str, new_value: float, target_file: str):

        # Encontrar el sensor para obtener el ID de clave
        # Esto es solo para asegurar que el sensor existe en el sistema.
        target_sensor: Optional[Sensor] = None
        for s in self.sensors:
            if s.type == sensor_type and str(s.data_path) == target_file:
                target_sensor = s
                break

        if not target_sensor:
            # En modo Mantenimiento, la escritura es siempre al archivo de la Escuela
            if target_file.endswith("escuela_data.json"):
                 pass # Permitimos continuar ya que el sensor_type es suficiente como clave.
            else:
                print(f"⚠️ Error: No se encontró el sensor '{sensor_type}' asociado al archivo '{target_file}'.")
                return

        # Leer todos los datos existentes del archivo objetivo
        try:
            target_path = Path(target_file)
            with target_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: Archivo de datos no encontrado: {target_file}")
            return
        except json.JSONDecodeError:
            print(f"Error: Formato JSON inválido en {target_file}")
            return

        # Actualizar el valor específico y escribir de vuelta
        try:
            # Usamos el tipo de sensor como la clave en el JSON
            data[sensor_type] = float(new_value)

            with target_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

        except Exception as e:
            print(f"Error al escribir en el archivo {target_file}: {e}")