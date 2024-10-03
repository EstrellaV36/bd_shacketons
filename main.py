# main.py
import sys
from PyQt6.QtWidgets import QApplication
from app.interfaz.gui import BasicApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BasicApp()
    window.show()
    sys.exit(app.exec())