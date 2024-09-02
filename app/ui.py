# app/ui.py
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QSizePolicy, QFileDialog, QMessageBox, QTableView, QComboBox
)
from PyQt6.QtCore import QAbstractTableModel, Qt
import pandas as pd
import sys

class PandasModel(QAbstractTableModel):
    def __init__(self, df):
        super().__init__()
        self._df = df

    def rowCount(self, parent=None):
        return self._df.shape[0]

    def columnCount(self, parent=None):
        return self._df.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole:
                return str(self._df.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._df.columns[section]
            if orientation == Qt.Orientation.Vertical:
                return str(self._df.index[section])
        return None

class BasicApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Basic PyQt6 Window")
        self.setGeometry(100, 100, 800, 600)  # x, y, width, height
        
        # Crear un widget central y establecer el diseño
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Crear un diseño vertical
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Crear un diseño horizontal para los botones y combo box
        button_layout = QHBoxLayout()
        
        # Crear botones
        self.button_on = QPushButton("ON")
        self.button_off = QPushButton("OFF")
        self.button_load = QPushButton("Cargar Excel")
        
        self.button_load.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Crear un combo box para seleccionar hojas
        self.sheet_selector = QComboBox()
        self.sheet_selector.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.sheet_selector.currentIndexChanged.connect(self.change_sheet)
        
        # Conectar el botón de carga al método de carga
        self.button_load.clicked.connect(self.load_excel_file)
        
        button_layout.addWidget(self.button_load)
        button_layout.addWidget(self.sheet_selector)
        
        # Agregar el diseño de los botones al diseño principal
        main_layout.addLayout(button_layout)

        # Crear y agregar una tabla para mostrar los datos
        self.table_view = QTableView()
        main_layout.addWidget(self.table_view)

        # Variable para almacenar los DataFrames de las hojas
        self.excel_data = {}

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
            # Leer todas las hojas del archivo Excel
            self.excel_data = pd.read_excel(file_path, sheet_name=None)  # Lee todas las hojas
            
            # Poblar el combo box con los nombres de las hojas
            self.sheet_selector.clear()
            self.sheet_selector.addItems(self.excel_data.keys())
            
            # Mostrar la primera hoja por defecto
            self.show_sheet(self.sheet_selector.currentText())
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al procesar el archivo: {e}")

    def show_sheet(self, sheet_name):
        # Mostrar los datos de la hoja seleccionada
        df = self.excel_data[sheet_name]
        model = PandasModel(df)
        self.table_view.setModel(model)

    def change_sheet(self):
        # Cambiar a la hoja seleccionada
        sheet_name = self.sheet_selector.currentText()
        if sheet_name:
            self.show_sheet(sheet_name)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BasicApp()
    window.show()
    sys.exit(app.exec())
