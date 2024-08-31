# app/ui.py
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QSizePolicy, QFileDialog, QMessageBox
)
import pandas as pd
import sys

class BasicApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Basic PyQt6 Window")
        self.setGeometry(100, 100, 500, 400)  # x, y, width, height
        
        # Crear un widget central y establecer el diseño
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Crear un diseño vertical
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Crear un diseño horizontal para los botones
        button_layout = QHBoxLayout()
        
        # Crear botones
        self.button_on = QPushButton("ON")
        self.button_off = QPushButton("OFF")
        self.button_load = QPushButton("Cargar Excel")
        
        self.button_load.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Conectar el botón de carga al método de carga
        self.button_load.clicked.connect(self.load_excel_file)
        
        button_layout.addWidget(self.button_load)
        
        # Agregar el diseño de los botones al diseño principal
        main_layout.addLayout(button_layout)

    def load_excel_file(self):
        # Abrir un cuadro de diálogo para seleccionar un archivo
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Archivos Excel (*.xlsx *.xls)")
        file_dialog.setViewMode(QFileDialog.ViewMode.List)

        if file_dialog.exec():
            # Obtener la ruta del archivo seleccionado
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                file_path = file_paths[0]
                self.process_excel_file(file_path)

    def process_excel_file(self, file_path):
        try:
            # Leer el archivo Excel
            df = pd.read_excel(file_path, sheet_name=None)  # Lee todas las hojas
            sheet_names = df.keys()
            
            # Procesar los datos (aquí solo mostramos los nombres de las hojas)
            message = "Hojas en el archivo:\n" + "\n".join(sheet_names)
            QMessageBox.information(self, "Archivo Excel Cargado", message)
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al procesar el archivo: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BasicApp()
    window.show()
    sys.exit(app.exec())

