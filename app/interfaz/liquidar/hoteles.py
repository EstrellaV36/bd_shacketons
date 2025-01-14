import pandas as pd
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QFileDialog, QCheckBox, QHBoxLayout, QDateEdit
from PyQt6.QtCore import Qt, QDate
from app.database import get_db_session
from app.models import Buque, EtaCiudad, Tripulante, Vuelo, TripulanteVuelo, Transporte, TripulanteTransporte, TripulanteAsistencia, Restaurante, TripulanteRestaurante, Hotel, TripulanteHotel, Viaje
from app.controller.controllers import CITY_AIRPORT_CODES, CITY_TO_AIRPORT_CODES
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Alignment, Font, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime, time, timedelta
from sqlalchemy import func, exists, case, and_
from collections import defaultdict
from datetime import datetime
from openpyxl.styles import Alignment, Font
from sqlalchemy.orm import aliased

from PyQt6.QtCore import QObject, QThread, pyqtSignal

class DataWorker(QObject):
    finished = pyqtSignal()  # Señal que indica que el trabajo ha terminado
    update_table = pyqtSignal(pd.DataFrame)  # Señal para enviar el DataFrame con los resultados
    additional_data = pyqtSignal(dict)  # Nueva señal para enviar el puerto y aeropuertos

    def __init__(self, ciudad, proveedor, owner, vessel, fecha_eta, tipo):
        super().__init__()
        self.ciudad = ciudad
        self.proveedor = proveedor
        self.owner = owner
        self.vessel = vessel
        self.fecha_eta = fecha_eta
        self.tipo = tipo

    def run(self):
        print(f"DataWorker started with: ciudad={self.ciudad}, owner={self.owner}, vessel={self.vessel}, fecha_eta={self.fecha_eta}")

        session = get_db_session()

        # Paso 1: Obtener los tripulantes con filtros aplicados
        tripulantes_query = session.query(
            Tripulante.tripulante_id.label("ID"),
            Buque.nombre.label("Vessel"),
            EtaCiudad.eta.label("ETA"),
            EtaCiudad.puerto.label("Puerto"), 
            Tripulante.nombre.label("First_Name"),
            Tripulante.apellido.label("Last_Name"),
            Viaje.estado.label("Estado"),
        ).select_from(EtaCiudad)\
            .join(Viaje, Tripulante.tripulante_id == Viaje.tripulante_id)\
            .join(Buque, EtaCiudad.buque_id == Buque.buque_id)\
            .join(Tripulante, Tripulante.buque_id == Buque.buque_id)\
            .distinct()

        # Aplicar filtros adicionales
        if self.owner and self.owner != "Owner":
            tripulantes_query = tripulantes_query.filter(func.trim(func.lower(Buque.empresa)) == self.owner.strip().lower())
        if self.vessel and self.vessel != "Vessel":
            tripulantes_query = tripulantes_query.filter(func.trim(func.lower(Buque.nombre)) == self.vessel.strip().lower())
        if self.fecha_eta:
            tripulantes_query = tripulantes_query.filter(func.date(EtaCiudad.eta) == self.fecha_eta)
        if self.tipo and self.tipo != "Tipo tripulante":
            tripulantes_query = tripulantes_query.filter(func.trim(Viaje.estado) == self.tipo)

        tripulantes = tripulantes_query.all()

        # Extraer los IDs de los tripulantes para usarlos en la consulta de hoteles
        tripulante_ids = [t.ID for t in tripulantes]

        #Obtener los hoteles con filtros aplicados
        if tripulante_ids:
            hoteles_query = session.query(
                TripulanteHotel.tripulante_id.label("Tripulante_ID"),
                Hotel.nombre.label("Hotel"),
                Hotel.ciudad.label("Ciudad_Hotel"),
                TripulanteHotel.tipo_habitacion.label("Room"),
                TripulanteHotel.fecha_entrada.label("Check_In"),
                TripulanteHotel.fecha_salida.label("Check_Out"),
                TripulanteHotel.numero_noches.label("Nights"),
            ).join(Hotel, TripulanteHotel.hotel_id == Hotel.hotel_id)\
                .filter(TripulanteHotel.tripulante_id.in_(tripulante_ids))

            # Aplicar filtro adicional para la ciudad del hotel
            if self.ciudad and self.ciudad != "Ciudad":
                hoteles_query = hoteles_query.filter(func.trim(Hotel.ciudad) == self.ciudad.strip())

            hoteles = hoteles_query.all()
        else:
            hoteles = []

        #Relacionar tripulantes con hoteles por separado
        tripulantes_hoteles = {t.ID: None for t in tripulantes}

        for hotel in hoteles:
            tripulantes_hoteles[hotel.Tripulante_ID] = {
                "Hotel": hotel.Hotel,
                "Ciudad_Hotel": hotel.Ciudad_Hotel,
                "Room": hotel.Room,
                "Check_In": hotel.Check_In,
                "Check_Out": hotel.Check_Out,
                "Nights": hotel.Nights,
            }

        #Unir los datos con las columnas de hotel por separado
        resultados = []
        for tripulante in tripulantes:
            hotel_data = tripulantes_hoteles.get(tripulante.ID, None)
            if hotel_data:
                resultados.append({
                    "Vessel": tripulante.Vessel,
                    "Name": tripulante.First_Name,
                    "Last Name": tripulante.Last_Name,
                    "Hotel": hotel_data["Hotel"],
                    "Room": hotel_data["Room"],
                    "Check in": hotel_data["Check_In"].date() if hotel_data["Check_In"] else None,  # Mostrar solo la fecha
                    "Check out": hotel_data["Check_Out"].date() if hotel_data["Check_Out"] else None,  # Mostrar solo la fecha
                    "Nights": hotel_data["Nights"],
                    "Cost": "",
                    "Invoice": "",
                })
            else:
                resultados.append({
                    "Vessel": tripulante.Vessel,
                    "Name": tripulante.First_Name,
                    "Last Name": tripulante.Last_Name,
                    "Hotel": "NO",
                    "Room": "",
                    "Check in": "",
                    "Check out": "",
                    "Nights": "",
                    "Cost": "",
                    "Invoice": "",
                })

        # Extraer datos adicionales para excel
        puerto = tripulantes[0].Puerto if tripulantes else "N/A"
        # Emitir los datos adicionales a través de una señal
        self.additional_data.emit({
            "Puerto": puerto,
        })

        # Opcional: Crear un DataFrame
        df = pd.DataFrame(resultados)

        # Emitir los datos procesados
        self.update_table.emit(df)
        self.finished.emit()

class HotelesLiquidarScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # Añadir esta pantalla al stacked_widget del main_window
        self.main_window.visualizacion_datos_index = self.main_window.stacked_widget.addWidget(self)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Botón "Volver" para regresar a la pantalla anterior
        button_volver = QPushButton("Volver")
        button_volver.setFixedWidth(100)
        button_volver.clicked.connect(self.volver_a_opciones_liquidar)
        layout.addWidget(button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        # Label principal
        self.label = QLabel("HOTELES LIQUIDAR")
        self.label.setStyleSheet("""
            font-size: 40px;
            font-weight: bold;
            color: #00272d;
            text-align: center;
            margin-bottom: 20px;
        """)
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Comboboxes
        self.combo_ciudades = QComboBox()
        self.combo_ciudades.currentTextChanged.connect(self.actualizar_datos)
        layout.addWidget(self.combo_ciudades)

        self.tipo_tripulante = QComboBox()
        self.tipo_tripulante.currentTextChanged.connect(self.actualizar_datos)
        layout.addWidget(self.tipo_tripulante)

        # self.combo_proveedor = QComboBox()
        # self.combo_proveedor.currentTextChanged.connect(self.actualizar_datos)
        # layout.addWidget(self.combo_proveedor)

        self.combo_owner = QComboBox()
        self.combo_owner.currentTextChanged.connect(self.actualizar_datos)
        layout.addWidget(self.combo_owner)

        self.combo_vessel = QComboBox()
        self.combo_vessel.currentTextChanged.connect(self.actualizar_datos)
        layout.addWidget(self.combo_vessel)

        # Iniciar el Worker para rellenar los combobox
        self.start_combobox_worker()

        # Layout horizontal para las fechas
        layout_filtro = QHBoxLayout()

        # Selector de fecha de ETA
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDate(QDate.currentDate())
        self.date_start.dateChanged.connect(self.actualizar_datos)  # Conectar señal de cambio de fecha
        layout_filtro.addWidget(QLabel("Fecha ETA:"))
        layout_filtro.addWidget(self.date_start)

        layout.addLayout(layout_filtro)

        # Tabla para mostrar datos
        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        # Botón para generar el Excel
        button_generar_reporte = QPushButton("Generar reporte")
        button_generar_reporte.clicked.connect(self.generar_reporte_liquidar)  # Conectar al método de generación de Excel
        layout.addWidget(button_generar_reporte)
        self.setLayout(layout)

    def actualizar_datos(self):
        ciudad_seleccionada = self.combo_ciudades.currentText()  # Obtiene la ciudad seleccionada
        proveedor_seleccionado = self.combo_ciudades.currentText()
        tipo_tripulante = self.tipo_tripulante.currentText()
        owner_seleccionado = self.combo_owner.currentText()
        vessel_selecciondo = self.combo_vessel.currentText()
        if ciudad_seleccionada.lower() != "ciudad":
            self.label.setText(f"HOTELES LIQUIDAR EN {ciudad_seleccionada.upper()}")  # Actualiza el label
        else:
            self.label.setText(f"HOTELES LIQUIDAR")  # Actualiza el label

        # Cargar datos en la tabla
        self.cargar_datos(ciudad_seleccionada, proveedor_seleccionado, tipo_tripulante, owner_seleccionado, vessel_selecciondo)

    def start_combobox_worker(self):
        """Inicia el Worker para rellenar los comboboxes en segundo plano."""
        self.thread = QThread()
        self.worker = ComboboxWorker()
        self.worker.moveToThread(self.thread)

        # Conectar señales y slots
        self.thread.started.connect(self.worker.run)
        self.worker.update_combobox.connect(self.update_comboboxes)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Iniciar el hilo
        self.thread.start()

    def update_comboboxes(self, data):
        """Actualiza los comboboxes con los datos recibidos del Worker."""
        self.combo_ciudades.blockSignals(True)
        self.combo_ciudades.clear()
        self.combo_ciudades.addItem("Ciudad")
        self.combo_ciudades.addItems(data["ciudades"])
        self.combo_ciudades.blockSignals(False)

        self.tipo_tripulante.blockSignals(True)
        self.tipo_tripulante.clear()
        self.tipo_tripulante.addItem("Tipo tripulante")
        self.tipo_tripulante.addItems(data["tipos_tripulante"])
        self.tipo_tripulante.blockSignals(False)

        # self.combo_proveedor.blockSignals(True)
        # self.combo_proveedor.clear()
        # self.combo_proveedor.addItem("Proveedor")
        # self.combo_proveedor.addItems(data["proveedores"])
        # self.combo_proveedor.blockSignals(False)

        self.combo_owner.blockSignals(True)
        self.combo_owner.clear()
        self.combo_owner.addItem("Owner")
        self.combo_owner.addItems(data["owners"])
        self.combo_owner.blockSignals(False)

        self.update_vessels(data)
        self.actualizar_datos()

    def update_vessels(self, data):
        """Actualiza el combobox de buques (vessels) basado en el proveedor y owner seleccionados."""
        owner_selected = self.combo_owner.currentText()

        self.combo_vessel.clear()
        self.combo_vessel.addItem("Vessel")

        if owner_selected == "Owner":
            # Mostrar todos los buques si no se selecciona un proveedor específico
            self.combo_vessel.addItems(data["all_vessels"])
        elif owner_selected in data["vessels"]:
            # Filtrar los buques por el owner seleccionado
            self.combo_vessel.addItems(data["vessels"][owner_selected])
    
    def save_additional_data(self, data):
        """Guarda los datos adicionales (puerto) recibidos del DataWorker."""
        self.puerto = data["Puerto"]

    def update_table_data(self, df):
        print("Updating table data...")
        print(df)

        self.table_widget.clear()

        if df.empty:
            print("No data to display.")
            return

        # Eliminar la columna 'ID' del DataFrame si existe
        if 'ID' in df.columns:
            df = df.drop(columns=['ID'])

        # Agregar una nueva columna '#' para numerar las filas
        df.insert(0, '#', range(1, len(df) + 1))

        # Configurar encabezados
        self.table_widget.setRowCount(len(df))
        self.table_widget.setColumnCount(len(df.columns))
        self.table_widget.setHorizontalHeaderLabels(df.columns)

        # Poblar la tabla
        for row_idx, row in df.iterrows():
            for col_idx, value in enumerate(row):
                self.table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def cargar_datos(self, ciudad_seleccionada, proveedor_seleccionado, tipo, owner, vessel):
        if hasattr(self, "is_running") and self.is_running:
            print("El hilo aún está ejecutándose. Espera a que termine antes de iniciar otro.")
            return

        self.is_running = True
        fecha_eta = self.date_start.date().toPyDate()
        print(f"Configurando DataWorker: ciudad={ciudad_seleccionada}, proveedor={proveedor_seleccionado}, owner={owner}, vessel={vessel}, fecha_eta={fecha_eta}")

        # Crear el hilo y el trabajador
        self.data_thread = QThread()
        self.data_worker = DataWorker(ciudad_seleccionada, proveedor_seleccionado, owner, vessel, fecha_eta, tipo)
        self.data_worker.moveToThread(self.data_thread)

        # Conectar señales
        self.data_thread.started.connect(self.data_worker.run)
        self.data_worker.update_table.connect(self.update_table_data)
        self.data_worker.additional_data.connect(self.save_additional_data)  # Conectar la señal para datos adicionales
        self.data_worker.finished.connect(self.data_thread.quit)
        self.data_worker.finished.connect(self.data_worker.deleteLater)
        self.data_thread.finished.connect(self.data_thread.deleteLater)
        self.data_thread.finished.connect(lambda: setattr(self, "is_running", False))  # Restablecer la bandera

        print("Iniciando el hilo para DataWorker...")
        self.data_thread.start()

    def generar_reporte_liquidar(self):
        if not self.puerto:
            print("No se han recibido los datos adicionales necesarios.")
            return

        AIRPORT_CODE_TO_NAME = {
            "SCL": "SANTIAGO",
            "PUQ": "PUNTA ARENAS",
            "WPU": "PUERTO WILLIAMS",
        }

        ciudad = self.combo_ciudades.currentText()
        ciudad_seleccionada = AIRPORT_CODE_TO_NAME.get(ciudad)
        tipo_crew = self.tipo_tripulante.currentText()
        vessel = self.combo_vessel.currentText()
        fecha_eta = self.date_start.date().toString("dd-MM-yyyy")

        # Obtén el DataFrame actual mostrado en la tabla
        df = self.get_current_dataframe()

        if df.empty:
            print("No hay datos disponibles para generar el reporte.")
            return

        # Mostrar un cuadro de diálogo para seleccionar la ubicación de guardado
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Reporte",
            f"liquidar_hoteles_{vessel}_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
            "Archivos de Excel (*.xlsx)"
        )

        if not file_path:
            print("Guardado cancelado por el usuario.")
            return

        # Generar el archivo Excel
        self.generar_reporte_excel(df, file_path, vessel, fecha_eta, self.puerto, ciudad_seleccionada, tipo_crew)
        print(f"Reporte generado: {file_path}")

    def generar_reporte_excel(self, df, output_file, vessel, fecha_eta, puerto, ciudad, tipo_crew):
        """Genera un reporte en formato Excel a partir de un DataFrame."""
        try:
            # Crear un libro de Excel
            with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Reporte", startrow=3)

                # Acceder al libro y la hoja
                workbook = writer.book
                sheet = writer.sheets["Reporte"]

                # Agregar título centrado en la primera fila
                titulo = f"{vessel} {fecha_eta} {puerto}"
                subtitulo = f"ACCOMMODATION HOTEL IN {ciudad.upper()} - {tipo_crew} SIGNERS"

                sheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(df.columns))
                sheet.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(df.columns))

                sheet.cell(row=1, column=1).value = titulo
                sheet.cell(row=2, column=1).value = subtitulo

                # Estilo de los títulos
                titulo_font = Font(bold=True, size=14)
                subtitulo_font = Font(bold=True, size=12)

                sheet.cell(row=1, column=1).font = titulo_font
                sheet.cell(row=2, column=1).font = subtitulo_font

                sheet.cell(row=1, column=1).alignment = Alignment(horizontal="center")
                sheet.cell(row=2, column=1).alignment = Alignment(horizontal="center")

                # Estilo para encabezados de la tabla
                header_font = Font(bold=True)
                border_style = Border(
                    left=Side(style="thin"),
                    right=Side(style="thin"),
                    top=Side(style="thin"),
                    bottom=Side(style="thin")
                )

                for col_idx, col in enumerate(df.columns, start=1):
                    cell = sheet.cell(row=4, column=col_idx)
                    cell.value = col
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    cell.border = border_style

                # Agregar bordes a todas las celdas de la tabla
                for row_idx in range(5, 5 + len(df)):  # Las filas de datos comienzan en la fila 5
                    for col_idx in range(1, len(df.columns) + 1):
                        cell = sheet.cell(row=row_idx, column=col_idx)
                        cell.border = border_style

                # Ajustar ancho de columnas automáticamente
                for col_idx, col in enumerate(df.columns, start=1):
                    max_length = max(
                        [len(str(value)) for value in df[col]] + [len(str(col))]
                    )
                    adjusted_width = max_length + 2
                    sheet.column_dimensions[get_column_letter(col_idx)].width = adjusted_width

            print(f"Archivo Excel guardado correctamente en {output_file}")
        except Exception as e:
            print(f"Error al generar el archivo Excel: {e}")

    def get_current_dataframe(self):
        """Obtiene los datos actuales del QTableWidget y los convierte en un DataFrame."""
        row_count = self.table_widget.rowCount()
        col_count = self.table_widget.columnCount()

        # Obtener los nombres de las columnas
        headers = [self.table_widget.horizontalHeaderItem(col).text() for col in range(col_count)]

        # Crear una lista de filas
        data = []
        for row in range(row_count):
            row_data = []
            for col in range(col_count):
                item = self.table_widget.item(row, col)
                row_data.append(item.text() if item is not None else "")
            data.append(row_data)

        # Convertir a DataFrame
        df = pd.DataFrame(data, columns=headers)
        return df
    
    def volver_a_opciones_liquidar(self):
        self.main_window.stacked_widget.setCurrentIndex(self.main_window.opciones_liquidar_index)

