class Usuario:
    #Representa cualquier usuario que quiera entrar al sistema.

    def __init__(self, nombre_usuario, contrasena, rol):
        self.nombre_usuario = nombre_usuario.lower().strip()
        self.contrasena = contrasena.strip()
        self.rol = rol.lower().strip()

    def verificar_credenciales(self, usuario, clave):
        #Comprueba si las credenciales son verdaderas.
        return self.nombre_usuario == usuario.lower().strip() and self.contrasena == clave.strip()

    def es_director(self):
        return self.rol == "director"

    def es_mantenimiento(self):
        return self.rol == "mantenimiento"

    def es_estudiante(self):
        return self.rol == "estudiante"

    def __repr__(self):
        return f"Usuario({self.nombre_usuario}, rol='{self.rol}')"
