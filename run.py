# run.py

from PySide6.QtWidgets import QApplication
from src.model.sensor import initialize_simulation_files
from src.view.inicio import Inicio
import sys

if __name__ == "__main__":
    try:
        initialize_simulation_files() 
    except Exception as e:
        print(f"ERROR FATAL al inicializar archivos JSON: {e}")
        sys.exit(1)

    app = QApplication(sys.argv)
    ventana = Inicio()
    ventana.show()
    sys.exit(app.exec())