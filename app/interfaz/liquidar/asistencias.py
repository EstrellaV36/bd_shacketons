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

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from fpdf import FPDF

class PDFReport(FPDF):
    def header(self):
        # Título del reporte
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, f"{self.vessel} {self.eta} {self.port_code}", ln=1, align='C')
        self.cell(0, 10, f"Meet and assistance crew in {self.city} airport ({self.crew_type}) signers", ln=1, align='C')
        self.ln(10)

    def add_table(self, dataframe):
        # Calcular ancho dinámico de las columnas
        page_width = self.w - 20  # Ancho de la página menos márgenes
        column_width = page_width / len(dataframe.columns)

        # Agregar encabezado de la tabla
        self.set_font('Arial', 'B', 10)
        for col_name in dataframe.columns:
            self.cell(column_width, 10, col_name, border=1, align='C')
        self.ln()

        # Agregar datos de la tabla
        self.set_font('Arial', '', 10)
        for _, row in dataframe.iterrows():
            for item in row:
                self.cell(column_width, 10, str(item), border=1, align='C')
            self.ln()

class DataWorker(QObject):
    finished = pyqtSignal()  # Señal que indica que el trabajo ha terminado
    update_table = pyqtSignal(pd.DataFrame)  # Señal para enviar el DataFrame con los resultados

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
        
        AIRPORT_CODE_TO_NAME = {
            "SCL": "SANTIAGO",
            "PUQ": "PUNTA ARENAS",
            "WPU": "PUERTO WILLIAMS",
        }
        CITY_TO_ASSISTANCE_FIELD = {
            "PUQ": "necesita_asistencia_puq",
            "SCL": "necesita_asistencia_scl",
            "WPU": "necesita_asistencia_wpu",
        }

        if self.ciudad and self.ciudad != "Ciudad":
            aeropuertos_filtrados = [AIRPORT_CODE_TO_NAME.get(self.ciudad.upper())]
            asistencia_field = CITY_TO_ASSISTANCE_FIELD.get(self.ciudad.upper())
        else:
            aeropuertos_filtrados = list(AIRPORT_CODE_TO_NAME.values())  # Todos los nombres de aeropuertos si no se selecciona uno
            asistencia_field = None

        if asistencia_field is None:
            print("Asistencia field no encontrado para la ciudad seleccionada. Omite asistencia.")
            asistencia_enabled = False
        else:
            asistencia_enabled = True

        query = session.query(
            Tripulante.tripulante_id.label("ID"),
            Buque.nombre.label("Vessel"),
            EtaCiudad.eta.label("ETA"),
            EtaCiudad.puerto.label("Puerto"),  # Incluir el puerto aquí
            Tripulante.nombre.label("First_Name"),
            Tripulante.apellido.label("Last_Name"),
            Vuelo.codigo.label("Domestic_flight"),
            Vuelo.fecha.label("Date"),
            Vuelo.hora_llegada.label("Arrival"),
        ).select_from(EtaCiudad)\
            .join(Viaje, Tripulante.tripulante_id == Viaje.tripulante_id)\
            .join(Buque, EtaCiudad.buque_id == Buque.buque_id)\
            .join(Tripulante, Tripulante.buque_id == Buque.buque_id)\
            .join(TripulanteVuelo, Tripulante.tripulante_id == TripulanteVuelo.tripulante_id)\
            .join(Vuelo, Vuelo.vuelo_id == TripulanteVuelo.vuelo_id)\
            .filter(
                Vuelo.aeropuerto_llegada.in_(aeropuertos_filtrados)
            )\
            .distinct()


        resultados_sin_filtros = query.all()
        #print(f"Resultados sin filtros: {resultados_sin_filtros}")

        #FALTA FILTRAR POR ON Y POR OFF
        # Filtros adicionales
        if self.owner and self.owner != "Owner":
            query = query.filter(func.trim(func.lower(Buque.empresa)) == self.owner.strip().lower())
        if self.vessel and self.vessel != "Vessel":
            query = query.filter(func.trim(func.lower(Buque.nombre)) == self.vessel.strip().lower())
        if self.fecha_eta:
            query = query.filter(func.date(EtaCiudad.eta) == self.fecha_eta)
        if self.tipo and self.tipo != "Tipo tripulante":
            query = query.filter(func.trim(Viaje.estado) == self.tipo)
    
        results = query.all()
        #print(f"Resultados principales: {results}")

        main_data = pd.DataFrame([{
            "ID": row.ID,
            "Vessel": row.Vessel,
            "ETA": row.ETA.date() if row.ETA else None,  # Extraer solo la fecha
            "First Name": row.First_Name,
            "Last Name": row.Last_Name,
            "Domestic flight": row.Domestic_flight,
            "Date": row.Date.date() if row.Date else None,  # Extraer solo la fecha
            "Arrival": row.Arrival.strftime("%H:%M") if row.Arrival else None,  # Extraer solo la hora
        } for row in results])


        if asistencia_enabled and not main_data.empty:
            tripulante_ids = main_data["ID"].tolist()
            asistencia_query = session.query(
                TripulanteAsistencia.tripulante_id.label("ID"),
                getattr(TripulanteAsistencia, asistencia_field).label("Assistance"),
            ).filter(
                TripulanteAsistencia.tripulante_id.in_(tripulante_ids)
            )

            asistencia_results = asistencia_query.all()
            asistencia_data = pd.DataFrame([{
                "ID": row.ID,
                "Assistance": "1" if row.Assistance else "0",
            } for row in asistencia_results])

            final_data = pd.merge(main_data, asistencia_data, on="ID", how="left")
        else:
            final_data = main_data
            final_data["Assistance"] = "0"

        #print(f"Datos finales: {final_data}")
        self.update_table.emit(final_data)
        self.finished.emit()

