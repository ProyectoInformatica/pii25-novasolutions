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

    # Sensores

    def obtener_sensores(self):
        conexion = self.conectar()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id, tipo_sensor, ubicacion, escuela FROM sensor")
            return cursor.fetchall()
        finally:
            conexion.close()

    def crear_sensor(self, tipo_sensor: str, ubicacion: str, escuela: str):
        conexion = self.conectar()
        if not conexion:
            return None
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO sensor (tipo_sensor, ubicacion, escuela) VALUES (%s, %s, %s)",
                (tipo_sensor, ubicacion, escuela)
            )
            conexion.commit()
            return cursor.lastrowid
        finally:
            conexion.close()

    def eliminar_sensor(self, id_sensor: int):
        conexion = self.conectar()
        if not conexion:
            return False
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM sensor WHERE id = %s", (id_sensor,))
            conexion.commit()
            return True
        finally:
            conexion.close()

    def obtener_ultima_medida(self, id_sensor: int):
        conexion = self.conectar()
        if not conexion:
            return None
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT medida FROM registros WHERE id_sensor = %s ORDER BY hora DESC LIMIT 1",
                (id_sensor,)
            )
            resultado = cursor.fetchone()
            return resultado[0] if resultado else None
        finally:
            conexion.close()

    # Actuadores

    def obtener_actuadores_con_sensor(self):
        conexion = self.conectar()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT a.*, s.tipo_sensor
                FROM actuador a
                JOIN sensor s ON a.id_sensor_vinculado = s.id
            """)
            return cursor.fetchall()
        finally:
            conexion.close()

    def crear_actuador(self, nombre: str, tipo: str, id_sensor: int):
        conexion = self.conectar()
        if not conexion:
            return None
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO actuador (nombre, tipo, id_sensor_vinculado) VALUES (%s, %s, %s)",
                (nombre, tipo, id_sensor)
            )
            conexion.commit()
            return cursor.lastrowid
        finally:
            conexion.close()

    def actualizar_estado_actuador(self, id_actuador, estado: bool):
        conexion = self.conectar()
        if not conexion:
            return False
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE actuador SET estado_actual = %s WHERE id = %s",
                (1 if estado else 0, id_actuador)
            )
            conexion.commit()
            return True
        finally:
            conexion.close()

    # Usuarios

    def obtener_todos_usuarios(self):
        conexion = self.conectar()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user")
            return cursor.fetchall()
        finally:
            conexion.close()

    def autenticar_usuario(self, email: str, password: str):
        conexion = self.conectar()
        if not conexion:
            return None
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM user WHERE mail = %s AND password = %s",
                (email.lower(), password)
            )
            return cursor.fetchone()
        finally:
            conexion.close()

    def obtener_usuario_por_email(self, email: str):
        conexion = self.conectar()
        if not conexion:
            return None
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user WHERE mail = %s", (email.lower().strip(),))
            return cursor.fetchone()
        finally:
            conexion.close()

    def registrar_usuario(self, nombre: str, password: str, apellido: str, email: str, tipo: str):
        conexion = self.conectar()
        if not conexion:
            return False
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO user (nombre, password, apellido, mail, tipo, salt) VALUES (%s, %s, %s, %s, %s, %s)",
                (nombre, password, apellido, email.lower(), tipo, "")
            )
            conexion.commit()
            return True
        except Exception as e:
            logger.error(f"Error al registrar usuario: {e}")
            return False
        finally:
            conexion.close()

    def eliminar_usuario(self, email: str):
        conexion = self.conectar()
        if not conexion:
            return False
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "DELETE FROM user WHERE mail = %s AND tipo != '1'",
                (email,)
            )
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()

    # Reportes

    def obtener_historial_registros(self, limit: int = 100):
        conexion = self.conectar()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT r.hora, s.tipo_sensor, s.ubicacion, r.medida
                FROM registros r
                JOIN sensor s ON r.id_sensor = s.id
                ORDER BY r.hora DESC
                LIMIT %s
            """, (limit,))
            return cursor.fetchall()
        finally:
            conexion.close()