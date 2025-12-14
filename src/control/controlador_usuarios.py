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
                json.dump(usuarios_json_array, openFile, indent=4)

        with open(self.ruta_json, "r", encoding="utf-8") as openFile:
            datos = json.load(openFile)
            return [Usuario.from_json_data(**u) for u in datos]

    def crearUsuariosIniciales(self):
        usuariosIniciales = [
            Usuario("director", "1234", "director"),
            Usuario("mantenimiento", "abcd", "mantenimiento"),
        ]
        return usuariosIniciales

    def usuariosToJson(self, usuarios):
        usuarios_array = []

        for user in usuarios:
            usuario_dict = {
                "nombre_usuario": user.nombre_usuario,
                "salt": self.asegurarHex(user.salt),
                "contrasena": self.asegurarHex(user.contrasenaHasheada),
                "rol": user.rol
            }
            usuarios_array.append(usuario_dict)

        return usuarios_array

    def asegurarHex(self, dato):
        if isinstance(dato, str):
            return dato
        else:
            return dato.hex()

    def asegurarBytes(self, dato):
        if isinstance(dato, bytes):
            return dato
        else:
            return bytes.fromhex(dato)

    def guardar_usuarios(self):
        datos = [
            {
                "nombre_usuario": u.nombre_usuario,
                "salt": self.asegurarHex(u.salt),
                "contrasena": self.asegurarHex(u.contrasenaHasheada),
                "rol": u.rol
            }
            for u in self.usuarios
        ]
        with open(self.ruta_json, "w", encoding="utf-8") as openFile:
            json.dump(datos, openFile, indent=4, ensure_ascii=False)

    def autenticar(self, nombre_usuario, contrasena):
        for usuario in self.usuarios:
            if usuario.verificar_credenciales(nombre_usuario, contrasena):
                return usuario
        return None

    def registrar_usuario(self, nombre_usuario, contrasena, rol):
        if any(u.nombre_usuario == nombre_usuario.lower().strip() for u in self.usuarios):
            print("El usuario ya existe.")
            return False

        nuevo_usuario = Usuario(nombre_usuario, contrasena, rol)
        self.usuarios.append(nuevo_usuario)
        self.guardar_usuarios()
        print(f"Usuario '{nombre_usuario}' registrado correctamente.")
        return True

    def eliminar_usuario(self, nombre_usuario):
        for usuario in self.usuarios:
            if usuario.nombre_usuario == nombre_usuario:
                self.usuarios.remove(usuario)
                self.guardar_usuarios()
                return True
        return False