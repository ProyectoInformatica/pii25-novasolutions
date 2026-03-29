# run.py

from PySide6.QtWidgets import QApplication
from src.view.inicio import Inicio
import sys

if __name__ == "__main__":
    # Eliminamos el bloque de initialize_simulation_files()
    # ya que ahora los datos vendrán de la Base de Datos.

    app = QApplication(sys.argv)

    # Iniciamos la ventana de Login/Inicio
    ventana = Inicio()
    ventana.show()

    sys.exit(app.exec())
