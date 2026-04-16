from typing import List
from src.model.basedatos import BaseDatos


class ControladorReportes:
    def __init__(self):
        self.db = BaseDatos()

    def obtener_historial(self, limit: int = 100) -> List[dict]:
        return self.db.obtener_historial_registros(limit)