from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget, QComboBox, QTableView, QSizePolicy, QMessageBox, QFileDialog, QProgressBar, QDialog
from PyQt6.QtCore import Qt, QThread, pyqtSignal
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

    def load_excel_file(self):
        # Crear y mostrar el diálogo de progreso
        self.progress_dialog = QDialog(self)
        self.progress_dialog.setWindowTitle("Cargando archivo Excel...")
        progress_layout = QVBoxLayout(self.progress_dialog)
        self.progress_bar = QProgressBar(self.progress_dialog)
        self.progress_bar.setRange(0, 100)
        progress_layout.addWidget(self.progress_bar)
        self.progress_dialog.setLayout(progress_layout)
        self.progress_dialog.show()

        # Crear el diálogo de selección de archivos
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Archivos Excel (*.xlsx *.xls)")
        file_dialog.setViewMode(QFileDialog.ViewMode.List)

        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                file_path = file_paths[0]
                
                # Crear el hilo para la carga masiva y pasar el file_path
                self.load_thread = LoadExcelThread(self.controller, file_path)
                
                # Conectar las señales
                self.load_thread.update_progress.connect(self.update_progress_bar)
                self.load_thread.update_tables.connect(self.update_tables)  # Conectar la señal de actualización de tablas
                self.load_thread.finished.connect(self.on_load_finished)
                self.load_thread.start()

    def update_progress_bar(self, progress_value):
        self.progress_bar.setValue(progress_value)

    def update_tables(self, buque_on, buque_off, tripulantes_on, tripulantes_off):
        # Actualizar las tablas en la interfaz
        self.show_sheet(buque_on, self.eta_on_buque_table_view)
        self.show_sheet(tripulantes_on, self.eta_on_tripulante_table_view)
        self.show_sheet(buque_off, self.eta_off_buque_table_view)
        self.show_sheet(tripulantes_off, self.eta_off_tripulante_table_view)

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

    def on_load_finished(self):
        self.progress_dialog.accept()  # Cerrar el diálogo de progreso

class LoadExcelThread(QThread):
    update_progress = pyqtSignal(int)
    update_tables = pyqtSignal(object, object, object, object)

    def __init__(self, controller, file_path):
        super().__init__()
        self.controller = controller
        self.file_path = file_path

    def run(self):
        try:
            # Abre y lee el archivo Excel
            buque_on, buque_off, tripulantes_on, tripulantes_off = None, None, None, None

            # Pasar la función de actualización de progreso al Controller
            def update_progress_callback(progress):
                self.update_progress.emit(progress)

            # Llamar a `process_excel_file` con la función de progreso
            buque_on, buque_off, tripulantes_on, tripulantes_off = self.controller.process_excel_file(self.file_path, update_progress_callback)

            # Emitir las señales para actualizar las tablas
            self.update_tables.emit(buque_on, buque_off, tripulantes_on, tripulantes_off)

        except Exception as e:
            print(f"Error al procesar el archivo: {e}")

    def emit_signal(self, buque_on, buque_off, tripulantes_on, tripulantes_off):
        # Emitir la señal para actualizar las tablas
        self.update_progress.emit(100)  # Indicar que la carga ha terminado
        # Aquí se puede invocar la actualización de las vistas de las tablas
        self.controller.show_sheet(buque_on, self.controller.eta_on_buque_table_view)
        self.controller.show_sheet(tripulantes_on, self.controller.eta_on_tripulante_table_view)
        self.controller.show_sheet(buque_off, self.controller.eta_off_buque_table_view)
        self.controller.show_sheet(tripulantes_off, self.controller.eta_off_tripulante_table_view)
