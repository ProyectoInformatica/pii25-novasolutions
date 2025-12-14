from os import urandom
from hashlib import pbkdf2_hmac


class Usuario:
    def __init__(self, nombre_usuario, contrasena, rol, salt=None):
        self.nombre_usuario = nombre_usuario.lower().strip()
        self.salt = self.asegurarBytes(salt) if salt is not None else self.asegurarBytes(urandom(16))
        self.contrasenaHasheada = self.asegurarBytes(self.hashAndSalt(contrasena.strip(), self.salt))
        self.rol = rol.lower().strip()

    # Constructor de sobrecarga para cargar usuarios desde json
    @classmethod
    def from_json_data(cls, nombre_usuario, salt, contrasena, rol):
        instance = cls.__new__(cls)
        instance.nombre_usuario = nombre_usuario.lower().strip()
        instance.rol = rol.lower().strip()

        # Convierte hex del json a bytes
        instance.salt = instance.asegurarBytes(salt)
        instance.contrasenaHasheada = instance.asegurarBytes(contrasena)

        return instance

    @classmethod
    def with_salt(cls, nombre_usuario, contrasena, rol, salt):
        return cls(nombre_usuario, contrasena, rol, salt=salt)

    def verificar_credenciales(self, usuario, clave):
        return self.nombre_usuario == usuario.lower().strip() and self.verificar_clave(self.salt,
                                                                                       self.contrasenaHasheada, clave)

    def es_director(self):
        return self.rol == "director"

    def es_mantenimiento(self):
        return self.rol == "mantenimiento"

    def es_estudiante(self):
        return self.rol == "estudiante"

    def __repr__(self):
        return f"Usuario({self.nombre_usuario}, rol='{self.rol}')"

    def hashAndSalt(self, toBeHashed, salt):
        saltBytes = self.asegurarBytes(salt)
        key = pbkdf2_hmac(
            'sha256',
            toBeHashed.encode('utf-8'),
            self.asegurarBytes(salt),
            100000
        )
        return key

    def verificar_clave(self, salUsuario, hashUsuario, contrasenaAVerificar):
        nueva_clave = pbkdf2_hmac(
            'sha256',
            contrasenaAVerificar.encode('utf-8'),
            self.asegurarBytes(salUsuario),
            100000
        )
        return nueva_clave == hashUsuario

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