class ComboboxWorker(QObject):
    finished = pyqtSignal()  # Señal que indica que el trabajo ha terminado
    update_combobox = pyqtSignal(dict)  # Señal para actualizar los combobox con datos

    def run(self):
        print(f"Llenando combobox")
        """Función ejecutada en segundo plano para rellenar los combobox."""
        session = get_db_session()

        # Consultas para rellenar los comboboxes
        data = {
            "ciudades": [ciudad.ciudad for ciudad in session.query(Hotel.ciudad).distinct().all()],
            "tipos_tripulante": ["ON", "OFF"],
            "owners": [owner.empresa for owner in session.query(Buque.empresa).distinct().all()],
            #"proveedores": set(),
            "all_vessels": [],  # Lista de todos los buques
            "vessels": {},  # Diccionario para almacenar buques por owner
        }

        # Proveedores
        # proveedores = session.query(TripulanteAsistencia.proveedor_puq, 
        #                             TripulanteAsistencia.proveedor_scl, 
        #                             TripulanteAsistencia.proveedor_wpu).distinct().all()
        # for proveedor in proveedores:
        #     for proveedor_ciudad in proveedor:
        #         if proveedor_ciudad:
        #             data["proveedores"].add(proveedor_ciudad)
        # data["proveedores"] = list(data["proveedores"])

        # Todos los buques
        all_vessels = session.query(Buque.nombre).distinct().all()
        data["all_vessels"] = [vessel.nombre for vessel in all_vessels]

        # Buques (Vessels) por empresa (Owner)
        owners = session.query(Buque.empresa).distinct().all()
        for owner in owners:
            owner_name = owner.empresa
            vessels = session.query(Buque.nombre).filter(Buque.empresa == owner_name).distinct().all()
            data["vessels"][owner_name] = [vessel.nombre for vessel in vessels]

        # Emitir los datos para actualizar la interfaz
        self.update_combobox.emit(data)
        self.finished.emit()