class ComboboxWorker(QObject):
    finished = pyqtSignal()  # Señal que indica que el trabajo ha terminado
    update_combobox = pyqtSignal(dict)  # Señal para actualizar los combobox con datos

    def run(self):
        """Función ejecutada en segundo plano para rellenar los combobox."""
        session = get_db_session()

        # Consultas para rellenar los comboboxes
        data = {
            "ciudades": [ciudad.ciudad for ciudad in session.query(Hotel.ciudad).distinct().all()],
            "tipos_tripulante": ["ON", "OFF"],
            "owners": [owner.empresa for owner in session.query(Buque.empresa).distinct().all()],
            "proveedores": set(),
            "all_vessels": [],  # Lista de todos los buques
            "vessels": {},  # Diccionario para almacenar buques por owner
        }

        # Proveedores
        proveedores = session.query(TripulanteAsistencia.proveedor_puq, 
                                    TripulanteAsistencia.proveedor_scl, 
                                    TripulanteAsistencia.proveedor_wpu).distinct().all()
        for proveedor in proveedores:
            for proveedor_ciudad in proveedor:
                if proveedor_ciudad:
                    data["proveedores"].add(proveedor_ciudad)
        data["proveedores"] = list(data["proveedores"])

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

class AsistenciasLiquidarScreen(QWidget):
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
        self.label = QLabel("ASISTENCIAS LIQUIDAR")
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

        self.combo_proveedor = QComboBox()
        self.combo_proveedor.currentTextChanged.connect(self.actualizar_datos)
        layout.addWidget(self.combo_proveedor)

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

        self.combo_proveedor.blockSignals(True)
        self.combo_proveedor.clear()
        self.combo_proveedor.addItem("Proveedor")
        self.combo_proveedor.addItems(data["proveedores"])
        self.combo_proveedor.blockSignals(False)

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

    def actualizar_datos(self):
        ciudad_seleccionada = self.combo_ciudades.currentText()  # Obtiene la ciudad seleccionada
        proveedor_seleccionado = self.combo_ciudades.currentText()
        tipo_tripulante = self.tipo_tripulante.currentText()
        owner_seleccionado = self.combo_owner.currentText()
        vessel_selecciondo = self.combo_vessel.currentText()
        if ciudad_seleccionada.lower() != "ciudad":
            self.label.setText(f"ASISTENCIAS LIQUIDAR |EN {ciudad_seleccionada.upper()}")  # Actualiza el label
        else:
            self.label.setText(f"ASISTENCIAS LIQUIDAR")  # Actualiza el label

        # Cargar datos en la tabla
        self.cargar_datos(ciudad_seleccionada, proveedor_seleccionado, tipo_tripulante, owner_seleccionado, vessel_selecciondo)

    def cargar_datos(self, ciudad_seleccionada, proveedor_seleccionado, tipo, owner, vessel):
        if hasattr(self, "is_running") and self.is_running:
            print("El hilo aún está ejecutándose. Espera a que termine antes de iniciar otro.")
            return

        self.is_running = True
        fecha_eta = self.date_start.date().toPyDate()
        print(f"Configurando DataWorker: ciudad={ciudad_seleccionada}, proveedor={proveedor_seleccionado}, owner={owner}, vessel={vessel}, fecha_eta={fecha_eta}")

        self.data_thread = QThread()
        self.data_worker = DataWorker(ciudad_seleccionada, proveedor_seleccionado, owner, vessel, fecha_eta, tipo)
        self.data_worker.moveToThread(self.data_thread)

        self.data_thread.started.connect(self.data_worker.run)
        self.data_worker.update_table.connect(self.update_table_data)
        self.data_worker.finished.connect(self.data_thread.quit)
        self.data_worker.finished.connect(self.data_worker.deleteLater)
        self.data_thread.finished.connect(self.data_thread.deleteLater)
        self.data_thread.finished.connect(lambda: setattr(self, "is_running", False))  # Restablece la bandera

        print("Iniciando el hilo para DataWorker...")
        self.data_thread.start()

    def update_table_data(self, df):
        print("Updating table data...")
        print(df)

        self.table_widget.clear()

        if df.empty:
            print("No data to display.")
            return

        # Configurar encabezados
        self.table_widget.setRowCount(len(df))
        self.table_widget.setColumnCount(len(df.columns))
        self.table_widget.setHorizontalHeaderLabels(df.columns)

        # Poblar la tabla
        for row_idx, row in df.iterrows():
            for col_idx, value in enumerate(row):
                self.table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def generar_reporte_liquidar(self):
        ciudad_seleccionada = self.combo_ciudades.currentText()
        tipo_crew = self.tipo_tripulante.currentText()
        owner = self.combo_owner.currentText()
        vessel = self.combo_vessel.currentText()
        fecha_eta = self.date_start.date().toString("dd-MM-yyyy")

        # Obtén el DataFrame actual mostrado en la tabla
        df = self.get_current_dataframe()

        if df.empty:
            print("No hay datos disponibles para generar el reporte.")
            return

        # Obtener el puerto desde la columna "Puerto" del DataFrame
        port_code = df["Puerto"].iloc[0] if "Puerto" in df.columns else "N/A"

        # Generar el PDF
        self.generar_reporte(
            df, vessel, fecha_eta, port_code, ciudad_seleccionada, tipo_crew, output_file="liquidar_report.pdf"
        )

    def generar_reporte(self, df, vessel, eta, port_code, city, crew_type, output_file="report.pdf"):
        pdf = PDFReport()
        pdf.vessel = vessel
        pdf.eta = eta
        pdf.port_code = port_code
        pdf.city = city
        pdf.crew_type = crew_type

        pdf.add_page()
        pdf.add_table(df)

        pdf.output(output_file)
        print(f"Reporte generado: {output_file}")

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

    def toggle_fechas(self, state):
        enabled = state == Qt.CheckState.Checked  # Verificar si el checkbox está marcado
        self.date_start.setEnabled(enabled)
        # Deshabilitar el cuadro emergente si está desmarcado
        self.date_start.setCalendarPopup(enabled)

    def closeEvent(self, event):
        """Sobrescribe el evento de cierre para limpiar hilos."""
        if hasattr(self, "data_thread") and self.data_thread.isRunning():
            self.data_thread.quit()
            self.data_thread.wait()  # Espera a que el hilo termine
        if hasattr(self, "thread") and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        event.accept()

    def volver_a_opciones_liquidar(self):
        self.main_window.stacked_widget.setCurrentIndex(self.main_window.opciones_liquidar_index)