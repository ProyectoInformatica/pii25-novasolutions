from PySide6.QtCore import QObject, Signal, QTimer
from pathlib import Path
import json
import logging
from typing import Optional, Dict, Any, Union

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SensorModel")

DEFAULT_SIM_DATA = {
    "temperature": 22.0,
    "smoke": 0.0,
    "light": 500.0,
    "distance": 100.0,
    "airQuality": 15.0
}

RESOURCES_DIR = Path("resources")
MUNICIPIO_DATA_FILE = str(RESOURCES_DIR / "municipio_data.json")
ESCUELA_DATA_FILE = str(RESOURCES_DIR / "escuela_data.json")


class Sensor(QObject):
    lectura_actualizada = Signal(float)
    error_lectura = Signal(str)
    air_quality_text_actualizada = Signal(str, str)

    def __init__(self, id: str, sensor_type: str, name: str = "", data_file: Optional[str] = None,
                 interval_ms: int = 1000):
        super().__init__()

        if sensor_type not in DEFAULT_SIM_DATA:
            raise ValueError(f"Tipo de sensor '{sensor_type}' no soportado.")

        self.id = id
        self.type = sensor_type
        self.name = name or f"{sensor_type}_sensor"

        self.data_path: Optional[Path] = Path(data_file) if data_file else None
        self.data_file = data_file

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.read)
        self.interval_ms = interval_ms
        self.last_reading: Optional[float] = None

        self.start_reading()

    def start_reading(self):
        if self.data_path:
            self._timer.start(self.interval_ms)
            logger.debug(f"Sensor '{self.name}' iniciado. Lectura cada {self.interval_ms}ms.")
        else:
            logger.warning(f"Sensor '{self.name}' no tiene archivo de datos configurado. Lectura inactiva.")

    def stop_reading(self):
        if self._timer.isActive():
            self._timer.stop()
            logger.debug(f"Sensor '{self.name}' detenido.")

    @staticmethod
    def map_air_quality_to_text(value: float) -> str:
        if value <= 10.0:
            return "Muy Buena"
        elif value <= 25.0:
            return "Buena"
        elif value <= 50.0:
            return "Aceptable"
        elif value <= 100.0:
            return "Mala"
        else:
            return "Muy Mala (Peligrosa)"

    def read(self) -> Optional[float]:
        # BUG 2 CORREGIDO: Si el archivo no existe, emitir error_lectura
        # en lugar de fallar silenciosamente.
        if not self.data_path or not self.data_path.exists():
            error_msg = f"Archivo de datos no encontrado para sensor '{self.name}': {self.data_path}"
            logger.warning(error_msg)
            self.error_lectura.emit(error_msg)
            return self.last_reading

        try:
            with self.data_path.open("r", encoding="utf-8") as f:
                data: Dict[str, Any] = json.load(f)

            if self.type in data and isinstance(data[self.type], (int, float)):
                value = float(data[self.type])
                self.last_reading = value

                if self.type == "airQuality":
                    text_value = Sensor.map_air_quality_to_text(value)
                    self.air_quality_text_actualizada.emit(text_value, self.id)
                else:
                    self.lectura_actualizada.emit(value)

                return value
            else:
                raise KeyError(f"El JSON no contiene el campo '{self.type}' o el valor no es numérico.")

        except (IOError, json.JSONDecodeError, KeyError, Exception) as e:
            error_msg = f"Error leyendo sensor {self.type} desde JSON: {e}"
            logger.error(error_msg)
            self.error_lectura.emit(error_msg)
            return None

    @staticmethod
    def generate_simulation_json(path: Path, data: Dict[str, Union[float, int]]):
        path.parent.mkdir(parents=True, exist_ok=True)
        data_to_dump = {k: float(v) for k, v in data.items() if k in DEFAULT_SIM_DATA}
        with path.open("w", encoding="utf-8") as f:
            json.dump(data_to_dump, f, indent=4)
        logger.info(f"Archivo de simulación creado: {path.name}")


def initialize_simulation_files():
    municipio_data = {
        "temperature": DEFAULT_SIM_DATA["temperature"] + 3.0,
        "airQuality": DEFAULT_SIM_DATA["airQuality"]
    }
    escuela_data = {
        "temperature": DEFAULT_SIM_DATA["temperature"],
        "smoke": DEFAULT_SIM_DATA["smoke"],
        "light": DEFAULT_SIM_DATA["light"],
        "distance": DEFAULT_SIM_DATA["distance"],
        "airQuality": DEFAULT_SIM_DATA["airQuality"]
    }

    municipio_path = Path(MUNICIPIO_DATA_FILE)
    escuela_path = Path(ESCUELA_DATA_FILE)

    if not municipio_path.exists():
        Sensor.generate_simulation_json(municipio_path, municipio_data)

    if not escuela_path.exists():
        Sensor.generate_simulation_json(escuela_path, escuela_data)