from src.model.usuario import Usuario

class ControladorUsuarios:
    def __init__(self):
        # Usuarios de prueba
        self.usuarios = [
            Usuario("director", "1234", "director"),
            Usuario("mantenimiento", "abcd", "mantenimiento"),
        ]

    def autenticar(self, nombre_usuario, contrasena):
        for usuario in self.usuarios:
            if usuario.verificar_credenciales(nombre_usuario, contrasena):
                return usuario
        return None
