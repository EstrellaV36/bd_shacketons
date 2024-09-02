# app/ui.py
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QSizePolicy, QFileDialog, QMessageBox, QTableView, QComboBox, QTabWidget
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
        self.button_load = QPushButton("Cargar Excel")
        self.button_load.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.button_load.clicked.connect(self.load_excel_file)
        
        button_layout.addWidget(self.button_load)
        
        # Agregar el diseño de los botones al diseño principal
        main_layout.addLayout(button_layout)

        # Crear un QTabWidget para las pestañas
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Crear widgets para cada pestaña
        self.on_tab = QWidget()
        self.off_tab = QWidget()
        
        # Agregar las pestañas al QTabWidget
        self.tabs.addTab(self.on_tab, "ON")
        self.tabs.addTab(self.off_tab, "OFF")

        # Crear un layout para cada pestaña
        self.on_layout = QVBoxLayout()
        self.off_layout = QVBoxLayout()
        
        self.on_tab.setLayout(self.on_layout)
        self.off_tab.setLayout(self.off_layout)

        # Crear un combo box para seleccionar hojas
        self.on_sheet_selector = QComboBox()
        self.off_sheet_selector = QComboBox()

        # Conectar la selección del combo box al método para cambiar de hoja
        self.on_sheet_selector.currentIndexChanged.connect(self.change_on_sheet)
        self.off_sheet_selector.currentIndexChanged.connect(self.change_off_sheet)

        # Crear un QTableView para cada pestaña
        self.on_table_view = QTableView()
        self.off_table_view = QTableView()

        # Agregar los combos y las tablas a los layouts de las pestañas
        self.on_layout.addWidget(self.on_sheet_selector)
        self.on_layout.addWidget(self.on_table_view)

        self.off_layout.addWidget(self.off_sheet_selector)
        self.off_layout.addWidget(self.off_table_view)

        # Variables para almacenar los DataFrames de las hojas "on" y "off"
        self.on_sheets = {}
        self.off_sheets = {}

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
            excel_data = pd.read_excel(file_path, sheet_name=None)  # Lee todas las hojas
            
            # Separar las hojas en "on" y "off"
            self.on_sheets = {name: df for name, df in excel_data.items() if "on" in name.lower()}
            self.off_sheets = {name: df for name, df in excel_data.items() if "off" in name.lower()}
            
            # Poblar los combo boxes con los nombres de las hojas
            self.on_sheet_selector.clear()
            self.on_sheet_selector.addItems(self.on_sheets.keys())
            
            self.off_sheet_selector.clear()
            self.off_sheet_selector.addItems(self.off_sheets.keys())
            
            # Mostrar la primera hoja "on" y "off" en sus respectivas pestañas
            if self.on_sheets:
                self.show_sheet(self.on_sheets[self.on_sheet_selector.currentText()], self.on_table_view)
            if self.off_sheets:
                self.show_sheet(self.off_sheets[self.off_sheet_selector.currentText()], self.off_table_view)
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al procesar el archivo: {e}")

    def show_sheet(self, df, table_view):
        # Mostrar los datos del DataFrame en la QTableView correspondiente
        model = PandasModel(df)
        table_view.setModel(model)

    def change_on_sheet(self):
        # Cambiar la hoja mostrada en la pestaña "ON"
        sheet_name = self.on_sheet_selector.currentText()
        if sheet_name:
            self.show_sheet(self.on_sheets[sheet_name], self.on_table_view)

    def change_off_sheet(self):
        # Cambiar la hoja mostrada en la pestaña "OFF"
        sheet_name = self.off_sheet_selector.currentText()
        if sheet_name:
            self.show_sheet(self.off_sheets[sheet_name], self.off_table_view)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BasicApp()
    window.show()
    sys.exit(app.exec())
