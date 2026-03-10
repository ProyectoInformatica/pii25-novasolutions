# src/control/controlador_usuarios.py

import json
import os
from src.model.usuario import Usuario


class ControladorUsuarios:
    def __init__(self):
        self.ruta_json = "usuarios.json"
        self.usuarios = self.cargar_usuarios()

    def cargar_usuarios(self):
        if not os.path.exists(self.ruta_json):
            usuarios_objects = self.crearUsuariosIniciales()
            usuarios_json_array = self.usuariosToJson(usuarios_objects)

            with open(self.ruta_json, "w", encoding="utf-8") as openFile:
                json.dump(usuarios_json_array, openFile, indent=4, ensure_ascii=False)

            return usuarios_objects

        with open(self.ruta_json, "r", encoding="utf-8") as openFile:
            datos = json.load(openFile)

            usuarios = []
            for u in datos:
                usuario = Usuario.from_json_data(**u)
                usuarios.append(usuario)
            return usuarios

    def crearUsuariosIniciales(self):
        usuariosIniciales = [
            Usuario(
                email="director@escuela.com",
                contrasena="1234",
                rol="director",
                nombre="Director",
                apellido="General"
            ),
            Usuario(
                email="mantenimiento@escuela.com",
                contrasena="abcd",
                rol="mantenimiento",
                nombre="Jefe",
                apellido="Mantenimiento"
            ),
        ]
        return usuariosIniciales

    def usuariosToJson(self, usuarios):
        usuarios_array = []
        for user in usuarios:
            usuario_dict = {
                "email": user.email,
                "nombre": user.nombre,
                "apellido": user.apellido,
                "salt": "",
                "contrasena": user.contrasena,
                "rol": user.rol
            }
            usuarios_array.append(usuario_dict)

        return usuarios_array

    def guardar_usuarios(self):
        datos = self.usuariosToJson(self.usuarios)
        with open(self.ruta_json, "w", encoding="utf-8") as openFile:
            json.dump(datos, openFile, indent=4, ensure_ascii=False)

    def autenticar(self, email, contrasena):
        for usuario in self.usuarios:
            if usuario.verificar_credenciales(email, contrasena):
                return usuario
        return None

    def registrar_usuario(self, email, nombre, apellido, contrasena, rol):
        email_limpio = email.lower().strip()
        if any(u.email == email_limpio for u in self.usuarios):
            print("El correo ya está registrado.")
            return False

        nuevo_usuario = Usuario(
            email=email_limpio,
            contrasena=contrasena,
            rol=rol,
            nombre=nombre,
            apellido=apellido
        )
        self.usuarios.append(nuevo_usuario)
        self.guardar_usuarios()
        print(f"Usuario '{email_limpio}' registrado correctamente.")
        return True

    def eliminar_usuario(self, email):
        email_limpio = email.lower().strip()
        for usuario in self.usuarios:
            if usuario.email == email_limpio:
                if usuario.es_director():
                    print("No se puede eliminar al usuario director.")
                    return False
                self.usuarios.remove(usuario)
                self.guardar_usuarios()
                return True
        return False

    def obtener_usuario_por_email(self, email):
        email_limpio = email.lower().strip()
        for usuario in self.usuarios:
            if usuario.email == email_limpio:
                return usuario
        return None