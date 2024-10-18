import pandas as pd
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QFileDialog
from PyQt6.QtCore import Qt
from app.database import get_db_session
from app.models import Buque, EtaCiudad, Tripulante, Vuelo, TripulanteVuelo, Restaurante, TripulanteRestaurante, Transporte, TripulanteTransporte, Hotel, TripulanteHotel# Asegúrate de que estos modelos se importen correctamente
from app.controllers import CITY_AIRPORT_CODES
from openpyxl.styles import PatternFill
from openpyxl import Workbook
from sqlalchemy import func


class GeneracionReportesScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Añadir un botón "Volver" al menú principal
        self.button_volver = QPushButton("Volver")
        self.button_volver.setFixedWidth(100)
        self.button_volver.clicked.connect(self.volver_al_menu_principal)
        layout.addWidget(self.button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        # Crear un layout horizontal para los botones
        layout_botones = QHBoxLayout()
        layout_botones.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Botones
        button_informar = QPushButton("Informar")
        button_informar.setFixedSize(140, 40)
        layout_botones.addWidget(button_informar)

        button_programar = QPushButton("Programar")
        button_programar.setFixedSize(140, 40)
        button_programar.clicked.connect(self.mostrar_opciones_programar)
        layout_botones.addWidget(button_programar)

        button_liquidar = QPushButton("Liquidar")
        button_liquidar.setFixedSize(140, 40)
        layout_botones.addWidget(button_liquidar)

        button_cuadrar_proveedor = QPushButton("Cuadrar Proveedor")
        button_cuadrar_proveedor.setFixedSize(140, 40)
        layout_botones.addWidget(button_cuadrar_proveedor)

        # Añadir el layout de botones al layout principal
        layout.addLayout(layout_botones)

    def mostrar_opciones_programar(self):
        opciones_programar_screen = OpcionesProgramarScreen(self.main_window)
        self.main_window.stacked_widget.addWidget(opciones_programar_screen)
        self.main_window.stacked_widget.setCurrentWidget(opciones_programar_screen)

    def volver_al_menu_principal(self):
        self.main_window.stacked_widget.setCurrentIndex(0)  # Regresar al menú principal

class OpcionesProgramarScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Botón "Volver" para regresar a la pantalla anterior (Generación de Reportes)
        button_volver = QPushButton("Volver")
        button_volver.setFixedWidth(100)
        button_volver.clicked.connect(self.volver_a_reportes)
        layout.addWidget(button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        layout_botones = QHBoxLayout()
        layout_botones.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Botones
        button_asistencias = QPushButton("Asistencias")
        button_asistencias.setFixedSize(140, 40)
        button_asistencias.clicked.connect(self.mostrar_asistencias)
        layout_botones.addWidget(button_asistencias)

        button_transportes = QPushButton("Requerimiento alojamientos")
        button_transportes.setFixedSize(140, 40)
        button_transportes.clicked.connect(self.mostrar_transportes)
        layout_botones.addWidget(button_transportes)

        button_room_list = QPushButton("Room List")
        button_room_list.setFixedSize(140, 40)
        button_room_list.clicked.connect(self.mostrar_room_list)
        layout_botones.addWidget(button_room_list)

        button_cuadrar_proveedor = QPushButton("Cuadrar Proveedor")
        button_cuadrar_proveedor.setFixedSize(140, 40)
        layout_botones.addWidget(button_cuadrar_proveedor)

        # Añadir el layout de botones al layout principal
        layout.addLayout(layout_botones)

    def mostrar_asistencias(self):
        asistencias_screen = AsistenciasScreen(self.main_window)
        self.main_window.stacked_widget.addWidget(asistencias_screen)
        self.main_window.stacked_widget.setCurrentWidget(asistencias_screen)

    def mostrar_transportes(self):
        transportes_screen = TransportesScreen(self.main_window)
        self.main_window.stacked_widget.addWidget(transportes_screen)
        self.main_window.stacked_widget.setCurrentWidget(transportes_screen)

    def mostrar_room_list(self):
        room_list_screen = RoomListScreen(self.main_window)
        self.main_window.stacked_widget.addWidget(room_list_screen)
        self.main_window.stacked_widget.setCurrentWidget(room_list_screen)

    def volver_a_reportes(self):
        self.main_window.stacked_widget.setCurrentIndex(self.main_window.stacked_widget.currentIndex() - 1)

class RoomListScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Cuadro de selección de ciudad dentro de AsistenciasScreen
        self.combo_hoteles = QComboBox()
        self.combo_hoteles.addItems(["Hotel", "CABO DE HORNOS", "TBC", "DIEGO DE ALMAGRO", "SIN HOTEL", "Holiday Inn", "Lukataia"])  # Agrega las ciudades al combo box
        layout.addWidget(self.combo_hoteles)

        self.combo_buques = QComboBox()
        self.combo_buques.addItems(["Buque", "Silver endeavour", "C-GEAI", "C-FMKB", "Silver Cloud", "Fram", "SYLVIA EARLE"])  # Agrega las ciudades al combo box
        layout.addWidget(self.combo_buques)

        # Label para mostrar asistencias
        self.label = QLabel()  # Mover el label aquí para que sea un atributo de la clase
        layout.addWidget(self.label)

        # Tabla para mostrar datos
        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        # Botón para generar el Excel
        button_generar_excel = QPushButton("Generar excel")
        button_generar_excel.clicked.connect(self.generar_excel_con_ciudad)  # Conectar al método de generación de Excel
        layout.addWidget(button_generar_excel)

        # Botón "Volver" para regresar a la pantalla anterior (Generación de Reportes)
        button_volver = QPushButton("Volver")
        button_volver.setFixedWidth(100)
        button_volver.clicked.connect(self.volver_a_reportes)
        layout.addWidget(button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        # Conectar el cambio en el QComboBox a un método
        self.combo_hoteles.currentTextChanged.connect(self.actualizar_datos)
        self.combo_buques.currentTextChanged.connect(self.actualizar_datos)

        # Actualizar datos inicialmente
        self.actualizar_datos()

    def generar_excel_con_ciudad(self):
        hotel_seleccionado = self.combo_hoteles.currentText()  # Obtener la ciudad seleccionada
        self.generar_excel(hotel_seleccionado)  # Llamar a generar_excel con la ciudad seleccionada

    def actualizar_datos(self):
        hotel_seleccionado = self.combo_hoteles.currentText()  # Obtiene la ciudad seleccionada
        buque_seleccionado = self.combo_buques.currentText()  # Obtiene la ciudad seleccionada
        self.label.setText(f"Room list en {hotel_seleccionado}")  # Actualiza el label

        # Cargar datos en la tabla
        self.cargar_datos(hotel_seleccionado, buque_seleccionado)

    def cargar_datos(self, hotel_seleccionado, buque_seleccionado):
        session = get_db_session()  # Obtener la sesión de la base de datos

        # Convertir las entradas a minúsculas para comparación
        hotel_seleccionado = hotel_seleccionado.lower()
        buque_seleccionado = buque_seleccionado.lower()

        #print(hotel_seleccionado)
        #print(buque_seleccionado)

        # Construir la consulta de roomlist
        roomlist_query = (
            session.query(
                Hotel.nombre.label("Nombre_hotel"),
                TripulanteHotel.fecha_entrada.label("check_in"),
                TripulanteHotel.fecha_salida.label("check_out"),
                TripulanteHotel.tipo_habitacion.label("Rooms"),
                Tripulante.nombre.label("First_Name"),
                Tripulante.apellido.label("Last_Name"),
                Tripulante.sexo.label("Gender"),
                Tripulante.nacionalidad.label("Nacionalidad"),
                Tripulante.posicion.label("Position"),
                Buque.nombre.label("Buque"),
                Tripulante.tripulante_id
            )
            .join(TripulanteHotel, Hotel.hotel_id == TripulanteHotel.hotel_id, isouter=True)
            .join(Tripulante, TripulanteHotel.tripulante_id == Tripulante.tripulante_id, isouter=True)
            .join(Buque, Buque.buque_id == Tripulante.buque_id, isouter=True)
        )

        # Aplicar filtro solo si no está seleccionado "hotel"
        if hotel_seleccionado != "hotel":
            roomlist_query = roomlist_query.filter(func.lower(Hotel.nombre) == hotel_seleccionado)

        # Aplicar filtro de buque si se seleccionó uno específico
        if buque_seleccionado != "buque":
            roomlist_query = roomlist_query.filter(func.lower(Buque.nombre) == buque_seleccionado)

        # Ejecutar la consulta
        roomlist_query = roomlist_query.all()

        # Limpiar la tabla
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(9)  # Número correcto de columnas
        self.table_widget.setHorizontalHeaderLabels(
            ["First Name", "Last Name", "Gender", "Nacionalidad", "Position", "Check In", "Check Out", "Rooms", "Buque"]
        )

        #print(roomlist_query)

        # Llenar la tabla con los resultados de la consulta
        for roomlist in roomlist_query:
            row = self.table_widget.rowCount()
            self.table_widget.insertRow(row)
            
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(roomlist.First_Name)))  # First Name
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(roomlist.Last_Name)))  # Last Name
            self.table_widget.setItem(row, 2, QTableWidgetItem(str(roomlist.Gender)))  # Gender
            self.table_widget.setItem(row, 3, QTableWidgetItem(str(roomlist.Nacionalidad)))  # Nacionalidad
            self.table_widget.setItem(row, 4, QTableWidgetItem(str(roomlist.Position)))  # Position
            
            # Check In
            self.table_widget.setItem(row, 5, QTableWidgetItem(str(roomlist.check_in) if roomlist.check_in else "Sin fecha"))
            # Check Out
            self.table_widget.setItem(row, 6, QTableWidgetItem(str(roomlist.check_out) if roomlist.check_out else "Sin fecha"))
            # Rooms
            self.table_widget.setItem(row, 7, QTableWidgetItem(str(roomlist.Rooms) if roomlist.Rooms else "Sin fecha"))
            # Buque
            self.table_widget.setItem(row, 8, QTableWidgetItem(str(roomlist.Buque)))  # Buque
            

    def generar_excel(self, hotel_seleccionado):
    # Crear un DataFrame con los datos de la tabla
        data = []

        for row in range(self.table_widget.rowCount()):
            row_data = []
            for column in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, column)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        # Definir los nombres de las columnas
        column_names = ["First Name", "Last Name", "Gender", "Nacionalidad", "Position", "Check In", "Check Out", "Rooms"]

        # Convertir a DataFrame
        df = pd.DataFrame(data, columns=column_names)

        # Construir el nombre del archivo Excel
        file_name = f'room_list_{hotel_seleccionado}.xlsx'
        
        # Guardar en un archivo Excel
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Guardar archivo Excel", 
            file_name,  # Usar el nombre del archivo predefinido
            "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if file_path:
            # Crear un nuevo libro de trabajo de Excel
            wb = Workbook()
            ws = wb.active

            # Definir el color de relleno para los encabezados (celeste claro)
            header_fill = PatternFill(start_color='ADD8E6', end_color='ADD8E6', fill_type='solid')
            # Definir el color de relleno para los datos (amarillo claro)
            data_fill = PatternFill(start_color='FFFF99', end_color='FFFF99', fill_type='solid')

            cell = ws.cell(row=1, column=1)
            cell.value = "HOLA"

            # Escribir los encabezados del DataFrame manualmente
            for col_num, col_name in enumerate(column_names, 1):
                cell = ws.cell(row=5, column=col_num)
                cell.value = col_name
                cell.fill = header_fill  # Aplicar color a los encabezados

            # Escribir los datos del DataFrame y aplicar color a las celdas
            for row_num, row_data in enumerate(df.values, start=6):
                for col_num, cell_value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_num, column=col_num)
                    cell.value = cell_value
                    cell.fill = data_fill  # Aplicar color a los datos

            # Guardar el archivo Excel con colores aplicados
            wb.save(file_path)

    def volver_a_reportes(self):
        self.main_window.stacked_widget.setCurrentIndex(self.main_window.stacked_widget.currentIndex() - 1)

class TransportesScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Cuadro de selección de ciudad dentro de AsistenciasScreen
        self.combo_ciudades = QComboBox()
        self.combo_ciudades.addItems(["SCL", "PUQ", "WPU"])  # Agrega las ciudades al combo box
        layout.addWidget(self.combo_ciudades)

        # Label para mostrar asistencias
        self.label = QLabel()  # Mover el label aquí para que sea un atributo de la clase
        layout.addWidget(self.label)

        # Tabla para mostrar datos
        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        # Botón para generar el Excel
        button_generar_excel = QPushButton("Generar excel")
        button_generar_excel.clicked.connect(self.generar_excel_con_ciudad)  # Conectar al método de generación de Excel
        layout.addWidget(button_generar_excel)

        # Botón "Volver" para regresar a la pantalla anterior (Generación de Reportes)
        button_volver = QPushButton("Volver")
        button_volver.setFixedWidth(100)
        button_volver.clicked.connect(self.volver_a_reportes)
        layout.addWidget(button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        # Conectar el cambio en el QComboBox a un método
        self.combo_ciudades.currentTextChanged.connect(self.actualizar_datos)

        # Actualizar datos inicialmente
        self.actualizar_datos()

    def generar_excel_con_ciudad(self):
        ciudad_seleccionada = self.combo_ciudades.currentText()  # Obtener la ciudad seleccionada
        self.generar_excel(ciudad_seleccionada)  # Llamar a generar_excel con la ciudad seleccionada

    def actualizar_datos(self):
        ciudad_seleccionada = self.combo_ciudades.currentText()  # Obtiene la ciudad seleccionada
        self.label.setText(f"Requerimiento transportes en {ciudad_seleccionada}")  # Actualiza el label

        # Cargar datos en la tabla
        self.cargar_datos(ciudad_seleccionada)

    def cargar_datos(self, ciudad_seleccionada):
        session = get_db_session()  # Obtener la sesión de la base de datos

        # Genera y muestra la consulta
        """query = (
            session.query(
                Transporte.ciudad.label("Ciudad_transporte"),
                Transporte.nombre.label("Tramo"),
                Tripulante.tripulante_id
            )
            .outerjoin(TripulanteTransporte, TripulanteTransporte.tripulante_id == Tripulante.tripulante_id)
            .outerjoin(Transporte, TripulanteTransporte.transporte_id == Transporte.transporte_id)
            .filter(func.lower(Transporte.ciudad) == ciudad_seleccionada)
        )

        print(str(query))"""
        #salida_vuelos = query.all()

        # Obtener el nombre de la ciudad a partir del código
        ciudad_seleccionada = CITY_AIRPORT_CODES.get(ciudad_seleccionada).lower()  # Convertir a minúsculas
        print(ciudad_seleccionada)

        # Obtener datos de vuelos de arribo
        arribo_vuelos = (
            session.query(
                Transporte.ciudad.label("Ciudad"),
                Transporte.nombre.label("Tramo"),
                Tripulante.nombre.label("First_Name"),
                Tripulante.apellido.label("Last_Name"),
                Tripulante.estado.label("Type"),
                TripulanteTransporte.fecha.label("Fecha"),
                Tripulante.tripulante_id
            )
            .join(TripulanteTransporte, Transporte.transporte_id == TripulanteTransporte.transporte_id, isouter=True)
            .join(Tripulante, TripulanteTransporte.tripulante_id == Tripulante.tripulante_id, isouter=True)
            .filter(func.lower(Transporte.ciudad) == ciudad_seleccionada)
            .all()
        )
        
        # Obtener datos de vuelos de salida
        """salida_vuelos = (
            session.query(
                Vuelo.aeropuerto_salida.label("Aeropuerto_Salida"),
                Vuelo.hora_salida.label("Hora_Salida"),
                Vuelo.codigo.label("Nro_Vuelo_Salida"),
                Vuelo.fecha.label("Fecha_Vuelo_Salida"),
                Tripulante.tripulante_id  # Incluir el tripulante_id
            )
            .outerjoin(TripulanteVuelo, TripulanteVuelo.tripulante_id == Tripulante.tripulante_id)
            .outerjoin(Vuelo, TripulanteVuelo.vuelo_id == Vuelo.vuelo_id)
            .filter(func.lower(Vuelo.aeropuerto_salida) == ciudad_seleccionada)
            .all()
        )"""

        # Limpiar la tabla
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(6)  # Número correcto de columnas
        self.table_widget.setHorizontalHeaderLabels(
            ["First Name", "Last Name", "Type", "Ciudad", "Tramo", "Fecha"]
        )

        print(arribo_vuelos)

        # Combinar y llenar la tabla
        for arribo in arribo_vuelos:
            # Buscar un vuelo de salida correspondiente usando el tripulante_id
            #salida = next((s for s in salida_vuelos if s.tripulante_id == arribo.tripulante_id), None)
            
            row = self.table_widget.rowCount()
            self.table_widget.insertRow(row)
            # Datos de arribo
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(arribo.First_Name)))  # First Name
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(arribo.Last_Name)))  # Last Name
            self.table_widget.setItem(row, 2, QTableWidgetItem(str(arribo.Type)))  # Type
            self.table_widget.setItem(row, 3, QTableWidgetItem(str(arribo.Ciudad)))  # Nro Vuelo Arribo
            self.table_widget.setItem(row, 4, QTableWidgetItem(str(arribo.Tramo)))  # Fecha Vuelo Arribo
            self.table_widget.setItem(row, 5, QTableWidgetItem(str(arribo.Fecha)))  # Fecha Vuelo Arribo

            # Si hay vuelo de salida, se añaden los detalles
            """
            if salida:
                print(f"Vuelo de salida encontrado para {arribo.First_Name} {arribo.Last_Name}: {salida.Nro_Vuelo_Salida}, {salida.Fecha_Vuelo_Salida}, {salida.Hora_Salida}")
                self.table_widget.setItem(row, 15, QTableWidgetItem(str(salida.Nro_Vuelo_Salida)))  # Nro Vuelo Salida
                self.table_widget.setItem(row, 16, QTableWidgetItem(str(salida.Fecha_Vuelo_Salida)))  # Fecha Vuelo Salida
                self.table_widget.setItem(row, 17, QTableWidgetItem(str(salida.Hora_Salida)))  # Hora Salida
            else:
                print(f"No se encontró vuelo de salida para {arribo.First_Name} {arribo.Last_Name}")"""


    def generar_excel(self, ciudad_seleccionada):
    # Crear un DataFrame con los datos de la tabla
        data = []
        for row in range(self.table_widget.rowCount()):
            row_data = []
            for column in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, column)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        # Definir los nombres de las columnas
        column_names = ["First Name", "Last Name", "Type", "Ciudad", "Tramo", "Fecha"]

        # Convertir a DataFrame
        df = pd.DataFrame(data, columns=column_names)

        # Construir el nombre del archivo Excel
        file_name = f'requerimiento_transportes_{ciudad_seleccionada}.xlsx'
        
        # Guardar en un archivo Excel
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Guardar archivo Excel", 
            file_name,  # Usar el nombre del archivo predefinido
            "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if file_path:
            # Crear un nuevo libro de trabajo de Excel
            wb = Workbook()
            ws = wb.active

            # Definir el color de relleno para los encabezados (celeste claro)
            header_fill = PatternFill(start_color='ADD8E6', end_color='ADD8E6', fill_type='solid')
            # Definir el color de relleno para los datos (amarillo claro)
            data_fill = PatternFill(start_color='FFFF99', end_color='FFFF99', fill_type='solid')

            # Escribir los encabezados del DataFrame manualmente
            for col_num, col_name in enumerate(column_names, 1):
                cell = ws.cell(row=5, column=col_num)
                cell.value = col_name
                cell.fill = header_fill  # Aplicar color a los encabezados

            # Escribir los datos del DataFrame y aplicar color a las celdas
            for row_num, row_data in enumerate(df.values, start=6):
                for col_num, cell_value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_num, column=col_num)
                    cell.value = cell_value
                    cell.fill = data_fill  # Aplicar color a los datos

            # Guardar el archivo Excel con colores aplicados
            wb.save(file_path)

    def volver_a_reportes(self):
        self.main_window.stacked_widget.setCurrentIndex(self.main_window.stacked_widget.currentIndex() - 1)

class AsistenciasScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Cuadro de selección de ciudad dentro de AsistenciasScreen
        self.combo_ciudades = QComboBox()
        self.combo_ciudades.addItems(["SCL", "PUQ", "WPU"])  # Agrega las ciudades al combo box
        layout.addWidget(self.combo_ciudades)

        # Label para mostrar asistencias
        self.label = QLabel()  # Mover el label aquí para que sea un atributo de la clase
        layout.addWidget(self.label)

        # Tabla para mostrar datos
        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        # Botón para generar el Excel
        button_generar_excel = QPushButton("Generar excel")
        button_generar_excel.clicked.connect(self.generar_excel_con_ciudad)  # Conectar al método de generación de Excel
        layout.addWidget(button_generar_excel)

        # Botón "Volver" para regresar a la pantalla anterior (Generación de Reportes)
        button_volver = QPushButton("Volver")
        button_volver.setFixedWidth(100)
        button_volver.clicked.connect(self.volver_a_reportes)
        layout.addWidget(button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        # Conectar el cambio en el QComboBox a un método
        self.combo_ciudades.currentTextChanged.connect(self.actualizar_datos)

        # Actualizar datos inicialmente
        self.actualizar_datos()

    def generar_excel_con_ciudad(self):
        ciudad_seleccionada = self.combo_ciudades.currentText()  # Obtener la ciudad seleccionada
        self.generar_excel(ciudad_seleccionada)  # Llamar a generar_excel con la ciudad seleccionada

    def actualizar_datos(self):
        ciudad_seleccionada = self.combo_ciudades.currentText()  # Obtiene la ciudad seleccionada
        self.label.setText(f"Asistencias en {ciudad_seleccionada}")  # Actualiza el label

        # Cargar datos en la tabla
        self.cargar_datos(ciudad_seleccionada)

    def cargar_datos(self, ciudad_seleccionada):
        session = get_db_session()  # Obtener la sesión de la base de datos

        # Genera y muestra la consulta
        query = (
            session.query(
                Vuelo.aeropuerto_salida.label("Aeropuerto_Salida"),
                Vuelo.hora_salida.label("Hora_Salida"),
                Vuelo.codigo.label("Nro_Vuelo_Salida"),
                Vuelo.fecha.label("Fecha_Vuelo_Salida"),
                Tripulante.tripulante_id
            )
            .outerjoin(TripulanteVuelo, TripulanteVuelo.tripulante_id == Tripulante.tripulante_id)
            .outerjoin(Vuelo, TripulanteVuelo.vuelo_id == Vuelo.vuelo_id)
            .filter(func.lower(Vuelo.aeropuerto_salida) == ciudad_seleccionada)
        )

        print(str(query))
        salida_vuelos = query.all()

        # Obtener el nombre de la ciudad a partir del código
        ciudad_seleccionada = CITY_AIRPORT_CODES.get(ciudad_seleccionada).lower()  # Convertir a minúsculas

        # Obtener datos de vuelos de arribo
        arribo_vuelos = (
            session.query(
                Buque.nombre.label("Vessel"),
                Vuelo.aeropuerto_llegada.label("Aeropuerto_Llegada"),
                EtaCiudad.eta.label("ETA"),
                Vuelo.hora_llegada.label("Hora_Arribo"),
                Tripulante.nombre.label("First_Name"),
                Tripulante.apellido.label("Last_Name"),
                Tripulante.estado.label("Type"),
                Vuelo.codigo.label("Nro_Vuelo_Arribo"),
                Tripulante.tripulante_id,
                Vuelo.fecha.label("Fecha_Vuelo_Arribo")
            )
            .outerjoin(TripulanteVuelo, TripulanteVuelo.tripulante_id == Tripulante.tripulante_id)
            .outerjoin(Vuelo, TripulanteVuelo.vuelo_id == Vuelo.vuelo_id)
            .outerjoin(Buque, Tripulante.buque_id == Buque.buque_id)
            .outerjoin(EtaCiudad, Buque.buque_id == EtaCiudad.buque_id)
            .filter(func.lower(Vuelo.aeropuerto_llegada) == ciudad_seleccionada)
            .all()
        )
        
        # Obtener datos de vuelos de salida
        salida_vuelos = (
            session.query(
                Vuelo.aeropuerto_salida.label("Aeropuerto_Salida"),
                Vuelo.hora_salida.label("Hora_Salida"),
                Vuelo.codigo.label("Nro_Vuelo_Salida"),
                Vuelo.fecha.label("Fecha_Vuelo_Salida"),
                Tripulante.tripulante_id  # Incluir el tripulante_id
            )
            .outerjoin(TripulanteVuelo, TripulanteVuelo.tripulante_id == Tripulante.tripulante_id)
            .outerjoin(Vuelo, TripulanteVuelo.vuelo_id == Vuelo.vuelo_id)
            .filter(func.lower(Vuelo.aeropuerto_salida) == ciudad_seleccionada)
            .all()
        )

        # Limpiar la tabla
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(18)  # Número correcto de columnas
        self.table_widget.setHorizontalHeaderLabels(
            ["Vessel", "ETA", "First Name", "Last Name", "Type", "Asistencia", "COLACION", 
            "COMIDAS", "Nro Vuelo Arribo", "Fecha Vuelo Arribo", 
            "Hora Arribo", "Hotel", "Habitación", "Date Pick Up", 
            "Hora Pick Up", "Nro Vuelo Salida", "Fecha Vuelo Salida", 
            "Hora Vuelo Salida"]
        )

        # Combinar y llenar la tabla
        for arribo in arribo_vuelos:
            # Buscar un vuelo de salida correspondiente usando el tripulante_id
            salida = next((s for s in salida_vuelos if s.tripulante_id == arribo.tripulante_id), None)
            
            row = self.table_widget.rowCount()
            self.table_widget.insertRow(row)
            # Datos de arribo
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(arribo.Vessel)))  # Vessel
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(arribo.ETA)))  # ETA
            self.table_widget.setItem(row, 2, QTableWidgetItem(str(arribo.First_Name)))  # First Name
            self.table_widget.setItem(row, 3, QTableWidgetItem(str(arribo.Last_Name)))  # Last Name
            self.table_widget.setItem(row, 4, QTableWidgetItem(str(arribo.Type)))  # Type
            self.table_widget.setItem(row, 8, QTableWidgetItem(str(arribo.Nro_Vuelo_Arribo)))  # Nro Vuelo Arribo
            self.table_widget.setItem(row, 9, QTableWidgetItem(str(arribo.Fecha_Vuelo_Arribo)))  # Fecha Vuelo Arribo
            self.table_widget.setItem(row, 10, QTableWidgetItem(str(arribo.Hora_Arribo)))  # Hora Arribo
            
            # Datos de asistencia
            asistencia = arribo.necesita_asistencia_puq if ciudad_seleccionada == 'puq' else \
                        arribo.necesita_asistencia_scl if ciudad_seleccionada == 'scl' else \
                        arribo.necesita_asistencia_wpu if ciudad_seleccionada == 'wpu' else False
            self.table_widget.setItem(row, 5, QTableWidgetItem("Sí" if asistencia else "No"))  # Asistencia

            # Datos de "Comida" y "Hotel"
            reserva_restaurante = (
                session.query(TripulanteRestaurante)
                .join(Restaurante, TripulanteRestaurante.restaurante_id == Restaurante.restaurante_id)
                .filter(TripulanteRestaurante.tripulante_id == arribo.tripulante_id)
                .filter(func.lower(Restaurante.ciudad) == ciudad_seleccionada)
                .first()
            )
            self.table_widget.setItem(row, 7, QTableWidgetItem("Sí" if reserva_restaurante else "No"))  # Comidas

            # Si hay vuelo de salida, se añaden los detalles
            if salida:
                print(f"Vuelo de salida encontrado para {arribo.First_Name} {arribo.Last_Name}: {salida.Nro_Vuelo_Salida}, {salida.Fecha_Vuelo_Salida}, {salida.Hora_Salida}")
                self.table_widget.setItem(row, 15, QTableWidgetItem(str(salida.Nro_Vuelo_Salida)))  # Nro Vuelo Salida
                self.table_widget.setItem(row, 16, QTableWidgetItem(str(salida.Fecha_Vuelo_Salida)))  # Fecha Vuelo Salida
                self.table_widget.setItem(row, 17, QTableWidgetItem(str(salida.Hora_Salida)))  # Hora Salida
            else:
                print(f"No se encontró vuelo de salida para {arribo.First_Name} {arribo.Last_Name}")


    def generar_excel(self, ciudad_seleccionada):
    # Crear un DataFrame con los datos de la tabla
        data = []
        for row in range(self.table_widget.rowCount()):
            row_data = []
            for column in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, column)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        # Definir los nombres de las columnas
        column_names = [
            "Vessel", "ETA", "First Name", "Last Name", "Type",
            "Nro Vuelo Arribo", "Fecha Vuelo Arribo", "Hora Arribo",
            "Nro Vuelo Salida", "Fecha Vuelo Salida", "Hora Vuelo Salida"
        ]

        # Convertir a DataFrame
        df = pd.DataFrame(data, columns=column_names)

        # Construir el nombre del archivo Excel
        file_name = f'asistencia_{ciudad_seleccionada}.xlsx'
        
        # Guardar en un archivo Excel
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Guardar archivo Excel", 
            file_name,  # Usar el nombre del archivo predefinido
            "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if file_path:
            # Crear un nuevo libro de trabajo de Excel
            wb = Workbook()
            ws = wb.active

            # Definir el color de relleno para los encabezados (celeste claro)
            header_fill = PatternFill(start_color='ADD8E6', end_color='ADD8E6', fill_type='solid')
            # Definir el color de relleno para los datos (amarillo claro)
            data_fill = PatternFill(start_color='FFFF99', end_color='FFFF99', fill_type='solid')

            # Escribir los encabezados del DataFrame manualmente
            for col_num, col_name in enumerate(column_names, 1):
                cell = ws.cell(row=5, column=col_num)
                cell.value = col_name
                cell.fill = header_fill  # Aplicar color a los encabezados

            # Escribir los datos del DataFrame y aplicar color a las celdas
            for row_num, row_data in enumerate(df.values, start=6):
                for col_num, cell_value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_num, column=col_num)
                    cell.value = cell_value
                    cell.fill = data_fill  # Aplicar color a los datos

            # Guardar el archivo Excel con colores aplicados
            wb.save(file_path)

    def volver_a_reportes(self):
        self.main_window.stacked_widget.setCurrentIndex(self.main_window.stacked_widget.currentIndex() - 1)
