from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTabWidget, QComboBox, QTableView, QSizePolicy, QMessageBox, QFileDialog
from PyQt6.QtCore import Qt
from app.interfaz.pandas_model import PandasModel
from app.controllers import Controller

class CargaMasivaScreen(QWidget):
    def __init__(self, controller, main_window):
        super().__init__()
        self.controller = controller
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

        self.on_layout = QVBoxLayout()
        self.off_layout = QVBoxLayout()
        
        self.on_tab.setLayout(self.on_layout)
        self.off_tab.setLayout(self.off_layout)

        self.on_sheet_selector = QComboBox()
        self.off_sheet_selector = QComboBox()

        self.on_layout.addWidget(self.on_sheet_selector)
        self.off_layout.addWidget(self.off_sheet_selector)

        self.eta_on_table_view = QTableView()
        self.eta_off_table_view = QTableView()
        self.on_layout.addWidget(self.eta_on_table_view)
        self.off_layout.addWidget(self.eta_off_table_view)

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
                self.process_excel_file(file_path)
    
    def process_excel_file(self, file_path):
        try:
            self.on_sheets, self.off_sheets = self.controller.process_excel_file(file_path)
            self.update_sheet_selectors()

            if self.on_sheets:
                first_on_sheet = next(iter(self.on_sheets))
                self.show_sheet(self.on_sheets[first_on_sheet], self.eta_on_table_view)

            if self.off_sheets:
                first_off_sheet = next(iter(self.off_sheets))
                self.show_sheet(self.off_sheets[first_off_sheet], self.eta_off_table_view)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al procesar el archivo: {e}")

    def show_sheet(self, df, table_view):
        model = PandasModel(df)
        table_view.setModel(model)
        table_view.resizeColumnsToContents()

    def update_sheet_selectors(self):
        self.on_sheet_selector.clear()
        self.on_sheet_selector.addItems(self.on_sheets.keys())
        self.off_sheet_selector.clear()
        self.off_sheet_selector.addItems(self.off_sheets.keys())

    def add_empty_row(self):
        current_index = self.tabs.currentIndex()
        model = None
        
        if current_index == 0:
            model = self.eta_on_table_view.model()
        elif current_index == 1:
            model = self.eta_off_table_view.model()
        
        if isinstance(model, PandasModel):
            model.add_empty_row()

    def save_changes(self):
        try:
            model_on = self.eta_on_table_view.model()
            model_off = self.eta_off_table_view.model()

            df_on = model_on.get_dataframe() if isinstance(model_on, PandasModel) else None
            df_off = model_off.get_dataframe() if isinstance(model_off, PandasModel) else None

            self.controller.save_tripulantes_to_db(df_on, df_off)
            QMessageBox.information(self, "Éxito", "Datos guardados correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar los datos: {e}")
