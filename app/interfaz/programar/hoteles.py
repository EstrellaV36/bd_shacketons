import pandas as pd
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QFileDialog, QDateEdit, QCheckBox
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from app.database import get_db_session
from app.models import Buque, EtaCiudad, Tripulante, Hotel, TripulanteHotel, Buque, Viaje
from app.controller.controllers import CITY_AIRPORT_CODES, CITY_TO_AIRPORT_CODES
from openpyxl.styles import PatternFill
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment
from datetime import datetime, time
from sqlalchemy import func, or_

class HotelScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        session = get_db_session()

        self.label = QLabel("REQUERIMIENTO HOTEL")
        self.label.setStyleSheet("""
            font-size: 40px;  /* Tamaño de fuente */
            font-weight: bold; /* Negrita */
            color: #00272d;    /* Color del texto */
            text-align: center; /* Centrar el texto horizontalmente */
            margin-bottom: 20px; /* Espacio debajo del título */
        """)
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
        owner_seleccionado = self.combo_owner.currentText()
        # Obtener las fechas seleccionadas
        fecha_inicio = self.date_start1.date().toString("dd-MM-yyyy")  # Formato de fecha: dd-mm-aaaa
        fecha_fin = self.date_end1.date().toString("dd-MM-yyyy")

    # Llamar a la función generar_excel con ciudad, buque y las fechas
        self.generar_excel(ciudad_seleccionada, buque_seleccionado,owner_seleccionado, fecha_inicio, fecha_fin)

    def actualizar_datos(self):
        ciudad_seleccionada = self.combo_ciudades.currentText()
        buque_seleccionado = self.combo_buques.currentText()
        owner_seleccionado = self.combo_owner.currentText()
        if ciudad_seleccionada != "Ciudad":
            self.label.setText(f"REQUERIMIENTO HOTEL EN {ciudad_seleccionada.upper()}")
        else: 
            self.label.setText(f"REQUERIMIENTO HOTEL")

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
                Viaje.estado.label("Estado"),
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
            .join(Viaje, Tripulante.tripulante_id==Viaje.tripulante_id)
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

    def generar_excel(self, ciudad_seleccionada, buque_seleccionado, owner_seleccionado, fecha_inicio, fecha_fin):
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

        # Crear un DataFrame con los datos de la tabla
        data = []
        for row in range(self.table_widget.rowCount()):
            row_data = []
            for column in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, column)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        column_names = ["Owner", "First name", "Last name", "Gender", "Nacionalidad", "Position",
                        "Categoria", "Hotel Ciudad", "Check in", "Check out", "Rooms"]
        df = pd.DataFrame(data, columns=column_names)

        # Normalizar columnas necesarias
        df['Rooms'] = df['Rooms'].str.lower()  # Normalizar tipo de habitación
        df['Gender'] = df['Gender'].str.lower()  # Normalizar género
        df['Check in'] = pd.to_datetime(df['Check in'], errors='coerce')
        df['Check out'] = pd.to_datetime(df['Check out'], errors='coerce')

        # Ordenar por categoría y fecha de check-in
        df.sort_values(by=["Categoria", "Check in"], ascending=[True, True], inplace=True)

        # Insertar columna de números
        df.insert(0, "Nro", range(1, len(df) + 1))

        # Formatear las columnas "Check in" y "Check out" para mostrar solo la fecha
        df['Check in'] = df['Check in'].dt.strftime('%Y-%m-%d')
        df['Check out'] = df['Check out'].dt.strftime('%Y-%m-%d')

        # Inicialización
        group_counter = 'A'
        current_category = None
        double_buffer_m = []  # Buffer para habitaciones dobles masculinas
        double_buffer_f = []  # Buffer para habitaciones dobles femeninas

        # Procesar cada fila
        for idx, row in df.iterrows():
            room_type = row['Rooms']
            gender = row['Gender']
            categoria = row['Categoria']  # Categoría del tripulante actual

            # Cambiar de categoría: limpiar buffers pendientes
            if current_category is None or current_category != categoria:
                current_category = categoria

                # Asignar grupos pendientes del buffer
                if double_buffer_m:
                    df.loc[double_buffer_m, 'Grupo'] = group_counter
                    group_counter = incrementar_grupo(group_counter)
                    double_buffer_m = []
                if double_buffer_f:
                    df.loc[double_buffer_f, 'Grupo'] = group_counter
                    group_counter = incrementar_grupo(group_counter)
                    double_buffer_f = []

            # Habitaciones dobles
            if "doble" in room_type:
                if gender == "m":
                    double_buffer_m.append(idx)
                    # Asignar si el buffer tiene dos personas
                    if len(double_buffer_m) == 2:
                        df.loc[double_buffer_m, 'Grupo'] = group_counter
                        group_counter = incrementar_grupo(group_counter)
                        double_buffer_m = []
                elif gender == "f":
                    double_buffer_f.append(idx)
                    # Asignar si el buffer tiene dos personas
                    if len(double_buffer_f) == 2:
                        df.loc[double_buffer_f, 'Grupo'] = group_counter
                        group_counter = incrementar_grupo(group_counter)
                        double_buffer_f = []

            # Habitaciones individuales
            elif "single" in room_type:
                df.loc[idx, 'Grupo'] = group_counter
                group_counter = incrementar_grupo(group_counter)

        # Asignar buffers pendientes al final
        if double_buffer_m:
            df.loc[double_buffer_m, 'Grupo'] = group_counter
            group_counter = incrementar_grupo(group_counter)

        if double_buffer_f:
            df.loc[double_buffer_f, 'Grupo'] = group_counter
            group_counter = incrementar_grupo(group_counter)


        # Exportar a Excel
        file_name_parts = ["informe_hotel"]
        if ciudad_seleccionada.lower() != "ciudad":
            file_name_parts.append(ciudad_seleccionada)
        if buque_seleccionado.lower() != "buque":
            file_name_parts.append(buque_seleccionado)
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

            # Escribir título
            ws['A1'] = "REQUERIMIENTO HOTEL"
            ws['A1'].font = Font(size=20, bold=True, underline="single")
            ws['A1'].alignment = Alignment(horizontal="left", vertical="center")

            # Información en la primera columna bajo el título
            ws['A2'] = "BUQUE"
            ws['A2'].font = Font(bold=True)
            ws['B2'] = buque_seleccionado if buque_seleccionado and buque_seleccionado.lower() != "buque" else "No seleccionado"

            ws['A3'] = "OWNER"
            ws['A3'].font = Font(bold=True)
            ws['B3'] = owner_seleccionado if owner_seleccionado and owner_seleccionado.lower() != "owner" else "No seleccionado"

            ws['A4'] = "ETA inicio"
            ws['A4'].font = Font(bold=True)
            ws['B4'] = fecha_inicio if fecha_inicio else "No especificado"

            ws['A5'] = "ETA fin"
            ws['A5'].font = Font(bold=True)
            ws['B5'] = fecha_fin if fecha_fin else "No especificado"

            ws['A6'] = "CIUDAD"
            ws['A6'].font = Font(bold=True)
            ws['B6'] = ciudad_seleccionada if ciudad_seleccionada and ciudad_seleccionada.lower() != "ciudad" else "No especificada"

            # Filtrar habitaciones
            filtered_df = df[df['Rooms'].str.contains('doble|single', case=False, na=False)]

            # Normalizar valores en Rooms y Gender para garantizar consistencia
            filtered_df['Rooms'] = filtered_df['Rooms'].str.strip().str.lower()
            filtered_df['Gender'] = filtered_df['Gender'].str.strip().str.lower()

            def ajustar_conteo_dobles(df):
                conteos = []
                for categoria in df['Categoria'].unique():
                    
                    # Sub DataFrame por categoría
                    sub_df = df[df['Categoria'] == categoria]

                    # Contar habitaciones dobles y singles para cada género
                    dobles_m = len(sub_df[(sub_df['Rooms'].str.contains('doble')) & (sub_df['Gender'] == 'm')]) // 2
                    dobles_f = len(sub_df[(sub_df['Rooms'].str.contains('doble')) & (sub_df['Gender'] == 'f')]) // 2
                    singles_m = len(sub_df[(sub_df['Rooms'].str.contains('single')) & (sub_df['Gender'] == 'm')])
                    singles_f = len(sub_df[(sub_df['Rooms'].str.contains('single')) & (sub_df['Gender'] == 'f')])

                    # Manejar casos de habitaciones dobles incompletas
                    dobles_m_extra = len(sub_df[(sub_df['Rooms'].str.contains('doble')) & (sub_df['Gender'] == 'm')]) % 2
                    dobles_f_extra = len(sub_df[(sub_df['Rooms'].str.contains('doble')) & (sub_df['Gender'] == 'f')]) % 2


                    conteos.append({
                        'Categoria': categoria,
                        'Singles M': singles_m,
                        'Dobles M': dobles_m + dobles_m_extra,
                        'Singles F': singles_f,
                        'Dobles F': dobles_f + dobles_f_extra,
                    })

                return pd.DataFrame(conteos)

            # Aplicar ajuste de conteo
            conteo_habitaciones = ajustar_conteo_dobles(filtered_df)

            # Agregar totales
            conteo_habitaciones['Total Singles'] = conteo_habitaciones['Singles M'] + conteo_habitaciones['Singles F']
            conteo_habitaciones['Total Dobles'] = conteo_habitaciones['Dobles M'] + conteo_habitaciones['Dobles F']

            # Escribir los datos en Excel
            conteo_start_row = 2  # La fila donde comenzará el conteo
            conteo_start_col = 4  # Columna D (columna 4 en Excel)

            conteo_headers = ['Categoria', 'Singles M', 'Dobles M', 'Singles F', 'Dobles F', 'Total Singles', 'Total Dobles']
            for col_offset, header_name in enumerate(conteo_headers):
                cell = ws.cell(row=conteo_start_row, column=conteo_start_col + col_offset)
                cell.value = header_name
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal="center", vertical="center")

            for idx, row in conteo_habitaciones.iterrows():
                for col_offset, key in enumerate(conteo_headers):
                    cell = ws.cell(row=conteo_start_row + 1 + idx, column=conteo_start_col + col_offset)
                    cell.value = row[key]
                    cell.alignment = Alignment(horizontal="center", vertical="center")


            # Fila en blanco antes de los encabezados
            header_start_row = 8  # Fila donde comienzan los encabezados de la tabla

            # Escribir encabezados de la tabla
            header_fill = PatternFill(start_color='ADD8E6', end_color='ADD8E6', fill_type='solid')
            thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

            for col_num, col_name in enumerate(df.columns, 1):
                cell = ws.cell(row=header_start_row, column=col_num)
                cell.value = col_name
                cell.fill = header_fill
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = thin_border

            # Escribir los datos de la tabla
            data_fill = PatternFill(start_color='FFFF99', end_color='FFFF99', fill_type='solid')
            for row_num, row_data in enumerate(df.values, start=header_start_row + 1):
                for col_num, cell_value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_num, column=col_num)
                    cell.value = cell_value
                    cell.fill = data_fill
                    cell.border = thin_border
                    cell.alignment = Alignment(horizontal="center", vertical="center")

            # Ajustar automáticamente el ancho de las columnas
            for col in ws.columns:
                max_length = 0
                column_letter = get_column_letter(col[0].column)  # Obtener la letra de la columna
                for cell in col:
                    if not isinstance(cell, MergedCell):  # Ignorar celdas combinadas
                        try:
                            if cell.value:
                                max_length = max(max_length, len(str(cell.value)))
                        except:
                            pass
                adjusted_width = max_length + 2  # Añadir un poco de espacio extra
                ws.column_dimensions[column_letter].width = adjusted_width

        # Guardar el archivo Excel
        wb.save(file_path)

    def toggle_fecha_fields(self):
        is_checked = self.check_fecha.isChecked()
        self.date_start1.setEnabled(is_checked)
        self.date_end1.setEnabled(is_checked)

    def volver_a_opciones_programar(self):
        self.main_window.stacked_widget.setCurrentIndex(self.main_window.opciones_programar_index)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        session = get_db_session()

        self.label = QLabel("REQUERIMIENTO HOTEL")
        self.label.setStyleSheet("""
            font-size: 40px;  /* Tamaño de fuente */
            font-weight: bold; /* Negrita */
            color: #00272d;    /* Color del texto */
            text-align: center; /* Centrar el texto horizontalmente */
            margin-bottom: 20px; /* Espacio debajo del título */
        """)

        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)  # Centrar el título

        layout.addSpacing(20)

        # Llenar el combo de ciudades desde la base de datos
        self.combo_ciudades = QComboBox()
        self.combo_ciudades.addItem("Ciudad") 
        ciudades = session.query(Hotel.ciudad).distinct().all()  # Consulta para obtener las ciudades únicas
        for ciudad in ciudades:
            self.combo_ciudades.addItem(ciudad.ciudad)
        layout.addWidget(self.combo_ciudades)

        self.combo_owner = QComboBox()
        self.combo_owner.addItems(["Owner"])
        owners = session.query(Buque.empresa).distinct().all()  # Consulta para obtener los nombres de los buques
        for owner in owners:
            self.combo_owner.addItem(owner.empresa)
        layout.addWidget(self.combo_owner)

        # Llenar el combo de buques desde la base de datos
        self.combo_buques = QComboBox()
        self.combo_buques.addItem("Buque")  # Agregar un valor por defecto

        buques = session.query(Buque.nombre).distinct().all()  # Consulta para obtener los nombres de los buques
        for buque in buques:
            self.combo_buques.addItem(buque.nombre)
        layout.addWidget(self.combo_buques)

        # Filtro por fechas
        self.check_fecha = QCheckBox("Habilitar filtro por fechas")
        self.check_fecha.setChecked(False)
        self.check_fecha.stateChanged.connect(self.actualizar_datos)
        layout.addWidget(self.check_fecha)

        # Layout horizontal para las fechas
        layout_filtro = QHBoxLayout()
        self.date_start1 = QDateEdit()
        self.date_start1.setCalendarPopup(True)
        self.date_start1.setDate(QDate.currentDate())
        layout_filtro.addWidget(QLabel("Fecha inicio:"))
        layout_filtro.addWidget(self.date_start1)

        self.date_end1 = QDateEdit()
        self.date_end1.setCalendarPopup(True)
        self.date_end1.setDate(QDate.currentDate())
        layout_filtro.addWidget(QLabel("Fecha fin:"))
        layout_filtro.addWidget(self.date_end1)

        layout.addLayout(layout_filtro)

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
        self.combo_owner.currentTextChanged.connect(self.actualizar_datos)
        self.combo_buques.currentTextChanged.connect(self.actualizar_datos)
        self.date_start1.dateChanged.connect(self.actualizar_datos)
        self.date_end1.dateChanged.connect(self.actualizar_datos)

        # Actualizar los datos inicialmente
        self.actualizar_datos()

    def generar_excel_con_ciudad(self):
        ciudad_seleccionada = self.combo_ciudades.currentText()
        buque_seleccionado = self.combo_buques.currentText()
        owner_seleccionado = self.combo_owner.currentText()
        # Obtener las fechas seleccionadas
        fecha_inicio = self.date_start1.date().toString("dd-MM-yyyy")  # Formato de fecha: dd-mm-aaaa
        fecha_fin = self.date_end1.date().toString("dd-MM-yyyy")

    # Llamar a la función generar_excel con ciudad, buque y las fechas
        self.generar_excel(ciudad_seleccionada, buque_seleccionado, owner_seleccionado, fecha_inicio, fecha_fin)

    def actualizar_datos(self):
        ciudad_seleccionada = self.combo_ciudades.currentText()
        buque_seleccionado = self.combo_buques.currentText()
        owner_seleccionado = self.combo_owner.currentText()
        if ciudad_seleccionada != "Ciudad":
            self.label.setText(f"REQUERIMIENTO HOTEL {ciudad_seleccionada.upper()}")
        else: 
            self.label.setText(f"REQUERIMIENTO HOTEL")

        # Cargar datos basados en los filtros seleccionados
        self.cargar_datos(ciudad_seleccionada, buque_seleccionado, owner_seleccionado)

    def cargar_datos(self, ciudad_seleccionada, buque_seleccionado, owner_seleccionado):
        session = get_db_session()

        buque_seleccionado = buque_seleccionado.lower()
        fecha_inicio = self.date_start1.date().toPyDate()
        fecha_fin = datetime.combine(self.date_end1.date().toPyDate(), time.max)

        hotel_necesario = (
            session.query(
                Tripulante.tripulante_id,
                Viaje.estado.label("Estado"),
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
                TripulanteHotel.tipo_habitacion.label("Rooms"),
                Buque.empresa.label("Owner"),
            )
            .join(TripulanteHotel, Tripulante.tripulante_id == TripulanteHotel.tripulante_id)
            .join(Viaje, Viaje.tripulante_id == Tripulante.tripulante_id)
            .join(Buque, Tripulante.buque_id == Buque.buque_id)
            .join(Hotel, Hotel.hotel_id == TripulanteHotel.hotel_id)
        )

        hotel_necesario = hotel_necesario.order_by(TripulanteHotel.categoria, TripulanteHotel.fecha_entrada)

        resultados_iniciales = hotel_necesario.all()
        filtros_activos = False

        if ciudad_seleccionada != "Ciudad":
            hotel_necesario = hotel_necesario.filter(Hotel.ciudad == ciudad_seleccionada)
            filtros_activos = True

        if buque_seleccionado != "buque":
            hotel_necesario = hotel_necesario.filter(func.lower(Buque.nombre) == buque_seleccionado)
            filtros_activos = True

        if owner_seleccionado != "Owner":
            hotel_necesario = hotel_necesario.filter((Buque.empresa) == owner_seleccionado)


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

            filtros_activos = True

        # Si hay filtros activos, ejecutar consulta filtrada
        if filtros_activos:
            resultados = hotel_necesario.all()
        else:
            # Si no hay filtros activos, usar los resultados iniciales
            resultados = resultados_iniciales

        # Ejecutar consulta con filtros y mostrar resultados
        hotel_necesario = hotel_necesario.order_by(TripulanteHotel.categoria, TripulanteHotel.fecha_entrada)
        resultados_filtrados = hotel_necesario.all()
        self.mostrar_resultados_en_tabla(resultados_filtrados)

    def mostrar_resultados_en_tabla(self, resultados):
        # Limpiar tabla
        self.table_widget.setRowCount(0)

        # Configurar encabezados
        self.table_widget.setColumnCount(11)
        self.table_widget.setHorizontalHeaderLabels(
            ["Owner", "First Name", "Last Name", "Gender", "Nacionalidad", "Position", "Categoria", "Hotel Ciudad", "Check In", "Check Out", "Rooms"]
        )

        # Llenar la tabla con resultados
        for resultado in resultados:
            row = self.table_widget.rowCount()
            self.table_widget.insertRow(row)
            self.table_widget.setItem(row, 0, QTableWidgetItem(resultado.Owner))
            self.table_widget.setItem(row, 1, QTableWidgetItem(resultado.First_Name))
            self.table_widget.setItem(row, 2, QTableWidgetItem(resultado.Last_Name))
            self.table_widget.setItem(row, 3, QTableWidgetItem(resultado.Genero))
            self.table_widget.setItem(row, 4, QTableWidgetItem(resultado.Nacionalidad))
            self.table_widget.setItem(row, 5, QTableWidgetItem(resultado.Position))
            self.table_widget.setItem(row, 6, QTableWidgetItem(str(resultado.Categoria)))
            self.table_widget.setItem(row, 7, QTableWidgetItem(resultado.Ciudad_Hotel))
            self.table_widget.setItem(row, 8, QTableWidgetItem(str(resultado.check_in)))
            self.table_widget.setItem(row, 9, QTableWidgetItem(str(resultado.check_out)))
            self.table_widget.setItem(row, 10, QTableWidgetItem(resultado.Rooms))

    def generar_excel(self, ciudad_seleccionada, buque_seleccionado, owner_seleccionado, fecha_inicio, fecha_fin,):
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
        if buque_seleccionado.lower() != "buque" and buque_seleccionado.lower() not in file_name_parts:
            file_name_parts.append(buque_seleccionado)
        if ciudad_seleccionada.lower() != "ciudad" and buque_seleccionado.lower() not in file_name_parts:
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

            # Solo mostrar las fechas si están seleccionadas
            if fecha_inicio and fecha_fin:
                ws.cell(row=3, column=1, value="ETA Desde:").font = Font(bold=True)
                ws.cell(row=3, column=2, value=fecha_inicio)
                ws.cell(row=4, column=1, value="ETA Hasta:").font = Font(bold=True)
                ws.cell(row=4, column=2, value=fecha_fin)
            else:
                ws.cell(row=3, column=1, value="ETA No seleccionada")

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

    def volver_a_opciones_programar(self):
        self.main_window.stacked_widget.setCurrentIndex(self.main_window.opciones_programar_index)