
import mysql.connector
from mysql.connector import Error
import logging

logger = logging.getLogger("BaseDatos")

class BaseDatos:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'pii26-novasolutions'
        }

    def conectar(self):
        try:
            return mysql.connector.connect(**self.config)
        except Error as e:
            logger.error(f"Error al conectar a MariaDB: {e}")
            return None

    def obtener_sensores(self):
        """Recupera todos los sensores de la tabla 'sensor'."""
        conexion = self.conectar()
        if not conexion: return []
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id, tipo_sensor, ubicacion, escuela FROM sensor")
            return cursor.fetchall()
        finally:
            conexion.close()

    def crear_sensor(self, tipo_sensor: str, ubicacion: str, escuela: str):
        """Inserta un nuevo sensor según las columnas del SQL."""
        conexion = self.conectar()
        if not conexion: return None
        try:
            cursor = conexion.cursor()
            query = "INSERT INTO sensor (tipo_sensor, ubicacion, escuela) VALUES (%s, %s, %s)"
            cursor.execute(query, (tipo_sensor, ubicacion, escuela))
            conexion.commit()
            return cursor.lastrowid
        finally:
            conexion.close()

    def obtener_ultima_medida(self, id_sensor: int):
        """Obtiene la medida más reciente de la tabla 'registros' para un sensor."""
        conexion = self.conectar()
        if not conexion: return None
        try:
            cursor = conexion.cursor()
            query = "SELECT medida FROM registros WHERE id_sensor = %s ORDER BY hora DESC LIMIT 1"
            cursor.execute(query, (id_sensor,))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else None
        finally:
            conexion.close()

    def eliminar_sensor(self, id_sensor: int):
        conexion = self.conectar()
        if not conexion: return False
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM sensor WHERE id = %s", (id_sensor,))
            conexion.commit()
            return True
        finally:
            conexion.close()

    def obtener_actuadores_con_sensor(self):
        conexion = self.conectar()
        if not conexion: return []
        try:
            cursor = conexion.cursor(dictionary=True)
            # Trae el actuador y el tipo de sensor al que está pegado
            query = """
                SELECT a.*, s.tipo_sensor 
                FROM actuador a
                JOIN sensor s ON a.id_sensor_vinculado = s.id
            """
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            conexion.close()

    def crear_actuador(self, nombre, tipo, id_sensor):
        conexion = self.conectar()
        if not conexion: return None
        try:
            cursor = conexion.cursor()
            query = "INSERT INTO actuador (nombre, tipo, id_sensor_vinculado) VALUES (%s, %s, %s)"
            cursor.execute(query, (nombre, tipo, id_sensor))
            conexion.commit()
            return cursor.lastrowid
        finally:
            conexion.close()

