import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QTabWidget, QWidget, QHBoxLayout, QVBoxLayout, QSizePolicy, QFileDialog, QMessageBox, QTableView, QComboBox, QStackedWidget, QListWidget, QLabel
)
from PyQt6.QtCore import QAbstractTableModel, Qt, QRect, QPropertyAnimation, QEasingCurve, QEvent
import pandas as pd
import sys
from database import SessionLocal, engine  # Importar el motor de base de datos
from models import Buque, Tripulante, Base  # Importar tus modelos y la clase Base

# Crear las tablas si no existen
Base.metadata.create_all(engine)

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
        self.setWindowTitle("Gestión Crew Shacketon's Way")
        self.setGeometry(100, 100, 1000, 800)  # x, y, width, height
        
        # Crear un widget central y establecer el diseño
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Crear un diseño vertical
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Crear un diseño horizontal para los botones y combo box
        button_layout = QHBoxLayout()
        
        # Crear un botón para mostrar/ocultar el menú
        self.button_toggle_menu = QPushButton("Mostrar/Ocultar Menú")
        self.button_toggle_menu.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.button_toggle_menu.clicked.connect(self.toggle_menu)

        button_layout.addWidget(self.button_toggle_menu)
        
        # Agregar el diseño de los botones al diseño principal
        main_layout.addLayout(button_layout)

        # Crear un QStackedWidget para cambiar entre las pantallas
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Crear las diferentes pantallas
        self.create_pasajeros_screen()
        self.create_generic_screen("Hotel")
        self.create_generic_screen("Transporte")
        self.create_generic_screen("Restaurant")

        # Crear el menú flotante
        self.create_floating_menu()

        # Instalar un filtro de eventos para capturar clics fuera del menú
        self.installEventFilter(self)
        self.load_existing_data()  # Aquí se cargan los tripulantes de la BD al iniciar la app

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
            
            # Filtrar las hojas que terminan en "ON" o "OFF" por separado
            self.on_sheets = {
                name: df for name, df in excel_data.items()
                if re.search(r'\bON\b$', name, re.IGNORECASE)
            }
            self.off_sheets = {
                name: df for name, df in excel_data.items()
                if re.search(r'\bOFF\b$', name, re.IGNORECASE)
            }
            
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

            self.save_tripulantes_to_db()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al procesar el archivo: {e}")

    def load_existing_data(self):
        session = SessionLocal()
        try:
            # Cargar los tripulantes ON desde la base de datos
            tripulantes_on = session.query(Tripulante).filter_by(estado='ON').all()
            df_on = pd.DataFrame([{
                'Vessel': trip.buque.nombre,
                'First name': trip.nombre,
                'Last name': trip.apellido,
                'Gender': trip.sexo,
                'Nationality': trip.nacionalidad,
                'Passport number': trip.pasaporte,
                'Date of birth': trip.fecha_nacimiento
            } for trip in tripulantes_on])
            
            if not df_on.empty:
                self.show_sheet(df_on, self.on_table_view)

            # Cargar los tripulantes OFF desde la base de datos
            tripulantes_off = session.query(Tripulante).filter_by(estado='OFF').all()
            df_off = pd.DataFrame([{
                'Vessel': trip.buque.nombre,
                'First name': trip.nombre,
                'Last name': trip.apellido,
                'Gender': trip.sexo,
                'Nationality': trip.nacionalidad,
                'Passport number': trip.pasaporte,
                'Date of birth': trip.fecha_nacimiento
            } for trip in tripulantes_off])

            if not df_off.empty:
                self.show_sheet(df_off, self.off_table_view)

        except Exception as e:
            print(f"Error al cargar datos existentes: {e}")
        finally:
            session.close()

    def save_tripulantes_to_db(self):
        # Inicia una sesión de la base de datos
        session = SessionLocal()
        try:
            # Procesar la hoja ON
            df_on = self.on_sheets.get('Pasajeros y Pasaportes ON', None)
            if df_on is not None:
                for _, row in df_on.iterrows():
                    if pd.isna(row['Vessel']) or pd.isna(row['First name']) or pd.isna(row['Last name']):
                        # Si falta algún dato clave, se omite este registro
                        continue

                    # Buscar la nave en la base de datos
                    nave = session.query(Buque).filter_by(nombre=row['Vessel']).first()

                    # Si la nave no existe, crearla
                    if not nave:
                        nave = Buque(
                            nombre=row['Vessel'],
                            compañia="Compañía Desconocida"
                        )
                        session.add(nave)
                        session.commit()

                    # Buscar el tripulante por pasaporte
                    tripulante = session.query(Tripulante).filter_by(pasaporte=row['Passport number']).first()

                    if tripulante:
                        # Si el tripulante ya existe, actualizar los datos
                        tripulante.nombre = row['First name']
                        tripulante.apellido = row['Last name']
                        tripulante.sexo = row['Gender'] if not pd.isna(row['Gender']) else None
                        tripulante.nacionalidad = row['Nationality'] if not pd.isna(row['Nationality']) else None
                        tripulante.fecha_nacimiento = pd.to_datetime(row['Date of birth']).date() if not pd.isna(row['Date of birth']) else None
                        tripulante.buque_id = nave.buque_id
                        tripulante.estado = 'ON'  # Marca el tripulante como ON
                        print(f"Tripulante {tripulante.nombre} actualizado")
                    else:
                        # Si el tripulante no existe, crear uno nuevo
                        try:
                            tripulante = Tripulante(
                                nombre=row['First name'],
                                apellido=row['Last name'],
                                sexo=row['Gender'] if not pd.isna(row['Gender']) else None,
                                nacionalidad=row['Nationality'] if not pd.isna(row['Nationality']) else None,
                                pasaporte=row['Passport number'] if not pd.isna(row['Passport number']) else None,
                                fecha_nacimiento=pd.to_datetime(row['Date of birth']).date() if not pd.isna(row['Date of birth']) else None,
                                buque_id=nave.buque_id,
                                estado='ON'  # Marca el tripulante como ON
                            )
                            session.add(tripulante)
                            print(f"Tripulante {tripulante.nombre} agregado")
                        except Exception as e:
                            print(f"Error al agregar tripulante ON: {e}")

            # Procesar la hoja OFF
            df_off = self.off_sheets.get('Pasajeros y Pasaportes OFF', None)
            if df_off is not None:
                for _, row in df_off.iterrows():
                    if pd.isna(row['Vessel']) or pd.isna(row['First name']) or pd.isna(row['Last name']):
                        # Si falta algún dato clave, se omite este registro
                        continue

                    # Buscar la nave en la base de datos
                    nave = session.query(Buque).filter_by(nombre=row['Vessel']).first()

                    # Si la nave no existe, crearla
                    if not nave:
                        nave = Buque(
                            nombre=row['Vessel'],
                            compañia="Compañía Desconocida"
                        )
                        session.add(nave)
                        session.commit()

                    # Buscar el tripulante por pasaporte
                    tripulante = session.query(Tripulante).filter_by(pasaporte=row['Passport number']).first()

                    if tripulante:
                        # Si el tripulante ya existe, actualizar los datos
                        tripulante.nombre = row['First name']
                        tripulante.apellido = row['Last name']
                        tripulante.sexo = row['Gender'] if not pd.isna(row['Gender']) else None
                        tripulante.nacionalidad = row['Nationality'] if not pd.isna(row['Nationality']) else None
                        tripulante.fecha_nacimiento = pd.to_datetime(row['Date of birth']).date() if not pd.isna(row['Date of birth']) else None
                        tripulante.buque_id = nave.buque_id
                        tripulante.estado = 'OFF'  # Marca el tripulante como OFF
                        print(f"Tripulante {tripulante.nombre} actualizado")
                    else:
                        # Si el tripulante no existe, crear uno nuevo
                        try:
                            tripulante = Tripulante(
                                nombre=row['First name'],
                                apellido=row['Last name'],
                                sexo=row['Gender'] if not pd.isna(row['Gender']) else None,
                                nacionalidad=row['Nationality'] if not pd.isna(row['Nationality']) else None,
                                pasaporte=row['Passport number'] if not pd.isna(row['Passport number']) else None,
                                fecha_nacimiento=pd.to_datetime(row['Date of birth']).date() if not pd.isna(row['Date of birth']) else None,
                                buque_id=nave.buque_id,
                                estado='OFF'  # Marca el tripulante como OFF
                            )
                            session.add(tripulante)
                            print(f"Tripulante {tripulante.nombre} agregado")
                        except Exception as e:
                            print(f"Error al agregar tripulante OFF: {e}")

            # Confirmar los cambios en la base de datos
            session.commit()

        except Exception as e:
            print(f"Error al guardar en la base de datos: {e}")
            session.rollback()

        finally:
            session.close()


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
