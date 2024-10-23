# main.py
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QShortcut, QKeySequence
from app.interfaz.gui import BasicApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BasicApp()
    
    # Crear un atajo de teclado para cerrar la ventana con Escape
    escape_shortcut = QShortcut(QKeySequence("Escape"), window)
    escape_shortcut.activated.connect(window.close)  # Conectar el atajo a la función de cerrar
    
    window.show()
    sys.exit(app.exec())