import re
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QSizePolicy, QFileDialog, QMessageBox, QTableView, QStackedWidget, QListWidget, QLabel
from PyQt6.QtCore import QAbstractTableModel, Qt, QRect, QPropertyAnimation, QEasingCurve, QEvent
import pandas as pd
import sys
from database import SessionLocal, engine
from models import Buque, Tripulante, Base, Vuelo, EtaCiudad, Hotel, Restaurante, Transporte  # Importar modelos y la clase Base

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
        
        # Crear un diseño vertical principal
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Botón para cargar Excel (permanecerá visible)
        self.button_load = QPushButton("Cargar Excel")
        self.button_load.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.button_load.clicked.connect(self.load_excel_file)
        main_layout.addWidget(self.button_load)

        # Crear el QStackedWidget para mostrar las vistas de cada categoría
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Crear botones ON y OFF para cada categoría (como Pasajeros, Hotel, etc.)
        self.create_category_widgets()

        # Crear el botón para mostrar/ocultar el menú
        self.button_toggle_menu = QPushButton("Mostrar/Ocultar Menú")
        self.button_toggle_menu.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.button_toggle_menu.clicked.connect(self.toggle_menu)
        main_layout.addWidget(self.button_toggle_menu)

        # Crear el menú flotante
        self.create_floating_menu()

        # Instalar un filtro de eventos para capturar clics fuera del menú
        self.installEventFilter(self)

        # Cargar los datos de la BD al iniciar la app, pero no mostrarlos aún
        self.on_data = {}
        self.off_data = {}
        self.load_existing_data()

    def create_category_widgets(self):
        """Crea widgets y botones ON/OFF independientes para cada categoría."""
        categories = ["Pasajeros", "Hotel", "Transporte", "Restaurant"]

        self.category_widgets = {}
        self.on_buttons = {}
        self.off_buttons = {}
        self.table_views = {}

        for category in categories:
            category_widget = QWidget()
            category_layout = QVBoxLayout(category_widget)

            # Crear los botones ON/OFF para cada categoría
            on_off_layout = QHBoxLayout()

            button_on = QPushButton(f"{category} ON")
            button_off = QPushButton(f"{category} OFF")

            # Estilos para los botones ON/OFF
            button_on.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 10px;
                    font-size: 16px;
                    padding: 10px;
                }
                QPushButton:pressed {
                    background-color: #45a049;
                }
            """)

            button_off.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border-radius: 10px;
                    font-size: 16px;
                    padding: 10px;
                }
                QPushButton:pressed {
                    background-color: #e53935;
                }
            """)

            # Agregar los botones al layout horizontal
            on_off_layout.addWidget(button_on)
            on_off_layout.addWidget(button_off)

            # Agregar el layout de botones al layout de la categoría
            category_layout.addLayout(on_off_layout)

            # Crear y agregar un QTableView para mostrar los datos de la categoría
            table_view = QTableView()
            category_layout.addWidget(table_view)

            # Guardar una referencia de los botones y la tabla para cada categoría
            self.on_buttons[category] = button_on
            self.off_buttons[category] = button_off
            self.table_views[category] = table_view

            # Conectar los botones a las funciones para mostrar ON y OFF de cada categoría
            button_on.clicked.connect(lambda _, c=category: self.show_category_on(c))
            button_off.clicked.connect(lambda _, c=category: self.show_category_off(c))

            # Añadir el widget de la categoría al stacked_widget
            self.stacked_widget.addWidget(category_widget)

    def show_category_on(self, category):
        """Muestra la vista 'ON' de la categoría seleccionada."""
        print(f"Mostrando vista ON para {category}")
        if category in self.on_data and self.on_data[category] is not None:
            self.show_sheet(self.on_data[category], self.table_views[category])

    def show_category_off(self, category):
        """Muestra la vista 'OFF' de la categoría seleccionada."""
        print(f"Mostrando vista OFF para {category}")
        if category in self.off_data and self.off_data[category] is not None:
            self.show_sheet(self.off_data[category], self.table_views[category])

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
            
            # Imprimir los nombres de las hojas del Excel para asegurarte de que están presentes
            print("Hojas de Excel encontradas:", excel_data.keys())

            # Procesar las hojas 'hotel', 'restaurant', 'transporte' y 'buque' y guardar en la base de datos si están disponibles
            if 'hotel' in excel_data:
                print("Procesando hoja 'hotel'")
                self.save_hotel_data(excel_data['hotel'])
            
            if 'restaurant' in excel_data:
                print("Procesando hoja 'restaurant'")
                self.save_restaurant_data(excel_data['restaurant'])

            if 'transporte' in excel_data:
                print("Procesando hoja 'transporte'")
                self.save_transporte_data(excel_data['transporte'])

            if 'buque' in excel_data:
                print("Procesando hoja 'buque'")
                self.save_buque_data(excel_data['buque'])
            else:
                print("Hoja 'buque' no encontrada")

            # Mostrar la primera hoja "on" y "off" en sus respectivas tablas
            if self.on_sheets:
                self.show_sheet(self.on_sheets[list(self.on_sheets.keys())[0]], self.table_views["Pasajeros"])
            if self.off_sheets:
                self.show_sheet(self.off_sheets[list(self.off_sheets.keys())[0]], self.table_views["Pasajeros"])

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al procesar el archivo: {e}")



    def save_hotel_data(self, hotel_df):
        """
        Guarda los datos de la hoja 'hotel' en la base de datos.
        """
        session = SessionLocal()
        try:
            # Iterar sobre cada fila del DataFrame
            for _, row in hotel_df.iterrows():
                nombre = row.get('nombre')
                ciudad = row.get('ciudad')

                # Validar que las columnas tengan datos
                if pd.isna(nombre) or pd.isna(ciudad):
                    continue

                # Crear y añadir el nuevo hotel a la base de datos
                hotel = Hotel(nombre=nombre, ciudad=ciudad)
                session.add(hotel)

            # Confirmar los cambios en la base de datos
            session.commit()

            QMessageBox.information(self, "Éxito", "Datos de hoteles guardados correctamente.")
        
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error al guardar los datos de hoteles: {e}")
        
        finally:
            session.close()

    def save_restaurant_data(self, restaurant_df):
        """
        Guarda los datos de la hoja 'restaurant' en la base de datos.
        """
        session = SessionLocal()
        try:
            # Iterar sobre cada fila del DataFrame
            for _, row in restaurant_df.iterrows():
                nombre = row.get('nombre')
                ciudad = row.get('ciudad')

                # Validar que las columnas tengan datos
                if pd.isna(nombre) or pd.isna(ciudad):
                    continue

                # Crear y añadir el nuevo restaurant a la base de datos
                restaurant = Restaurante(nombre=nombre, ciudad=ciudad)
                session.add(restaurant)

            # Confirmar los cambios en la base de datos
            session.commit()

            QMessageBox.information(self, "Éxito", "Datos de restaurantes guardados correctamente.")
        
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error al guardar los datos de restaurantes: {e}")
        
        finally:
            session.close()

    def save_transporte_data(self, transporte_df):
        """
        Guarda los datos de la hoja 'transporte' en la base de datos.
        """
        session = SessionLocal()
        try:
            # Iterar sobre cada fila del DataFrame
            for _, row in transporte_df.iterrows():
                nombre = row.get('nombre')
                ciudad = row.get('ciudad')

                # Imprimir para verificar los datos que se están procesando
                # print(f"Procesando transporte: nombre={nombre}, ciudad={ciudad}")

                # Validar que las columnas tengan datos
                if pd.isna(nombre) or pd.isna(ciudad):
                    print("Datos faltantes, omitiendo esta fila.")
                    continue

                # Crear y añadir el nuevo transporte a la base de datos
                transporte = Transporte(nombre=nombre, ciudad=ciudad)
                session.add(transporte)

            # Confirmar los cambios en la base de datos
            session.commit()
            print("Datos de transporte guardados correctamente.")
            QMessageBox.information(self, "Éxito", "Datos de transporte guardados correctamente.")
        
        except Exception as e:
            session.rollback()
            print(f"Error al guardar los datos de transporte: {e}")
            QMessageBox.critical(self, "Error", f"Error al guardar los datos de transporte: {e}")
        
        finally:
            session.close()

    def save_buque_data(self, buque_df):
        """
        Guarda los datos de la hoja 'buque' en la base de datos.
        """
        session = SessionLocal()
        try:
            # Iterar sobre cada fila del DataFrame
            for _, row in buque_df.iterrows():
                barco = row.get('barco')
                cliente = row.get('cliente')
                ciudad = row.get('ciudad')

                # Imprimir para verificar los datos que se están procesando
                # print(f"Procesando buque: barco={barco}, cliente={cliente}, ciudad={ciudad}")

                # Validar que las columnas tengan datos
                if pd.isna(barco) or pd.isna(cliente) or pd.isna(ciudad):
                    print("Datos faltantes, omitiendo esta fila.")
                    continue

                # Crear y añadir el nuevo buque a la base de datos
                buque = Buque(nombre=barco, cobrar_a=cliente, ciudad=ciudad)
                session.add(buque)

            # Confirmar los cambios en la base de datos
            session.commit()
            print("Datos de buques guardados correctamente.")
            QMessageBox.information(self, "Éxito", "Datos de buques guardados correctamente.")
        
        except Exception as e:
            session.rollback()
            print(f"Error al guardar los datos de buques: {e}")
            QMessageBox.critical(self, "Error", f"Error al guardar los datos de buques: {e}")
        
        finally:
            session.close()

    def load_existing_data(self):
        """Carga los datos existentes de la base de datos para 'Pasajeros ON' y 'OFF'."""
        session = SessionLocal()
        try:
            # Cargar los tripulantes ON desde la base de datos
            tripulantes_on = session.query(Tripulante).filter_by(estado='ON').all()
            self.on_data["Pasajeros"] = pd.DataFrame([{
                'Vessel': trip.buque.nombre,
                'First name': trip.nombre,
                'Last name': trip.apellido,
                'Gender': trip.sexo,
                'Nationality': trip.nacionalidad,
                'Passport number': trip.pasaporte,
                'Date of birth': trip.fecha_nacimiento
            } for trip in tripulantes_on])

            # Cargar los tripulantes OFF desde la base de datos
            tripulantes_off = session.query(Tripulante).filter_by(estado='OFF').all()
            self.off_data["Pasajeros"] = pd.DataFrame([{
                'Vessel': trip.buque.nombre,
                'First name': trip.nombre,
                'Last name': trip.apellido,
                'Gender': trip.sexo,
                'Nationality': trip.nacionalidad,
                'Passport number': trip.pasaporte,
                'Date of birth': trip.fecha_nacimiento
            } for trip in tripulantes_off])

        except Exception as e:
            print(f"Error al cargar datos existentes: {e}")
        finally:
            session.close()

    def show_sheet(self, df, table_view):
        """Muestra los datos del DataFrame en la QTableView correspondiente."""
        if df is not None and not df.empty:
            model = PandasModel(df)
            table_view.setModel(model)
        else:
            # Mostrar un mensaje si no hay datos
            model = PandasModel(pd.DataFrame({"Mensaje": ["No hay datos disponibles"]}))
            table_view.setModel(model)

    # Funciones para el menú flotante
    def create_floating_menu(self):
        """Crea el menú flotante para navegar entre las diferentes categorías."""
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
        """Función para mostrar y ocultar el menú con una animación."""
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
        """Si el menú está visible y se hace clic fuera de él, se cierra."""
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

    def create_generic_screens(self):
        """Crea pantallas genéricas para las categorías del menú."""
        categories = ["Pasajeros", "Hotel", "Transporte", "Restaurant"]

        for category in categories:
            screen = QWidget()
            layout = QVBoxLayout(screen)
            label = QLabel(category, alignment=Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            self.stacked_widget.addWidget(screen)

    def change_tab(self, index):
        """Cambia la pantalla según la selección del menú."""
        self.stacked_widget.setCurrentIndex(index)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BasicApp()
    window.show()
    sys.exit(app.exec())
