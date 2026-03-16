# src/control/controlador_usuarios.py
from src.model.basedatos import BaseDatos
from src.model.usuario import Usuario


class ControladorUsuarios:
    def __init__(self):
        self.db = BaseDatos()

    def obtener_todos(self):
        usuarios = []
        con = self.db.conectar()
        if con:
            cursor = con.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user")
            for row in cursor.fetchall():
                usuarios.append(Usuario(
                    email=row['mail'],
                    contrasena=row['password'],
                    rol=row['tipo'],
                    nombre=row['nombre'],
                    apellido=row['apellido'],
                    id_db=row['id']
                ))
            con.close()
        return usuarios

    def autenticar(self, email, contrasena):
        con = self.db.conectar()
        if con:
            cursor = con.cursor(dictionary=True)
            # Buscamos directamente en la base de datos
            query = "SELECT * FROM user WHERE mail = %s AND password = %s"
            cursor.execute(query, (email.lower(), contrasena))
            row = cursor.fetchone()
            con.close()

            if row:
                return Usuario(
                    email=row['mail'],
                    contrasena=row['password'],
                    rol=row['tipo'],
                    nombre=row['nombre'],
                    apellido=row['apellido'],
                    id_db=row['id']
                )
        return None

    def registrar_usuario(self, email, nombre, apellido, contrasena, rol):
        # Convertimos el rol de texto a ENUM de la BD
        tipo_db = '1' if rol == "director" else '0'

        con = self.db.conectar()
        if con:
            try:
                cursor = con.cursor()
                query = """INSERT INTO user (nombre, password, apellido, mail, tipo, salt) 
                           VALUES (%s, %s, %s, %s, %s, %s)"""
                cursor.execute(query, (nombre, contrasena, apellido, email.lower(), tipo_db, ""))
                con.commit()
                return True
            except Exception as e:
                print(f"Error al registrar: {e}")
                return False
            finally:
                con.close()
        return False

    def eliminar_usuario(self, email):
        con = self.db.conectar()
        if con:
            try:
                cursor = con.cursor()
                # Evitamos borrar al director (tipo '1')
                query = "DELETE FROM user WHERE mail = %s AND tipo != '1'"
                cursor.execute(query, (email,))
                con.commit()
                return cursor.rowcount > 0
            finally:
                con.close()
        return False

    def obtener_usuario_por_email(self, email):
        con = self.db.conectar()
        if con:
            cursor = con.cursor(dictionary=True)
            query = "SELECT * FROM user WHERE mail = %s"
            cursor.execute(query, (email.lower().strip(),))
            row = cursor.fetchone()
            con.close()

            if row:
                return Usuario(
                    email=row['mail'],
                    contrasena=row['password'],
                    rol=row['tipo'],
                    nombre=row['nombre'],
                    apellido=row['apellido'],
                    id_db=row['id']
                )
        return None

    # Propiedad para mantener compatibilidad con tu vista gestion_usuarios.py
    @property
    def usuarios(self):
        return self.obtener_todos()