import secrets
import logging
import mysql.connector
from mysql.connector import Error

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

    @staticmethod
    def _generar_salt() -> str:
        return secrets.token_hex(16)

    # Métodos de usuario

    def autenticar_usuario(self, email: str, password: str):
        # La verificación del hash se hace en SQL, no en Python
        conexion = self.conectar()
        if not conexion:
            return None
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                """SELECT id, nombre, apellido, mail, tipo
                   FROM user
                   WHERE mail     = %s
                     AND password = SHA2(CONCAT(%s, salt), 256)
                     AND activo   = 1""",
                (email.lower().strip(), password)
            )
            return cursor.fetchone()
        finally:
            conexion.close()

    def obtener_todos_usuarios(self):
        conexion = self.conectar()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                """SELECT id, nombre, apellido, mail, tipo
                   FROM user
                   WHERE activo = 1
                   ORDER BY apellido, nombre"""
            )
            return cursor.fetchall()
        finally:
            conexion.close()

    def obtener_usuario_por_email(self, email: str):
        conexion = self.conectar()
        if not conexion:
            return None
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                """SELECT id, nombre, apellido, mail, tipo
                   FROM user
                   WHERE mail   = %s
                     AND activo = 1""",
                (email.lower().strip(),)
            )
            return cursor.fetchone()
        finally:
            conexion.close()

    def registrar_usuario(self, nombre: str, password: str, apellido: str, email: str, tipo: str):
        # Generamos un salt aleatorio y dejamos que la BD calcule el hash
        conexion = self.conectar()
        if not conexion:
            return False
        try:
            salt = self._generar_salt()
            cursor = conexion.cursor()
            cursor.execute(
                """INSERT INTO user (nombre, apellido, mail, password, salt, tipo)
                   VALUES (%s, %s, %s, SHA2(CONCAT(%s, %s), 256), %s, %s)""",
                (nombre, apellido, email.lower(), password, salt, salt, tipo)
            )
            conexion.commit()
            return True
        except Exception as e:
            logger.error(f"Error al registrar usuario: {e}")
            return False
        finally:
            conexion.close()

    def dar_baja_usuario(self, id_user: int) -> bool:
        # Baja lógica: no se borra la fila, se marca como inactivo
        conexion = self.conectar()
        if not conexion:
            return False
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """UPDATE user
                   SET activo = 0, fecha_baja = NOW()
                   WHERE id    = %s
                     AND tipo != '1'""",
                (id_user,)
            )
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()

    # Métodos auxiliares de escuela

    def _obtener_o_crear_escuela(self, nombre: str, cursor) -> int:
        # Busca la escuela por nombre; si no existe la crea
        cursor.execute(
            "SELECT id FROM escuela WHERE nombre = %s AND activo = 1 LIMIT 1",
            (nombre,)
        )
        fila = cursor.fetchone()
        if fila:
            return fila[0]
        cursor.execute(
            "INSERT INTO escuela (nombre, direccion) VALUES (%s, 'Sin direccion')",
            (nombre,)
        )
        return cursor.lastrowid

    # Métodos de sensor

    def obtener_sensores(self):
        conexion = self.conectar()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                """SELECT s.id, s.tipo_sensor, s.ubicacion, e.nombre AS escuela
                   FROM sensor s
                   JOIN escuela e ON s.id_escuela = e.id
                   WHERE s.activo = 1
                   ORDER BY e.nombre, s.ubicacion"""
            )
            return cursor.fetchall()
        finally:
            conexion.close()

    def crear_sensor(self, tipo_sensor: str, ubicacion: str, escuela_nombre: str):
        conexion = self.conectar()
        if not conexion:
            return None
        try:
            cursor = conexion.cursor()
            id_escuela = self._obtener_o_crear_escuela(escuela_nombre, cursor)
            cursor.execute(
                """INSERT INTO sensor (tipo_sensor, ubicacion, id_escuela)
                   VALUES (%s, %s, %s)""",
                (tipo_sensor, ubicacion, id_escuela)
            )
            conexion.commit()
            return cursor.lastrowid
        finally:
            conexion.close()

    def dar_baja_sensor(self, id_sensor: int) -> bool:
        # Baja lógica: no se borra la fila, se marca como inactivo
        conexion = self.conectar()
        if not conexion:
            return False
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE sensor SET activo = 0, fecha_baja = NOW() WHERE id = %s",
                (id_sensor,)
            )
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()

    def obtener_ultima_medida(self, id_sensor: int):
        conexion = self.conectar()
        if not conexion:
            return None
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """SELECT medida
                   FROM registros
                   WHERE id_sensor = %s
                   ORDER BY hora DESC
                   LIMIT 1""",
                (id_sensor,)
            )
            resultado = cursor.fetchone()
            return resultado[0] if resultado else None
        finally:
            conexion.close()

    # Métodos de actuador

    def obtener_actuadores_con_sensor(self):
        conexion = self.conectar()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                """SELECT a.id, a.nombre, a.tipo, a.estado_actual,
                          a.id_sensor_vinculado, s.tipo_sensor
                   FROM actuador a
                   JOIN sensor s ON a.id_sensor_vinculado = s.id
                   WHERE a.activo = 1
                     AND s.activo = 1
                   ORDER BY a.nombre"""
            )
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
                """INSERT INTO actuador (nombre, tipo, id_sensor_vinculado)
                   VALUES (%s, %s, %s)""",
                (nombre, tipo, id_sensor)
            )
            conexion.commit()
            return cursor.lastrowid
        finally:
            conexion.close()

    def actualizar_estado_actuador(self, id_actuador: int, estado: bool) -> bool:
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

    # Métodos de reportes e historial

    def obtener_historial_registros(self, limit: int = 100):
        conexion = self.conectar()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                """SELECT r.hora, s.tipo_sensor, s.ubicacion,
                          e.nombre AS escuela, r.medida
                   FROM registros r
                   JOIN sensor  s ON r.id_sensor  = s.id
                   JOIN escuela e ON s.id_escuela = e.id
                   ORDER BY r.hora DESC
                   LIMIT %s""",
                (limit,)
            )
            return cursor.fetchall()
        finally:
            conexion.close()
