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

    # Métodos de escuela

    def obtener_escuelas(self):
        conexion = self.conectar()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, nombre, direccion FROM escuela WHERE activo = 1 ORDER BY nombre"
            )
            return cursor.fetchall()
        finally:
            conexion.close()

    def crear_escuela(self, nombre: str, direccion: str) -> bool:
        conexion = self.conectar()
        if not conexion:
            return False
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO escuela (nombre, direccion) VALUES (%s, %s)",
                (nombre, direccion)
            )
            conexion.commit()
            return True
        except Exception as e:
            logger.error(f"Error al crear escuela: {e}")
            return False
        finally:
            conexion.close()

    def dar_baja_escuela(self, id_escuela: int) -> bool:
        conexion = self.conectar()
        if not conexion:
            return False
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE escuela SET activo = 0, fecha_baja = NOW() WHERE id = %s",
                (id_escuela,)
            )
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()

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

    def crear_sensor(self, tipo_sensor: str, ubicacion: str, id_escuela: int):
        conexion = self.conectar()
        if not conexion:
            return None
        try:
            cursor = conexion.cursor()
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

    # Métodos de mensajería

    def obtener_usuarios_activos(self):
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

    def obtener_conversacion(self, id_user1: int, id_user2: int, limite: int = 50):
        conexion = self.conectar()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                """SELECT
                       m.id          AS id_mensaje,
                       m.contenido,
                       m.hora,
                       m.estado,
                       er.id_user1   AS id_remitente,
                       er.id_user2   AS id_destinatario,
                       u.nombre      AS nombre_remitente,
                       u.apellido    AS apellido_remitente
                   FROM mensaje m
                   JOIN envia_recibe er ON er.id_mensaje = m.id
                   JOIN user u          ON u.id = er.id_user1
                   WHERE m.activo = 1
                     AND (
                         (er.id_user1 = %s AND er.id_user2 = %s)
                      OR (er.id_user1 = %s AND er.id_user2 = %s)
                     )
                   ORDER BY m.hora ASC
                   LIMIT %s""",
                (id_user1, id_user2, id_user2, id_user1, limite)
            )
            return cursor.fetchall()
        finally:
            conexion.close()

    def enviar_mensaje(self, id_remitente: int, id_destinatario: int, contenido: str) -> bool:
        conexion = self.conectar()
        if not conexion:
            return False
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO mensaje (contenido, estado, activo) VALUES (%s, '0', 1)",
                (contenido,)
            )
            id_mensaje = cursor.lastrowid
            cursor.execute(
                """INSERT INTO envia_recibe (id_mensaje, id_user1, id_user2, fecha_envio)
                   VALUES (%s, %s, %s, NOW())""",
                (id_mensaje, id_remitente, id_destinatario)
            )
            conexion.commit()
            return True
        except Exception as e:
            logger.error(f"Error al enviar mensaje: {e}")
            conexion.rollback()
            return False
        finally:
            conexion.close()

    def contar_no_leidos(self, id_destinatario: int) -> int:
        conexion = self.conectar()
        if not conexion:
            return 0
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """SELECT COUNT(*) FROM mensaje m
                   JOIN envia_recibe er ON er.id_mensaje = m.id
                   WHERE m.activo = 1 AND m.estado = '0'
                     AND er.id_user2 = %s""",
                (id_destinatario,)
            )
            resultado = cursor.fetchone()
            return resultado[0] if resultado else 0
        finally:
            conexion.close()

    def contar_no_leidos_de_contacto(self, id_remitente: int, id_destinatario: int) -> int:
        conexion = self.conectar()
        if not conexion:
            return 0
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """SELECT COUNT(*) FROM mensaje m
                   JOIN envia_recibe er ON er.id_mensaje = m.id
                   WHERE m.activo = 1 AND m.estado = '0'
                     AND er.id_user1 = %s AND er.id_user2 = %s""",
                (id_remitente, id_destinatario)
            )
            resultado = cursor.fetchone()
            return resultado[0] if resultado else 0
        finally:
            conexion.close()

    def marcar_leidos(self, id_remitente: int, id_destinatario: int) -> bool:
        conexion = self.conectar()
        if not conexion:
            return False
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """UPDATE mensaje m
                   JOIN envia_recibe er ON er.id_mensaje = m.id
                   SET m.estado = '1'
                   WHERE m.activo = 1 AND m.estado = '0'
                     AND er.id_user1 = %s AND er.id_user2 = %s""",
                (id_remitente, id_destinatario)
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
