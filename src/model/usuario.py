# src/model/usuario.py

class Usuario:
    def __init__(self, email, contrasena, rol, nombre="", apellido=""):
        self.email = email.lower().strip()
        self.nombre = nombre.strip()
        self.apellido = apellido.strip()
        self.contrasena = contrasena.strip()
        self.rol = rol.lower().strip()

    @classmethod
    def from_json_data(cls, email, nombre, apellido, salt, contrasena, rol):
        return cls(
            email=email,
            contrasena=contrasena,
            rol=rol,
            nombre=nombre,
            apellido=apellido
        )

    def verificar_credenciales(self, email, clave):
        return (
            self.email == email.lower().strip()
            and self.contrasena == clave.strip()
        )

    def es_director(self):
        return self.rol == "director"

    def es_mantenimiento(self):
        return self.rol == "mantenimiento"

    def es_estudiante(self):
        return self.rol == "estudiante"

    def __repr__(self):
        return (
            f"Usuario(email='{self.email}', "
            f"nombre='{self.nombre}', apellido='{self.apellido}', rol='{self.rol}')"
        )