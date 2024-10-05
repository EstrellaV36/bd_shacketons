from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget, QComboBox, QTableView, QSizePolicy, QMessageBox, QFileDialog
from PyQt6.QtCore import Qt
from app.interfaz.pandas_model import PandasModel
from app.controllers import Controller
from app.database import get_db_session

class CargaMasivaScreen(QWidget):
    def __init__(self, controller, main_window):
        super().__init__()

        db_session = get_db_session()
        self.controller = Controller(db_session)
        
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Botón "Volver" al menú principal
        button_volver = QPushButton("Volver")
        button_volver.setFixedWidth(100)
        button_volver.clicked.connect(lambda: self.main_window.stacked_widget.setCurrentIndex(0))
        layout.addWidget(button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        self.button_load = QPushButton("Cargar Excel")
        self.button_load.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.button_load.clicked.connect(self.load_excel_file)
        layout.addWidget(self.button_load)

        self.button_add_row = QPushButton("Agregar Fila Vacía")
        self.button_add_row.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.button_add_row.clicked.connect(self.add_empty_row)
        layout.addWidget(self.button_add_row)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.on_tab = QWidget()
        self.off_tab = QWidget()
        
        self.tabs.addTab(self.on_tab, "ON")
        self.tabs.addTab(self.off_tab, "OFF")

        # Layouts horizontales para tener buques y tripulantes uno al lado del otro
        self.on_layout = QHBoxLayout()
        self.off_layout = QHBoxLayout()
        
        self.on_tab.setLayout(self.on_layout)
        self.off_tab.setLayout(self.off_layout)

        # Tablas para buques y tripulantes ON
        self.eta_on_buque_table_view = QTableView()  # Tabla para buques ON
        self.eta_on_tripulante_table_view = QTableView()  # Tabla para tripulantes ON
        self.on_layout.addWidget(self.eta_on_buque_table_view)
        self.on_layout.addWidget(self.eta_on_tripulante_table_view)

        # Tablas para buques y tripulantes OFF
        self.eta_off_buque_table_view = QTableView()  # Tabla para buques OFF
        self.eta_off_tripulante_table_view = QTableView()  # Tabla para tripulantes OFF
        self.off_layout.addWidget(self.eta_off_buque_table_view)
        self.off_layout.addWidget(self.eta_off_tripulante_table_view)

        self.on_sheets = {}
        self.off_sheets = {}

        self.button_save_changes = QPushButton("Guardar Cambios")
        self.button_save_changes.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.button_save_changes.clicked.connect(self.save_changes)
        layout.addWidget(self.button_save_changes)

    def load_excel_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Archivos Excel (*.xlsx *.xls)")
        file_dialog.setViewMode(QFileDialog.ViewMode.List)

        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                file_path = file_paths[0]
                
                # Procesar el archivo Excel y obtener los DataFrames
                buque_on, buque_off, tripulantes_on, tripulantes_off = self.controller.process_excel_file(file_path)
                
                # Mostrar los DataFrames en las tablas correspondientes
                self.show_sheet(buque_on, self.eta_on_buque_table_view)   # Mostrar buques ON
                self.show_sheet(tripulantes_on, self.eta_on_tripulante_table_view)  # Mostrar tripulantes ON
                
                self.show_sheet(buque_off, self.eta_off_buque_table_view)  # Mostrar buques OFF
                self.show_sheet(tripulantes_off, self.eta_off_tripulante_table_view)  # Mostrar tripulantes OFF

    def show_sheet(self, df, table_view):
        model = PandasModel(df)
        table_view.setModel(model)
        table_view.resizeColumnsToContents()

    def add_empty_row(self):
        current_index = self.tabs.currentIndex()
        model = None
        
        if current_index == 0:
            model = self.eta_on_buque_table_view.model()
        elif current_index == 1:
            model = self.eta_off_buque_table_view.model()
        
        if isinstance(model, PandasModel):
            model.add_empty_row()

    def save_changes(self):
        try:
            model_on_buque = self.eta_on_buque_table_view.model()
            model_on_tripulante = self.eta_on_tripulante_table_view.model()
            model_off_buque = self.eta_off_buque_table_view.model()
            model_off_tripulante = self.eta_off_tripulante_table_view.model()

            df_on_buque = model_on_buque.get_dataframe() if isinstance(model_on_buque, PandasModel) else None
            df_on_tripulante = model_on_tripulante.get_dataframe() if isinstance(model_on_tripulante, PandasModel) else None
            df_off_buque = model_off_buque.get_dataframe() if isinstance(model_off_buque, PandasModel) else None
            df_off_tripulante = model_off_tripulante.get_dataframe() if isinstance(model_off_tripulante, PandasModel) else None

            self.controller.save_tripulantes_to_db(df_on_buque, df_on_tripulante, df_off_buque, df_off_tripulante)
            QMessageBox.information(self, "Éxito", "Datos guardados correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar los datos: {e}")