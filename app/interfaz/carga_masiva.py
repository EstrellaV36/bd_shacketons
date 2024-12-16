import os
import json
from openpyxl import load_workbook
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTabWidget, QTableView, QSizePolicy, QFileDialog, QProgressBar, QDialog
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from app.interfaz.pandas_model import PandasModel
from app.controller.controllers import Controller
from app.database import get_db_session


class CargaMasivaScreen(QWidget):
    def __init__(self, controller, main_window):
        super().__init__()

        self.controller = controller
        self.main_window = main_window
        self.excel_format_manager = ExcelFormatManager()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

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

        self.layout_on_table = QVBoxLayout()
        self.layout_off_table = QVBoxLayout()

        self.on_tab.setLayout(self.layout_on_table)
        self.off_tab.setLayout(self.layout_off_table)

        self.on_table_view = QTableView()
        self.off_table_view = QTableView()

        self.layout_on_table.addWidget(self.on_table_view)
        self.layout_off_table.addWidget(self.off_table_view)

    def load_excel_file(self):
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

                # Cargar el archivo sin modificarlo
                self.start_excel_processing(file_path)

    def start_excel_processing(self, file_path):
        # Crear diálogo de progreso
        self.progress_dialog = QDialog(self)
        self.progress_dialog.setWindowTitle("Cargando archivo Excel...")
        progress_layout = QVBoxLayout(self.progress_dialog)
        self.progress_bar = QProgressBar(self.progress_dialog)
        self.progress_bar.setRange(0, 100)
        progress_layout.addWidget(self.progress_bar)
        self.progress_dialog.setLayout(progress_layout)
        self.progress_dialog.show()

        self.load_thread = LoadExcelThread(self.controller, file_path)
        self.load_thread.update_progress.connect(self.update_progress_bar)
        self.load_thread.finished.connect(self.on_load_finished)
        self.load_thread.start()

    def update_progress_bar(self, progress_value):
        self.progress_bar.setValue(progress_value)

    def on_load_finished(self):
        self.progress_dialog.accept()
        print("Carga completada. El archivo se procesó correctamente.")

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


class LoadExcelThread(QThread):
    update_progress = pyqtSignal(int)

    def __init__(self, controller, file_path):
        super().__init__()
        self.controller = controller
        self.file_path = file_path

    def run(self):
        self.controller.process_excel_file(self.file_path, self.update_progress.emit)
