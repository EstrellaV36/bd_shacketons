import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QSizePolicy, QFileDialog, 
    QMessageBox, QTableView, QComboBox, QTabWidget
)
from PyQt6.QtCore import QAbstractTableModel, Qt
import pandas as pd
import sys
import re
from database import SessionLocal
from models import Buque, Tripulante

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
        self.setGeometry(100, 100, 1000, 800)  # x, y, width, height
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        button_layout = QHBoxLayout()
        
        self.button_load = QPushButton("Cargar Excel")
        self.button_load.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.button_load.clicked.connect(self.load_excel_file)
        
        button_layout.addWidget(self.button_load)
        
        main_layout.addLayout(button_layout)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.on_tab = QWidget()
        self.off_tab = QWidget()
        
        self.tabs.addTab(self.on_tab, "ON")
        self.tabs.addTab(self.off_tab, "OFF")

        self.on_layout = QVBoxLayout()
        self.off_layout = QVBoxLayout()
        
        self.on_tab.setLayout(self.on_layout)
        self.off_tab.setLayout(self.off_layout)

        self.on_sheet_selector = QComboBox()
        self.off_sheet_selector = QComboBox()

        self.on_sheet_selector.currentIndexChanged.connect(self.change_on_sheet)
        self.off_sheet_selector.currentIndexChanged.connect(self.change_off_sheet)

        self.on_table_view = QTableView()
        self.off_table_view = QTableView()

        self.on_layout.addWidget(self.on_sheet_selector)
        self.on_layout.addWidget(self.on_table_view)

        self.off_layout.addWidget(self.off_sheet_selector)
        self.off_layout.addWidget(self.off_table_view)

        self.on_sheets = {}
        self.off_sheets = {}

        self.load_data_from_db()

    def load_excel_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Archivos Excel (*.xlsx *.xls)")
        file_dialog.setViewMode(QFileDialog.ViewMode.List)

        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                file_path = file_paths[0]
                self.process_excel_file(file_path)

    def process_excel_file(self, file_path):
        try:
            excel_data = pd.read_excel(file_path, sheet_name=None)  # Lee todas las hojas
            
            on_sheets_new = {
                name: df for name, df in excel_data.items()
                if re.search(r'\bON\b$', name, re.IGNORECASE)
            }
            off_sheets_new = {
                name: df for name, df in excel_data.items()
                if re.search(r'\bOFF\b$', name, re.IGNORECASE)
            }
            
            # Combina los nuevos datos con los existentes en las variables self.on_sheets y self.off_sheets
            for name, df in on_sheets_new.items():
                if name in self.on_sheets:
                    self.on_sheets[name] = pd.concat([self.on_sheets[name], df], ignore_index=True)
                else:
                    self.on_sheets[name] = df

            for name, df in off_sheets_new.items():
                if name in self.off_sheets:
                    self.off_sheets[name] = pd.concat([self.off_sheets[name], df], ignore_index=True)
                else:
                    self.off_sheets[name] = df

            self.on_sheet_selector.clear()
            self.on_sheet_selector.addItems(self.on_sheets.keys())
            
            self.off_sheet_selector.clear()
            self.off_sheet_selector.addItems(self.off_sheets.keys())
            
            if self.on_sheets:
                self.show_sheet(self.on_sheets[self.on_sheet_selector.currentText()], self.on_table_view)
            if self.off_sheets:
                self.show_sheet(self.off_sheets[self.off_sheet_selector.currentText()], self.off_table_view)
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al procesar el archivo: {e}")

    def save_tripulantes_to_db(self):
        # Inicia una sesión de la base de datos
        session = SessionLocal()
        try:
            # Procesar las hojas ON
            for sheet_name, df in self.on_sheets.items():
                for _, row in df.iterrows():
                    nave = session.query(Buque).filter_by(nombre=row['Vessel']).first()
                    if nave:
                        tripulante = Tripulante(
                            nombre=row['First name'],
                            apellido=row['Last name'],
                            sexo=row['Gender'],
                            nacionalidad=row['Nationality'],
                            pasaporte=row['Passport number'],
                            fecha_nacimiento=pd.to_datetime(row['Date of birth']).date(),
                            buque_id=nave.buque_id,
                            estado="ON"
                        )
                        session.add(tripulante)

            # Procesar las hojas OFF
            for sheet_name, df in self.off_sheets.items():
                for _, row in df.iterrows():
                    nave = session.query(Buque).filter_by(nombre=row['Vessel']).first()
                    if nave:
                        tripulante = Tripulante(
                            nombre=row['First name'],
                            apellido=row['Last name'],
                            sexo=row['Gender'],
                            nacionalidad=row['Nationality'],
                            pasaporte=row['Passport number'],
                            fecha_nacimiento=pd.to_datetime(row['Date of birth']).date(),
                            buque_id=nave.buque_id,
                            estado="OFF"
                        )
                        session.add(tripulante)

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def load_data_from_db(self):
        try:
            conn = sqlite3.connect("shacketons_db.sqlite3")
            query_on = "SELECT * FROM tripulantes WHERE estado = 'ON';"
            query_off = "SELECT * FROM tripulantes WHERE estado = 'OFF';"

            df_on = pd.read_sql(query_on, conn)
            df_off = pd.read_sql(query_off, conn)

            conn.close()

            if not df_on.empty:
                self.on_sheets["Datos desde DB"] = df_on
                self.show_sheet(df_on, self.on_table_view)
                self.on_sheet_selector.addItem("Datos desde DB")

            if not df_off.empty:
                self.off_sheets["Datos desde DB"] = df_off
                self.show_sheet(df_off, self.off_table_view)
                self.off_sheet_selector.addItem("Datos desde DB")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar datos desde la base de datos: {e}")

    def show_sheet(self, df, table_view):
        model = PandasModel(df)
        table_view.setModel(model)

    def change_on_sheet(self):
        sheet_name = self.on_sheet_selector.currentText()
        if sheet_name and sheet_name in self.on_sheets:
            self.show_sheet(self.on_sheets[sheet_name], self.on_table_view)

    def change_off_sheet(self):
        sheet_name = self.off_sheet_selector.currentText()
        if sheet_name and sheet_name in self.off_sheets:
            self.show_sheet(self.off_sheets[sheet_name], self.off_table_view)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BasicApp()
    window.show()
    sys.exit(app.exec())
