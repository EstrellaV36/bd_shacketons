import pandas as pd
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QFileDialog, QDateEdit, QCheckBox
from PyQt6.QtCore import Qt, QDate
from app.database import get_db_session
from app.models import Buque, EtaCiudad, Tripulante, Vuelo, TripulanteVuelo, Restaurante, TripulanteRestaurante, Transporte, TripulanteTransporte, Hotel, TripulanteHotel, Buque, TripulanteAsistencia
from app.controllers import CITY_AIRPORT_CODES, CITY_TO_AIRPORT_CODES
from openpyxl.styles import PatternFill
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment
from datetime import datetime, time, timedelta
from sqlalchemy import func, and_, or_, case
from collections import defaultdict

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
        # Guardar el índice de OpcionesProgramarScreen
        self.main_window.opciones_programar_index = self.main_window.stacked_widget.addWidget(opciones_programar_screen)
        self.main_window.stacked_widget.setCurrentWidget(opciones_programar_screen)

    def volver_al_menu_principal(self):
        self.main_window.stacked_widget.setCurrentIndex(0)  # Regresar al menú principal

class OpcionesProgramarScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
        self.menu_reportes_index = main_window.stacked_widget.addWidget(self)

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

        button_transportes = QPushButton("Req. transportes")
        button_transportes.setFixedSize(140, 40)
        button_transportes.clicked.connect(self.mostrar_transportes)
        layout_botones.addWidget(button_transportes)

        button_room_list = QPushButton("Room List")
        button_room_list.setFixedSize(140, 40)
        button_room_list.clicked.connect(self.mostrar_room_list)
        layout_botones.addWidget(button_room_list)

        button_hoteles = QPushButton("Req. Hoteles")
        button_hoteles.setFixedSize(140, 40)
        button_hoteles.clicked.connect(self.mostrar_req_hoteles)
        layout_botones.addWidget(button_hoteles)

        button_alimentos = QPushButton("Solicitud SS Alimentación")
        button_alimentos.setFixedSize(180, 40)
        button_alimentos.clicked.connect(self.mostrar_solicitud_alimentacion)
        layout_botones.addWidget(button_alimentos)

        # Añadir el layout de botones al layout principal
        layout.addLayout(layout_botones)

    def mostrar_asistencias(self):
        asistencias_screen = AsistenciasScreen(self.main_window)
        asistencias_screen.opciones_programar_index = self.main_window.opciones_programar_index
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

    def mostrar_req_hoteles(self):
        hotel_screen = HotelScreen(self.main_window)
        self.main_window.stacked_widget.addWidget(hotel_screen)
        self.main_window.stacked_widget.setCurrentWidget(hotel_screen)

    def mostrar_solicitud_alimentacion(self):
        alimentos_screen = AlimentosScreen(self.main_window)
        self.main_window.stacked_widget.addWidget(alimentos_screen)
        self.main_window.stacked_widget.setCurrentWidget(alimentos_screen)

    def volver_a_reportes(self):
        self.main_window.stacked_widget.setCurrentIndex(self.main_window.menu_reportes_index)

class HotelScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        session = get_db_session()

        # Llenar el combo de buques desde la base de datos
        self.combo_buques = QComboBox()
        self.combo_buques.addItem("Buque")  # Agregar un valor por defecto

        buques = session.query(Buque.nombre).distinct().all()  # Consulta para obtener los nombres de los buques
        for buque in buques:
            self.combo_buques.addItem(buque.nombre)
        layout.addWidget(self.combo_buques)

        # Cuadro de selección de buque
        self.combo_owner = QComboBox()
        self.combo_owner.addItems(["Owner"])
        owners = session.query(Buque.empresa).distinct().all()  # Consulta para obtener los nombres de los buques
        for owner in owners:
            self.combo_owner.addItem(owner.empresa)
        layout.addWidget(self.combo_owner)

        # Filtro por fechas
        self.check_fecha = QCheckBox("Habilitar filtro por ETA")
        self.check_fecha.setChecked(False)
        self.check_fecha.stateChanged.connect(self.toggle_fecha_fields)
        layout.addWidget(self.check_fecha)

        # Layout horizontal para las fechas
        layout_filtro = QHBoxLayout()

        self.date_start1 = QDateEdit()
        self.date_start1.setCalendarPopup(True)
        self.date_start1.setDate(QDate.currentDate())
        self.date_start1.setEnabled(False)  # Deshabilitado por defecto
        layout_filtro.addWidget(QLabel("Fecha ETA inicio:"))
        layout_filtro.addWidget(self.date_start1)

        self.date_end1 = QDateEdit()
        self.date_end1.setCalendarPopup(True)
        self.date_end1.setDate(QDate.currentDate())
        self.date_end1.setEnabled(False)  # Deshabilitado por defecto
        layout_filtro.addWidget(QLabel("Fecha ETA fin:"))
        layout_filtro.addWidget(self.date_end1)

        layout.addLayout(layout_filtro)

        self.combo_ciudades = QComboBox()
        self.combo_ciudades.addItems(["SCL", "PUQ", "WPU"]) 
        layout.addWidget(self.combo_ciudades)
        self.label = QLabel()
        layout.addWidget(self.label)

        # Tabla para mostrar los datos
        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        # Botón para generar el Excel
        button_generar_excel = QPushButton("Generar Excel")
        button_generar_excel.clicked.connect(self.generar_excel_con_ciudad)
        layout.addWidget(button_generar_excel)

        # Botón para volver a la pantalla principal
        button_volver = QPushButton("Volver")
        button_volver.setFixedWidth(100)
        button_volver.clicked.connect(self.volver_a_opciones_programar)
        layout.addWidget(button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        # Conectar señales
        self.combo_ciudades.currentTextChanged.connect(self.actualizar_datos)
        self.combo_buques.currentTextChanged.connect(self.actualizar_datos)
        self.combo_owner.currentTextChanged.connect(self.actualizar_datos)
        self.date_start1.dateChanged.connect(self.actualizar_datos)
        self.date_end1.dateChanged.connect(self.actualizar_datos)

        # Actualizar los datos inicialmente
        self.actualizar_datos()

    def generar_excel_con_ciudad(self):
        ciudad_seleccionada = self.combo_ciudades.currentText()
        buque_seleccionado = self.combo_buques.currentText()
        # Obtener las fechas seleccionadas
        fecha_inicio = self.date_start1.date().toString("dd-MM-yyyy")  # Formato de fecha: dd-mm-aaaa
        fecha_fin = self.date_end1.date().toString("dd-MM-yyyy")

    # Llamar a la función generar_excel con ciudad, buque y las fechas
        self.generar_excel(ciudad_seleccionada, buque_seleccionado, fecha_inicio, fecha_fin)

    def actualizar_datos(self):
        ciudad_seleccionada = self.combo_ciudades.currentText()
        buque_seleccionado = self.combo_buques.currentText()
        owner_seleccionado = self.combo_owner.currentText()
        self.label.setText(f"Lista de hoteles en {ciudad_seleccionada}")

        # Cargar datos basados en los filtros seleccionados
        self.cargar_datos(ciudad_seleccionada, buque_seleccionado, owner_seleccionado)

    def cargar_datos(self, ciudad_seleccionada, buque_seleccionado, owner):
        session = get_db_session()
        ciudad_seleccionada = CITY_AIRPORT_CODES.get(ciudad_seleccionada)

        buque_seleccionado = buque_seleccionado.lower()

        ciudad_select = CITY_TO_AIRPORT_CODES.get(ciudad_seleccionada)
        print(ciudad_select)
        # Obtener fechas seleccionadas
        fecha_inicio = self.date_start1.date().toPyDate()
        fecha_fin = datetime.combine(self.date_end1.date().toPyDate(), time.max)

        hotel_necesario = (
            session.query(
                Buque.empresa.label("Owner"),
                Tripulante.tripulante_id,
                Tripulante.estado.label("Estado"),
                Tripulante.nombre.label("First_Name"),
                Tripulante.apellido.label("Last_Name"),
                Tripulante.sexo.label("Genero"),
                Tripulante.nacionalidad.label("Nacionalidad"),
                Tripulante.posicion.label("Position"),
                TripulanteHotel.categoria.label("Categoria"),
                Hotel.ciudad.label("Ciudad_Hotel"),
                Hotel.nombre.label("Nombre_Hotel"),
                TripulanteHotel.fecha_entrada.label("check_in"),
                TripulanteHotel.fecha_salida.label("check_out"),
                TripulanteHotel.tipo_habitacion.label("Rooms")
            )
            .join(TripulanteHotel, Tripulante.tripulante_id == TripulanteHotel.tripulante_id)
            .join(Buque, Tripulante.buque_id == Buque.buque_id)
            .join(Hotel, Hotel.hotel_id == TripulanteHotel.hotel_id)
            .filter(or_(
                func.lower(Hotel.ciudad) == ciudad_select.lower(),
                func.lower(Hotel.ciudad) == ciudad_select.lower() #CAMBIE LA CONSULTA PORQUE YA NO SE GUARDAN CIUDADES COMO DAY USE O HOTEL 
            ))
        )

        #for tripulante in hotel_necesario:
        #    print(f"Nombre: {tripulante.First_Name}, Check-in: {tripulante.check_in}, Check-out: {tripulante.check_out}")

        if buque_seleccionado != "buque":
            hotel_necesario = hotel_necesario.filter(func.lower(Buque.nombre) == buque_seleccionado)

        if owner != "Owner":
            hotel_necesario = hotel_necesario.filter((Buque.empresa) == owner)

        if self.check_fecha.isChecked():
            # Obtener las fechas seleccionadas de la interfaz
            fecha_inicio_date = datetime.combine(fecha_inicio, time.min)  # Primer momento del día
            fecha_fin_date = datetime.combine(fecha_fin, time.max)  # Último momento del día

            # Obtener las fechas ETA y ETD del tripulante asociado al buque seleccionado
            fechas_eta_etd = (
                session.query(EtaCiudad.eta, EtaCiudad.etd)
                .join(Tripulante, EtaCiudad.tripulante_id == Tripulante.tripulante_id)  
                .join(Buque, Tripulante.buque_id == Buque.buque_id) 
                .filter(func.lower(Buque.nombre) == buque_seleccionado)
                .filter(EtaCiudad.eta >= fecha_inicio_date, EtaCiudad.eta <= fecha_fin_date)
                .first()
            )

            if fechas_eta_etd:
                eta = fechas_eta_etd.eta.date()  # Convertir a date
                etd = fechas_eta_etd.etd.date()  # Convertir a date

                # Filtrar por las fechas de entrada y salida del hotel
                hotel_necesario = hotel_necesario.filter(
                    TripulanteHotel.fecha_entrada >= eta,
                    TripulanteHotel.fecha_salida <= etd
                )


        # Ordenar los resultados
        hotel_necesario = hotel_necesario.order_by(
            TripulanteHotel.categoria,  # Ordenar por Categoria
            TripulanteHotel.fecha_entrada,  # Check-in
            case(
                (func.lower(TripulanteHotel.tipo_habitacion) == "single", 1),
                (func.lower(TripulanteHotel.tipo_habitacion) == "double", 2),
                (func.lower(TripulanteHotel.tipo_habitacion) == "triple", 3),
                else_=4  # Cualquier otro tipo de habitación
            ),
            case(
                (Tripulante.sexo == "F", 1),
                (Tripulante.sexo == "M", 2),
                else_=3  # Otros valores posibles
            )
        )

        # Obtener los resultados de la consulta
        resultados = hotel_necesario.all()

        # Limpiar tabla y mostrar resultados
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(11)
        self.table_widget.setHorizontalHeaderLabels(
            ["Owner", "First Name", "Last Name", "Gender", "Nacionalidad", "Position", "Categoria", "Hotel Ciudad", "Check In", "Check Out", "Rooms"]
        )

        # Rellenar la tabla con los resultados
        for resultado in resultados:
            row = self.table_widget.rowCount()
            self.table_widget.insertRow(row)

            # Asumiendo que resultado es una tupla y que los índices coinciden con los campos de la consulta
            self.table_widget.setItem(row, 0, QTableWidgetItem(resultado.Owner)) 
            self.table_widget.setItem(row, 1, QTableWidgetItem(resultado.First_Name))  # First Name
            self.table_widget.setItem(row, 2, QTableWidgetItem(resultado.Last_Name))   # Last Name
            self.table_widget.setItem(row, 3, QTableWidgetItem(resultado.Genero))      # Gender
            self.table_widget.setItem(row, 4, QTableWidgetItem(resultado.Nacionalidad)) # Nacionalidad
            self.table_widget.setItem(row, 5, QTableWidgetItem(resultado.Position))     # Position
            self.table_widget.setItem(row, 6, QTableWidgetItem(str(resultado.Categoria))) # Categoria
            hotel_info = f"{resultado.Ciudad_Hotel}, {resultado.Nombre_Hotel}"
            self.table_widget.setItem(row, 7, QTableWidgetItem(hotel_info))  # Ciudad y Nombre del Hotel            
            self.table_widget.setItem(row, 8, QTableWidgetItem(str(resultado.check_in.date())))  # Check In sin hora
            self.table_widget.setItem(row, 9, QTableWidgetItem(str(resultado.check_out.date())))
            # Normalizar el texto de Rooms
            rooms_value = resultado.Rooms.capitalize() if resultado.Rooms else "N/A"
            # Agregar a la tabla
            self.table_widget.setItem(row, 10, QTableWidgetItem(rooms_value))  # Rooms

    def generar_excel(self, hotel_seleccionado, buque_seleccionado, fecha_inicio, fecha_fin):
        # Crear un DataFrame con los datos de la tabla
        data = []
        for row in range(self.table_widget.rowCount()):
            row_data = []
            for column in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, column)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        # Definir los nombres de las columnas
        column_names = ["Owner", "First name", "Last name", "Gender", "Nacionalidad", "Position", 
                        "Categoria", "Hotel Ciudad", "Check in", "Check out", "Rooms"]

        df = pd.DataFrame(data, columns=column_names)

        df.insert(0, "Nro", range(1, len(df) + 1))

        # Generar nombre de archivo basado en buque y hotel seleccionados
        file_name_parts = ["informe_hotel"]
        if hotel_seleccionado.lower() != "hotel" and hotel_seleccionado.lower() not in file_name_parts:
            file_name_parts.append(hotel_seleccionado)
        if buque_seleccionado.lower() != "buque" and buque_seleccionado.lower() not in file_name_parts:
            file_name_parts.append(buque_seleccionado)

        file_name = "_".join(file_name_parts) + ".xlsx"

        # Guardar archivo Excel
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar archivo Excel",
            file_name,
            "Excel Files (*.xlsx);;All Files (*)"
        )

        if file_path:
            wb = Workbook()
            ws = wb.active

            # Encabezados personalizados
            ws.cell(row=1, column=1, value="BUQUE").font = Font(bold=True)
            ws.cell(row=1, column=2, value=buque_seleccionado if buque_seleccionado else "N/A")

            ws.cell(row=2, column=1, value="CIUDAD").font = Font(bold=True)
            ws.cell(row=2, column=2, value=hotel_seleccionado if hotel_seleccionado else "N/A")

            # Verificar si se seleccionaron fechas de inicio y fin
            if self.check_fecha.isChecked() and fecha_inicio and fecha_fin:
                ws.cell(row=3, column=1, value="ETA Desde:").font = Font(bold=True)
                ws.cell(row=3, column=2, value=fecha_inicio)
                ws.cell(row=4, column=1, value="ETA Hasta:").font = Font(bold=True)
                ws.cell(row=4, column=2, value=fecha_fin)
            else:
                # Dejar las celdas vacías si no se seleccionaron fechas
                ws.cell(row=3, column=1, value="")
                ws.cell(row=3, column=2, value="")
                ws.cell(row=4, column=1, value="")
                ws.cell(row=4, column=2, value="")

            # Escribir el texto final antes de la tabla
            ws.cell(row=6, column=1, value="Informe necesidad hotel").font = Font(bold=True)

            # Aplicar negrita a los encabezados
            header_fill = PatternFill(start_color='ADD8E6', end_color='ADD8E6', fill_type='solid')
            for col_num, col_name in enumerate(df.columns, 1):
                cell = ws.cell(row=7, column=col_num)  # Cambiar a fila 7
                cell.value = col_name
                cell.fill = header_fill
                cell.font = Font(bold=True)  # Negrita

            # Escribir los datos del DataFrame
            data_fill = PatternFill(start_color='FFFF99', end_color='FFFF99', fill_type='solid')
            for row_num, row_data in enumerate(df.values, start=8):  # Cambiar a fila 8
                for col_num, cell_value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_num, column=col_num)
                    cell.value = cell_value
                    cell.fill = data_fill

            # Centrar el número correlativo
            for row_num in range(8, len(df) + 8):  # Cambiar el rango según donde se escriban los datos
                ws.cell(row=row_num, column=1).alignment = Alignment(horizontal='center')

            # Ajustar el ancho de las columnas
            for col_num in range(1, len(df.columns) + 1):
                max_length = 0
                column = get_column_letter(col_num)
                for row in ws[column]:
                    try:
                        if len(str(row.value)) > max_length:
                            max_length = len(str(row.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)  # Agregar un poco de espacio extra
                ws.column_dimensions[column].width = adjusted_width

            # Guardar el archivo Excel
            wb.save(file_path)

    def toggle_fecha_fields(self):
        is_checked = self.check_fecha.isChecked()
        self.date_start1.setEnabled(is_checked)
        self.date_end1.setEnabled(is_checked)

    def volver_a_opciones_programar(self):
        self.main_window.stacked_widget.setCurrentIndex(self.main_window.menu_reportes_index)

class RoomListScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        session = get_db_session()
        layout = QVBoxLayout(self)

        # Llenar el combo de buques desde la base de datos
        self.combo_buques = QComboBox()
        self.combo_buques.addItem("Buque")  # Agregar un valor por defecto

        buques = session.query(Buque.nombre).distinct().all()  # Consulta para obtener los nombres de los buques
        for buque in buques:
            self.combo_buques.addItem(buque.nombre)
        layout.addWidget(self.combo_buques)

        # Llenar el combo de hoteles desde la base de datos
        self.combo_hoteles = QComboBox()
        self.combo_hoteles.addItem("Hotel")  # Agregar un valor por defecto

        hoteles = session.query(Hotel.nombre).distinct().all()  # Consulta para obtener los nombres de los hoteles
        for hotel in hoteles:
            self.combo_hoteles.addItem(hotel.nombre)
        layout.addWidget(self.combo_hoteles)

        # Llenar el combo de ciudades desde la base de datos
        self.combo_ciudades = QComboBox()
        self.combo_ciudades.addItem("Ciudad")  # Agregar un valor por defecto

        ciudades = session.query(Hotel.ciudad).distinct().all()  # Consulta para obtener las ciudades únicas
        for ciudad in ciudades:
            self.combo_ciudades.addItem(ciudad.ciudad)
        layout.addWidget(self.combo_ciudades)

        # Llenar el combo de owners desde la base de datos
        self.combo_owners = QComboBox()
        self.combo_owners.addItem("Owner")  # Agregar un valor por defecto

        owners = session.query(Buque.empresa).distinct().all()  # Consulta para obtener los owners únicos
        for owner in owners:
            self.combo_owners.addItem(owner.empresa)
        layout.addWidget(self.combo_owners)

        self.check_fecha = QCheckBox("Habilitar filtro por fecha de ETA")
        self.check_fecha.setChecked(False)  # Inicialmente deshabilitado
        self.check_fecha.stateChanged.connect(self.toggle_fechas)  # Conectar evento de cambio de estado
        self.check_fecha.stateChanged.connect(self.actualizar_datos)  # Conectar evento de cambio de estado
        layout.addWidget(self.check_fecha)

        # Layout horizontal para las fechas
        layout_filtro = QHBoxLayout()

        # Selector de fecha de inicio
        self.date_start1 = QDateEdit()
        self.date_start1.setCalendarPopup(True)
        self.date_start1.setDate(QDate.currentDate())
        self.date_start1.setEnabled(False)  # Inicialmente deshabilitado
        layout_filtro.addWidget(QLabel("Fecha ETA inicio:"))
        layout_filtro.addWidget(self.date_start1)

        # Agregar el layout horizontal al layout principal
        layout.addLayout(layout_filtro)

        # Label para mostrar asistencias
        self.label = QLabel()
        layout.addWidget(self.label)

        # Tabla para mostrar datos
        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        # Botón para generar el Excel
        button_generar_excel = QPushButton("Generar Excel")
        button_generar_excel.clicked.connect(self.generar_excel_con_ciudad)
        layout.addWidget(button_generar_excel)

        # Botón "Volver" para regresar a la pantalla anterior
        button_volver = QPushButton("Volver")
        button_volver.setFixedWidth(100)
        button_volver.clicked.connect(self.volver_a_opciones_programar)
        layout.addWidget(button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        # Conectar cambios en los QComboBox
        self.combo_hoteles.currentTextChanged.connect(self.actualizar_datos)
        self.combo_buques.currentTextChanged.connect(self.actualizar_datos)
        self.combo_ciudades.currentTextChanged.connect(self.actualizar_datos)
        self.combo_owners.currentTextChanged.connect(self.actualizar_datos)
        self.date_start1.dateChanged.connect(self.actualizar_datos)

        # Actualizar datos inicialmente
        self.actualizar_datos()

    def generar_excel_con_ciudad(self):
        hotel_seleccionado = self.combo_hoteles.currentText()  # Obtener la ciudad seleccionada
        buque_seleccionado = self.combo_buques.currentText()  # Obtener la ciudad seleccionada
        ciudad_seleccionada = self.combo_ciudades.currentText()  # Obtiene la ciudad seleccionada
        owner_seleccionado = self.combo_owners.currentText()  # Obtiene la ciudad seleccionada
        self.generar_excel(hotel_seleccionado, buque_seleccionado, ciudad_seleccionada, owner_seleccionado)  # Llamar a generar_excel con la ciudad seleccionada

    def actualizar_datos(self):
        hotel_seleccionado = self.combo_hoteles.currentText()  # Obtiene la ciudad seleccionada
        buque_seleccionado = self.combo_buques.currentText()  # Obtiene la ciudad seleccionada
        ciudad_seleccionada = self.combo_ciudades.currentText()  # Obtiene la ciudad seleccionada
        owner_seleccionado = self.combo_owners.currentText()  # Obtiene la ciudad seleccionada
        self.label.setText(f"Room list en {hotel_seleccionado}")  # Actualiza el label

        # Cargar datos en la tabla
        self.cargar_datos(hotel_seleccionado, buque_seleccionado, ciudad_seleccionada, owner_seleccionado)

    def toggle_fechas(self):
        # Habilitar/deshabilitar según el estado del checkbox
        estado = self.check_fecha.isChecked()
        self.date_start1.setEnabled(estado)

    def cargar_datos(self, hotel_seleccionado, buque_seleccionado, ciudad_seleccionada, owner_seleccionado):
        session = get_db_session()  # Obtener la sesión de la base de datos

        # Convertir las entradas a minúsculas para comparación
        hotel_seleccionado = hotel_seleccionado.lower()
        buque_seleccionado = buque_seleccionado.lower()
        ciudad_seleccionada = ciudad_seleccionada.lower()
        owner_seleccionado = owner_seleccionado.lower()

        # Obtener las fechas seleccionadas en QDateEdit
        fecha_inicio = self.date_start1.date().toPyDate()  # Convertir a objeto de fecha de Python
        fecha_fin = datetime.combine(self.date_start1.date().toPyDate(), time.max)  # Combinar con la hora máxima del día

        # Construir la consulta de roomlist
        roomlist_query = (
            session.query(
                Tripulante.tripulante_id.label("ID"),
                Hotel.nombre.label("Nombre_hotel"),
                TripulanteHotel.fecha_entrada.label("check_in"),
                TripulanteHotel.fecha_salida.label("check_out"),
                TripulanteHotel.tipo_habitacion.label("Rooms"),
                Tripulante.nombre.label("First_Name"),
                Tripulante.apellido.label("Last_Name"),
                Tripulante.sexo.label("Gender"),
                Tripulante.nacionalidad.label("Nacionalidad"),
                Tripulante.posicion.label("Position"),
                Buque.empresa.label("Owner"),
                TripulanteHotel.categoria.label("Categoria")
            )
            .join(Buque, Buque.buque_id == Tripulante.buque_id)
            .filter(Tripulante.buque_id == EtaCiudad.buque_id)
            .filter(Tripulante.tripulante_id == EtaCiudad.tripulante_id)
            .filter(Tripulante.tripulante_id == TripulanteHotel.tripulante_id)
            .filter(TripulanteHotel.hotel_id == Hotel.hotel_id)
            .distinct()
        )

        # Aplicar filtro de hotel si se seleccionó uno específico
        if hotel_seleccionado != "hotel":
            roomlist_query = roomlist_query.filter(func.lower(Hotel.nombre) == hotel_seleccionado)

        # Aplicar filtro de buque si se seleccionó uno específico
        if buque_seleccionado != "buque":
            roomlist_query = roomlist_query.filter(func.lower(Buque.nombre) == buque_seleccionado)

        if ciudad_seleccionada != "ciudad":
            roomlist_query = roomlist_query.filter(func.lower(Hotel.ciudad) == ciudad_seleccionada)

        if owner_seleccionado != "owner":
            roomlist_query = roomlist_query.filter(func.lower(Buque.empresa) == owner_seleccionado)

        # Aplicar filtro de ETA por rango de fechas si está habilitado
        if self.check_fecha.isChecked():
            roomlist_query = (
                roomlist_query
                .join(EtaCiudad, and_(
                    Tripulante.buque_id == EtaCiudad.buque_id,
                    EtaCiudad.eta >= fecha_inicio,
                    EtaCiudad.eta <= fecha_fin
                ))
                .filter(
                    EtaCiudad.eta >= fecha_inicio,
                    EtaCiudad.eta <= fecha_fin
                )
            )

        # Limpiar la tabla
        headers = ["Owner", "First Name", "Last Name", "Gender", "Nacionalidad", "Position", "Categoria", "Check In", "Check Out", "Rooms"]

        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(len(headers))  # Número correcto de columnas
        self.table_widget.setHorizontalHeaderLabels(headers)

        roomlist_query = roomlist_query.order_by(TripulanteHotel.categoria, TripulanteHotel.fecha_entrada)

        self.tripulante_ids = []

        # Convertir 'Check In' a datetime
        # df['Check In'] = pd.to_datetime(df['Check In'], errors='coerce')

        # # Ordenar el DataFrame primero por 'Check In', luego por 'Position' y finalmente por 'Gender'
        # df = df.sort_values(by=["Categoria", "Check In", "Gender"])

        # # Formatear 'Check In' de nuevo a string con el formato deseado
        # df['Check In'] = df['Check In'].dt.strftime('%Y-%m-%d')

        # Llenar la tabla con los resultados de la consulta
        for roomlist in roomlist_query:
            if str(roomlist.Categoria) != "0":
                row = self.table_widget.rowCount()
                self.table_widget.insertRow(row)
                self.tripulante_ids.append(roomlist.ID)
                
                self.table_widget.setItem(row, 0, QTableWidgetItem(str(roomlist.Owner)))  # First Name
                self.table_widget.setItem(row, 1, QTableWidgetItem(str(roomlist.First_Name)))  # First Name
                self.table_widget.setItem(row, 2, QTableWidgetItem(str(roomlist.Last_Name)))  # Last Name
                self.table_widget.setItem(row, 3, QTableWidgetItem(str(roomlist.Gender)))  # Gender
                self.table_widget.setItem(row, 4, QTableWidgetItem(str(roomlist.Nacionalidad)))  # Nacionalidad
                self.table_widget.setItem(row, 5, QTableWidgetItem(str(roomlist.Position)))  # Position
                self.table_widget.setItem(row, 6, QTableWidgetItem(str(roomlist.Categoria)))  # Position
                
                # Check In
                self.table_widget.setItem(row, 7, QTableWidgetItem(str(roomlist.check_in) if roomlist.check_in else ""))
                # Check Out
                self.table_widget.setItem(row, 8, QTableWidgetItem(str(roomlist.check_out) if roomlist.check_out else ""))
                # Rooms
                self.table_widget.setItem(row, 9, QTableWidgetItem(str(roomlist.Rooms) if roomlist.Rooms else ""))

    def generar_excel(self, hotel_seleccionado, buque_seleccionado, ciudad_seleccionada, owner_seleccionado):
        def incrementar_grupo(group_counter):
            group_list = list(group_counter)
            i = len(group_list) - 1
            while i >= 0:
                if group_list[i] != 'Z':
                    group_list[i] = chr(ord(group_list[i]) + 1)
                    return ''.join(group_list)
                else:
                    group_list[i] = 'A'
                    i -= 1
            return 'A' + ''.join(group_list)

        data = []
        for row in range(self.table_widget.rowCount()):
            row_data = []
            for column in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, column)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        column_names = [self.table_widget.horizontalHeaderItem(i).text() for i in range(self.table_widget.columnCount())]
        df = pd.DataFrame(data, columns=column_names)

        # Agregar el tripulante_id al DataFrame como una columna separada
        df['ID'] = self.tripulante_ids

        # Convertir 'Check In' a datetime para ordenar correctamente
        df['Check In'] = pd.to_datetime(df['Check In'], errors='coerce')

        # Realiza cualquier lógica que necesites usando el 'ID'
        for idx, row in df.iterrows():
            tripulante_id = row['ID']
            #print(f"Procesando ID: {tripulante_id}")

        # Ordenar el DataFrame por 'Categoria', 'Check In', 'Gender' en orden ascendente y 'Rooms' en orden descendente
        df = df.sort_values(by=["Categoria", "Check In", "Gender", "Rooms"], ascending=[True, True, True, False]).reset_index(drop=True)

        # Formatear 'Check In' de nuevo a string con el formato deseado
        df['Check In'] = df['Check In'].dt.strftime('%Y-%m-%d')

        df.insert(0, "Nro", range(1, len(df) + 1))

        group_counter = 'A'
        double_buffer_m = []  # Buffer para hombres
        double_buffer_f = []  # Buffer para mujeres

        #print(df)
        idx_categoria = pd.to_numeric(df['Categoria']).min()

        for idx, row in df.iterrows():
            tripulante_id = row['ID']
            room_type = row['Rooms'].lower()
            gender = row['Gender'].lower()
            categoria = pd.to_numeric(row['Categoria']).min()
            check_in = ['Check In']

            if idx + 1 < len(df):
                tripulante_id_next = df.iloc[idx + 1]['ID']
                check_in_next = df.iloc[idx + 1]['Check In']
                #print(f"ID actual: {tripulante_id} | ID siguiente: {tripulante_id_next} | Check in: {check_in_next} ")

            if idx_categoria != categoria:
                idx_categoria += 1
                double_buffer_m = []  # Limpia el buffer de hombres
                double_buffer_f = []  # Limpia el buffer de hombres
            
            # Verifica si es una habitación doble
            if "doble" in room_type:                
                # Gestión para hombres
                print(gender)
                if gender == "m":
                    double_buffer_m.append(idx)

                    # Si hay un solo hombre en el buffer, asigna el grupo provisional
                    if len(double_buffer_m) == 1:
                        #print(f"A | {group_counter}\n")
                        group_aux_m = group_counter
                        #print(f"A | {group_aux_m}\n")
                        df.loc[double_buffer_m, 'Grupo'] = group_aux_m
                        group_counter = incrementar_grupo(group_counter)

                    # Si hay dos hombres en el buffer, asigna el grupo definitivo y limpia el buffer
                    if len(double_buffer_m) == 2 and categoria == idx_categoria:
                        #print(f"B | {group_aux_m}\n")
                        df.loc[double_buffer_m, 'Grupo'] = group_aux_m
                        double_buffer_m = []  # Limpia el buffer de hombres
                    elif len(double_buffer_m) == 2 and categoria != idx_categoria:
                        #print(f"C | {group_counter}\n")
                        df.loc[double_buffer_m, 'Grupo'] = group_counter
                        double_buffer_m = []  # Limpia el buffer de hombres
                        group_counter = incrementar_grupo(group_counter)
                        #idx_categoria += 1


                # Gestión para mujeres
                elif gender == "f":
                    double_buffer_f.append(idx)

                    # Si hay una sola mujer en el buffer, asigna el grupo provisional
                    if len(double_buffer_f) == 1:
                        #print(f"D | {group_counter}\n")
                        group_aux_f = group_counter
                        df.loc[double_buffer_f, 'Grupo'] = group_aux_f
                        group_counter = incrementar_grupo(group_counter)

                    # Si hay dos mujeres en el buffer, asigna el grupo definitivo y limpia el buffer
                    if len(double_buffer_f) == 2 and categoria == idx_categoria:
                        #print(f"E | {group_aux_m}\n")
                        df.loc[double_buffer_f, 'Grupo'] = group_aux_f
                        double_buffer_f = []  # Limpia el buffer de mujeres
                    elif len(double_buffer_f) == 2 and categoria != idx_categoria:
                        #print(f"F | {group_counter}\n")
                        df.loc[double_buffer_f, 'Grupo'] = group_counter
                        double_buffer_f = []  # Limpia el buffer de hombres
                        group_counter = incrementar_grupo(group_counter)
                        #idx_categoria += 1

            # Gestión para habitaciones individuales
            elif "single" in room_type:
                df.loc[idx, 'Grupo'] = group_counter
                group_counter = incrementar_grupo(group_counter)

            # Si no se encuentra una categoría conocida, asigna un grupo vacío
            else:
                df.loc[idx, 'Grupo'] = ""

            if tripulante_id == tripulante_id_next and check_in != check_in_next:
                #print("Limpie el buffer")
                double_buffer_m = []  # Limpia el buffer de hombres
                double_buffer_f = []

        df = df.drop('ID', axis=1)

        file_name_parts = ["room_list"]
        if hotel_seleccionado.lower() != "hotel" and hotel_seleccionado.lower() not in file_name_parts:
            file_name_parts.append(hotel_seleccionado)
        if buque_seleccionado.lower() != "buque" and buque_seleccionado.lower() not in file_name_parts:
            file_name_parts.append(buque_seleccionado)
        if ciudad_seleccionada.lower() != "ciudad" and ciudad_seleccionada.lower() not in file_name_parts:
            file_name_parts.append(ciudad_seleccionada)

        file_name = "_".join(file_name_parts) + ".xlsx"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar archivo Excel",
            file_name,
            "Excel Files (*.xlsx);;All Files (*)"
        )

        if file_path:
            wb = Workbook()
            ws = wb.active

            cell = ws.cell(row=1, column=1, value="VESSEL")
            cell.font = Font(bold=True)

            cell = ws.cell(row=1, column=2)
            cell.value = buque_seleccionado if buque_seleccionado.lower() != "buque" else "Todos"
            cell.font = Font(bold=True)

            cell = ws.cell(row=2, column=1)
            cell.value = "HOTEL"
            cell.font = Font(bold=True)

            cell = ws.cell(row=2, column=2)
            cell.value = hotel_seleccionado if hotel_seleccionado.lower() != "hotel" else "Todos"
            cell.font = Font(bold=True)

            if self.check_fecha.isChecked():
                fecha_inicio = self.date_start1.date().toPyDate()
                fecha_fin = datetime.combine(self.date_end1.date().toPyDate(), time.max)
            else:
                fecha_inicio = None
                fecha_fin = None

            cell = ws.cell(row=3, column=1)
            cell.value = "FECHA"
            cell.font = Font(bold=True)

            cell = ws.cell(row=3, column=2)
            if fecha_inicio is not None:
                cell.value = f"{fecha_inicio} - {fecha_fin}"
            else:
                cell.value = ""

            # Paso 1: Filtrar solo las habitaciones que contienen "doble" o "single", ignorando mayúsculas/minúsculas
            filtered_df = df[df['Rooms'].str.lower().str.contains('doble|single', na=False)]

            # Normalizar la columna 'Rooms' en minúsculas solo en el DataFrame filtrado
            filtered_df['Rooms'] = filtered_df['Rooms'].str.lower()

            # Paso 2: Eliminar duplicados por 'Categoria' y 'Grupo' para contar habitaciones dobles como una sola
            filtered_df = filtered_df.drop_duplicates(subset=['Categoria', 'Grupo', 'Rooms'])

            # Paso 3: Agrupar y contar habitaciones por 'Categoria' y 'Rooms' (doble o single)
            conteo_habitaciones = (
                filtered_df.groupby(['Categoria', 'Rooms'])['Rooms']
                .count()
                .unstack(fill_value=0)
                .reindex(columns=['doble', 'single'], fill_value=0)  # Asegurar que tenga solo las columnas 'doble' y 'single'
                .reset_index()
            )

            # Renombrar columnas para claridad
            conteo_habitaciones.columns = ['Categoria', 'Cantidad de Dobles', 'Cantidad de Singles']


            # Escribir encabezados en Excel
            ws.cell(row=1, column=4, value="Categoria").font = Font(bold=True)
            ws.cell(row=1, column=5, value="Cantidad de Singles").font = Font(bold=True)
            ws.cell(row=1, column=6, value="Cantidad de Dobles").font = Font(bold=True)

            # Escribir el conteo de habitaciones en Excel
            for idx, row in conteo_habitaciones.iterrows():
                ws.cell(row=2 + idx, column=4, value=row['Categoria'])
                ws.cell(row=2 + idx, column=5, value=row['Cantidad de Singles'])
                ws.cell(row=2 + idx, column=6, value=row['Cantidad de Dobles'])

            # Imprimir el conteo de habitaciones por categoría para depuración (opcional)
            #print(conteo_habitaciones['Categoria'])

            # Escribir el texto antes de la tabla
            ws.cell(row=5, column=1, value="Informe roomlist").font = Font(bold=True)

            header_fill = PatternFill(start_color='ADD8E6', end_color='ADD8E6', fill_type='solid')
            data_fill = PatternFill(start_color='FFFF99', end_color='FFFF99', fill_type='solid')

            for col_num, col_name in enumerate(df.columns, 1):
                cell = ws.cell(row=6, column=col_num)
                cell.value = col_name
                cell.fill = header_fill

            for row_num, row_data in enumerate(df.values, start=7):
                for col_num, cell_value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_num, column=col_num)
                    cell.value = cell_value
                    cell.fill = data_fill

                    # Centrar el número correlativo
                    if col_num == 1:  # Columna "Nro"
                        cell.alignment = Alignment(horizontal="left")

            # Ajustar automáticamente el ancho de las columnas
            for col in ws.columns:
                max_length = 0
                column = col[0].column_letter  # Get the column name
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = max_length + 1
                ws.column_dimensions[column].width = adjusted_width

            wb.save(file_path)

    def volver_a_opciones_programar(self):
        self.main_window.stacked_widget.setCurrentIndex(self.main_window.opciones_programar_index)

class TransportesScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        session = get_db_session()
        layout = QVBoxLayout(self)

        # Llenar el combo de ciudades desde la base de datos
        self.combo_ciudades = QComboBox()
        self.combo_ciudades.addItem("Ciudad")  # Agregar un valor por defecto

        ciudades = session.query(Transporte.city_in).distinct().all()  # Consulta para obtener las ciudades únicas
        for ciudad in ciudades:
            self.combo_ciudades.addItem(ciudad.city_in)
            #print(ciudad.ciudad)
        layout.addWidget(self.combo_ciudades)

        self.check_fecha = QCheckBox("Habilitar filtro por fechas")
        self.check_fecha.setChecked(False)  # Inicialmente deshabilitado
        self.check_fecha.stateChanged.connect(self.actualizar_datos)  # Conectar evento de cambio de estado
        layout.addWidget(self.check_fecha)

        # Layout horizontal para las fechas
        layout_filtro = QHBoxLayout()

        # Selector de fecha de inicio
        self.date_start1 = QDateEdit()
        self.date_start1.setCalendarPopup(True)
        self.date_start1.setDate(QDate.currentDate())
        layout_filtro.addWidget(QLabel("Fecha inicio:"))
        layout_filtro.addWidget(self.date_start1)

        # Selector de fecha de fin
        self.date_end1 = QDateEdit()
        self.date_end1.setCalendarPopup(True)
        self.date_end1.setDate(QDate.currentDate())
        layout_filtro.addWidget(QLabel("Fecha fin:"))
        layout_filtro.addWidget(self.date_end1)

        layout.addLayout(layout_filtro)

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
        button_volver.clicked.connect(self.volver_a_opciones_programar)
        layout.addWidget(button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        # Conectar el cambio en el QComboBox a un método
        self.combo_ciudades.currentTextChanged.connect(self.actualizar_datos)
        self.date_start1.dateChanged.connect(self.actualizar_datos)
        self.date_end1.dateChanged.connect(self.actualizar_datos)

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

    def toggle_fechas(self, state):
        enabled = state == Qt.CheckState.Checked  # Verificar si el checkbox está marcado
        self.date_start1.setEnabled(enabled)
        self.date_end1.setEnabled(enabled)
        # Deshabilitar el cuadro emergente si está desmarcado
        self.date_start1.setCalendarPopup(enabled)
        self.date_end1.setCalendarPopup(enabled)

    def cargar_datos(self, ciudad_seleccionada):
        session = get_db_session()
        ciudad_seleccionada = str(ciudad_seleccionada).lower()
        print(ciudad_seleccionada)

        fecha_inicio = self.date_start1.date().toPyDate()
        fecha_fin = datetime.combine(self.date_end1.date().toPyDate(), time.max)

        # Construir la consulta de transporte
        transporte_necesario = (
            session.query(
                Tripulante.tripulante_id,
                Tripulante.estado.label("Estado"),
                Tripulante.nombre.label("First_Name"),
                Tripulante.apellido.label("Last_Name"),
                Tripulante.nacionalidad.label("Nacionalidad"),
                Transporte.city_in.label("Ciudad_Transporte_in"),
                Transporte.place_in.label("Lugar_Transporte_in"),
                Transporte.city_end.label("Ciudad_Transporte_end"),
                Transporte.place_end.label("Lugar_Transporte_end"),
                TripulanteTransporte.date_pickup.label("Fecha_Pickup"),
                TripulanteTransporte.hours_pickup.label("Hora_Pickup")
            )
            .join(TripulanteTransporte, Tripulante.tripulante_id == TripulanteTransporte.tripulante_id)
            .filter(Transporte.transporte_id == TripulanteTransporte.transporte_id)
            .filter(and_(func.lower(Transporte.city_in) == ciudad_seleccionada),
                                                               Transporte.transporte_id == TripulanteTransporte.transporte_id)
        )

        if self.check_fecha.isChecked():
            transporte_necesario = transporte_necesario.filter(
                TripulanteTransporte.date_pickup >= fecha_inicio,
                TripulanteTransporte.date_pickup <= fecha_fin
            )

        hotel_necesario = (
            session.query(
                Tripulante.tripulante_id,
                Tripulante.estado.label("Estado"),
                Tripulante.nombre.label("First_Name"),
                Tripulante.apellido.label("Last_Name"),
                Hotel.ciudad.label("Ciudad_Hotel"),
                Hotel.nombre.label("Nombre_Hotel"),
                TripulanteHotel.fecha_salida.label("Check_Out")
            )
            .join(TripulanteHotel, Tripulante.tripulante_id == TripulanteHotel.tripulante_id)
            .filter(Hotel.hotel_id == TripulanteHotel.hotel_id)
            .filter(func.lower(Hotel.ciudad) == ciudad_seleccionada)
            .distinct()
        )

        if ciudad_seleccionada != "ciudad":    
            ciudad_seleccionada = CITY_AIRPORT_CODES.get(ciudad_seleccionada.upper())

        vuelo_necesario = (
            session.query(
                Tripulante.tripulante_id,
                Tripulante.estado.label("Estado"),
                Tripulante.nombre.label("First_Name"),
                Tripulante.apellido.label("Last_Name"),
                Vuelo.codigo.label("Codigo"),
                Vuelo.fecha.label("Fecha"),
                Vuelo.hora_salida.label("Hora_Salida"),
                Vuelo.hora_llegada.label("Hora_Llegada"),
                Vuelo.aeropuerto_salida.label("Aeropuerto_Salida"),
                Vuelo.aeropuerto_llegada.label("Aeropuerto_Llegada")
            )
            .join(TripulanteVuelo, Tripulante.tripulante_id == TripulanteVuelo.tripulante_id)
            .filter(Vuelo.vuelo_id == TripulanteVuelo.vuelo_id)
            .filter(or_(
                func.lower(Vuelo.aeropuerto_salida) == ciudad_seleccionada.lower(),
                func.lower(Vuelo.aeropuerto_llegada) == ciudad_seleccionada.lower()
            ))
            .distinct()
        )

        buque_necesario = (
            session.query(
                Tripulante.tripulante_id,
                Buque.nombre.label("Nombre_Buque"),
                Buque.empresa.label("Owner"),  # Agregar la columna "empresa"
                EtaCiudad.eta.label("Eta")
            )
            .join(EtaCiudad, Tripulante.tripulante_id == EtaCiudad.tripulante_id)
            .join(Buque, EtaCiudad.buque_id == Buque.buque_id)
            .filter(Buque.buque_id == EtaCiudad.buque_id)
            .distinct()
        )

        transporte_necesario = transporte_necesario.all()
        hotel_necesario = hotel_necesario.all()
        vuelo_necesario = vuelo_necesario.all()
        buque_necesario = buque_necesario.all()

        #print(buque_necesario)

        # Organizar vuelos y transportes por tripulante_id
        transporte_dict = defaultdict(list)
        for transporte in transporte_necesario:
            transporte_dict[transporte.tripulante_id].append(transporte)

        vuelo_dict = defaultdict(list)
        for vuelo in vuelo_necesario:
            vuelo_dict[vuelo.tripulante_id].append(vuelo)

        hotel_dict = {hotel.tripulante_id: hotel for hotel in hotel_necesario}
        buque_dict = {buque.tripulante_id: (buque.Owner, buque.Nombre_Buque, buque.Eta) for buque in buque_necesario}

        headers = ["Estado", "Desde Ciudad Lugar", "Desde Ciudad Destino", "Hasta Ciudad Lugar", "Hasta Ciudad Destino", "Nombre Hotel", "Código Vuelo Llegada", "Date Llegada", "Hora Llegada", "Hora Pick Up", "Lugar Pick Up", "Código Vuelo Salida", "Date Salida", "Fecha Salida", "Owner", "Nave", "ETA", "First Name", "Last Name", "Nacionalidad"]
        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)
        self.table_widget.setRowCount(0)

        # Construir filas para cada tripulante con vuelos y transportes
        for tripulante_id, transportes in transporte_dict.items():
            vuelos = vuelo_dict.get(tripulante_id, [])
            hotel = hotel_dict.get(tripulante_id)
            owner, buque, eta = buque_dict.get(tripulante_id, ("", "", ""))  # Obtener el valor de "Owner"

            # Filtrar y asociar transporte al vuelo correcto
            for transporte in transportes:
                #print(transporte)
                tramo = f"{transporte.Lugar_Transporte_in}-{transporte.Lugar_Transporte_end}"
                #print(tramo)

                if ciudad_seleccionada != "ciudad":
                    #ciudad_code = self.combo_ciudades.currentText()
                    city_select = CITY_AIRPORT_CODES.get(self.combo_ciudades.currentText())

                if 'ATO-HOTEL' == tramo:  # Transporte hacia el hotel
                    # if ciudad_seleccionada == "ciudad":
                    #     city_select = str(vuelo.Aeropuerto_Llegada).lower()

                    vuelos_llegada = [v for v in vuelos if v.Aeropuerto_Llegada.lower() == city_select.lower()]
                    for vuelo in vuelos_llegada:
                        #print(vuelo)
                        row = self.table_widget.rowCount()
                        self.table_widget.insertRow(row)

                        a1 = CITY_TO_AIRPORT_CODES.get(str(vuelo.Aeropuerto_Salida))
                        a2 = CITY_TO_AIRPORT_CODES.get(str(vuelo.Aeropuerto_Llegada))

                        #ciudad = CITY_AIRPORT_CODES.get(transporte.Ciudad_Transporte_in)

                        codigo = f"{str(vuelo.Codigo)} {a1}-{a2}"

                        self.table_widget.setItem(row, 0, QTableWidgetItem(transporte.Estado))
                        self.table_widget.setItem(row, 1, QTableWidgetItem(transporte.Ciudad_Transporte_in))
                        self.table_widget.setItem(row, 2, QTableWidgetItem(transporte.Lugar_Transporte_in))
                        self.table_widget.setItem(row, 3, QTableWidgetItem(transporte.Ciudad_Transporte_end))
                        self.table_widget.setItem(row, 4, QTableWidgetItem(transporte.Lugar_Transporte_end))
                        #self.table_widget.setItem(row, 2, QTableWidgetItem(str(transporte.Fecha)))
                        #self.table_widget.setItem(row, 5, QTableWidgetItem(f"Hotel {hotel.Ciudad_Hotel}" if hotel else f"Hotel {transporte.Ciudad_Transporte_in}"))
                        self.table_widget.setItem(row, 5, QTableWidgetItem(hotel.Nombre_Hotel if hotel else "Sin hotel"))
                        self.table_widget.setItem(row, 6, QTableWidgetItem(codigo))
                        self.table_widget.setItem(row, 7, QTableWidgetItem(str(vuelo.Fecha.date())))
                        self.table_widget.setItem(row, 8, QTableWidgetItem(str(vuelo.Hora_Llegada.time())))
                        self.table_widget.setItem(row, 9, QTableWidgetItem(str(vuelo.Hora_Llegada.time())))
                        self.table_widget.setItem(row, 10, QTableWidgetItem(transporte.Lugar_Transporte_in))
                        #self.table_widget.setItem(row, 7, QTableWidgetItem(aeropuerto_llegada))
                        self.table_widget.setItem(row, 12, QTableWidgetItem(owner))
                        self.table_widget.setItem(row, 13, QTableWidgetItem(buque))
                        self.table_widget.setItem(row, 14, QTableWidgetItem(str(eta)))
                        self.table_widget.setItem(row, 15, QTableWidgetItem(transporte.First_Name))
                        self.table_widget.setItem(row, 16, QTableWidgetItem(transporte.Last_Name))
                        self.table_widget.setItem(row, 17, QTableWidgetItem(transporte.Nacionalidad))

                elif 'HOTEL-ATO' in tramo:  # Transporte desde el hotel
                    # if ciudad_seleccionada == "ciudad":
                    #     city_select = str(vuelo.Aeropuerto_Salida).lower()
                    vuelos_salida = [v for v in vuelos if v.Aeropuerto_Salida.lower() == city_select.lower()]
                    for vuelo in vuelos_salida:
                        #print(vuelo)
                        row = self.table_widget.rowCount()
                        self.table_widget.insertRow(row)

                        a1 = CITY_TO_AIRPORT_CODES.get(str(vuelo.Aeropuerto_Salida))
                        a2 = CITY_TO_AIRPORT_CODES.get(str(vuelo.Aeropuerto_Llegada))

                        if a1 == 'SCL' and a2 == 'PUQ':
                            a1 = f"{a1} Nacional"
                        elif a1 == 'SCL' and a2 != 'PUQ':
                            a1 = f"{a1} Internacional"

                        codigo = f"{str(vuelo.Codigo)} {a1}-{a2}"
                        lugar_pick_up = "Hotel"

                        if a1 == "PUQ":
                            tiempo_a_restar = timedelta(hours=2, minutes=30)
                        elif a1 == "SCL Nacional":
                            tiempo_a_restar = timedelta(hours=2, minutes=30)
                        elif a1 == "SCL Internacional":
                            tiempo_a_restar = timedelta(hours=3, minutes=30)
                        elif a1 == "WPU":
                            tiempo_a_restar = timedelta(hours=1, minutes=30)
                        elif a1 == "KGI":
                            tiempo_a_restar = timedelta(hours=3, minutes=30)
                        else:
                            tiempo_a_restar = timedelta()

                        hora_pick_up = (vuelo.Hora_Salida - tiempo_a_restar).time()

                        self.table_widget.setItem(row, 0, QTableWidgetItem(transporte.Estado))
                        self.table_widget.setItem(row, 1, QTableWidgetItem(transporte.Ciudad_Transporte_in))
                        self.table_widget.setItem(row, 2, QTableWidgetItem(transporte.Lugar_Transporte_in))
                        self.table_widget.setItem(row, 3, QTableWidgetItem(transporte.Ciudad_Transporte_end))
                        self.table_widget.setItem(row, 4, QTableWidgetItem(transporte.Lugar_Transporte_end))
                        #self.table_widget.setItem(row, 2, QTableWidgetItem(str(transporte.Fecha)))
                        #self.table_widget.setItem(row, 2, QTableWidgetItem(f"Hotel {hotel.Ciudad_Hotel}" if hotel else f"NO"))
                        self.table_widget.setItem(row, 5, QTableWidgetItem(hotel.Nombre_Hotel if hotel else "Sin hotel"))
                        self.table_widget.setItem(row, 6, QTableWidgetItem(codigo))
                        self.table_widget.setItem(row, 7, QTableWidgetItem(str(vuelo.Fecha.date())))
                        self.table_widget.setItem(row, 8, QTableWidgetItem(str(vuelo.Hora_Salida.time())))
                        self.table_widget.setItem(row, 9, QTableWidgetItem(str(hora_pick_up)))
                        self.table_widget.setItem(row, 10, QTableWidgetItem(lugar_pick_up))
                        #self.table_widget.setItem(row, 7, QTableWidgetItem(aeropuerto_llegada))
                        self.table_widget.setItem(row, 12, QTableWidgetItem(owner))
                        self.table_widget.setItem(row, 13, QTableWidgetItem(buque))
                        self.table_widget.setItem(row, 14, QTableWidgetItem(str(eta)))
                        #self.table_widget.setItem(row, 13, QTableWidgetItem(buque.ETA))
                        self.table_widget.setItem(row, 15, QTableWidgetItem(transporte.First_Name))
                        self.table_widget.setItem(row, 16, QTableWidgetItem(transporte.Last_Name))
                        self.table_widget.setItem(row, 17, QTableWidgetItem(transporte.Nacionalidad))
                
                elif 'HOTEL-VESSEL' == tramo:  # Transporte desde el hotel
                    # if ciudad_seleccionada == "ciudad":
                    #     city_select = str(vuelo.Aeropuerto_Salida).lower()
                    vuelos_salida = [v for v in vuelos if v.Aeropuerto_Salida.lower() == city_select.lower()]
                    for vuelo in vuelos_salida:
                        #print(vuelo)
                        row = self.table_widget.rowCount()
                        self.table_widget.insertRow(row)

                        a1 = CITY_TO_AIRPORT_CODES.get(str(vuelo.Aeropuerto_Salida))
                        a2 = CITY_TO_AIRPORT_CODES.get(str(vuelo.Aeropuerto_Llegada))

                        if a1 == 'SCL' and a2 == 'PUQ':
                            a1 = f"{a1} Nacional"
                        elif a1 == 'SCL' and a2 != 'PUQ':
                            a1 = f"{a1} Internacional"

                        codigo = f"{str(vuelo.Codigo)} {a1}-{a2}"
                        lugar_pick_up = "Hotel"

                        if a1 == "PUQ":
                            tiempo_a_restar = timedelta(hours=2, minutes=30)
                        elif a1 == "SCL Nacional":
                            tiempo_a_restar = timedelta(hours=2, minutes=30)
                        elif a1 == "SCL Internacional":
                            tiempo_a_restar = timedelta(hours=3, minutes=30)
                        elif a1 == "WPU":
                            tiempo_a_restar = timedelta(hours=1, minutes=30)
                        elif a1 == "KGI":
                            tiempo_a_restar = timedelta(hours=3, minutes=30)
                        else:
                            tiempo_a_restar = timedelta()

                        hora_pickup_datetime = datetime.combine(datetime.min, transporte.Hora_Pickup)
                        hora_pick_up = (hora_pickup_datetime - tiempo_a_restar).time()

                        self.table_widget.setItem(row, 0, QTableWidgetItem(transporte.Estado))
                        self.table_widget.setItem(row, 1, QTableWidgetItem(transporte.Ciudad_Transporte_in))
                        self.table_widget.setItem(row, 2, QTableWidgetItem(transporte.Lugar_Transporte_in))
                        self.table_widget.setItem(row, 3, QTableWidgetItem(transporte.Ciudad_Transporte_end))
                        self.table_widget.setItem(row, 4, QTableWidgetItem(transporte.Lugar_Transporte_end))
                        #self.table_widget.setItem(row, 2, QTableWidgetItem(str(transporte.Fecha)))
                        #self.table_widget.setItem(row, 2, QTableWidgetItem(f"Hotel {hotel.Ciudad_Hotel}" if hotel else f"NO"))
                        self.table_widget.setItem(row, 5, QTableWidgetItem(hotel.Nombre_Hotel if hotel else "Sin hotel"))
                        self.table_widget.setItem(row, 6, QTableWidgetItem(codigo))
                        self.table_widget.setItem(row, 7, QTableWidgetItem(str(vuelo.Fecha.date())))
                        self.table_widget.setItem(row, 8, QTableWidgetItem(str(vuelo.Hora_Salida.time())))
                        self.table_widget.setItem(row, 9, QTableWidgetItem(str(hora_pick_up)))
                        self.table_widget.setItem(row, 10, QTableWidgetItem(lugar_pick_up))
                        #self.table_widget.setItem(row, 7, QTableWidgetItem(aeropuerto_llegada))
                        self.table_widget.setItem(row, 12, QTableWidgetItem(owner))
                        self.table_widget.setItem(row, 13, QTableWidgetItem(buque))
                        self.table_widget.setItem(row, 14, QTableWidgetItem(str(eta)))
                        #self.table_widget.setItem(row, 13, QTableWidgetItem(buque.ETA))
                        self.table_widget.setItem(row, 15, QTableWidgetItem(transporte.First_Name))
                        self.table_widget.setItem(row, 16, QTableWidgetItem(transporte.Last_Name))
                        self.table_widget.setItem(row, 17, QTableWidgetItem(transporte.Nacionalidad))

                elif 'VESSEL-HOTEL' == tramo:# and str(vuelo.Codigo) in 'BUS':  # Transporte desde el hotel 
                    # if ciudad_seleccionada == "ciudad":
                    #     city_select = str(transporte.Ciudad_Transporte_in).lower()
                    # else:
                    city_select = transporte.Ciudad_Transporte_in

                    vuelos_salida1 = [v for v in vuelos if transporte.Ciudad_Transporte_in.lower() == city_select.lower() and v.Codigo.lower() == 'bus']
                    for vuelo in vuelos_salida1:
                        row = self.table_widget.rowCount()
                        self.table_widget.insertRow(row)

                        a1 = CITY_TO_AIRPORT_CODES.get(str(vuelo.Aeropuerto_Salida))
                        a2 = CITY_TO_AIRPORT_CODES.get(str(vuelo.Aeropuerto_Llegada))

                        codigo = f"{str(vuelo.Codigo)} {a1}-{a2}"
                        lugar_pick_up = "Hotel"

                        self.table_widget.setItem(row, 0, QTableWidgetItem(transporte.Estado))
                        self.table_widget.setItem(row, 1, QTableWidgetItem(transporte.Ciudad_Transporte_in))
                        self.table_widget.setItem(row, 2, QTableWidgetItem(transporte.Lugar_Transporte_in))
                        self.table_widget.setItem(row, 3, QTableWidgetItem(transporte.Ciudad_Transporte_end))
                        self.table_widget.setItem(row, 4, QTableWidgetItem(transporte.Lugar_Transporte_end))
                        #self.table_widget.setItem(row, 2, QTableWidgetItem(str(transporte.Fecha)))
                        #self.table_widget.setItem(row, 2, QTableWidgetItem(f"Hotel {hotel.Ciudad_Hotel}" if hotel else f"NO"))
                        self.table_widget.setItem(row, 5, QTableWidgetItem(hotel.Nombre_Hotel if hotel else "Sin hotel"))
                        self.table_widget.setItem(row, 6, QTableWidgetItem(codigo))
                        self.table_widget.setItem(row, 7, QTableWidgetItem(str(vuelo.Fecha.date())))
                        self.table_widget.setItem(row, 8, QTableWidgetItem(str(vuelo.Hora_Salida.time())))
                        self.table_widget.setItem(row, 9, QTableWidgetItem(str(transporte.Hora_Pickup)))
                        self.table_widget.setItem(row, 10, QTableWidgetItem(lugar_pick_up))
                        #self.table_widget.setItem(row, 7, QTableWidgetItem(aeropuerto_llegada))
                        self.table_widget.setItem(row, 12, QTableWidgetItem(owner))
                        self.table_widget.setItem(row, 13, QTableWidgetItem(buque))
                        self.table_widget.setItem(row, 14, QTableWidgetItem(str(eta)))
                        #self.table_widget.setItem(row, 13, QTableWidgetItem(buque.ETA))
                        self.table_widget.setItem(row, 15, QTableWidgetItem(transporte.First_Name))
                        self.table_widget.setItem(row, 16, QTableWidgetItem(transporte.Last_Name))
                        self.table_widget.setItem(row, 17, QTableWidgetItem(transporte.Nacionalidad))

                # elif 'Hotel-Hotel' in tramo:  # Transporte desde el hotel
                #     if ciudad_seleccionada == "ciudad":
                #         city_select = str(vuelo.Aeropuerto_Salida).lower()
                #     vuelos_salida = [t for t in transportes if "Hotel-Hotel" in t.Ciudad_Transporte]
                #     for vuelo in vuelos_salida:
                #         #print(transportes)
                #         #print(hotel_dict)
                #         row = self.table_widget.rowCount()
                #         self.table_widget.insertRow(row)

                #         #a1 = CITY_TO_AIRPORT_CODES.get(str(vuelo.Aeropuerto_Salida))
                #         #a2 = CITY_TO_AIRPORT_CODES.get(str(vuelo.Aeropuerto_Llegada))

                #         #codigo = f"{str(vuelo.Codigo)} {a1}-{a2}"
                #         lugar_pick_up = "Hotel"

                #         self.table_widget.setItem(row, 0, QTableWidgetItem(transporte.Estado))
                #         self.table_widget.setItem(row, 1, QTableWidgetItem(tramo))
                #         #self.table_widget.setItem(row, 2, QTableWidgetItem(str(transporte.Fecha)))
                #         #self.table_widget.setItem(row, 2, QTableWidgetItem(f"Hotel {hotel.Ciudad_Hotel}" if hotel else f"Hotel {ciudad_code}"))
                #         self.table_widget.setItem(row, 3, QTableWidgetItem(hotel.Nombre_Hotel if hotel else "Sin hotel"))
                #         self.table_widget.setItem(row, 7, QTableWidgetItem(str(hotel.Check_Out.time())))
                #         self.table_widget.setItem(row, 8, QTableWidgetItem(lugar_pick_up))
                #         #self.table_widget.setItem(row, 7, QTableWidgetItem(aeropuerto_llegada))
                #         self.table_widget.setItem(row, 12, QTableWidgetItem(owner))
                #         self.table_widget.setItem(row, 13, QTableWidgetItem(buque))
                #         self.table_widget.setItem(row, 14, QTableWidgetItem(str(eta)))
                #         #self.table_widget.setItem(row, 13, QTableWidgetItem(buque.ETA))
                #         self.table_widget.setItem(row, 15, QTableWidgetItem(transporte.First_Name))
                #         self.table_widget.setItem(row, 16, QTableWidgetItem(transporte.Last_Name))
                #         self.table_widget.setItem(row, 17, QTableWidgetItem(transporte.Nacionalidad))

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
        headers = ["Estado", "Transporte", "Hotel Ciudad", "Nombre Hotel", "Código Vuelo Llegada", "Date Llegada", "Hora Llegada", "Hora Pick Up", "Lugar Pick Up", "Código Vuelo Salida", "Date Salida", "Fecha Salida", "Owner", "Nave", "ETA", "First Name", "Last Name", "Nacionalidad", "Transportista", "Anfitrión", "Vehículo", "Vehículo apoyo"]
        df = pd.DataFrame(data, columns=headers)

        # Convertir "Hora Pick Up" a datetime para una ordenación correcta
        df['Hora Pick Up'] = pd.to_datetime(df['Hora Pick Up'], format='%H:%M:%S', errors='coerce')

        # Ordenar el DataFrame por "Hora Pick Up", "Lugar Pick Up" y "Nombre Hotel"
        df = df.sort_values(by=["Hora Pick Up", "Lugar Pick Up", "Nombre Hotel"])

        # Convertir "Hora Pick Up" de nuevo a solo hora para el Excel
        df['Hora Pick Up'] = df['Hora Pick Up'].dt.strftime('%H:%M:%S')

        file_name_parts = ["requerimiento_transporte"]
        if ciudad_seleccionada.lower() != "ciudad" and ciudad_seleccionada.lower() not in file_name_parts:
            file_name_parts.append(ciudad_seleccionada)

        file_name = "_".join(file_name_parts) + ".xlsx"
        
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
            cell.value = "Date Pick Up"

            if self.check_fecha.isChecked():
                fecha_inicio = self.date_start1.date().toPyDate()
                fecha_fin = datetime.combine(self.date_end1.date().toPyDate(), time.max)
            else:
                fecha_inicio = None
                fecha_fin = None

            cell = ws.cell(row=1, column=2)
            if fecha_inicio != None:
                cell.value = f"({fecha_inicio}) - ({fecha_fin.date()})"
            else:
                cell.value = ""

            cell = ws.cell(row=2, column=1)
            cell.value = "Ciudad"
            cell = ws.cell(row=2, column=2)
            cell.value = CITY_AIRPORT_CODES.get(ciudad_seleccionada)

            # Escribir los encabezados del DataFrame manualmente
            for col_num, col_name in enumerate(headers, 1):
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

    def volver_a_opciones_programar(self):
        self.main_window.stacked_widget.setCurrentIndex(self.main_window.opciones_programar_index)

class AsistenciasScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        session = get_db_session()

        # Cuadro de selección de ciudad dentro de AsistenciasScreen
        self.combo_ciudades = QComboBox()
        self.combo_ciudades.addItems(["SCL", "PUQ", "WPU"])  # Agrega las ciudades al combo box
        layout.addWidget(self.combo_ciudades)

        # Cuadro de selección de buque
        self.combo_owner = QComboBox()
        self.combo_owner.addItems(["Owner"])
        owners = session.query(Buque.empresa).distinct().all()  # Consulta para obtener los nombres de los buques
        for owner in owners:
            self.combo_owner.addItem(owner.empresa)
        layout.addWidget(self.combo_owner)

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
        button_volver.clicked.connect(self.volver_a_opciones_programar)
        layout.addWidget(button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        # Conectar el cambio en el QComboBox a un método
        self.combo_ciudades.currentTextChanged.connect(self.actualizar_datos)
        self.combo_owner.currentTextChanged.connect(self.actualizar_datos)

        # Actualizar datos inicialmente
        self.actualizar_datos()

    def generar_excel_con_ciudad(self):
        ciudad_seleccionada = self.combo_ciudades.currentText()  # Obtener la ciudad seleccionada
        self.generar_excel(ciudad_seleccionada)  # Llamar a generar_excel con la ciudad seleccionada

    def actualizar_datos(self):
        ciudad_seleccionada = self.combo_ciudades.currentText()  # Obtiene la ciudad seleccionada
        owner_seleccionado = self.combo_owner.currentText()
        self.label.setText(f"Asistencias en {ciudad_seleccionada}")  # Actualiza el label

        # Cargar datos en la tabla
        self.cargar_datos(ciudad_seleccionada, owner_seleccionado)

    def cargar_datos(self, ciudad_seleccionada, owner):
        session = get_db_session()  # Obtener la sesión de la base de datos
        print(owner)
        # Obtener el nombre de la ciudad a partir del código
        codigo_ciudad = ciudad_seleccionada
        ciudad_seleccionada = CITY_AIRPORT_CODES.get(ciudad_seleccionada).lower()  # Convertir a minúsculas

        # Obtener datos de vuelos de arribo
        arribo_vuelos = (
            session.query(
                Buque.empresa.label("Owner"),
                Buque.nombre.label("Vessel"),
                Vuelo.aeropuerto_llegada.label("Aeropuerto_Llegada"),
                EtaCiudad.eta.label("ETA"),
                Vuelo.hora_llegada.label("Hora_Arribo"),
                Tripulante.nombre.label("First_Name"),
                Tripulante.apellido.label("Last_Name"),
                Tripulante.condicion.label("Condition"),
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
        )

        # Filtro adicional si owner no es "Owner"
        if owner != "Owner":
            arribo_vuelos = arribo_vuelos.filter(Buque.empresa == owner)

        arribo_vuelos = arribo_vuelos.all()

        # Obtener datos de vuelos de salida
        salida_vuelos = (
            session.query(
                Vuelo.aeropuerto_salida.label("Aeropuerto_Salida"),
                Vuelo.hora_salida.label("Hora_Salida"),
                Vuelo.codigo.label("Nro_Vuelo_Salida"),
                Vuelo.fecha.label("Fecha_Vuelo_Salida"),
                Tripulante.tripulante_id,
                Tripulante.estado.label("Estado")
            )
            .outerjoin(TripulanteVuelo, TripulanteVuelo.tripulante_id == Tripulante.tripulante_id)
            .outerjoin(Vuelo, TripulanteVuelo.vuelo_id == Vuelo.vuelo_id)
            .filter(func.lower(Vuelo.aeropuerto_salida) == ciudad_seleccionada)
            .all()
        )

        # Construir un diccionario para almacenar la información de los tripulantes
        tripulantes_info = {}

        # Agregar la información de vuelos de arribo al diccionario
        for arribo in arribo_vuelos:
            tripulante_id = arribo.tripulante_id
            if tripulante_id not in tripulantes_info:
                tripulantes_info[tripulante_id] = {
                    "Owner": arribo.Owner,
                    "Vessel": arribo.Vessel,
                    "ETA": arribo.ETA,
                    "First_Name": arribo.First_Name,
                    "Last_Name": arribo.Last_Name,
                    "Condition": arribo.Condition,
                    "Type": arribo.Type,
                    "Nro_Vuelo_Arribo": arribo.Nro_Vuelo_Arribo,
                    "Fecha_Vuelo_Arribo": arribo.Fecha_Vuelo_Arribo,
                    "Hora_Arribo": arribo.Hora_Arribo,
                    "Nro_Vuelo_Salida": None,
                    "Fecha_Vuelo_Salida": None,
                    "Hora_Vuelo_Salida": None,
                    "Asistencia": None,
                    "Comidas": None,
                    "Transportes": None,
                    "Hotel": None,
                    "Habitación": None
                }

        # Agregar la información de vuelos de salida al diccionario
        for salida in salida_vuelos:
            tripulante_id = salida.tripulante_id
            if tripulante_id in tripulantes_info:
                tripulantes_info[tripulante_id]["Nro_Vuelo_Salida"] = salida.Nro_Vuelo_Salida
                tripulantes_info[tripulante_id]["Fecha_Vuelo_Salida"] = salida.Fecha_Vuelo_Salida
                tripulantes_info[tripulante_id]["Hora_Vuelo_Salida"] = salida.Hora_Salida

        # Obtener la información de asistencia
        if codigo_ciudad == "SCL":
            asistencia_data = (
                session.query(
                    TripulanteAsistencia.tripulante_id,
                    TripulanteAsistencia.necesita_asistencia_scl.label("Necesita_Asistencia"),
                    TripulanteAsistencia.proveedor_scl.label("Proveedor"),
                )
                .all()
            )
        elif codigo_ciudad == "PUQ":
            asistencia_data = (
                session.query(
                    TripulanteAsistencia.tripulante_id,
                    TripulanteAsistencia.necesita_asistencia_puq.label("Necesita_Asistencia"),
                    TripulanteAsistencia.proveedor_puq.label("Proveedor"),
                )
                .all()
            )
        elif codigo_ciudad == "WPU":
            asistencia_data = (
                session.query(
                    TripulanteAsistencia.tripulante_id,
                    TripulanteAsistencia.necesita_asistencia_wpu.label("Necesita_Asistencia"),
                    TripulanteAsistencia.proveedor_wpu.label("Proveedor")
                )
                .all()
            )

        # Agregar información de asistencia y proveedor al diccionario
        for asistencia in asistencia_data:
            tripulante_id = asistencia.tripulante_id
            if tripulante_id in tripulantes_info:
                # Almacenar el nombre del proveedor
                tripulantes_info[tripulante_id]["Proveedor"] = asistencia.Proveedor
                # Almacenar la información de asistencia
                tripulantes_info[tripulante_id]["Asistencia"] = "Sí" if asistencia.Necesita_Asistencia else "No"

        comida_requerida = (
            session.query(
                Tripulante.tripulante_id,
                case(
                    (TripulanteRestaurante.tripulante_id.isnot(None), "Sí"),
                    else_="No"
                ).label("Requiere_Comida")
            )
            .outerjoin(TripulanteRestaurante, Tripulante.tripulante_id == TripulanteRestaurante.tripulante_id)
            .outerjoin(Restaurante, TripulanteRestaurante.restaurante_id == Restaurante.restaurante_id)  # Añadir el join con Restaurante
            .filter(
                Restaurante.ciudad == codigo_ciudad
            )
            .group_by(Tripulante.tripulante_id)
            .all()
        )

        #print("Comida requerida:", comida_requerida)
        # Agregar información de comidas al diccionario
        for tripulante_id, requiere_comida in comida_requerida:
            if tripulante_id in tripulantes_info:
                tripulantes_info[tripulante_id]["Comidas"] = requiere_comida


        transporte_requerido = (
            session.query(
                Tripulante.tripulante_id,
                case(
                        (TripulanteTransporte.tripulante_id.isnot(None), "Sí"),
                    else_="No" 
                ).label("Requiere_Transporte")
            )
            .outerjoin(TripulanteTransporte, Tripulante.tripulante_id == TripulanteTransporte.tripulante_id)
            .outerjoin(Transporte, TripulanteTransporte.transporte_id==Transporte.transporte_id)
            .filter(
                    Transporte.city_in == codigo_ciudad
            )
            .group_by(Tripulante.tripulante_id)
            .all()
        )

        #print("Transporte requerida:", transporte_requerido)
        # Agregar información de transporte al diccionario
        for tripulante_id, requiere_transporte in transporte_requerido:
            if tripulante_id in tripulantes_info:
                tripulantes_info[tripulante_id]["Transportes"] = requiere_transporte
                
        # Obtener la información del hotel
        tripulantes_con_hotel = (
            session.query(
                Tripulante.tripulante_id,
                Hotel.nombre.label("Nombre_Hotel"),
                TripulanteHotel.tipo_habitacion,
            )
            .join(TripulanteHotel, TripulanteHotel.tripulante_id == Tripulante.tripulante_id)
            .join(Hotel, TripulanteHotel.hotel_id == Hotel.hotel_id)
            .filter(func.lower(Hotel.ciudad) == codigo_ciudad.lower())
            .all()
        )

        # Agregar información del hotel al diccionario
        for tripulante_id, nombre_hotel, tipo_habitacion in tripulantes_con_hotel:
            if tripulante_id in tripulantes_info:
                tripulantes_info[tripulante_id]["Hotel"] = nombre_hotel
                tripulantes_info[tripulante_id]["Habitación"] = tipo_habitacion
        
        #print("Información de tripulantes:", tripulantes_info)

        # Limpiar la tabla antes de llenarla
        self.table_widget.setRowCount(0)  # Limpia filas existentes

        self.table_widget.setColumnCount(20)  # Asegúrate de que este número coincida con el número de columnas
        self.table_widget.setHorizontalHeaderLabels(
            ["Vessel", "ETA", "First Name", "Last Name", "Condition", "Type", 
            "Proveedor", "Asistencia", "Transportes", "Comidas", "Nro Vuelo Arribo", 
            "Fecha Vuelo Arribo", "Hora Arribo", "Hotel", "Habitación", 
            "Date Pick Up", "Hora Pick Up", "Nro Vuelo Salida", 
            "Fecha Vuelo Salida", "Hora Vuelo Salida"]
        )

        try:
            for tripulante_id, info in tripulantes_info.items():
                #print(f"Agregando tripulante: {tripulante_id}, info: {info}")  
                row_position = self.table_widget.rowCount()  
                self.table_widget.insertRow(row_position)  

                # Aquí puedes imprimir para ver si estás configurando el item correctamente
                for col, key in enumerate(["Vessel", "ETA", "First_Name", "Last_Name", "Condition", "Type", "Proveedor", "Asistencia", 
                                        "Transportes", "Comidas", "Nro_Vuelo_Arribo", "Fecha_Vuelo_Arribo", 
                                        "Hora_Arribo", "Hotel", "Habitación", "Date Pick Up", "Hora Pick Up", 
                                        "Nro_Vuelo_Salida", "Fecha_Vuelo_Salida", "Hora_Vuelo_Salida"]):
                    value = info.get(key, "")
                    self.table_widget.setItem(row_position, col, QTableWidgetItem(str(value)))

            self.table_widget.repaint()  # Forzar la actualización de la tabla
        except Exception as e:
            print(f"Error al llenar la tabla: {e}")

    def format_datetime(self, value):
        """Convierte un valor datetime a string, o lo devuelve como está si no es un datetime."""
        if isinstance(value, datetime):
            return value.strftime('%d-%m-%Y %H:%M')
        return str(value)

    def generar_excel(self, ciudad_seleccionada):
        # Crear un DataFrame con los datos de la tabla
        data = []
        for row in range(self.table_widget.rowCount()):
            row_data = []
            for column in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, column)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        # Verificar los datos recolectados
        print(f"Datos: {data}")
        print(f"Número de columnas en los datos: {len(data[0]) if data else 0}")

        # Definir los nombres de las columnas
        column_names = ["Vessel", "ETA", "First Name", "Last Name", "Condition", "Type", 
                        "Proveedor","Asistencia", "Transportes", "Comidas", "Nro Vuelo Arribo", 
                        "Fecha Vuelo Arribo", "Hora Arribo", "Hotel", "Habitación", 
                        "Date Pick Up", "Hora Pick Up", "Nro Vuelo Salida", 
                        "Fecha Vuelo Salida", "Hora Vuelo Salida"]

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

            # Escribir encabezados adicionales en negrita
            ws.cell(row=1, column=1).value = "CIUDAD"
            ws.cell(row=1, column=2).value = ciudad_seleccionada
            ws.cell(row=2, column=1).value = "Asistencias"
            ws.cell(row=2, column=2).value = ciudad_seleccionada

            # Aplicar formato de negrita a los encabezados
            for col in range(1, 3):
                ws.cell(row=1, column=col).font = Font(bold=True)
                ws.cell(row=2, column=col).font = Font(bold=True)

            # Escribir los encabezados del DataFrame manualmente
            for col_num, col_name in enumerate(column_names, 1):
                cell = ws.cell(row=5, column=col_num)
                cell.value = col_name
                cell.fill = header_fill  # Aplicar color a los encabezados
                cell.font = Font(bold=True)  # Poner encabezados en negrita

            # Escribir los datos del DataFrame y aplicar color a las celdas
            for row_num, row_data in enumerate(df.values, start=6):
                for col_num, cell_value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_num, column=col_num)
                    cell.value = cell_value
                    cell.fill = data_fill  # Aplicar color a los datos

            # Ajustar el ancho de las columnas para que se vea todo
            for col in ws.columns:
                max_length = 0
                column = col[0].column_letter  # Get the column name
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)  # Agregar un margen
                ws.column_dimensions[column].width = adjusted_width

            # Guardar el archivo Excel con colores aplicados
            wb.save(file_path)

    def volver_a_opciones_programar(self):
        self.main_window.stacked_widget.setCurrentIndex(self.main_window.opciones_programar_index)

class AlimentosScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        session = get_db_session()
        layout = QVBoxLayout(self)

        # Llenar el combo de buques desde la base de datos
        self.combo_buques = QComboBox()
        self.combo_buques.addItem("Buque")  # Agregar un valor por defecto

        buques = session.query(Buque.nombre).distinct().all()  # Consulta para obtener los nombres de los buques
        for buque in buques:
            self.combo_buques.addItem(buque.nombre)
        layout.addWidget(self.combo_buques)

        self.check_fecha_eta = QCheckBox("Filtro por ETA")
        self.check_fecha_eta.setChecked(False)  # Inicialmente deshabilitado
        self.check_fecha_eta.stateChanged.connect(self.toggle_fechas_eta)  # Conectar evento de cambio de estado
        self.check_fecha_eta.stateChanged.connect(self.actualizar_datos)  # Conectar evento de cambio de estado
        layout.addWidget(self.check_fecha_eta)

        # Selector de fecha de inicio
        self.date_start1_eta = QDateEdit()
        self.date_start1_eta.setCalendarPopup(True)
        self.date_start1_eta.setDate(QDate.currentDate())
        self.date_start1_eta.setEnabled(False)  # Inicialmente deshabilitado
        layout.addWidget(self.date_start1_eta)

        # Llenar el combo de owners desde la base de datos
        self.combo_owners = QComboBox()
        self.combo_owners.addItem("Owner")  # Agregar un valor por defecto

        owners = session.query(Buque.empresa).distinct().all()  # Consulta para obtener los owners únicos
        for owner in owners:
            self.combo_owners.addItem(owner.empresa)
        layout.addWidget(self.combo_owners)

        # Llenar el combo de ciudades desde la base de datos
        self.combo_ciudades = QComboBox()
        self.combo_ciudades.addItem("Ciudad")  # Agregar un valor por defecto

        ciudades = session.query(Hotel.ciudad).distinct().all()  # Consulta para obtener las ciudades únicas
        for ciudad in ciudades:
            self.combo_ciudades.addItem(ciudad.ciudad)
        layout.addWidget(self.combo_ciudades)

        layout_filtro = QHBoxLayout()  # Crear sin asignar al widget principal
        layout.addLayout(layout_filtro)  # Agregarlo al layout principal

        self.check_fecha_rango = QCheckBox("Filtro por rango de fechas")
        self.check_fecha_rango.setChecked(False)  # Inicialmente deshabilitado
        self.check_fecha_rango.stateChanged.connect(self.toggle_fechas_rango)  # Conectar evento de cambio de estado
        self.check_fecha_rango.stateChanged.connect(self.actualizar_datos)  # Conectar evento de cambio de estado
        layout_filtro.addWidget(self.check_fecha_rango)

        # Selector de fecha de inicio
        self.date_start1_rango = QDateEdit()
        self.date_start1_rango.setCalendarPopup(True)
        self.date_start1_rango.setDate(QDate.currentDate())
        self.date_start1_rango.setEnabled(False)  # Inicialmente deshabilitado
        layout_filtro.addWidget(self.date_start1_rango)

        # Selector de fecha de inicio
        self.date_end1_rango = QDateEdit()
        self.date_end1_rango.setCalendarPopup(True)
        self.date_end1_rango.setDate(QDate.currentDate())
        self.date_end1_rango.setEnabled(False)  # Inicialmente deshabilitado
        layout_filtro.addWidget(self.date_end1_rango)

        # Llenar el combo de restaurantes desde la base de datos
        self.combo_restaurantes = QComboBox()
        self.combo_restaurantes.addItem("Restaurante")  # Agregar un valor por defecto

        restaurantes = session.query(Restaurante.nombre).distinct().all()  # Consulta para obtener los nombres de los hoteles
        for restaurante in restaurantes:
            self.combo_restaurantes.addItem(restaurante.nombre)
        layout.addWidget(self.combo_restaurantes)

        self.combo_tipo_comidas = QComboBox()
        self.combo_tipo_comidas.addItem("Tipo comida")  # Agregar un valor por defecto

        tipo_comidas = session.query(TripulanteRestaurante.tipo_comida).distinct().all()  # Consulta para obtener los nombres de los hoteles
        for tipo_comida in tipo_comidas:
            self.combo_tipo_comidas.addItem(tipo_comida.tipo_comida)
        layout.addWidget(self.combo_tipo_comidas)

        self.label = QLabel()
        layout.addWidget(self.label)

        # Tabla para mostrar datos
        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        # Botón para generar el Excel
        button_generar_excel = QPushButton("Generar Excel")
        button_generar_excel.clicked.connect(self.generar_excel_con_ciudad)
        layout.addWidget(button_generar_excel)

        # Botón "Volver" para regresar a la pantalla anterior
        button_volver = QPushButton("Volver")
        button_volver.setFixedWidth(100)
        button_volver.clicked.connect(self.volver_a_opciones_programar)
        layout.addWidget(button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        # Conectar cambios en los QComboBox
        self.combo_buques.currentTextChanged.connect(self.actualizar_datos)
        self.check_fecha_eta.stateChanged.connect(self.actualizar_datos)
        self.date_start1_eta.dateChanged.connect(self.actualizar_datos)
        self.combo_owners.currentTextChanged.connect(self.actualizar_datos)
        self.combo_ciudades.currentTextChanged.connect(self.actualizar_datos)
        self.check_fecha_rango.stateChanged.connect(self.actualizar_datos)
        self.date_start1_rango.dateChanged.connect(self.actualizar_datos)
        self.date_end1_rango.dateChanged.connect(self.actualizar_datos)
        self.combo_restaurantes.currentTextChanged.connect(self.actualizar_datos)
        self.combo_tipo_comidas.currentTextChanged.connect(self.actualizar_datos)

        # Actualizar datos inicialmente
        self.actualizar_datos()

    def toggle_fechas_eta(self):
        # Habilitar/deshabilitar según el estado del checkbox
        estado = self.check_fecha_eta.isChecked()
        self.date_start1_eta.setEnabled(estado)

    def toggle_fechas_rango(self):
        # Habilitar/deshabilitar según el estado del checkbox
        estado = self.check_fecha_rango.isChecked()
        self.date_start1_rango.setEnabled(estado)
        self.date_end1_rango.setEnabled(estado)

    def generar_excel_con_ciudad(self):
        ciudad_seleccionada = self.combo_ciudades.currentText()
        buque_seleccionado = self.combo_buques.currentText()
        restaurant_seleccionado = self.combo_restaurantes.currentText()
        owner_seleccionado = self.combo_owners.currentText()
        tipo_comida_seleccionado = self.combo_tipo_comidas.currentText()

        fecha_inicio_eta = self.date_start1_eta.date().toString("dd-MM-yyyy")  # Formato de fecha: dd-mm-aaaa
        fecha_inicio_rango = self.date_start1_rango.date().toString("dd-MM-yyyy")  # Formato de fecha: dd-mm-aaaa
        fecha_fin_rango = self.date_end1_rango.date().toString("dd-MM-yyyy")  # Formato de fecha: dd-mm-aaaa

        eta_check = self.check_fecha_eta.isChecked()
        rango_check = self.check_fecha_rango.isChecked()
        #fecha_fin = self.date_end1.date().toString("dd-MM-yyyy")

    # Llamar a la función generar_excel con ciudad, buque y las fechas
        self.generar_excel(ciudad_seleccionada, buque_seleccionado, restaurant_seleccionado, owner_seleccionado, fecha_inicio_eta, fecha_inicio_rango, fecha_fin_rango, eta_check, rango_check, tipo_comida_seleccionado)#, fecha_fin)

    def actualizar_datos(self):
        ciudad_seleccionada = self.combo_ciudades.currentText()
        buque_seleccionado = self.combo_buques.currentText()
        restaurant_seleccionado = self.combo_restaurantes.currentText()
        owner_seleccionado = self.combo_owners.currentText()
        tipo_comida_seleccionado = self.combo_tipo_comidas.currentText()

        fecha_inicio_eta = self.date_start1_eta.date().toString("dd-MM-yyyy")  # Formato de fecha: dd-mm-aaaa
        fecha_inicio_rango = self.date_start1_rango.date().toString("dd-MM-yyyy")  # Formato de fecha: dd-mm-aaaa
        fecha_fin_rango = self.date_end1_rango.date().toString("dd-MM-yyyy")  # Formato de fecha: dd-mm-aaaa
        self.label.setText(f"Lista de hoteles en {ciudad_seleccionada}")

        # Cargar datos basados en los filtros seleccionados
        self.cargar_datos(ciudad_seleccionada, buque_seleccionado, restaurant_seleccionado, owner_seleccionado, fecha_inicio_eta, fecha_inicio_rango, fecha_fin_rango, tipo_comida_seleccionado)

    def cargar_datos(self, ciudad_seleccionada, buque_seleccionado, restaurant_seleccionado, owner_seleccionado, fecha_inicio_eta, fecha_inicio_rango, fecha_fin_rango, tipo_comida_seleccionado):
        session = get_db_session()  # Obtener la sesión de la base de datos

        # Convertir las entradas a minúsculas para comparación
        restaurant_seleccionado = restaurant_seleccionado.lower()
        buque_seleccionado = buque_seleccionado.lower()
        ciudad_seleccionada = ciudad_seleccionada.lower()
        owner_seleccionado = owner_seleccionado.lower()
        tipo_comida_seleccionado = tipo_comida_seleccionado.lower()

        # Obtener las fechas seleccionadas en QDateEdit
        fecha_inicio_eta = fecha_inicio_eta 
        fecha_fin_eta = datetime.strptime(fecha_inicio_eta, "%d-%m-%Y")
        fecha_fin_eta = datetime.combine(fecha_fin_eta, time.max)  # Convertir a objeto de fecha de Python
        #fecha_fin = datetime.combine(self.date_start1_eta.toPyDate(), time.max)  # Combinar con la hora máxima del día

        fecha_inicio_rango = fecha_inicio_rango 
        fecha_fin_rango = datetime.strptime(fecha_fin_rango, "%d-%m-%Y")
        fecha_fin_rango = datetime.combine(fecha_fin_rango, time.max)  # Convertir a objeto de fecha de Python

        print(f"{fecha_inicio_rango} | {fecha_fin_rango}")

        # Construir la consulta de roomlist
        query = (
            session.query(
                Tripulante.tripulante_id.label("ID"),
                Tripulante.nombre.label("First_Name"),
                Tripulante.apellido.label("Last_Name"),
                Restaurante.ciudad.label("Restaurante_Ciudad"),
                TripulanteRestaurante.pref_alimenticia.label("Preferencia"),
                func.coalesce(TripulanteHotel.categoria, "").label("Categoria"),  # Usa "Sin categoría" si es NULL
                Buque.empresa.label("Owner")
            )
            .join(Restaurante, Restaurante.restaurante_id == TripulanteRestaurante.restaurante_id)
            .join(Tripulante, Tripulante.tripulante_id == TripulanteRestaurante.tripulante_id)
            .join(Buque, Buque.buque_id == Tripulante.buque_id)
            .outerjoin(TripulanteHotel, Tripulante.tripulante_id == TripulanteHotel.tripulante_id)  # LEFT JOIN en TripulanteHotel
            .filter(Tripulante.tripulante_id == TripulanteRestaurante.tripulante_id)
            .distinct()
        )

        # Aplicar filtro de buque si se seleccionó uno específico
        if buque_seleccionado != "buque":
            query = query.filter(func.lower(Buque.nombre) == buque_seleccionado)

        if owner_seleccionado != "owner":
            query = query.filter(func.lower(Buque.empresa) == owner_seleccionado)

        if ciudad_seleccionada != "ciudad":
            query = query.filter(func.lower(Restaurante.ciudad) == ciudad_seleccionada)

        if restaurant_seleccionado != "restaurante":
            query = query.filter(func.lower(Restaurante.nombre) == restaurant_seleccionado)

        if tipo_comida_seleccionado != "tipo comida":
            query = query.filter(func.lower(TripulanteRestaurante.tipo_comida) == tipo_comida_seleccionado)

        # Aplicar filtro de ETA por rango de fechas si está habilitado
        if self.check_fecha_eta.isChecked():
            query = (
                query
                .join(EtaCiudad, and_(
                    Tripulante.buque_id == EtaCiudad.buque_id,
                    EtaCiudad.eta >= fecha_inicio_eta,
                    EtaCiudad.eta <= fecha_fin_eta
                ))
                .filter(
                    EtaCiudad.eta >= fecha_inicio_eta,
                    EtaCiudad.eta <= fecha_fin_eta
                )
            )

        # Limpiar la tabla
        headers = ["First Name", "Last Name", "Preferencia", "Categoria", "Signature"]

        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(len(headers))  # Número correcto de columnas
        self.table_widget.setHorizontalHeaderLabels(headers)

        query = query.order_by(Tripulante.apellido)

        self.tripulante_ids = []

        # # Ordenar el DataFrame primero por 'Check In', luego por 'Position' y finalmente por 'Gender'
        #df = df.sort_values(by=["Last Name"])

        # # Formatear 'Check In' de nuevo a string con el formato deseado
        # df['Check In'] = df['Check In'].dt.strftime('%Y-%m-%d')

        # Llenar la tabla con los resultados de la consulta
        for tripulante in query:
            row = self.table_widget.rowCount()
            self.table_widget.insertRow(row)
            self.tripulante_ids.append(tripulante.ID)
            
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(tripulante.First_Name)))  # First Name
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(tripulante.Last_Name)))  # Last Name
            self.table_widget.setItem(row, 2, QTableWidgetItem(str(tripulante.Preferencia)))  # Gender
            self.table_widget.setItem(row, 3, QTableWidgetItem(str(tripulante.Categoria)))  # Gender
            
            # Check In
            #self.table_widget.setItem(row, 6, QTableWidgetItem(str(roomlist.check_in) if roomlist.check_in else ""))

    def generar_excel(self, ciudad_seleccionada, buque_seleccionado, restaurant_seleccionado, owner_seleccionado, fecha_inicio_eta, fecha_inicio_rango, fecha_fin_rango, eta_check, rango_check, tipo_comida_seleccionado):
        # Crear un DataFrame con los datos de la tabla
        data = []
        for row in range(self.table_widget.rowCount()):
            row_data = []
            for column in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, column)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        # Definir los nombres de las columnas
        column_names = ["First Name", "Last Name", "Preferencia", "Categoria", "Signature"]

        df = pd.DataFrame(data, columns=column_names)

        # Ordenar el DataFrame por "Categoria" y "Check in"
        df.sort_values(by=["Last Name"], ascending=True, inplace=True)

        df.insert(0, "Nro", range(1, len(df) + 1))

        # Generar nombre de archivo basado en buque y hotel seleccionados
        file_name_parts = ["requerimientos_comida"]
        if ciudad_seleccionada.lower() != "ciudad" and ciudad_seleccionada.lower() not in file_name_parts:
            file_name_parts.append(ciudad_seleccionada)
        if buque_seleccionado.lower() != "buque" and buque_seleccionado.lower() not in file_name_parts:
            file_name_parts.append(buque_seleccionado)

        file_name = "_".join(file_name_parts) + ".xlsx"

        # Guardar archivo Excel
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar archivo Excel",
            file_name,
            "Excel Files (*.xlsx);;All Files (*)"
        )

        if file_path:
            wb = Workbook()
            ws = wb.active

            # Encabezados personalizados
            ws.cell(row=1, column=1, value="BUQUE").font = Font(bold=True)
            ws.cell(row=1, column=2, value=buque_seleccionado if buque_seleccionado.lower() != "buque" else "")

            ws.cell(row=2, column=1, value="ETA").font = Font(bold=True)
            if fecha_inicio_eta and self.check_fecha_eta.isChecked():
                ws.cell(row=2, column=2, value=fecha_inicio_eta)
            else:
                ws.cell(row=2, column=2, value="ETA No seleccionada")

            ws.cell(row=3, column=1, value="OWNER").font = Font(bold=True)
            ws.cell(row=3, column=2, value=owner_seleccionado if owner_seleccionado.lower() != "owner" else "")

            ws.cell(row=4, column=1, value="CIUDAD COMIDA").font = Font(bold=True)
            ws.cell(row=4, column=2, value=ciudad_seleccionada if ciudad_seleccionada.lower() != "ciudad" else "")

            ws.cell(row=5, column=1, value="ENTRE FECHA").font = Font(bold=True)
            if fecha_inicio_eta and self.check_fecha_rango.isChecked():
                ws.cell(row=5, column=2, value=fecha_inicio_rango)
                ws.cell(row=5, column=3, value=fecha_fin_rango)
            else:
                ws.cell(row=5, column=2, value="Fechas no seleccionadas")

            ws.cell(row=4, column=1, value="RESTAURANTE").font = Font(bold=True)
            ws.cell(row=4, column=2, value=restaurant_seleccionado if restaurant_seleccionado.lower() != "restaurante" else "")

            # Escribir el texto final antes de la tabla
            ws.cell(row=6, column=1, value="Informe necesidad comidas").font = Font(bold=True)

            # Aplicar negrita a los encabezados
            header_fill = PatternFill(start_color='ADD8E6', end_color='ADD8E6', fill_type='solid')
            for col_num, col_name in enumerate(df.columns, 1):
                cell = ws.cell(row=8, column=col_num)  # Cambiar a fila 7
                cell.value = col_name
                cell.fill = header_fill
                cell.font = Font(bold=True)  # Negrita

            # Escribir los datos del DataFrame
            data_fill = PatternFill(start_color='FFFF99', end_color='FFFF99', fill_type='solid')
            for row_num, row_data in enumerate(df.values, start=9):  # Cambiar a fila 8
                for col_num, cell_value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_num, column=col_num)
                    cell.value = cell_value
                    cell.fill = data_fill

            # Centrar el número correlativo
            for row_num in range(9, len(df) + 9):  # Cambiar el rango según donde se escriban los datos
                ws.cell(row=row_num, column=1).alignment = Alignment(horizontal='center')

            # Ajustar el ancho de las columnas
            for col_num in range(1, len(df.columns) + 1):
                max_length = 0
                column = get_column_letter(col_num)
                for row in ws[column]:
                    try:
                        if len(str(row.value)) > max_length:
                            max_length = len(str(row.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)  # Agregar un poco de espacio extra
                ws.column_dimensions[column].width = adjusted_width

            # Guardar el archivo Excel
            wb.save(file_path)

    def volver_a_opciones_programar(self):
        self.main_window.stacked_widget.setCurrentIndex(self.main_window.menu_reportes_index)