# app/gui.py
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QTabWidget, QWidget, QHBoxLayout, QVBoxLayout,
    QSizePolicy, QFileDialog, QMessageBox, QTableView, QComboBox, QStackedWidget, QListWidget, QLabel
)
from PyQt6.QtCore import QAbstractTableModel, Qt, QRect, QPropertyAnimation, QEasingCurve, QEvent
from app.controllers import Controller  # Import the controller

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
            
class BasicApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión Crew Shacketon's Way")
        self.setGeometry(100, 100, 1000, 800)
        
        self.controller = Controller()  # Instantiate the controller

        # UI setup methods
        self.setup_ui()
        self.create_pasajeros_screen()
        self.create_generic_screen("Hotel")
        self.create_generic_screen("Transporte")
        self.create_generic_screen("Restaurant")
        self.create_floating_menu()

        self.installEventFilter(self)
        self.load_existing_data()  # This will call a method in the controller

    def setup_ui(self):
        # Setting up the central widget and layouts
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        button_layout = QHBoxLayout()
        
        self.button_toggle_menu = QPushButton("Mostrar/Ocultar Menú")
        self.button_toggle_menu.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.button_toggle_menu.clicked.connect(self.toggle_menu)
        button_layout.addWidget(self.button_toggle_menu)

        self.city_combo_box = QComboBox()
        self.city_combo_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.city_combo_box.addItems(self.controller.get_city_list())
        self.city_combo_box.currentIndexChanged.connect(self.city_selected)
        button_layout.addWidget(self.city_combo_box)
        
        main_layout.addLayout(button_layout)
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

    def create_pasajeros_screen(self):
        # Crear la pantalla "Pasajeros"
        pasajeros_widget = QWidget()
        layout = QVBoxLayout(pasajeros_widget)

        # Crear el botón para cargar el Excel
        self.button_load = QPushButton("Cargar Excel")
        self.button_load.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.button_load.clicked.connect(self.load_excel_file)
        
        layout.addWidget(self.button_load)

        # Crear un QTabWidget para las pestañas
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

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

        # Agregar la pantalla "Pasajeros" al stacked widget
        self.stacked_widget.addWidget(pasajeros_widget)

    def create_generic_screen(self, title):
        # Crear una pantalla genérica con solo un título
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel(title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        # Agregar la pantalla genérica al stacked widget
        self.stacked_widget.addWidget(widget)

    def create_floating_menu(self):
        # Crear el widget flotante
        self.menu_widget = QWidget(self)
        self.menu_widget.setGeometry(-250, 0, 250, self.height())  # Inicialmente fuera de la vista
        self.menu_widget.setStyleSheet("background-color: rgba(0, 0, 0, 0.8); color: white;")
        
        # Crear un layout vertical para el menú
        menu_layout = QVBoxLayout()
        self.menu_widget.setLayout(menu_layout)
        
        # Agregar opciones al menú
        self.menu_list = QListWidget()
        self.menu_list.addItems(["Pasajeros", "Hotel", "Transporte", "Restaurant"])
        self.menu_list.currentRowChanged.connect(self.change_tab)

        # Botón para cerrar el menú
        close_button = QPushButton("Cerrar Menú")
        close_button.clicked.connect(self.toggle_menu)

        # Agregar elementos al layout del menú
        menu_layout.addWidget(QLabel("Menú"))
        menu_layout.addWidget(self.menu_list)
        menu_layout.addWidget(close_button)

        # Inicialmente ocultar el menú
        self.menu_widget.hide()

    def toggle_menu(self):
        # Crear una animación para el menú
        if self.menu_widget.isVisible():
            # Animación para ocultar el menú
            self.animation = QPropertyAnimation(self.menu_widget, b"geometry")
            self.animation.setDuration(500)
            self.animation.setStartValue(QRect(0, 0, 250, self.height()))
            self.animation.setEndValue(QRect(-250, 0, 250, self.height()))
            self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.animation.start()
            self.animation.finished.connect(lambda: self.menu_widget.hide())
            self.centralWidget().setEnabled(True)  # Habilitar la ventana principal
        else:
            # Mostrar el menú antes de iniciar la animación
            self.menu_widget.show()
            self.animation = QPropertyAnimation(self.menu_widget, b"geometry")
            self.animation.setDuration(500)
            self.animation.setStartValue(QRect(-250, 0, 250, self.height()))
            self.animation.setEndValue(QRect(0, 0, 250, self.height()))
            self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.animation.start()
            self.centralWidget().setEnabled(False)  # Deshabilitar la ventana principal

    def eventFilter(self, source, event):
        # Si el menú está visible y se hace clic fuera de él, se cierra
        if event.type() == QEvent.Type.MouseButtonPress and self.menu_widget.isVisible():
            # Convertir el rectángulo del menú a coordenadas globales
            menu_rect = self.menu_widget.rect()
            global_top_left = self.menu_widget.mapToGlobal(menu_rect.topLeft())
            global_bottom_right = self.menu_widget.mapToGlobal(menu_rect.bottomRight())
            global_menu_rect = QRect(global_top_left, global_bottom_right)
        
            if not global_menu_rect.contains(event.globalPosition().toPoint()):
                self.toggle_menu()
                return True
        return super().eventFilter(source, event)

    def change_tab(self, index):
        # Cambiar la pantalla según la selección del menú
        self.stacked_widget.setCurrentIndex(index)

    def load_excel_file(self):
        # This method remains, but will call the controller
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
        # Delegate processing to the controller
        try:
            self.on_sheets, self.off_sheets = self.controller.process_excel_file(file_path)

            # Update the UI
            self.update_sheet_selectors()
            self.show_current_sheets()

            # Load data into the database
            self.controller.save_tripulantes_to_db(self.on_sheets, self.off_sheets)

            # Assign flights to tripulantes
            self.controller.assign_flights_to_tripulantes()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al procesar el archivo: {e}")

    def update_sheet_selectors(self):
        # Update the combo boxes with the sheet names
        self.on_sheet_selector.clear()
        self.on_sheet_selector.addItems(self.on_sheets.keys())
        self.off_sheet_selector.clear()
        self.off_sheet_selector.addItems(self.off_sheets.keys())

    def show_current_sheets(self):
        # Show the first sheets in the table views
        if self.on_sheets:
            self.show_sheet(self.on_sheets[self.on_sheet_selector.currentText()], self.on_table_view)
        if self.off_sheets:
            self.show_sheet(self.off_sheets[self.off_sheet_selector.currentText()], self.off_table_view)

    def show_sheet(self, df, table_view):
        model = PandasModel(df)
        table_view.setModel(model)

    def change_on_sheet(self):
        sheet_name = self.on_sheet_selector.currentText()
        if sheet_name:
            self.show_sheet(self.on_sheets[sheet_name], self.on_table_view)

    def change_off_sheet(self):
        sheet_name = self.off_sheet_selector.currentText()
        if sheet_name:
            self.show_sheet(self.off_sheets[sheet_name], self.off_table_view)

    def city_selected(self, index):
        city = self.city_combo_box.itemText(index)
        tripulantes = self.controller.get_tripulantes_by_city(city)
        # Update the UI with tripulantes information

    def load_existing_data(self):
        # Load existing data using the controller
        on_data, off_data = self.controller.load_existing_data()
        if on_data is not None:
            self.show_sheet(on_data, self.on_table_view)
        if off_data is not None:
            self.show_sheet(off_data, self.off_table_view)
