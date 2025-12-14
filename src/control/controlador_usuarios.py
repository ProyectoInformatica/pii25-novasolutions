import json
import os
from src.model.usuario import Usuario


class ControladorUsuarios:
    def __init__(self, ruta_json="usuarios.json"):
        self.ruta_json = ruta_json
        self.usuarios = self.cargar_usuarios()

    def cargar_usuarios(self):
        # Carga los usuarios desde un archivo JSON o crea uno por defecto.
        if not os.path.exists(self.ruta_json):
            # Si no existe, crear usuarios de prueba y guardarlos
            usuarios_iniciales = [
                {"nombre_usuario": "director", "contrasena": "1234", "rol": "director"},
                {"nombre_usuario": "mantenimiento", "contrasena": "abcd", "rol": "mantenimiento"}
            ]
            try:
                with open(self.ruta_json, "w", encoding="utf-8") as f:
                    json.dump(usuarios_iniciales, f, indent=4)
            except Exception as e:
                print(f"Advertencia: No se pudo crear el archivo {self.ruta_json}: {e}")

            return [Usuario(**u) for u in usuarios_iniciales]

        # Leer usuarios desde JSON
        with open(self.ruta_json, "r", encoding="utf-8") as f:
            datos = json.load(f)
            return [Usuario(**u) for u in datos]

    def guardar_usuarios(self):
        # Guarda la lista actual de usuarios en el archivo JSON.
        datos = [
            {
                "nombre_usuario": u.nombre_usuario,
                "contrasena": u.contrasena,
                "rol": u.rol
            }
            for u in self.usuarios
        ]
        with open(self.ruta_json, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

    def autenticar(self, nombre_usuario, contrasena):
        # Verifica si las credenciales son correctas.
        for usuario in self.usuarios:
            if usuario.verificar_credenciales(nombre_usuario, contrasena):
                return usuario
        return None

    def registrar_usuario(self, nombre_usuario, contrasena, rol):
        # Registra un nuevo usuario y lo guarda en el archivo JSON.
        # Verificar si ya existe el usuario
        user_name = nombre_usuario.lower().strip()
        if any(u.nombre_usuario == user_name for u in self.usuarios):
            print("El usuario ya existe.")
            return False

        nuevo_usuario = Usuario(nombre_usuario, contrasena, rol)
        self.usuarios.append(nuevo_usuario)
        self.guardar_usuarios()
        print(f"Usuario '{nombre_usuario}' registrado correctamente.")
        return True

    def eliminar_usuario(self, nombre_usuario):
        # Elimina un usuario por nombre y guarda el JSON.
        nombre_usuario_clean = nombre_usuario.lower().strip()
        for usuario in self.usuarios:
            if usuario.nombre_usuario == nombre_usuario_clean:
                self.usuarios.remove(usuario)
                self.guardar_usuarios()
                return True
        return False