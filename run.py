from PySide6.QtWidgets import QApplication
from src.view.inicio import Inicio
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Inicio()
    ventana.show()
    sys.exit(app.exec())
