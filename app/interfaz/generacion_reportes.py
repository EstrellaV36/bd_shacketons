import pandas as pd
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QFileDialog, QDateEdit, QCheckBox
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from app.database import get_db_session
from app.models import Buque, EtaCiudad, Tripulante, Vuelo, TripulanteVuelo, Restaurante, TripulanteRestaurante, Transporte, TripulanteTransporte, Hotel, TripulanteHotel, Buque, TripulanteAsistencia
from app.controllers import CITY_AIRPORT_CODES, CITY_TO_AIRPORT_CODES
from openpyxl.styles import PatternFill
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment, Border, Side
from datetime import datetime, time, timedelta
from sqlalchemy import func, and_, or_, case
from sqlalchemy.orm import aliased
from sqlalchemy.sql import exists

from collections import defaultdict

class GeneracionReportesScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.main_window.generacion_reportes_index = self.main_window.stacked_widget.addWidget(self)
        self.setup_ui()

    def setup_ui(self):
        #print("Índices en stacked_widget:")
        for i in range(self.main_window.stacked_widget.count()):
            #print(f"Índice {i}: {self.main_window.stacked_widget.widget(i)}")
            continue
            
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
        print(f"Regresando a GeneracionReportesScreen con índice {self.main_window.generacion_reportes_index}")
        self.main_window.stacked_widget.setCurrentIndex(self.main_window.generacion_reportes_index)

class HotelScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        session = get_db_session()

        self.label = QLabel("Lista de Hoteles")
        font = QFont()
        font.setPointSize(20)  # Tamaño de fuente
        font.setBold(True)      # Negrita
        self.label.setFont(font)
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)  # Centrar el título

        layout.addSpacing(20)

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

    def generar_excel(self, ciudad_seleccionada, buque_seleccionado, fecha_inicio, fecha_fin):
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

        # Ordenar el DataFrame por "Categoria" y "Check in"
        df.sort_values(by=["Categoria", "Check in"], ascending=[True, True], inplace=True)

        df.insert(0, "Nro", range(1, len(df) + 1))

        # Generar nombre de archivo basado en buque y hotel seleccionados
        file_name_parts = ["informe_hotel"]
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

            # Añadir el título al principio de todo
            ws.merge_cells('A1:K1')
            title_cell = ws['A1']
            title_cell.value = "Requerimiento Hotel"
            title_cell.font = Font(size=20, bold=True, underline="single")
            title_cell.alignment = Alignment(horizontal="center", vertical="center")

            # Encabezados personalizados
            ws.cell(row=2, column=1, value="BUQUE").font = Font(bold=True)
            ws.cell(row=2, column=2, value=buque_seleccionado if buque_seleccionado and buque_seleccionado.lower() != "buque" else "Buque no seleccionado")
            ws.cell(row=3, column=1, value="CIUDAD").font = Font(bold=True)
            ws.cell(row=3, column=2, value=ciudad_seleccionada if ciudad_seleccionada and ciudad_seleccionada != "Ciudad" else "Ciudad no seleccionada")

            # Mostrar las fechas de ETA solo si están seleccionadas
            if fecha_inicio and fecha_fin:
                ws.cell(row=4, column=1, value="ETA Desde:").font = Font(bold=True)
                ws.cell(row=4, column=2, value=fecha_inicio)
                ws.cell(row=5, column=1, value="ETA Hasta:").font = Font(bold=True)
                ws.cell(row=5, column=2, value=fecha_fin)
            else:
                ws.cell(row=4, column=1, value="ETA").font = Font(bold=True)
                ws.cell(row=4, column=2, value="ETA no seleccionada")

            # Aplicar negrita y centrado a los encabezados
            header_fill = PatternFill(start_color='ADD8E6', end_color='ADD8E6', fill_type='solid')
            thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
            
            for col_num, col_name in enumerate(df.columns, 1):
                cell = ws.cell(row=7, column=col_num)  # Cambiar a fila 7
                cell.value = col_name
                cell.fill = header_fill
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal="center", vertical="center")  # Centrar encabezado
                cell.border = thin_border  # Aplicar borde al encabezado

            # Escribir los datos del DataFrame y aplicar bordes y centrado
            data_fill = PatternFill(start_color='FFFF99', end_color='FFFF99', fill_type='solid')
            for row_num, row_data in enumerate(df.values, start=8):  # Cambiar a fila 8
                for col_num, cell_value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_num, column=col_num)
                    cell.value = cell_value
                    cell.fill = data_fill
                    cell.border = thin_border  # Aplicar borde a cada celda

                    # Centrar columnas específicas (excluyendo First Name, Last Name, y Position)
                    if col_num not in [3, 4, 6, 7]:  # No centrar First Name, Last Name, Position
                        cell.alignment = Alignment(horizontal="center", vertical="center")
                    else:
                        cell.alignment = Alignment(horizontal="left", vertical="center")

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
        self.main_window.stacked_widget.setCurrentIndex(self.main_window.opciones_programar_index)

class RoomListScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        session = get_db_session()
        layout = QVBoxLayout(self)

        self.label = QLabel("Room List")
        font = QFont()
        font.setPointSize(20)  # Tamaño de fuente
        font.setBold(True)      # Negrita
        self.label.setFont(font)
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)  # Centrar el título

        layout.addSpacing(20)

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
        if hotel_seleccionado != "Hotel":
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
        df['Check Out'] = pd.to_datetime(df['Check Out'], errors='coerce')

        # Realiza cualquier lógica que necesites usando el 'ID'
        for idx, row in df.iterrows():
            tripulante_id = row['ID']
            #print(f"Procesando ID: {tripulante_id}")

        # Ordenar el DataFrame por 'Categoria', 'Check In', 'Gender' en orden ascendente y 'Rooms' en orden descendente
        df = df.sort_values(by=["Categoria", "Check In", "Gender", "Rooms"], ascending=[True, True, True, False]).reset_index(drop=True)

        # Formatear 'Check In' de nuevo a string con el formato deseado
        df['Check In'] = df['Check In'].dt.strftime('%Y-%m-%d')
        df['Check Out'] = df['Check Out'].dt.strftime('%Y-%m-%d')

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

            # Escribir el texto final antes de la tabla
            ws.cell(row=1, column=1, value="Informe Room List").font = Font(size=20, bold=True, underline="single")

            cell = ws.cell(row=2, column=1, value="VESSEL")
            cell.font = Font(bold=True)

            cell = ws.cell(row=2, column=2)
            cell.value = buque_seleccionado if buque_seleccionado.lower() != "buque" else "Todos"
            cell.font = Font(bold=True)

            cell = ws.cell(row=3, column=1)
            cell.value = "HOTEL"
            cell.font = Font(bold=True)

            cell = ws.cell(row=3, column=2)
            cell.value = hotel_seleccionado if hotel_seleccionado.lower() != "hotel" else "Todos"
            cell.font = Font(bold=True)

            if self.check_fecha.isChecked():
                fecha_inicio = self.date_start1.date().toPyDate()
                fecha_fin = datetime.combine(self.date_end1.date().toPyDate(), time.max)
            else:
                fecha_inicio = None
                fecha_fin = None

            cell = ws.cell(row=4, column=1)
            cell.value = "FECHA"
            cell.font = Font(bold=True)

            cell = ws.cell(row=4, column=2)
            if fecha_inicio is not None:
                cell.value = f"{fecha_inicio} - {fecha_fin}"
            else:
                cell.value = ""

            # Paso 1: Filtrar solo las habitaciones que contienen "doble" o "single", ignorando mayúsculas/minúsculas
            filtered_df = df[df['Rooms'].str.lower().str.contains('doble|single', na=False)]

            # Normalizar la columna 'Rooms' en minúsculas solo en el DataFrame filtrado
            filtered_df['Rooms'] = filtered_df['Rooms'].str.lower()

            # Paso 2: Eliminar duplicados por 'Categoria', 'Grupo' y 'Rooms' para contar habitaciones dobles como una sola
            filtered_df = filtered_df.drop_duplicates(subset=['Categoria', 'Grupo', 'Rooms', 'Gender'])

            # Paso 3: Agrupar y contar habitaciones por 'Categoria', 'Rooms', y 'Gender' (single M, single F, doble M, doble F)
            conteo_habitaciones = (
                filtered_df.groupby(['Categoria', 'Rooms', 'Gender']).size()
                .unstack(level=['Rooms', 'Gender'], fill_value=0)
                .reindex(columns=[('single', 'M'), ('doble', 'M'), ('single', 'F'), ('doble', 'F')], fill_value=0)
                .reset_index()
            )

            # Asegurarse de que los nombres de las columnas estén claros
            conteo_habitaciones.columns = ['Categoria', 'Cantidad de Singles M', 'Cantidad de Dobles M', 'Cantidad de Singles F', 'Cantidad de Dobles F']

            conteo_habitaciones['Total Single'] = conteo_habitaciones['Cantidad de Singles M'] + conteo_habitaciones['Cantidad de Singles F']
            conteo_habitaciones['Total Doble'] = conteo_habitaciones['Cantidad de Dobles M'] + conteo_habitaciones['Cantidad de Dobles F']

            # Escribir encabezados en Excel
            ws.cell(row=1, column=5, value="Categoria").font = Font(bold=True)
            ws.cell(row=1, column=6, value="Cantidad de Singles M").font = Font(bold=True)
            ws.cell(row=1, column=7, value="Cantidad de Dobles M").font = Font(bold=True)
            ws.cell(row=1, column=8, value="Cantidad de Singles F").font = Font(bold=True)
            ws.cell(row=1, column=9, value="Cantidad de Dobles F").font = Font(bold=True)
            ws.cell(row=1, column=10, value="Total Single").font = Font(bold=True)
            ws.cell(row=1, column=11, value="Total Doble").font = Font(bold=True)

            # Escribir el conteo de habitaciones en Excel
            for idx, row in conteo_habitaciones.iterrows():
                ws.cell(row=2 + idx, column=5, value=row['Categoria'])
                ws.cell(row=2 + idx, column=6, value=row['Cantidad de Singles M'])
                ws.cell(row=2 + idx, column=7, value=row['Cantidad de Dobles M'])
                ws.cell(row=2 + idx, column=8, value=row['Cantidad de Singles F'])
                ws.cell(row=2 + idx, column=9, value=row['Cantidad de Dobles F'])
                ws.cell(row=2 + idx, column=10, value=row['Total Single'])
                ws.cell(row=2 + idx, column=11, value=row['Total Doble'])

            header_fill = PatternFill(start_color='ADD8E6', end_color='ADD8E6', fill_type='solid')
            data_fill = PatternFill(start_color='FFFF99', end_color='FFFF99', fill_type='solid')

            # Estilos de borde y relleno
            thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
            header_fill = PatternFill(start_color='ADD8E6', end_color='ADD8E6', fill_type='solid')
            data_fill = PatternFill(start_color='FFFF99', end_color='FFFF99', fill_type='solid')

            # Encabezados de la tabla
            for col_num, col_name in enumerate(df.columns, 1):
                cell = ws.cell(row=7, column=col_num)
                cell.value = col_name
                cell.fill = header_fill
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = thin_border

            # Escribir los datos en la tabla
            for row_num, row_data in enumerate(df.values, start=8):
                for col_num, cell_value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_num, column=col_num)
                    cell.value = cell_value
                    cell.fill = data_fill
                    cell.border = thin_border

                    # Centrar columnas especificadas
                    if col_num == 1:  # Columna "Nro"
                        cell.alignment = Alignment(horizontal="center")
                    elif col_num not in [2, 3, 6]:  # No centrar "First Name", "Last Name", "Position"
                        cell.alignment = Alignment(horizontal="center")
                    else:
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

        self.label = QLabel("Requerimiento transportes")
        font = QFont()
        font.setPointSize(20)  # Tamaño de fuente
        font.setBold(True)      # Negrita
        self.label.setFont(font)
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)  # Centrar el título

        layout.addSpacing(20)

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
        if ciudad_seleccionada != "Ciudad":
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

        headers = ["Estado", "Fecha Pickup", "Hora Pickup", "Nombre hotel", "Desde Ciudad", "Desde Lugar", "Hasta Ciudad", "Hasta Lugar", "Código Vuelo Llegada", "Date Llegada", "Hora Llegada", "Código Vuelo Salida", "Date Salida", "Fecha Salida", "Owner", "Nave", "ETA", "First Name", "Last Name", "Nacionalidad"]
        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)
        self.table_widget.setRowCount(0)

        data_rows = []

        # Construir filas para cada tripulante con vuelos y transportes
        for tripulante_id, transportes in transporte_dict.items():
            vuelos = vuelo_dict.get(tripulante_id, [])
            hotel = hotel_dict.get(tripulante_id)
            owner, buque, eta = buque_dict.get(tripulante_id, ("", "", ""))

            for transporte in transportes:
                date_pickup = transporte.Fecha_Pickup
                tramo = f"{transporte.Lugar_Transporte_in}-{transporte.Lugar_Transporte_end}"
                city_select = CITY_AIRPORT_CODES.get(self.combo_ciudades.currentText(), "").lower()

                # Caso 'ATO-HOTEL'
                if 'ATO-HOTEL' == tramo:
                    vuelos_llegada = [
                        v for v in vuelos['arribo']
                        if v is not None and v.get('Aeropuerto_Llegada') and ciudad_seleccionada
                        and v['Aeropuerto_Llegada'].lower() == ciudad_seleccionada.lower()
                    ]

                    for vuelo in vuelos_llegada:
                        codigo = f"{str(vuelo.Codigo)} {CITY_TO_AIRPORT_CODES.get(vuelo.Aeropuerto_Salida)}-{CITY_TO_AIRPORT_CODES.get(vuelo.Aeropuerto_Llegada)}"
                        data_rows.append({
                            "estado": transporte.Estado,
                            "fecha_pickup": date_pickup,
                            "hora_pick_up": transporte.Hora_Pickup,
                            "nombre_hotel": hotel.Nombre_Hotel if hotel else "Sin hotel",
                            "ciudad_transporte_in": transporte.Ciudad_Transporte_in,
                            "lugar_transporte_in": transporte.Lugar_Transporte_in,
                            "ciudad_transporte_end": transporte.Ciudad_Transporte_end,
                            "lugar_transporte_end": transporte.Lugar_Transporte_end,
                            "codigo_vuelo": codigo,
                            "fecha_vuelo": vuelo.Fecha.date(),
                            "hora_llegada": vuelo.Hora_Llegada.time(),
                            "owner": owner,
                            "buque": buque,
                            "eta": eta,
                            "first_name": transporte.First_Name,
                            "last_name": transporte.Last_Name,
                            "nacionalidad": transporte.Nacionalidad
                        })

                # Caso 'HOTEL-ATO'
                elif 'HOTEL-ATO' == tramo:
                    vuelos_salida = [v for v in vuelos if v.Aeropuerto_Salida.lower() == city_select]
                    for vuelo in vuelos_salida:
                        codigo = f"{str(vuelo.Codigo)} {CITY_TO_AIRPORT_CODES.get(vuelo.Aeropuerto_Salida)}-{CITY_TO_AIRPORT_CODES.get(vuelo.Aeropuerto_Llegada)}"
                        tiempo_a_restar = timedelta(hours=2, minutes=30) if city_select == 'puq' else timedelta(hours=3, minutes=30)
                        hora_pick_up = (vuelo.Hora_Salida - tiempo_a_restar).time()
                        data_rows.append({
                            "estado": transporte.Estado,
                            "fecha_pickup": date_pickup,
                            "hora_pick_up": hora_pick_up,
                            "nombre_hotel": hotel.Nombre_Hotel if hotel else "Sin hotel",
                            "ciudad_transporte_in": transporte.Ciudad_Transporte_in,
                            "lugar_transporte_in": transporte.Lugar_Transporte_in,
                            "ciudad_transporte_end": transporte.Ciudad_Transporte_end,
                            "lugar_transporte_end": transporte.Lugar_Transporte_end,
                            "codigo_vuelo": codigo,
                            "fecha_vuelo": vuelo.Fecha.date(),
                            "hora_llegada": vuelo.Hora_Llegada.time(),
                            "owner": owner,
                            "buque": buque,
                            "eta": eta,
                            "first_name": transporte.First_Name,
                            "last_name": transporte.Last_Name,
                            "nacionalidad": transporte.Nacionalidad
                        })

                # Caso 'HOTEL-VESSEL'
                elif 'HOTEL-VESSEL' == tramo:
                    vuelos_salida = [v for v in vuelos if v.Aeropuerto_Salida.lower() == city_select]
                    for vuelo in vuelos_salida:
                        codigo = f"{str(vuelo.Codigo)} {CITY_TO_AIRPORT_CODES.get(vuelo.Aeropuerto_Salida)}-{CITY_TO_AIRPORT_CODES.get(vuelo.Aeropuerto_Llegada)}"
                        tiempo_a_restar = timedelta(hours=3) if city_select == 'scl' else timedelta(hours=2)
                        hora_pick_up = (vuelo.Hora_Salida - tiempo_a_restar).time()
                        data_rows.append({
                            "estado": transporte.Estado,
                            "fecha_pickup": date_pickup,
                            "hora_pick_up": hora_pick_up,
                            "nombre_hotel": hotel.Nombre_Hotel if hotel else "Sin hotel",
                            "ciudad_transporte_in": transporte.Ciudad_Transporte_in,
                            "lugar_transporte_in": transporte.Lugar_Transporte_in,
                            "ciudad_transporte_end": transporte.Ciudad_Transporte_end,
                            "lugar_transporte_end": transporte.Lugar_Transporte_end,
                            "codigo_vuelo": codigo,
                            "fecha_vuelo": vuelo.Fecha.date(),
                            "hora_llegada": vuelo.Hora_Llegada.time(),
                            "owner": owner,
                            "buque": buque,
                            "eta": eta,
                            "first_name": transporte.First_Name,
                            "last_name": transporte.Last_Name,
                            "nacionalidad": transporte.Nacionalidad
                        })

                # Caso 'VESSEL-HOTEL'
                elif 'VESSEL-HOTEL' == tramo:
                    vuelos_bus = [v for v in vuelos if v.Codigo.lower() == 'bus']
                    for vuelo in vuelos_bus:
                        codigo = f"{str(vuelo.Codigo)} {CITY_TO_AIRPORT_CODES.get(vuelo.Aeropuerto_Salida)}-{CITY_TO_AIRPORT_CODES.get(vuelo.Aeropuerto_Llegada)}"
                        data_rows.append({
                            "estado": transporte.Estado,
                            "fecha_pickup": date_pickup,
                            "hora_pick_up": transporte.Hora_Pickup,
                            "nombre_hotel": hotel.Nombre_Hotel if hotel else "Sin hotel",
                            "ciudad_transporte_in": transporte.Ciudad_Transporte_in,
                            "lugar_transporte_in": transporte.Lugar_Transporte_in,
                            "ciudad_transporte_end": transporte.Ciudad_Transporte_end,
                            "lugar_transporte_end": transporte.Lugar_Transporte_end,
                            "codigo_vuelo": codigo,
                            "fecha_vuelo": vuelo.Fecha.date(),
                            "hora_llegada": vuelo.Hora_Llegada.time(),
                            "owner": owner,
                            "buque": buque,
                            "eta": eta,
                            "first_name": transporte.First_Name,
                            "last_name": transporte.Last_Name,
                            "nacionalidad": transporte.Nacionalidad
                        })

        # Ordenar la lista de filas por `fecha_pickup`
        data_rows = sorted(data_rows, key=lambda x: x["fecha_pickup"])

        # Insertar filas ordenadas en la tabla
        self.table_widget.setRowCount(len(data_rows))
        for row, row_data in enumerate(data_rows):
            self.table_widget.setItem(row, 0, QTableWidgetItem(row_data["estado"]))
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(row_data["fecha_pickup"])))
            self.table_widget.setItem(row, 2, QTableWidgetItem(str(row_data["hora_pick_up"])))
            self.table_widget.setItem(row, 3, QTableWidgetItem(row_data["nombre_hotel"]))
            self.table_widget.setItem(row, 4, QTableWidgetItem(row_data["ciudad_transporte_in"]))
            self.table_widget.setItem(row, 5, QTableWidgetItem(row_data["lugar_transporte_in"]))
            self.table_widget.setItem(row, 6, QTableWidgetItem(row_data["ciudad_transporte_end"]))
            self.table_widget.setItem(row, 7, QTableWidgetItem(row_data["lugar_transporte_end"]))
            self.table_widget.setItem(row, 8, QTableWidgetItem(row_data["codigo_vuelo"]))
            self.table_widget.setItem(row, 9, QTableWidgetItem(str(row_data["fecha_vuelo"])))
            self.table_widget.setItem(row, 10, QTableWidgetItem(str(row_data["hora_llegada"])))
            self.table_widget.setItem(row, 14, QTableWidgetItem(row_data["owner"]))
            self.table_widget.setItem(row, 15, QTableWidgetItem(row_data["buque"]))
            self.table_widget.setItem(row, 16, QTableWidgetItem(str(row_data["eta"])))
            self.table_widget.setItem(row, 17, QTableWidgetItem(row_data["first_name"]))
            self.table_widget.setItem(row, 18, QTableWidgetItem(row_data["last_name"]))
            self.table_widget.setItem(row, 19, QTableWidgetItem(row_data["nacionalidad"]))
 

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
        headers = ["Estado", "Fecha Pickup", "Hora Pickup", "Nombre hotel", "Desde Ciudad", "Desde Lugar", "Hasta Ciudad", "Hasta Lugar", "Código Vuelo Llegada", "Date Llegada", "Hora Llegada", "Código Vuelo Salida", "Date Salida", "Fecha Salida", "Owner", "Nave", "ETA", "First Name", "Last Name", "Nacionalidad", "Transportista", "Anfitrión", "Vehículo", "Vehículo apoyo"]
        for row in data:
            while len(row) < len(headers):
                row.append("")  # Add empty strings to fill up to 24 columns
        df = pd.DataFrame(data, columns=headers)

        # Convertir "Hora Pick Up" a datetime para una ordenación correcta
        df['Hora Pickup'] = pd.to_datetime(df['Hora Pickup'], format='%H:%M:%S', errors='coerce')

        # Ordenar el DataFrame por "Hora Pick Up", "Lugar Pick Up" y "Nombre Hotel"
        df = df.sort_values(by=["Fecha Pickup", "Hora Pickup", "Desde Lugar", "Nombre hotel"])

        # Convertir "Hora Pick Up" de nuevo a solo hora para el Excel
        df['Hora Pickup'] = df['Hora Pickup'].dt.strftime('%H:%M:%S')

        file_name_parts = ["req_transporte"]
        if ciudad_seleccionada.lower() != "ciudad" and ciudad_seleccionada.lower() not in file_name_parts:
            file_name_parts.append(ciudad_seleccionada)
        if self.check_fecha.isChecked():
            file_name_parts.append(f"{self.date_start1.date().toPyDate()}_{self.date_end1.date().toPyDate()}")

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

            # Escribir el texto final antes de la tabla
            ws.cell(row=1, column=1, value="Informe requerimientos transportes").font = Font(size=20, bold=True, underline="single")

            # Escribir "Date Pick Up" y "Ciudad" en negrita
            ws.cell(row=2, column=1, value="Date Pick Up").font = Font(bold=True)
            if self.check_fecha.isChecked():
                fecha_inicio = self.date_start1.date().toPyDate()
                fecha_fin = self.date_end1.date().toPyDate()
                ws.cell(row=2, column=2, value=f"({fecha_inicio}) - ({fecha_fin})")
            else:
                ws.cell(row=2, column=2, value="")

            ws.cell(row=3, column=1, value="Ciudad").font = Font(bold=True)
            ws.cell(row=3, column=2, value=ciudad_seleccionada)

            # Definir estilos de borde, relleno y alineación
            thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
            header_fill = PatternFill(start_color='ADD8E6', end_color='ADD8E6', fill_type='solid')
            data_fill = PatternFill(start_color='FFFF99', end_color='FFFF99', fill_type='solid')

            # Escribir los encabezados de la tabla
            for col_num, col_name in enumerate(headers, 1):
                cell = ws.cell(row=5, column=col_num)
                cell.value = col_name
                cell.fill = header_fill
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = thin_border

            # Escribir los datos y aplicar estilos
            for row_num, row_data in enumerate(df.values, start=6):
                for col_num, cell_value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_num, column=col_num)
                    cell.value = cell_value
                    cell.fill = data_fill
                    cell.border = thin_border

            for col in ws.columns:
                max_length = 0
                column = col[0].column_letter  # Obtener la letra de la columna

                for cell in col[1:]:  # Empezar desde el índice 1, que corresponde a la fila 2 en Excel 
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass

                # Ajustar el ancho de la columna en base al contenido
                adjusted_width = max_length + 1
                ws.column_dimensions[column].width = adjusted_width


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
        session = get_db_session()
        layout = QVBoxLayout(self)

        # Label para mostrar asistencias
        self.label = QLabel("Asistencias")  # Mover el label aquí para que sea un atributo de la clase
        font = QFont()
        font.setPointSize(20)  # Tamaño de fuente
        font.setBold(True)      # Negrita
        self.label.setFont(font)
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)  # Centrar el título

        layout.addSpacing(20)

        # Llenar el combo de ciudades desde la base de datos
        self.combo_ciudades = QComboBox()
        self.combo_ciudades.addItem("Ciudad")  # Agregar un valor por defecto
        ciudades = session.query(Hotel.ciudad).distinct().all()  # Consulta para obtener las ciudades únicas
        for ciudad in ciudades:
            self.combo_ciudades.addItem(ciudad.ciudad)
            #print(ciudad.ciudad)
        layout.addWidget(self.combo_ciudades)

        # Cuadro de selección de tipo tripulante
        self.tipo_tripulante = QComboBox()
        self.tipo_tripulante.addItem("Tipo tripulante")  # Agregar un valor por defecto
        self.tipo_tripulante.addItems(["AMBOS", "ON", "OFF"])  
        layout.addWidget(self.tipo_tripulante)

        # Cuadro de selección de tipo tripulante
        self.combo_proveedor = QComboBox()
        self.combo_proveedor.addItem("Proveedor")  # Agregar un valor por defecto
        self.combo_proveedor.addItems(["C&L", "FBAGS", "SHACK", "WPU"])  
        layout.addWidget(self.combo_proveedor)

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
        self.tipo_tripulante.currentTextChanged.connect(self.actualizar_datos)
        self.combo_proveedor.currentTextChanged.connect(self.actualizar_datos)
        self.date_start1.dateChanged.connect(self.actualizar_datos)
        self.date_end1.dateChanged.connect(self.actualizar_datos)

        # Actualizar datos inicialmente
        self.actualizar_datos()

    def generar_excel_con_ciudad(self):
        ciudad_seleccionada = self.combo_ciudades.currentText()  # Obtener la ciudad seleccionada
        tipo_crew = self.tipo_tripulante.currentText()
        proveedor = self.combo_proveedor.currentText()
        fecha_inicio = self.date_start1.date().toString("dd-MM-yyyy")
        fecha_fin = self.date_start1.date().toString("dd-MM-yyyy")
        self.generar_excel(ciudad_seleccionada, tipo_crew, proveedor, fecha_inicio, fecha_fin)  # Llamar a generar_excel con la ciudad seleccionada

    def actualizar_datos(self):
        ciudad_seleccionada = self.combo_ciudades.currentText()  # Obtiene la ciudad seleccionada
        proveedor_seleccionado = self.combo_ciudades.currentText()
        tipo_tripulante = self.tipo_tripulante.currentText()
        if ciudad_seleccionada.lower() != "ciudad":
            self.label.setText(f"Asistencias en {ciudad_seleccionada}")  # Actualiza el label

        # Cargar datos en la tabla
        self.cargar_datos(ciudad_seleccionada, proveedor_seleccionado, tipo_tripulante)

    def toggle_fechas(self, state):
        enabled = state == Qt.CheckState.Checked  # Verificar si el checkbox está marcado
        self.date_start1.setEnabled(enabled)
        self.date_end1.setEnabled(enabled)
        # Deshabilitar el cuadro emergente si está desmarcado
        self.date_start1.setCalendarPopup(enabled)
        self.date_end1.setCalendarPopup(enabled)

    def cargar_datos(self, ciudad_seleccionada, proveedor_seleccionado, tipo_tripulante):
        session = get_db_session()  # Obtener la sesión de la base de datos

        # Obtener el nombre de la ciudad a partir del código
        codigo_ciudad = ciudad_seleccionada
        ciudad_seleccionada = CITY_AIRPORT_CODES.get(ciudad_seleccionada)
        # Obtener las fechas seleccionadas en QDateEdit
        fecha_inicio = self.date_start1.date().toPyDate()
        fecha_fin = datetime.combine(self.date_end1.date().toPyDate(), time.max)

        # Obtener datos de vuelos de arribo
        arribo_vuelos_query = (
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
            .filter(Vuelo.aeropuerto_llegada == ciudad_seleccionada)
        )

        # Aplicar filtro de ETA por rango de fechas si está habilitado
        if self.check_fecha.isChecked():
            arribo_vuelos_query = arribo_vuelos_query.filter(
                EtaCiudad.eta >= fecha_inicio,
                EtaCiudad.eta <= fecha_fin
            )

        # Ejecutar la consulta
        arribo_vuelos = arribo_vuelos_query.all()
        # Construir un diccionario para almacenar la información de los tripulantes
        tripulantes_info = {}

        vuelos_dict = defaultdict(lambda: {
            "arribo": [],
            "salida": []
        })

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
                    "Transportes": None,
                    "Hotel": None,
                    "Habitación": None
                }

            # Agregar vuelo de arribo al diccionario de vuelos
            vuelos_dict[tripulante_id]["arribo"].append({
                "Nro_Vuelo_Arribo": arribo.Nro_Vuelo_Arribo,
                "Fecha_Vuelo_Arribo": arribo.Fecha_Vuelo_Arribo,
                "Hora_Arribo": arribo.Hora_Arribo,
                "Aeropuerto_Llegada": arribo.Aeropuerto_Llegada
            })

        #Esta consulta esta capturando tambien los viajes en bus guardados en "vuelos"
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
            .filter((Vuelo.aeropuerto_salida) == ciudad_seleccionada)
            .all()
        )

        # Agregar la información de vuelos de salida al diccionario
        for salida in salida_vuelos:
            tripulante_id = salida.tripulante_id
            if tripulante_id in tripulantes_info:
                tripulantes_info[tripulante_id]["Nro_Vuelo_Salida"] = salida.Nro_Vuelo_Salida
                tripulantes_info[tripulante_id]["Fecha_Vuelo_Salida"] = salida.Fecha_Vuelo_Salida
                tripulantes_info[tripulante_id]["Hora_Vuelo_Salida"] = salida.Hora_Salida

                # Agregar vuelo de salida al diccionario de vuelos
                vuelos_dict[tripulante_id]["salida"].append({
                    "Nro_Vuelo_Salida": salida.Nro_Vuelo_Salida,
                    "Fecha_Vuelo_Salida": salida.Fecha_Vuelo_Salida,
                    "Hora_Salida": salida.Hora_Salida,
                    "Aeropuerto_Salida": salida.Aeropuerto_Salida

                })

        # Construir la consulta de transporte
        transporte_necesario = (
            session.query(
                Tripulante.tripulante_id,
                Tripulante.estado.label("Estado"),
                Tripulante.nombre.label("First_Name"),
                Tripulante.apellido.label("Last_Name"),
                Tripulante.nacionalidad.label("Nacionalidad"),
                exists().where(
                    (Transporte.city_in == codigo_ciudad) &
                    (Transporte.transporte_id == TripulanteTransporte.transporte_id) &
                    (TripulanteTransporte.tripulante_id == Tripulante.tripulante_id)
                ).label("Tiene_Transporte")
            )
            .join(TripulanteTransporte, Tripulante.tripulante_id == TripulanteTransporte.tripulante_id)
            .group_by(Tripulante.tripulante_id, Tripulante.estado, Tripulante.nombre, Tripulante.apellido, Tripulante.nacionalidad)
        )

        resultados_transporte = transporte_necesario.all()
        # Agregar la información de transporte al diccionario
        for resultado in resultados_transporte:
            tripulante_id = resultado.tripulante_id
            if tripulante_id in tripulantes_info:
                tripulantes_info[tripulante_id]["Transporte"] = resultado.Tiene_Transporte

        # Inicializar asistencia_data como una consulta vacía
        asistencia_data = None

        # Obtener la información de asistencia y proveedores según la ciudad seleccionada
        if codigo_ciudad == "SCL":
            asistencia_data = (
                session.query(
                    TripulanteAsistencia.tripulante_id,
                    TripulanteAsistencia.necesita_asistencia_scl.label("Necesita_Asistencia"),
                    TripulanteAsistencia.proveedor_scl.label("Proveedor")
                )
            )
        elif codigo_ciudad == "PUQ":
            asistencia_data = (
                session.query(
                    TripulanteAsistencia.tripulante_id,
                    TripulanteAsistencia.necesita_asistencia_puq.label("Necesita_Asistencia"),
                    TripulanteAsistencia.proveedor_puq.label("Proveedor")
                )
            )
        elif codigo_ciudad == "WPU":
            asistencia_data = (
                session.query(
                    TripulanteAsistencia.tripulante_id,
                    TripulanteAsistencia.necesita_asistencia_wpu.label("Necesita_Asistencia"),
                    TripulanteAsistencia.proveedor_wpu.label("Proveedor")
                )
            )

        # Ejecutar la consulta y obtener resultados
        resultados_asistencia = asistencia_data.all() if asistencia_data else []

        # Agregar la información de asistencia al diccionario
        for resultado in resultados_asistencia:
            tripulante_id = resultado.tripulante_id
            if tripulante_id in tripulantes_info:
                # Obtener el valor de asistencia como "Sí" o "No"
                tripulantes_info[tripulante_id]["Asistencia"] = "Sí" if resultado.Necesita_Asistencia else "No"
                tripulantes_info[tripulante_id]["Proveedor"] = resultado.Proveedor if resultado.Proveedor else ""

        comida_requerida = (
            session.query(
                Tripulante.tripulante_id,
                case(
                    (TripulanteRestaurante.tripulante_id.isnot(None), "Sí"),
                    else_="No"
                ).label("Requiere_Comida")
            )
            .outerjoin(TripulanteRestaurante, Tripulante.tripulante_id == TripulanteRestaurante.tripulante_id)
            .outerjoin(Restaurante, TripulanteRestaurante.restaurante_id == Restaurante.restaurante_id)
            .filter(
            (Restaurante.ciudad == codigo_ciudad)  # Filtrar por ciudad
            )
            .group_by(Tripulante.tripulante_id)
            .all()
        )

        # Agregar la información de comidas al diccionario
        for resultado in comida_requerida:
            tripulante_id = resultado.tripulante_id
            if tripulante_id in tripulantes_info:
                tripulantes_info[tripulante_id]["Requiere_Comida"] = resultado.Requiere_Comida
            else:
                # Si el tripulante no está en tripulantes_info, añadirlo con "No"
                pass

        # Si un tripulante no tiene registro de comida, agregar "No"
        for tripulante_id in tripulantes_info.keys():
            if "Requiere_Comida" not in tripulantes_info[tripulante_id]:
                tripulantes_info[tripulante_id]["Requiere_Comida"] = "No"

        # Obtener la información del hotel
        tripulantes_con_hotel = (
            session.query(
                Tripulante.tripulante_id,
                Hotel.nombre.label("Nombre_Hotel"),
                TripulanteHotel.tipo_habitacion,
                TripulanteHotel.fecha_salida,
            )
            .join(TripulanteHotel, TripulanteHotel.tripulante_id == Tripulante.tripulante_id)
            .join(Hotel, TripulanteHotel.hotel_id == Hotel.hotel_id)
            .filter(func.lower(Hotel.ciudad) == codigo_ciudad.lower())
            .all()
        )

        # Agregar la información de hotel y habitación al diccionario
        for resultado in tripulantes_con_hotel:
            tripulante_id = resultado.tripulante_id
            if tripulante_id in tripulantes_info:
                tripulantes_info[tripulante_id]["Hotel"] = resultado.Nombre_Hotel
                tripulantes_info[tripulante_id]["Habitación"] = resultado.tipo_habitacion
            else:
                # Si el tripulante no está en tripulantes_info, añadirlo con la información del hotel y habitación
                tripulantes_info[tripulante_id] = {
                    "Hotel": resultado.Nombre_Hotel,
                    "Habitación": resultado.tipo_habitacion
                }

        # Construir la consulta de transporte
        transporte_pick_up = (
            session.query(
                Tripulante.tripulante_id,
                Transporte.city_in.label("Ciudad_Transporte_in"),
                Transporte.place_in.label("Lugar_Transporte_in"),
                Transporte.city_end.label("Ciudad_Transporte_end"),
                Transporte.place_end.label("Lugar_Transporte_end"),
                TripulanteTransporte.date_pickup.label("Fecha_Pickup"),
                TripulanteTransporte.hours_pickup.label("Hora_Pickup")
            )
            .join(TripulanteTransporte, Tripulante.tripulante_id == TripulanteTransporte.tripulante_id)
            .filter(Transporte.transporte_id == TripulanteTransporte.transporte_id)
        )
        if ciudad_seleccionada != "ciudad":
            transporte_necesario = transporte_necesario.filter(and_(func.lower(Transporte.city_in) == ciudad_seleccionada),
                                                               Transporte.transporte_id == TripulanteTransporte.transporte_id)

        transporte_dict = defaultdict(list)
        for transporte in transporte_pick_up:
            transporte_dict[transporte.tripulante_id].append(transporte)

        # Procesar la información de transporte
        for tripulante_id, transportes in transporte_dict.items():
            vuelos = vuelos_dict.get(tripulante_id, {'arribo': [], 'salida': []})
            
            for transporte in transportes:
                tramo = f"{transporte.Lugar_Transporte_in}-{transporte.Lugar_Transporte_end}"
                if 'ATO-HOTEL' == tramo:  # Transporte hacia el hotel
                    vuelos_llegada = [
                        v for v in vuelos['arribo']
                        if v is not None and v.get('Aeropuerto_Llegada') and ciudad_seleccionada
                        and v['Aeropuerto_Llegada'].lower() == ciudad_seleccionada.lower()
                    ]
                    for vuelo in vuelos_llegada:
                        tripulantes_info[tripulante_id]["Fecha_Pick_Up"] = vuelo["Fecha_Vuelo_Arribo"]
                        tripulantes_info[tripulante_id]["Hora_Pick_Up"] = vuelo['Hora_Arribo'].time()

                elif 'HOTEL-ATO' in tramo:  # Transporte desde el hotel
                    vuelos_salida = [
                        v for v in vuelos['salida']
                        if v is not None and v.get('Aeropuerto_Salida') and v['Aeropuerto_Salida'].lower() == (ciudad_seleccionada.lower() if ciudad_seleccionada else '')
                    ]

                    for vuelo in vuelos_salida:
                        a1 = CITY_TO_AIRPORT_CODES.get(str(vuelo['Aeropuerto_Salida']))
                        try:
                            a2 = CITY_TO_AIRPORT_CODES.get(str(vuelo['Aeropuerto_Llegada']))
                        except KeyError:
                            #print(f"Error: 'Aeropuerto_Llegada' no encontrado en vuelo: {vuelo}")
                            a2 = None  # O alguna otra acción que consideres necesaria                      
                        if a1 == 'SCL' and a2 == 'PUQ':
                            a1 = f"{a1} Nacional"
                        elif a1 == 'SCL' and a2 != 'PUQ':
                            a1 = f"{a1} Internacional"

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

                        # Ajustar el tiempo
                        hora_pick_up = (vuelo['Hora_Salida'] - tiempo_a_restar).time()
                        tripulantes_info[tripulante_id]['Fecha_Pick_Up'] = vuelo['Fecha_Vuelo_Salida']
                        tripulantes_info[tripulante_id]["Hora_Pick_Up"] = hora_pick_up


        # Asegurarse de que todos los tripulantes tengan asignada la información del hotel y habitación
        for tripulante_id in tripulantes_info.keys():
            if "Hotel" not in tripulantes_info[tripulante_id]:
                tripulantes_info[tripulante_id]["Hotel"] = "No"
            if "Habitación" not in tripulantes_info[tripulante_id]:
                tripulantes_info[tripulante_id]["Habitación"] = "No"

        # Filtrar por tipo de tripulante
        if tipo_tripulante != "Tipo tripulante":  # Cambia este valor por el valor por defecto que tengas
            if tipo_tripulante == "AMBOS":
                # Si el tipo de tripulante es "AMBOS", no aplicamos filtro
                pass  
            else:
                tripulantes_info = {
                    tripulante_id: info for tripulante_id, info in tripulantes_info.items()
                    if "Type" in info and info["Type"] == tipo_tripulante
                }
                
                # Depuración: imprimir tripulantes sin el campo "Type"
                for tripulante_id, info in tripulantes_info.items():
                    if "Type" not in info:
                        print(f"El tripulante con ID {tripulante_id} no tiene el campo 'Type' en su información: {info}")
                    elif info["Type"] != tipo_tripulante:
                        print(f"El tripulante con ID {tripulante_id} tiene 'Type' distinto a '{tipo_tripulante}': {info['Type']}")

        
        # Filtrar por proveedor si se ha seleccionado uno
        proveedor_seleccionado = self.combo_proveedor.currentText()  # Obtener proveedor seleccionado
        if proveedor_seleccionado != "Proveedor":  # Comprobar que no sea el valor por defecto
            tripulantes_info = {
                tripulante_id: info for tripulante_id, info in tripulantes_info.items()
                if info.get("Proveedor", "").lower() == proveedor_seleccionado.lower()
            }

        # Filtrar para asegurar que solo queden registros completos
        tripulantes_info = {
            tripulante_id: info for tripulante_id, info in tripulantes_info.items()
            if info.get("First_Name") or info.get("Last_Name") or info.get("Vessel")  # Puedes ajustar según el criterio
        }


        headers = [
            "Owner", "Vessel", "ETA", "First Name", "Last Name", "Condition", "Type", "Proveedor", "Asistencia", "Transporte",
            "Comidas", "Nro Vuelo Arribo", "Fecha Vuelo Arribo", "Hora Arribo",
            "Hotel", "Habitacion", "Date Pick up", "Hora Pick Up",
            "Nro Vuelo Salida", "Fecha Vuelo Salida", "Hora Vuelo Salida"
        ]

        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)
        self.table_widget.setRowCount(0)
    
        # Agregar filas a la tabla
        for tripulante_id, info in tripulantes_info.items():
            row_position = self.table_widget.rowCount()  # Obtener la cantidad de filas actuales
            self.table_widget.insertRow(row_position)  # Insertar una nueva fila

            # Llenar las celdas de la fila con la información del tripulante
            self.table_widget.setItem(row_position, 0, QTableWidgetItem(info.get("Owner", "")))
            self.table_widget.setItem(row_position, 1, QTableWidgetItem(info.get("Vessel", "")))
            self.table_widget.setItem(row_position, 2, QTableWidgetItem(
                info.get("ETA", "").strftime("%d-%m-%Y") if isinstance(info.get("ETA", ""), datetime) else ""
            ))
            self.table_widget.setItem(row_position, 3, QTableWidgetItem(info.get("First_Name", "")))
            self.table_widget.setItem(row_position, 4, QTableWidgetItem(info.get("Last_Name", "")))
            self.table_widget.setItem(row_position, 5, QTableWidgetItem(info.get("Condition", "")))
            self.table_widget.setItem(row_position, 6, QTableWidgetItem(info.get("Type", "")))
            self.table_widget.setItem(row_position, 7, QTableWidgetItem(info.get("Proveedor", "")))
            self.table_widget.setItem(row_position, 8, QTableWidgetItem(info.get("Asistencia", "")))
            self.table_widget.setItem(row_position, 9, QTableWidgetItem(
                "Sí" if info.get("Transporte", False) else "No"
            ))
            self.table_widget.setItem(row_position, 10, QTableWidgetItem(info.get("Requiere_Comida", "")))
            self.table_widget.setItem(row_position, 11, QTableWidgetItem(info.get("Nro_Vuelo_Arribo", "")))
            self.table_widget.setItem(row_position, 12, QTableWidgetItem(
                info.get("Fecha_Vuelo_Arribo", "").strftime("%d-%m-%Y") if isinstance(info.get("Fecha_Vuelo_Arribo", ""), datetime) else ""
            ))
            self.table_widget.setItem(row_position, 13, QTableWidgetItem(
                info.get("Hora_Arribo", "").strftime("%H:%M") if isinstance(info.get("Hora_Arribo", ""), datetime) else ""
            ))
            self.table_widget.setItem(row_position, 14, QTableWidgetItem(info.get("Hotel", "")))
            self.table_widget.setItem(row_position, 15, QTableWidgetItem(info.get("Habitación", "")))
            self.table_widget.setItem(row_position, 16, QTableWidgetItem(
                info.get("Fecha_Pick_Up", "").strftime("%d-%m-%Y") if isinstance(info.get("Fecha_Pick_Up", ""), datetime) else ""
            ))
            # Obtén el valor de "Hora_Pick_Up"
            hora_pick_up_value = info.get("Hora_Pick_Up", None)

            # Inicializa la cadena para almacenar el valor
            hora_pick_up_str = ""

            # Verifica si es un datetime o un time
            if isinstance(hora_pick_up_value, datetime):
                hora_pick_up_str = hora_pick_up_value.strftime("%H:%M")
            elif isinstance(hora_pick_up_value, time):
                hora_pick_up_str = hora_pick_up_value.strftime("%H:%M")

            # Imprime el resultado
            self.table_widget.setItem(row_position, 17, QTableWidgetItem(hora_pick_up_str))  

            self.table_widget.setItem(row_position, 18, QTableWidgetItem(info.get("Nro_Vuelo_Salida", "")))
            self.table_widget.setItem(row_position, 19, QTableWidgetItem(
                info.get("Fecha_Vuelo_Salida", "").strftime("%d-%m-%Y") if isinstance(info.get("Fecha_Vuelo_Salida", ""), datetime) else ""
            ))
            self.table_widget.setItem(row_position, 20, QTableWidgetItem(
                info.get("Hora_Vuelo_Salida", "").strftime("%H:%M") if isinstance(info.get("Hora_Vuelo_Salida", ""), datetime) else ""
            ))

    # Mantén las funciones de formateo separadas
    def format_date(self, value):
        """Convierte un valor datetime a solo la fecha."""
        if isinstance(value, datetime):
            return value.strftime('%d-%m-%Y')
        return str(value)

    def format_time(self, value):
        """Convierte un valor datetime a solo la hora."""
        if isinstance(value, datetime):
            return value.strftime('%H:%M')
        return str(value)

    def generar_excel(self, ciudad_seleccionada, tipo_crew, proveedor, fecha_inicio, fecha_fin):
        # Crear un DataFrame con los datos de la tabla
        data = []
        for row in range(self.table_widget.rowCount()):
            row_data = []
            for column in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, column)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        # Definir los nombres de las columnas
        column_names = ["Owner", "Vessel", "ETA", "First Name", "Last Name", "Condition", "Type", 
                        "Proveedor", "Asistencia", "Transportes", "Comidas", "Nro Vuelo Arribo", 
                        "Fecha Vuelo Arribo", "Hora Arribo", "Hotel", "Habitación", 
                        "Date Pick Up", "Hora Pick Up", "Nro Vuelo Salida", 
                        "Fecha Vuelo Salida", "Hora Vuelo Salida"]

        df = pd.DataFrame(data, columns=column_names)

        # Generar nombre de archivo basado en buque y hotel seleccionados
        file_name_parts = ["asistencia"]
        if ciudad_seleccionada.lower() != "ciudad" and ciudad_seleccionada.lower() not in file_name_parts:
            file_name_parts.append(ciudad_seleccionada)
        if tipo_crew.lower() != "tipo tripulante" and tipo_crew.lower() not in file_name_parts:
            file_name_parts.append(tipo_crew)
        if proveedor.lower() != "proveedor" and proveedor.lower() not in file_name_parts:
            file_name_parts.append(proveedor)

        file_name = "_".join(file_name_parts) + ".xlsx"


        # Guardar en un archivo Excel
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Guardar archivo Excel", 
            file_name,
            "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if file_path:
            wb = Workbook()
            ws = wb.active

            # Título en negrita, subrayado y de tamaño grande, centrado en más columnas
            ws.merge_cells('A1:T1')  # Fusionar más columnas para centrar el título
            title_cell = ws['A1']
            title_cell.value = "Requerimiento asistencias"
            title_cell.font = Font(size=24, bold=True, underline="single")  # Tamaño de fuente más grande
            title_cell.alignment = Alignment(horizontal="center", vertical="center")

            # Mostrar "CIUDAD" solo si es diferente de "Ciudad"
            if ciudad_seleccionada.lower() != "ciudad":
                ws.cell(row=2, column=1, value="CIUDAD").font = Font(bold=True)
                ws.cell(row=2, column=2, value=ciudad_seleccionada)

            # Configurar el valor predeterminado para "TIPO" y "PROVEEDOR" si no están seleccionados
            tipo_crew_text = tipo_crew if tipo_crew.lower() != "tipo tripulante" else "Ambos"
            proveedor_text = proveedor if proveedor.lower() != "proveedor" else "No se seleccionó proveedor"

            # Agregar "TIPO" con el valor de tipo_crew
            ws.cell(row=3, column=1, value="TIPO").font = Font(bold=True)
            ws.cell(row=3, column=2, value=tipo_crew_text)

            # Agregar "PROVEEDOR" con el valor de proveedor
            ws.cell(row=4, column=1, value="PROVEEDOR").font = Font(bold=True)
            ws.cell(row=4, column=2, value=proveedor_text)

            # Verificar si el filtro de fechas está activado y mostrar "ETA Desde" y "ETA Hasta"
            if self.check_fecha.isChecked() and fecha_inicio and fecha_fin:
                ws.cell(row=5, column=1, value="ETA Desde:").font = Font(bold=True)
                ws.cell(row=5, column=2, value=fecha_inicio.strftime("%d-%m-%Y"))
                ws.cell(row=6, column=1, value="ETA Hasta:").font = Font(bold=True)
                ws.cell(row=6, column=2, value=fecha_fin.strftime("%d-%m-%Y"))
            else:
                ws.cell(row=5, column=1, value="ETA No seleccionada").font = Font(bold=True)

            # Estilos de borde, relleno y alineación
            thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
            header_fill = PatternFill(start_color='ADD8E6', end_color='ADD8E6', fill_type='solid')
            data_fill = PatternFill(start_color='FFFF99', end_color='FFFF99', fill_type='solid')

            # Escribir los encabezados de la tabla
            for col_num, col_name in enumerate(column_names, 1):
                cell = ws.cell(row=8, column=col_num)
                cell.value = col_name
                cell.fill = header_fill
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = thin_border

            # Escribir los datos del DataFrame y aplicar borde a las celdas
            for row_num, row_data in enumerate(df.values, start=9):
                for col_num, cell_value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_num, column=col_num)
                    cell.value = cell_value
                    cell.fill = data_fill
                    cell.border = thin_border

            # Ajustar el ancho de las columnas basándonos en los datos del DataFrame
            for col_num, column in enumerate(df.columns, 1):
                max_length = max(df[column].astype(str).apply(len).max(), len(column)) + 2
                ws.column_dimensions[get_column_letter(col_num)].width = max_length

            # Guardar el archivo Excel
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

        self.label = QLabel("Requerimientos alimentación")
        font = QFont()
        font.setPointSize(20)  # Tamaño de fuente
        font.setBold(True)      # Negrita
        self.label.setFont(font)
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)  # Centrar el título

        layout.addSpacing(20)

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
        file_name_parts = ["req_ali"]
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

            # Escribir el texto final antes de la tabla
            ws.cell(row=1, column=1, value="Informe requerimientos alimentación").font = Font(size=20, bold=True, underline="single")

            # Encabezados personalizados
            ws.cell(row=2, column=1, value="BUQUE").font = Font(bold=True)
            ws.cell(row=2, column=2, value=buque_seleccionado if buque_seleccionado.lower() != "buque" else "")

            ws.cell(row=3, column=1, value="ETA").font = Font(bold=True)
            if fecha_inicio_eta and self.check_fecha_eta.isChecked():
                ws.cell(row=3, column=2, value=fecha_inicio_eta)
            else:
                ws.cell(row=3, column=2, value="ETA No seleccionada")

            ws.cell(row=4, column=1, value="OWNER").font = Font(bold=True)
            ws.cell(row=4, column=2, value=owner_seleccionado if owner_seleccionado.lower() != "owner" else "")

            ws.cell(row=5, column=1, value="CIUDAD COMIDA").font = Font(bold=True)
            ws.cell(row=5, column=2, value=ciudad_seleccionada if ciudad_seleccionada.lower() != "ciudad" else "")

            ws.cell(row=6, column=1, value="ENTRE FECHA").font = Font(bold=True)
            if fecha_inicio_eta and self.check_fecha_rango.isChecked():
                ws.cell(row=6, column=2, value=fecha_inicio_rango)
                ws.cell(row=6, column=3, value=fecha_fin_rango)
            else:
                ws.cell(row=6, column=2, value="Fechas no seleccionadas")

            ws.cell(row=7, column=1, value="RESTAURANTE").font = Font(bold=True)
            ws.cell(row=7, column=2, value=restaurant_seleccionado if restaurant_seleccionado.lower() != "restaurante" else "")            

            # Aplicar negrita a los encabezados
            header_fill = PatternFill(start_color='ADD8E6', end_color='ADD8E6', fill_type='solid')
            for col_num, col_name in enumerate(df.columns, 1):
                cell = ws.cell(row=9, column=col_num)  # Cambiar a fila 7
                cell.value = col_name
                cell.fill = header_fill
                cell.font = Font(bold=True)  # Negrita


            # Crear un borde
            thin_border = Border(
                left=Side(style='thin'), 
                right=Side(style='thin'), 
                top=Side(style='thin'), 
                bottom=Side(style='thin')
            )

            # Aplicar el borde y centrado en el encabezado
            header_fill = PatternFill(start_color='ADD8E6', end_color='ADD8E6', fill_type='solid')
            for col_num, col_name in enumerate(df.columns, 1):
                cell = ws.cell(row=9, column=col_num)  # Cambiar a fila de encabezado
                cell.value = col_name
                cell.fill = header_fill
                cell.font = Font(bold=True)
                cell.border = thin_border  # Aplicar el borde al encabezado
                cell.alignment = Alignment(horizontal="center", vertical="center")  # Centrar el encabezado

            # Escribir los datos del DataFrame
            data_fill = PatternFill(start_color='FFFF99', end_color='FFFF99', fill_type='solid')
            for row_num, row_data in enumerate(df.values, start=10):  # Cambiar a fila 8
                for col_num, cell_value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_num, column=col_num)
                    cell.value = cell_value
                    cell.fill = data_fill
                    cell.border = thin_border  # Aplicar el borde
  
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

            signature_col_index = df.columns.get_loc("Signature") + 1  # +1 porque los índices de columna en openpyxl comienzan en 1

            # Ajusta el ancho de la columna "Signature"
            signature_column_letter = get_column_letter(signature_col_index)
            ws.column_dimensions[signature_column_letter].width = 30

            for row_num in range(10, 10 + len(df)):
                for col_num in range(1, len(df.columns) + 1):
                    if col_num == 1 or col_num == 5:  # Columna "Nro"
                        ws.cell(row=row_num, column=col_num).alignment = Alignment(horizontal="center", vertical="center")
                    else:  # Otras columnas
                        ws.cell(row=row_num, column=col_num).alignment = Alignment(horizontal="left", vertical="center")
                
                # Ajustar la altura de todas las filas
                ws.row_dimensions[row_num].height = 30

            # Guardar el archivo Excel
            wb.save(file_path)

    def volver_a_opciones_programar(self):
        self.main_window.stacked_widget.setCurrentIndex(self.main_window.menu_reportes_index)