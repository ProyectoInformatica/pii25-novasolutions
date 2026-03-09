import json
import threading
from datetime import datetime
from pathlib import Path

HISTORY_FILE_NAME = "sensor_history.json"
DEFAULT_DATA_FILE_NAME = "escuela_data.json"


class Reporteador:
    def __init__(self, data_file: str = DEFAULT_DATA_FILE_NAME):
        base_dir = Path(__file__).resolve().parent.parent.parent
        resources_dir = base_dir / "resources"

        self.history_full_path = resources_dir / HISTORY_FILE_NAME
        self.current_full_path = resources_dir / data_file

        self._lock = threading.Lock()

        self.inicializar_historial_desde_simulacion()

    def _leer_estado_actual(self) -> dict | None:
        try:
            if not self.current_full_path.exists():
                print(f"Advertencia: Archivo de datos actual ({self.current_full_path.name}) no encontrado.")
                return None

            with open(self.current_full_path, 'r', encoding='utf-8') as f:
                lectura_actual = json.load(f)

            if isinstance(lectura_actual, dict):
                return lectura_actual
            else:
                print(f"Advertencia: El contenido de {self.current_full_path.name} no es un diccionario JSON.")
                return None
        except Exception as e:
            print(f"ERROR al leer el estado actual para registro: {e}")
            return None

    def inicializar_historial_desde_simulacion(self):
        if self.history_full_path.exists():
            return

        print(f"INFO: El archivo de historial ({self.history_full_path.name}) no existe. Creando y poblando.")

        lectura_base = self._leer_estado_actual()
        historial_inicial = []

        if lectura_base:
            lectura_base['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            historial_inicial = [lectura_base]

        self.history_full_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.history_full_path, 'w', encoding='utf-8') as f:
                json.dump(historial_inicial, f, indent=4)

            if lectura_base:
                print(f"INFO: {self.history_full_path.name} creado exitosamente con 1 entrada.")
            else:
                print(f"INFO: {self.history_full_path.name} creado como lista vacía.")
        except Exception as e:
            print(f"ERROR: No se pudo crear/escribir el archivo de historial: {e}")

    def get_historial_sensores(self) -> list:
        try:
            if not self.history_full_path.exists():
                self.inicializar_historial_desde_simulacion()
                if not self.history_full_path.exists():
                    return []

            with open(self.history_full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, list):
                print(f"Advertencia: El archivo de historial tiene un formato incorrecto (no es una lista).")
                return []

            return data

        except json.JSONDecodeError:
            print(f"ERROR: No se pudo decodificar el JSON de historial.")
            return []
        except Exception as e:
            print(f"ERROR inesperado al leer el historial: {e}")
            return []

    def registrar_lectura_actual(self):
        lectura_actual = self._leer_estado_actual()

        if not lectura_actual:
            return

        lectura_actual['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self._lock:
            historial = self.get_historial_sensores()
            historial.append(lectura_actual)

            try:
                with open(self.history_full_path, 'w', encoding='utf-8') as f:
                    json.dump(historial, f, indent=4)
            except Exception as e:
                print(f"ERROR al escribir en el archivo de historial: {e}")