import pandas as pd
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QFileDialog, QDateEdit, QCheckBox
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from app.database import get_db_session
from app.models import Buque, EtaCiudad, Tripulante, Restaurante, TripulanteRestaurante, Hotel, TripulanteHotel, Buque
from openpyxl.styles import PatternFill
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment
from datetime import datetime, time
from sqlalchemy import func

class AlimentosScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        session = get_db_session()
        layout = QVBoxLayout(self)

        # Botón "Volver" para regresar a la pantalla anterior
        button_volver = QPushButton("Volver")
        button_volver.setStyleSheet("""
            font-size: 16px;  /* Tamaño de la letra */
            padding: 0px;    /* Elimina el espacio interno */
            line-height: 18px; /* Asegura que el texto no se corte verticalmente */
            text-align: center; /* Centra el texto */
        """)
        button_volver.setFixedWidth(80)
        button_volver.setFixedHeight(40)
        button_volver.clicked.connect(self.volver_a_opciones_programar)
        layout.addWidget(button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        self.label = QLabel("Requerimientos alimentación")
        font = QFont()
        font.setPointSize(20)  # Tamaño de fuente
        font.setBold(True)      # Negrita
        self.label.setFont(font)
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)  # Centrar el título

        layout.addSpacing(20)

        # Crear un QHBoxLayout para agrupar los combos de Owner y Ciudad
        layout_owner_ciudad = QHBoxLayout()

        # Llenar el combo de buques desde la base de datos
        self.combo_buques = QComboBox()
        self.combo_buques.addItem("Buque")  # Agregar un valor por defecto

        buques = session.query(Buque.nombre).distinct().all()  # Consulta para obtener los nombres de los buques
        for buque in buques:
            self.combo_buques.addItem(buque.nombre)
        layout.addWidget(self.combo_buques)

        layout_owner_ciudad.addWidget(self.combo_buques)

        # Llenar el combo de owners desde la base de datos
        self.combo_owners = QComboBox()
        self.combo_owners.addItem("Owner")  # Agregar un valor por defecto

        owners = session.query(Buque.empresa).distinct().all()  # Consulta para obtener los owners únicos
        for owner in owners:
            self.combo_owners.addItem(owner.empresa)

        layout_owner_ciudad.addWidget(self.combo_owners)

        # Llenar el combo de ciudades desde la base de datos
        self.combo_ciudades = QComboBox()
        self.combo_ciudades.addItem("Ciudad")  # Agregar un valor por defecto

        ciudades = session.query(Hotel.ciudad).distinct().all()  # Consulta para obtener las ciudades únicas
        for ciudad in ciudades:
            self.combo_ciudades.addItem(ciudad.ciudad)

        layout_owner_ciudad.addWidget(self.combo_ciudades)

        # Agregar el QHBoxLayout al layout principal
        layout.addLayout(layout_owner_ciudad)

        layout_filtros_fechas = QHBoxLayout()

        # Checkbox para el filtro por ETA
        self.check_fecha_eta = QCheckBox("Filtro por ETA")
        self.check_fecha_eta.setChecked(False)  # Inicialmente deshabilitado
        self.check_fecha_eta.stateChanged.connect(self.toggle_fechas_eta)  # Conectar evento de cambio de estado
        self.check_fecha_eta.stateChanged.connect(self.actualizar_datos)  # Conectar evento de cambio de estado
        layout_filtros_fechas.addWidget(self.check_fecha_eta)

        # Selector de fecha de inicio para ETA
        self.date_start1_eta = QDateEdit()
        self.date_start1_eta.setCalendarPopup(True)
        self.date_start1_eta.setDate(QDate.currentDate())
        self.date_start1_eta.setEnabled(False)  # Inicialmente deshabilitado
        layout_filtros_fechas.addWidget(self.date_start1_eta)

        # Checkbox para el filtro por rango de fechas
        self.check_fecha_rango = QCheckBox("Filtro por rango de fechas")
        self.check_fecha_rango.setChecked(False)  # Inicialmente deshabilitado
        self.check_fecha_rango.stateChanged.connect(self.toggle_fechas_rango)  # Conectar evento de cambio de estado
        self.check_fecha_rango.stateChanged.connect(self.actualizar_datos)  # Conectar evento de cambio de estado
        layout_filtros_fechas.addWidget(self.check_fecha_rango)

        # Selector de fecha de inicio para el rango
        self.date_start1_rango = QDateEdit()
        self.date_start1_rango.setCalendarPopup(True)
        self.date_start1_rango.setDate(QDate.currentDate())
        self.date_start1_rango.setEnabled(False)  # Inicialmente deshabilitado
        layout_filtros_fechas.addWidget(self.date_start1_rango)

        # Selector de fecha final para el rango
        self.date_end1_rango = QDateEdit()
        self.date_end1_rango.setCalendarPopup(True)
        self.date_end1_rango.setDate(QDate.currentDate())
        self.date_end1_rango.setEnabled(False)  # Inicialmente deshabilitado
        layout_filtros_fechas.addWidget(self.date_end1_rango)

        # Agregar el QHBoxLayout al layout principal
        layout.addLayout(layout_filtros_fechas)

        layout_restaurante_tipo_comida = QHBoxLayout()

        # Llenar el combo de restaurantes desde la base de datos
        self.combo_restaurantes = QComboBox()
        self.combo_restaurantes.addItem("Restaurante")  # Agregar un valor por defecto

        restaurantes = session.query(Restaurante.nombre).distinct().all()  # Consulta para obtener los nombres de los restaurantes
        for restaurante in restaurantes:
            self.combo_restaurantes.addItem(restaurante.nombre)

        layout_restaurante_tipo_comida.addWidget(self.combo_restaurantes)

        # Llenar el combo de tipo de comidas desde la base de datos
        self.combo_tipo_comidas = QComboBox()
        self.combo_tipo_comidas.addItem("Tipo comida")  # Agregar un valor por defecto

        tipo_comidas = session.query(TripulanteRestaurante.tipo_comida).distinct().all()  # Consulta para obtener los tipos de comida
        for tipo_comida in tipo_comidas:
            self.combo_tipo_comidas.addItem(tipo_comida.tipo_comida)

        layout_restaurante_tipo_comida.addWidget(self.combo_tipo_comidas)

        # Agregar el QHBoxLayout al layout principal
        layout.addLayout(layout_restaurante_tipo_comida)

        self.label = QLabel()
        layout.addWidget(self.label)

        # Tabla para mostrar datos
        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        # Botón para generar el Excel
        button_generar_excel = QPushButton("Generar Excel")
        button_generar_excel.setStyleSheet("""
            font-size: 18px;  /* Tamaño de la letra */
            padding: 0px;    /* Elimina el espacio interno */
            line-height: 18px; /* Asegura que el texto no se corte verticalmente */
            text-align: center; /* Centra el texto */
        """)
        button_generar_excel.setFixedHeight(45)
        button_generar_excel.setFixedWidth(245)
        button_generar_excel.clicked.connect(self.generar_excel_con_ciudad)
        layout.addWidget(button_generar_excel, alignment=Qt.AlignmentFlag.AlignRight)

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

        if self.check_fecha_eta.isChecked():
            # Configurar el rango de fecha para el filtro ETA
            fecha_inicio_eta_dt = datetime.combine(datetime.strptime(fecha_inicio_eta, "%d-%m-%Y"), time.min)  # 00:00:00
            fecha_fin_eta_dt = datetime.combine(datetime.strptime(fecha_inicio_eta, "%d-%m-%Y"), time.max)  # 23:59:59

            # Aplicar el filtro de rango de fecha a la consulta
            query = query.filter(
                EtaCiudad.eta >= fecha_inicio_eta_dt,
                EtaCiudad.eta <= fecha_fin_eta_dt
            )

        if self.check_fecha_rango.isChecked():
            # Configurar el rango de fecha para el filtro de reserva
            fecha_inicio_rango_dt = datetime.strptime(fecha_inicio_rango, "%d-%m-%Y")
            fecha_inicio_rango_dt = datetime.combine(fecha_inicio_rango_dt, time.min)  # 00:00:00
            fecha_fin_rango_dt = datetime.strptime(fecha_fin_rango, "%d-%m-%Y")
            fecha_fin_rango_dt = datetime.combine(fecha_fin_rango_dt, time.max)  # 23:59:59

            # Aplicar el filtro de rango de fecha a la consulta
            query = query.filter(
                TripulanteRestaurante.fecha_reserva >= fecha_inicio_rango_dt,
                TripulanteRestaurante.fecha_reserva <= fecha_fin_rango_dt
            )

        # Limpiar la tabla
        headers = ["First Name", "Last Name", "Preferencia", "Categoria", "Signature"]

        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(len(headers))  # Número correcto de columnas
        self.table_widget.setHorizontalHeaderLabels(headers)

        query = query.order_by(Tripulante.apellido)

        self.tripulante_ids = []

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

        if self.check_fecha_eta.isChecked():
            file_name_parts.append(fecha_inicio_eta)
        if self.check_fecha_rango.isChecked():
            file_name_parts.append(f"{fecha_inicio_rango}_{fecha_fin_rango}")

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

            # Escribir los datos del DataFrame
            data_fill = PatternFill(start_color='FFFF99', end_color='FFFF99', fill_type='solid')
            for row_num, row_data in enumerate(df.values, start=10):  # Cambiar a fila 8
                for col_num, cell_value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_num, column=col_num)
                    cell.value = cell_value
                    cell.fill = data_fill

            # Centrar el número correlativo
            # for row_num in range(9, len(df) + 9):  # Cambiar el rango según donde se escriban los datos
            #     ws.cell(row=row_num, column=1).alignment = Alignment(horizontal='center')

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
        self.main_window.stacked_widget.setCurrentIndex(self.main_window.opciones_programar_index)