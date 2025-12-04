# src/model/sensor.py

# src/model/sensor.py

from PySide6.QtCore import QObject, Signal, QTimer
from pathlib import Path
import json
import logging
from typing import Optional, Dict, Any, Union

# Configuración básica del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SensorModel")

# Constante de módulo para los valores de simulación
DEFAULT_SIM_DATA = {
    "temperature": 22.0,  # Temperatura segura
    "smoke": 0.0,         # Sin humo
    "light": 500.0,       # Luz media
    "distance": 100.0,    # NUEVO: Distancia por defecto (cm)
    "airQuality": 15.0    # Calidad de aire
}


class Sensor(QObject):
    # Señales para comunicar cambios y errores al Controlador
    lectura_actualizada = Signal(float)
    error_lectura = Signal(str)

    def __init__(self, id: str, sensor_type: str, name: str = "", data_file: Optional[str] = None,
                 interval_ms: int = 1000):
        # 1. Llamada obligatoria al constructor de QObject
        super().__init__()

        if sensor_type not in DEFAULT_SIM_DATA:
            raise ValueError(f"Tipo de sensor '{sensor_type}' no soportado.")

        self.id = id
        self.type = sensor_type
        self.name = name or f"{sensor_type}_sensor"

        # 2. Uso de pathlib.Path para manejo de archivos
        self.data_path: Optional[Path] = Path(data_file) if data_file else None

        # 3. Check y creación del archivo de simulación si no existe
        if self.data_path and not self.data_path.exists():
            logger.info(
                f"Archivo de simulación '{self.data_path.name}' no encontrado. Creando con valores por defecto...")
            Sensor.generate_simulation_json(self.data_path, DEFAULT_SIM_DATA)

        # 4. Configuración de QTimer para la lectura periódica (asincronía ligera)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.read)
        self.interval_ms = interval_ms

        # Iniciar la lectura al crear la instancia
        self.start_reading()

    def start_reading(self):
        if self.data_path:
            self._timer.start(self.interval_ms)
            logger.info(f"Sensor '{self.name}' iniciado. Lectura cada {self.interval_ms}ms.")
        else:
            logger.warning(f"Sensor '{self.name}' no tiene archivo de datos configurado. Lectura inactiva.")

    def stop_reading(self):
        if self._timer.isActive():
            self._timer.stop()
            logger.info(f"Sensor '{self.name}' detenido.")

    def read(self) -> Optional[float]:
        if not self.data_path or not self.data_path.exists():
            error_msg = f"Archivo de datos de simulación no encontrado: {self.data_path}"
            logger.error(error_msg)
            self.error_lectura.emit(error_msg)
            return None

        try:
            with self.data_path.open("r", encoding="utf-8") as f:
                data: Dict[str, Any] = json.load(f)

            # Intentar leer el valor correspondiente
            if self.type in data and isinstance(data[self.type], (int, float)):
                value = float(data[self.type])

                # 5. Emitir señal al Controlador para notificar el nuevo valor
                self.lectura_actualizada.emit(value)
                return value
            else:
                raise KeyError(f"El JSON no contiene el campo '{self.type}' o el valor no es numérico.")

        except (IOError, json.JSONDecodeError, KeyError, Exception) as e:
            # 6. Capturar errores, loguear y emitir señal de error
            error_msg = f"Error leyendo sensor {self.type} desde JSON: {e}"
            logger.error(error_msg)
            self.error_lectura.emit(error_msg)
            return None

    @staticmethod
    def generate_simulation_json(path: Path, data: Dict[str, Union[float, int]]):
        # Crea los directorios padres si no existen
        path.parent.mkdir(parents=True, exist_ok=True)
        data_to_dump = {k: float(v) for k, v in data.items()}
        with path.open("w", encoding="utf-8") as f:
            json.dump(data_to_dump, f, indent=4)