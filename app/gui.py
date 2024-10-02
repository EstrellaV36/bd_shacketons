# app/gui.py
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QTabWidget, QWidget, QHBoxLayout, QVBoxLayout,
    QSizePolicy, QFileDialog, QMessageBox, QTableView, QComboBox, QStackedWidget, QListWidget, QLabel, QDateEdit
)
from PyQt6.QtCore import QAbstractTableModel, Qt, QRect, QPropertyAnimation, QEasingCurve, QEvent, QDate
from app.controllers import Controller  # Import the controller
from app.database import get_db_session  # Importa la función para obtener la sesión

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
            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                return str(self._df.iloc[index.row(), index.column()]) if not pd.isna(self._df.iloc[index.row(), index.column()]) else ""
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if index.isValid() and role == Qt.ItemDataRole.EditRole:
            try:
                # Intenta convertir el valor ingresado al tipo adecuado para la columna
                dtype = self._df.iloc[:, index.column()].dtype
                if pd.api.types.is_numeric_dtype(dtype):
                    value = float(value)  # Convertir a número si la columna es numérica
                self._df.iat[index.row(), index.column()] = value
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
                return True
            except ValueError:
                # Manejar el caso donde la conversión falla
                print("Error: El valor ingresado no es válido para esta columna.")
                return False
        return False

    def flags(self, index):
        if index.isValid():
            return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
        return Qt.ItemFlag.NoItemFlags

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._df.columns[section]
            if orientation == Qt.Orientation.Vertical:
                return str(self._df.index[section])
    
    def add_empty_row(self):
        # Añadir una fila vacía al DataFrame
        empty_row = pd.Series([None] * self._df.shape[1], index=self._df.columns)
        self._df = pd.concat([self._df, pd.DataFrame([empty_row])], ignore_index=True)
        self.layoutChanged.emit()  # Notificar a la vista que el modelo cambió

    def get_dataframe(self):
        # Retornar el DataFrame actual
        return self._df

class BasicApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión Crew Shacketon's Way")
        self.setGeometry(100, 100, 1000, 800)
        
        db_session = get_db_session()
        self.controller = Controller(db_session)  # Instantiate the controller

        # UI setup methods
        self.setup_ui()
        self.create_pasajeros_screen()
        self.create_generic_screen("Hotel")
        self.create_generic_screen("Transporte")
        self.create_generic_screen("Restaurant")
        self.create_floating_menu()

        self.installEventFilter(self)
        self.load_existing_data() #Para cargar datos iniciales. No es necesario

    def setup_ui(self):
        # Setting up the central widget and layouts
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        button_layout = QHBoxLayout()

        self.button_toggle_menu = QPushButton("Menú")
        self.button_toggle_menu.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.button_toggle_menu.clicked.connect(self.toggle_menu)
        button_layout.addWidget(self.button_toggle_menu)

        self.city_combo_box = QComboBox()
        self.city_combo_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.city_combo_box.addItems(self.controller.get_city_list())
        self.city_combo_box.currentIndexChanged.connect(self.city_selected)  # Conexión a city_selected        
        button_layout.addWidget(self.city_combo_box)

        # Agregar los campos de selección de rango de fecha
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")  # Formato de la fecha
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1))  # Fecha inicial por defecto (1 mes atrás)

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit.setDate(QDate.currentDate())  # Fecha final por defecto (hoy)

        # Conectar los cambios de fecha a la función que recarga los datos
        self.start_date_edit.dateChanged.connect(self.reload_data_on_date_change)
        self.end_date_edit.dateChanged.connect(self.reload_data_on_date_change)

        button_layout.addWidget(QLabel("Fecha inicio"))
        button_layout.addWidget(self.start_date_edit)

        button_layout.addWidget(QLabel("Fecha fin"))
        button_layout.addWidget(self.end_date_edit)

        main_layout.addLayout(button_layout)
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

    def reload_data_on_date_change(self):
        # Limpiar las tablas y recargar los datos con el nuevo rango de fechas
        self.eta_on_table_view.setModel(None)  # Limpia el modelo de la tabla "ON"
        self.eta_off_table_view.setModel(None)  # Limpia el modelo de la tabla "OFF"
        self.load_existing_data()  # Cargar los datos con el rango de fechas actualizado

    def create_pasajeros_screen(self):
        # Crear la pantalla "Pasajeros"
        pasajeros_widget = QWidget()
        layout = QVBoxLayout(pasajeros_widget)

        # Crear el botón para cargar el Excel
        self.button_load = QPushButton("Cargar Excel")
        self.button_load.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.button_load.clicked.connect(self.load_excel_file)
        layout.addWidget(self.button_load)

        # Crear el botón para agregar una fila vacía
        self.button_add_row = QPushButton("Agregar Fila Vacía")
        self.button_add_row.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.button_add_row.clicked.connect(self.add_empty_row)
        layout.addWidget(self.button_add_row)

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
        self.on_sheet_selector = QComboBox()  # Definir on_sheet_selector correctamente
        self.off_sheet_selector = QComboBox()  # Definir off_sheet_selector correctamente

        # Conectar la selección del combo box al método para cambiar de hoja
        self.on_sheet_selector.currentIndexChanged.connect(self.change_on_sheet)
        self.off_sheet_selector.currentIndexChanged.connect(self.change_off_sheet)

        # Añadir los combo boxes al layout
        self.on_layout.addWidget(self.on_sheet_selector)
        self.off_layout.addWidget(self.off_sheet_selector)

        # Crear un QTableView para las ETAs
        self.eta_on_table_view = QTableView()
        self.eta_off_table_view = QTableView()
        self.on_layout.addWidget(self.eta_on_table_view)  # Agregar a la pestaña "ON"
        self.off_layout.addWidget(self.eta_off_table_view)  # Agregar a la pestaña "OFF"

        # Variables para almacenar los DataFrames de las hojas "on" y "off"
        self.on_sheets = {}
        self.off_sheets = {}

        # Agregar la pantalla "Pasajeros" al stacked widget
        self.stacked_widget.addWidget(pasajeros_widget)

        # Crear un botón para guardar los cambios
        self.button_save_changes = QPushButton("Guardar Cambios")
        self.button_save_changes.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.button_save_changes.clicked.connect(self.save_changes)
        layout.addWidget(self.button_save_changes)

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
        try:
            self.on_sheets, self.off_sheets = self.controller.process_excel_file(file_path)

            # Actualizar los combo boxes con los nombres de las hojas
            self.update_sheet_selectors()

            # Mostrar la primera hoja en los QTableViews
            if self.on_sheets:
                first_on_sheet = next(iter(self.on_sheets))
                self.show_sheet(self.on_sheets[first_on_sheet], self.eta_on_table_view)

            if self.off_sheets:
                first_off_sheet = next(iter(self.off_sheets))
                self.show_sheet(self.off_sheets[first_off_sheet], self.eta_off_table_view)

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
            self.show_sheet(self.on_sheets[self.on_sheet_selector.currentText()], self.eta_on_table_view)
        if self.off_sheets:
            self.show_sheet(self.off_sheets[self.off_sheet_selector.currentText()], self.eta_off_table_view)

    def show_sheet(self, df, table_view):
        model = PandasModel(df)
        table_view.setModel(model)
        table_view.resizeColumnsToContents()

    def change_on_sheet(self):
        sheet_name = self.on_sheet_selector.currentText()
        if sheet_name:
            self.show_sheet(self.on_sheets[sheet_name], self.eta_on_table_view)

    def change_off_sheet(self):
        sheet_name = self.off_sheet_selector.currentText()
        if sheet_name:
            self.show_sheet(self.off_sheets[sheet_name], self.eta_off_table_view)

    def city_selected(self):
        print("Ciudad seleccionada: ", self.city_combo_box.currentText())  # Verifica qué ciudad se seleccionó
        self.load_existing_data()  # Carga los datos existentes basados en la ciudad seleccionada

    def clear_tripulantes_display(self):
        # Aquí puedes limpiar la visualización anterior, por ejemplo:
        for i in reversed(range(self.stacked_widget.count())): 
            self.stacked_widget.itemAt(i).widget().deleteLater()

    def load_existing_data(self):
        print("Cambiando ciudad")  # Verifica si este mensaje se imprime
        selected_city = self.city_combo_box.currentText()  # Obtén la ciudad seleccionada del combo box

        # Limpiar las tablas antes de cargar nuevos datos
        self.eta_on_table_view.setModel(None)  # Limpia el modelo de la tabla "ON"
        self.eta_off_table_view.setModel(None)  # Limpia el modelo de la tabla "OFF"

        # Load existing data using the controller
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")

        eta_vuelo_df_on, eta_vuelo_df_off = self.controller.load_existing_data(selected_city, start_date, end_date)

        
        # Mostrar vuelos y ETAs para tripulantes 'ON'
        if eta_vuelo_df_on is not None and not eta_vuelo_df_on.empty:
            self.show_sheet(eta_vuelo_df_on, self.eta_on_table_view)  # Mostrar en el QTableView para ETA ON
                
        # Mostrar vuelos y ETAs para tripulantes 'OFF'
        if eta_vuelo_df_off is not None and not eta_vuelo_df_off.empty:
            self.show_sheet(eta_vuelo_df_off, self.eta_off_table_view)  # Mostrar en el QTableView para ETA OFF

        # Imprimir los dataframes generados
        print(f"DataFrame de tripulantes 'ON':\n{eta_vuelo_df_on}")
        print(f"DataFrame de tripulantes 'OFF':\n{eta_vuelo_df_off}")

    def save_changes(self):
        try:
            # Obtener el modelo de las tablas "ON" y "OFF"
            model_on = self.eta_on_table_view.model()
            model_off = self.eta_off_table_view.model()

            # Obtener los DataFrames actualizados desde el modelo
            df_on = model_on.get_dataframe() if isinstance(model_on, PandasModel) else None
            df_off = model_off.get_dataframe() if isinstance(model_off, PandasModel) else None

            # Pasar los DataFrames al controlador para guardar los datos en la base de datos
            self.controller.save_tripulantes_to_db(df_on, df_off)
            
            QMessageBox.information(self, "Éxito", "Datos guardados correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar los datos: {e}")

    def add_empty_row(self):
        # Obtener la pestaña actual ("ON" o "OFF")
        current_index = self.tabs.currentIndex()
        model = None
        
        if current_index == 0:
            # Pestaña "ON"
            model = self.eta_on_table_view.model()
        elif current_index == 1:
            # Pestaña "OFF"
            model = self.eta_off_table_view.model()
        
        if isinstance(model, PandasModel):
            # Añadir una fila vacía al modelo
            model.add_empty_row()

