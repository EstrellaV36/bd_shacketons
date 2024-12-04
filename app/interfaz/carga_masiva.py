from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget, QComboBox, QTableView, QSizePolicy, QMessageBox, QFileDialog
from PyQt6.QtCore import Qt
from app.interfaz.pandas_model import PandasModel
from app.controller.controllers import Controller
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
                #buque_on, buque_off, tripulantes_on, tripulantes_off = self.controller.process_excel_file(file_path)
                #self.controller.buques_on, self.controller.buques_off = self.controller.process_excel_file(file_path)
                self.controller.buques_on, self.controller.buques_off, self.controller.tripulantes_on, self.controller.tripulantes_off = self.controller.process_excel_file(file_path)

                #print(self.controller.tripulantes_on)
                
                # Mostrar los DataFrames en las tablas correspondientes
                self.show_sheet(self.controller.buques_on, self.eta_on_buque_table_view)   # Mostrar buques ON
                self.show_sheet(self.controller.tripulantes_on, self.eta_on_tripulante_table_view)  # Mostrar tripulantes ON
                
                self.show_sheet(self.controller.buques_off, self.eta_off_buque_table_view)  # Mostrar buques OFF
                self.show_sheet(self.controller.tripulantes_off, self.eta_off_tripulante_table_view)  # Mostrar tripulantes OFF

    def show_sheet(self, df, table_view):
        model = PandasModel(df)
        table_view.setModel(model)

        # Configura el estilo y formato del QTableView
        table_view.resizeColumnsToContents()  # Ajusta el ancho de las columnas
        table_view.setAlternatingRowColors(True)  # Alterna colores de filas
        table_view.setStyleSheet("""
            QTableView {
                gridline-color: #00272d;
                background-color: white;  /* Fondo blanco */
                alternate-background-color: #f9f9f9;  /* Fondo alternado */
                font-size: 14px;
                font-family: Arial, sans-serif;
                color: #00272d;  /* Color del texto */
                selection-background-color: #134647;  /* Fondo para filas seleccionadas */
                selection-color: white;  /* Texto de las filas seleccionadas */
            }
            QHeaderView::section {
                background-color: #134647;  /* Fondo del encabezado */
                color: white;  /* Color del texto del encabezado */
                font-size: 15px;
                font-weight: bold;
                border: 1px solid #134647;  /* Bordes del encabezado */
            }
        """)
        table_view.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)  # Deshabilita edición
        table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)  # Selección por filas
        table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)  # Solo permite seleccionar una fila