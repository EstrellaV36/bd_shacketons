from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget, QComboBox, QTableView, QSizePolicy, QMessageBox, QFileDialog, QProgressBar, QDialog, QLabel
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from app.interfaz.pandas_model import PandasModel
from app.controller.controllers import Controller
from app.database import get_db_session
import pandas as pd
from openpyxl import load_workbook
import json
import os

class CargaMasivaScreen(QWidget):
    def __init__(self, controller, main_window):
        super().__init__()

        db_session = get_db_session()
        self.controller = Controller(db_session)
        self.excel_format_manager = ExcelFormatManager()
        
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Botón "Volver" al menú principal
        button_volver = QPushButton("Volver")
        button_volver.setStyleSheet("""
            font-size: 16px;  /* Tamaño de la letra */
            padding: 0px;    /* Elimina el espacio interno */
            line-height: 18px; /* Asegura que el texto no se corte verticalmente */
            text-align: center; /* Centra el texto */
        """)
        button_volver.setFixedWidth(80)
        button_volver.setFixedHeight(40)
        button_volver.clicked.connect(lambda: self.main_window.stacked_widget.setCurrentIndex(0))
        layout.addWidget(button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        # Label para mostrar asistencias
        self.label = QLabel("CARGA MASIVA")
        self.label.setStyleSheet("""
            font-size: 40px;  /* Tamaño de fuente */
            font-weight: bold; /* Negrita */
            color: #00272d;    /* Color del texto */
            text-align: center; /* Centrar el texto horizontalmente */
            margin-bottom: 20px; /* Espacio debajo del título */
        """)
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)  # Centrar el título

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.on_tab = QWidget()
        self.off_tab = QWidget()
        
        self.tabs.addTab(self.on_tab, "ON")
        self.tabs.addTab(self.off_tab, "OFF")

        self.button_load = QPushButton("Cargar Excel")
        self.button_load.setStyleSheet("""
            font-size: 18px;  /* Tamaño de la letra */
            padding: 0px;    /* Elimina el espacio interno */
            line-height: 18px; /* Asegura que el texto no se corte verticalmente */
            text-align: center; /* Centra el texto */
        """)
        self.button_load.setFixedHeight(45)
        self.button_load.setFixedWidth(245)
        self.button_load.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.button_load.clicked.connect(self.load_excel_file)
        layout.addWidget(self.button_load, alignment=Qt.AlignmentFlag.AlignRight)

        # Layout para la tabla en cada pestaña
        self.layout_on_table = QVBoxLayout()
        self.layout_off_table = QVBoxLayout()

        self.on_tab.setLayout(self.layout_on_table)
        self.off_tab.setLayout(self.layout_off_table)

        # Crear las tablas para cada pestaña
        self.on_table_view = QTableView()  # Tabla para los datos "ON"
        self.off_table_view = QTableView()  # Tabla para los datos "OFF"

        self.layout_on_table.addWidget(self.on_table_view)
        self.layout_off_table.addWidget(self.off_table_view)

    def load_excel_file(self):
        # Crear el diálogo de selección de archivos
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Archivos Excel (*.xlsx *.xls)")
        file_dialog.setViewMode(QFileDialog.ViewMode.List)

        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                file_path = file_paths[0]

                # Verificar y guardar estilos de encabezado si no existen
                if not os.path.exists("header_styles.json"):
                    self.excel_format_manager.save_header_styles(file_path)
                else:
                    print("Archivo de estilos de encabezado ya existe. Usando estilos guardados.")
                
                # Crear y mostrar el diálogo de progreso
                self.progress_dialog = QDialog(self)
                self.progress_dialog.setWindowTitle("Cargando archivo Excel...")
                progress_layout = QVBoxLayout(self.progress_dialog)
                self.progress_bar = QProgressBar(self.progress_dialog)
                self.progress_bar.setRange(0, 100)
                progress_layout.addWidget(self.progress_bar)
                self.progress_dialog.setLayout(progress_layout)
                self.progress_dialog.show()  # Mostrar el diálogo de progreso

                # Crear el hilo para la carga masiva y pasar el file_path
                self.load_thread = LoadExcelThread(self.controller, file_path)
                
                # Conectar las señales
                self.load_thread.update_progress.connect(self.update_progress_bar)
                self.load_thread.update_tables.connect(self.update_tables)  # Conectar la señal de actualización de la tabla
                self.load_thread.finished.connect(self.on_load_finished)
                self.load_thread.start()

    def update_progress_bar(self, progress_value):
        self.progress_bar.setValue(progress_value)

    def update_tables(self, buque_on, buque_off, tripulantes_on, tripulantes_off, errors_on, errors_off, errors_on_message, errors_off_message):
        # Convertir las columnas ETA y ETD a solo fecha, sin la hora
        buque_on['ETA Vessel'] = pd.to_datetime(buque_on['ETA Vessel']).dt.date
        buque_on['ETD Vessel'] = pd.to_datetime(buque_on['ETD Vessel']).dt.date
        buque_off['ETA Vessel'] = pd.to_datetime(buque_off['ETA Vessel']).dt.date
        buque_off['ETD Vessel'] = pd.to_datetime(buque_off['ETD Vessel']).dt.date
        tripulantes_on['DOB'] = pd.to_datetime(tripulantes_on['DOB']).dt.date
        tripulantes_off['DOB'] = pd.to_datetime(tripulantes_off['DOB']).dt.date

        # Actualiza la tabla de "ON"
        combined_on_df = pd.concat([buque_on, tripulantes_on], axis=1)
        self.show_sheet(combined_on_df, self.on_table_view, errors_on, errors_on_message)  # Mostrar en la pestaña "ON"
        
        # Actualiza la tabla de "OFF"
        combined_off_df = pd.concat([buque_off, tripulantes_off], axis=1)
        self.show_sheet(combined_off_df, self.off_table_view, errors_off, errors_off_message)  # Mostrar en la pestaña "OFF"

    def show_sheet(self, df, table_view, errors_df, errors_message_df):
        highlighted_rows = errors_df
        model = PandasModel(df, highlighted_rows)
        table_view.setModel(model)

        print(type(errors_message_df))

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

        # Mostrar errores si existen
        if errors_message_df:
            print("Entre al if de error")
            error_messages = "\n".join(errors_message_df)  # Combina los errores en texto separado por líneas
            error_box = QMessageBox(self)
            error_box.setIcon(QMessageBox.Icon.Warning)
            error_box.setWindowTitle("Errores en los datos")
            error_box.setText("Se encontraron los siguientes errores:")
            error_box.setDetailedText(error_messages)  # Mostrar los detalles con los errores específicos
            error_box.exec()

    def on_load_finished(self):
        self.progress_dialog.accept()

