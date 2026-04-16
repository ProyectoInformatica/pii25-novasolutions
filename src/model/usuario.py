class Usuario:
    def __init__(self, email: str, contrasena: str, rol: str, nombre: str = "", apellido: str = "", id_db=None):
        self.id_db = id_db
        self.email = email.lower().strip()
        self.nombre = nombre.strip()
        self.apellido = apellido.strip()
        self.contrasena = contrasena.strip()
        if rol == '1':
            self.rol = "director"
        elif rol == '0':
            self.rol = "mantenimiento"
        else:
            self.rol = rol.lower().strip()

    def verificar_credenciales(self, email: str, clave: str) -> bool:
        return self.email == email.lower().strip() and self.contrasena == clave.strip()

    def es_director(self) -> bool:
        return self.rol == "director"

    def es_mantenimiento(self) -> bool:
        return self.rol == "mantenimiento"

    def es_estudiante(self) -> bool:
        return self.rol == "estudiante"

    def __repr__(self) -> str:
        return f"Usuario(email='{self.email}', nombre='{self.nombre}', apellido='{self.apellido}', rol='{self.rol}')"