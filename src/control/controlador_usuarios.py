from typing import List, Optional
from src.model.basedatos import BaseDatos
from src.model.usuario import Usuario


class ControladorUsuarios:
    def __init__(self):
        self.db = BaseDatos()

    def autenticar(self, email: str, contrasena: str) -> Optional[Usuario]:
        row = self.db.autenticar_usuario(email, contrasena)
        return self._fila_a_usuario(row) if row else None

    def obtener_todos(self) -> List[Usuario]:
        return [self._fila_a_usuario(row) for row in self.db.obtener_todos_usuarios()]

    def registrar_usuario(self, email: str, nombre: str, apellido: str, contrasena: str, rol: str) -> bool:
        tipo_db = '1' if rol == "director" else '0'
        return self.db.registrar_usuario(nombre, contrasena, apellido, email, tipo_db)

    def eliminar_usuario(self, id_user: int) -> bool:
        """Baja lógica por PK. No borra la fila de la base de datos."""
        return self.db.dar_baja_usuario(id_user)

    def obtener_usuario_por_email(self, email: str) -> Optional[Usuario]:
        row = self.db.obtener_usuario_por_email(email)
        return self._fila_a_usuario(row) if row else None

    @property
    def usuarios(self) -> List[Usuario]:
        return self.obtener_todos()

    @staticmethod
    def _fila_a_usuario(row: dict) -> Usuario:
        return Usuario(
            email=row['mail'],
            contrasena=row.get('password', ''),
            rol=row['tipo'],
            nombre=row['nombre'],
            apellido=row['apellido'],
            id_db=row['id']
        )
