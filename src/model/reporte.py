import json
from datetime import datetime
import os
from pathlib import Path

# Definimos el nombre del archivo de historial
HISTORY_FILE = "sensor_history.json"


class Reporteador:
    """Clase encargada de generar reportes a partir de los datos históricos."""

    def __init__(self, data_file="simulation_data.json"):
        self.current_data_file = data_file
        self.history_file = HISTORY_FILE

        # CÁLCULO ROBUSTO DE LA RUTA (Subir a la raíz del proyecto)
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.history_full_path = base_dir / self.history_file
        self.current_full_path = base_dir / self.current_data_file

        # 🌟 NUEVA LÓGICA DE INICIALIZACIÓN 🌟
        self.inicializar_historial_desde_simulacion()

    def _leer_estado_actual(self):
        """Función auxiliar para leer el contenido del simulation_data.json."""
        try:
            if not self.current_full_path.exists():
                print(f"Advertencia: Archivo de datos actual ({self.current_data_file}) no encontrado.")
                return None

            with open(self.current_full_path, 'r', encoding='utf-8') as f:
                lectura_actual = json.load(f)

            if isinstance(lectura_actual, dict):
                return lectura_actual
            else:
                print(
                    f"Advertencia: El contenido de {self.current_data_file} no es un único objeto JSON (diccionario).")
                return None
        except Exception as e:
            print(f"ERROR al leer el estado actual para inicializar: {e}")
            return None

    def inicializar_historial_desde_simulacion(self):
        """
        Crea el archivo de historial si no existe. 
        Si lo crea, usa la lectura actual de simulation_data.json como primera entrada.
        """
        if self.history_full_path.exists():
            # Si el historial ya existe, no hacemos nada.
            return

        print(f"INFO: El archivo de historial ({self.history_file}) no existe. Creando y poblando.")

        lectura_base = self._leer_estado_actual()

        if lectura_base:
            # 1. Añadir marca de tiempo a la lectura base
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            lectura_base['timestamp'] = timestamp

            # 2. Crear el historial con esta única entrada
            historial_inicial = [lectura_base]
        else:
            # Si no se pudo leer el archivo de simulación, creamos un historial vacío
            historial_inicial = []

        # 3. Guardar el historial inicial en el nuevo archivo
        try:
            with open(self.history_full_path, 'w', encoding='utf-8') as f:
                json.dump(historial_inicial, f, indent=4)

            if lectura_base:
                print(f"INFO: {self.history_file} creado exitosamente con 1 entrada de {self.current_data_file}.")
            else:
                print(f"INFO: {self.history_file} creado como lista vacía (no se pudo leer el estado actual).")
        except Exception as e:
            print(f"ERROR: No se pudo crear/escribir el archivo de historial: {e}")

    def get_historial_sensores(self):
        """
        Lee el historial de lecturas del archivo sensor_history.json.
        (El parámetro from_history_file=True/False ha sido eliminado para simplificar).
        """
        ruta_archivo = self.history_full_path

        try:
            if not ruta_archivo.exists():
                # Ya que se llama a inicializar_historial_desde_simulacion en __init__, 
                # esto solo debería ocurrir si hay un fallo de permiso grave.
                print(
                    f"Advertencia: Archivo de historial {self.history_file} no encontrado después de la inicialización.")
                return []

            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, list):
                print(f"Advertencia: El archivo de historial tiene un formato incorrecto (no es una lista).")
                return []

            return data

        except json.JSONDecodeError:
            print(f"ERROR: No se pudo decodificar el JSON de historial. Revisa el formato.")
            return []
        except Exception as e:
            print(f"ERROR inesperado al leer el historial: {e}")
            return []

    def registrar_lectura_actual(self):
        """
        Lee el último estado (de simulation_data.json), añade la marca de tiempo 
        y lo registra al final del archivo de historial.
        """
        lectura_actual = self._leer_estado_actual()

        if not lectura_actual:
            # El error ya se mostró en _leer_estado_actual
            return

        # 1. Añadir la marca de tiempo
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lectura_actual['timestamp'] = timestamp

        # 2. Cargar el historial existente
        historial = self.get_historial_sensores()  # Ahora usa el método principal

        # 3. Añadir la nueva lectura y guardar todo de nuevo
        historial.append(lectura_actual)

        try:
            with open(self.history_full_path, 'w', encoding='utf-8') as f:
                json.dump(historial, f, indent=4)
            # print(f"INFO: Lectura registrada en {self.history_file}") # Se puede comentar para no llenar la consola
        except Exception as e:
            print(f"ERROR al escribir en el archivo de historial: {e}")