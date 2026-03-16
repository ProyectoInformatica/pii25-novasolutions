
import mysql.connector
from mysql.connector import Error

class BaseDatos:
    def __init__(self):
        # Datos extraídos de tu dump SQL
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'pii26-novasolutions'
        }

    def conectar(self):
        try:
            conexion = mysql.connector.connect(**self.config)
            return conexion
        except Error as e:
            print(f"Error al conectar a MariaDB: {e}")
            return None