class LoadExcelThread(QThread):
    update_progress = pyqtSignal(int)
    update_tables = pyqtSignal(object, object, object, object, object, object, object, object)

    def __init__(self, controller, file_path):
        super().__init__()
        self.controller = controller
        self.file_path = file_path

    def run(self):
        try:
            buque_on, buque_off, tripulantes_on, tripulantes_off, errors_on, errors_off, errors_on_message, errors_off_message = None, None, None, None, None, None, None, None

            # Pasar la función de actualización de progreso al Controller
            def update_progress_callback(progress):
                self.update_progress.emit(progress)

            # Llamar a `process_excel_file` con la función de progreso
            buque_on, buque_off, tripulantes_on, tripulantes_off, errors_on, errors_off, errors_on_message, errors_off_message = self.controller.process_excel_file(self.file_path, update_progress_callback)

            # Emitir las señales para actualizar las tablas
            self.update_tables.emit(buque_on, buque_off, tripulantes_on, tripulantes_off, errors_on, errors_off, errors_on_message, errors_off_message)

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

class ExcelFormatManager:
    def __init__(self):
        self.header_styles = {}

    def save_header_styles(self, file_path):
        """
        Guarda los estilos de encabezados y otras propiedades del archivo Excel en un archivo JSON.
        """
        try:
            workbook = load_workbook(file_path)
            self.header_styles = {}

            # Iterar sobre todas las hojas en el libro
            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                sheet_header_styles = {}

                # Obtener los nombres de las columnas (suponiendo que la primera fila contiene los encabezados)
                column_names = [cell.value.strip() if cell.value else '' for cell in sheet[1]]  # Limpiar posibles espacios en blanco

                # Guardar las propiedades de las filas y columnas
                row_dimensions = {}
                column_dimensions = {}

                # Iterar sobre las columnas y guardar los estilos con los nombres de las columnas como claves
                for col, col_name in enumerate(column_names, start=1):
                    for cell in sheet.iter_cols(min_col=col, max_col=col, min_row=1, max_row=1):  # Solo la primera fila
                        for c in cell:
                            if col_name:  # Asegurarse de que el nombre de la columna no sea None
                                sheet_header_styles[col_name] = {
                                    "font": {
                                        "name": c.font.name,
                                        "size": c.font.size,
                                        "bold": c.font.bold,
                                        "italic": c.font.italic,
                                        "color": c.font.color.rgb if c.font.color else None,
                                    },
                                    "fill": {
                                        "color": c.fill.fgColor.rgb if c.fill.fgColor else None,
                                    },
                                    "border": {
                                        "top": c.border.top.style if c.border.top else None,
                                        "bottom": c.border.bottom.style if c.border.bottom else None,
                                        "left": c.border.left.style if c.border.left else None,
                                        "right": c.border.right.style if c.border.right else None,
                                    },
                                }

                    # Guardar tamaño de columna (ancho)
                    column_width = sheet.column_dimensions.get(col_name, {}).get('width', 20)  # Valor predeterminado si no se encuentra
                    column_dimensions[col_name] = column_width

                # Obtener las propiedades de las filas
                for row_num in range(1, sheet.max_row + 1):
                    row_dimensions[row_num] = sheet.row_dimensions[row_num].height if row_num in sheet.row_dimensions else None

                # Agregar al diccionario de estilos generales
                self.header_styles[sheet_name] = {
                    "styles": sheet_header_styles,
                    "row_dimensions": row_dimensions,
                    "column_dimensions": column_dimensions
                }

            # Guardar los estilos en un archivo JSON
            with open("header_styles.json", "w") as f:
                json.dump(self.header_styles, f, indent=4)
            print("Estilos de encabezado y otras propiedades guardadas exitosamente.")
        except Exception as e:
            print(f"Error al guardar estilos: {e}")