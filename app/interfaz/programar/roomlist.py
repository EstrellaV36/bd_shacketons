import pandas as pd
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QFileDialog, QDateEdit, QCheckBox
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from app.database import get_db_session
from app.models import Buque, EtaCiudad, Tripulante, Hotel, TripulanteHotel, Buque
from openpyxl.styles import PatternFill
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from datetime import datetime, time
from sqlalchemy import func, and_

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
                room_type = str(roomlist.Rooms).capitalize() if roomlist.Rooms else ""
                self.table_widget.setItem(row, 9, QTableWidgetItem(room_type))

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

            for col_num, col_name in enumerate(df.columns, 1):
                cell = ws.cell(row=7, column=col_num)
                cell.value = col_name
                cell.fill = header_fill

            for row_num, row_data in enumerate(df.values, start=8):
                for col_num, cell_value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_num, column=col_num)
                    cell.value = cell_value
                    cell.fill = data_fill

                    # Centrar el número correlativo
                    if col_num == 1:  # Columna "Nro"
                        cell.alignment = Alignment(horizontal="center")

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