from datetime import datetime
import pandas as pd
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QComboBox, QLabel, QTableView,
    QPushButton, QSizePolicy, QTabWidget, QHBoxLayout
)
from PyQt6.QtCore import Qt
from sqlalchemy.sql import func
from sqlalchemy import cast, Integer
from app.interfaz.pandas_model import PandasModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import case
from app.database import get_db_session
from app.models import Buque, EtaCiudad, Tripulante, Viaje, Vuelo, TripulanteVuelo, Restaurante, TripulanteRestaurante, Transporte, TripulanteTransporte, Hotel, TripulanteHotel, Buque, TripulanteAsistencia
from PyQt6.QtCore import QRunnable, pyqtSignal, QObject
from PyQt6.QtCore import QAbstractTableModel, QThreadPool

CITY_AIRPORT_CODES = {
    'PUQ': "PUNTA ARENAS",
    'SCL': "SANTIAGO",
    'PMC': "PUERTO MONTT",
    'VAP': "VALPARAISO",
    'ZAL': "VALDIVIA",
    'WPU': "PUERTO WILLIAMS",
    'CDG': 'PARIS',  # París, Francia
    'NY': 'NUEVA YORK',  # Nueva York, EE. UU.
    'SPU': 'SPLIT',  # Split, Croacia
    'ZAG': 'ZAGREB',  # Zagreb, Croacia
    'AMS': 'AMSTERDAM',  # Ámsterdam, Países Bajos
    'EZE': 'BUENOS AIRES',  # Buenos Aires, Argentina
    'LUN': "LUSAKA",  # Lusaka, Zambia
    'DOH': "DOHA",  # Doha, Catar
    'PUJ': "PUNTA CANA",  # Punta Cana, República Dominicana
    'LIM': "LIMA",  # Lima, Perú
    'ANF': "ANTOFAGASTA",  # Antofagasta, Chile
    'IQQ': "IQUIQUE",  # Iquique, Chile
    'CCP': "CONCEPCIÓN",  # Concepción, Chile
    'LSC': "LA SERENA",  # La Serena, Chile
    'ARI': "ARICA",  # Arica, Chile
    'IPC': "RAPA NUI",  # Rapa Nui, Chile
    'LAX': "LOS ÁNGELES",  # Los Ángeles, EE. UU.
    'JFK': "NUEVA YORK",  # Nueva York, EE. UU.
    'MAD': "MADRID",  # Madrid, España
    'LHR': "LONDRES",  # Londres, Reino Unido
    'DXB': "DUBÁI",  # Dubái, Emiratos Árabes Unidos
    'MQP': "MPUMALANGA",  # Mpumalanga, Sudáfrica
    'JNB': "JOHANNESBURGO",  # Johannesburgo, Sudáfrica
    'FRA': 'FRANKFURT',  # Frankfurt, Alemania
    'LCA': "LÁRNACA",  # Lárnaca, Chipre
    'ZRH': "ZÚRICH",  # Zúrich, Suiza
    'GOX': "GOLFE DE GARABOGAZ",  # Golfe de Garabogaz, Turkmenistán
    'TRV': "THIRUVANANTHAPURAM",  # Thiruvananthapuram, India
    'PVG': "SHANGHAI",  # Shanghái, China
    'CGK': "YAKARTA",  # Yakarta, Indonesia
    'BDS': "BRINDISI",  # Brindisi, Italia
    'GRU': "SÃO PAULO",  # São Paulo, Brasil
    'NBO': "NAIROBI",  # Nairobi, Kenia
    'ICN': "SEÚL",  # Seúl, Corea del Sur
    'HRE': "HARARE",  # Harare, Zimbabue
    'OTP': "BUCARESTANT",  # Bucarest, Rumanía
    'AKL': "AUCKLAND",  # Auckland, Nueva Zelanda
    'FCO': "ROMA",  # Roma, Italia
    'PTY': "PANAMÁ",  # Ciudad de Panamá, Panamá
    'MNL': "MANILA",  # Manila, Filipinas
    'IST': "ESTAMBUL",  # Estambul, Turquía
    'LED': "SAN PETERSBURGO",  # San Petersburgo, Rusia
    'IMF': "IMPHAL",  # Imphal, India
    'TDG': "TANDAG",  # Tandag, Filipinas
    'SUB': "SURABAYA",  # Surabaya, Indonesia
    'MGA': "MANAGUA",  # Managua, Nicaragua
    'DEL': "DELHI",  # Delhi, India
    'GEO': "GEORGETOWN",  # Georgetown, Guyana
    'DPS': "DENPASAR",  # Denpasar, Indonesia
    'MIA': "MIAMI",  # Miami, EE. UU.
    'SAL': "SAN SALVADOR",  # San Salvador, El Salvador
    'MRU': "MAURICIO",  # Mauricio, Isla de Mauricio
    'JKT': "YAKARTA",  # Yakarta, Indonesia
    'SAP': "SAN PEDRO SULA",  # San Pedro Sula, Honduras
    'SOC': "SOLO CITY",  # Solo City, Indonesia
    'MBJ': "MONTEGO BAY",  # Montego Bay, Jamaica
    'BOM': "BOMBAY",  # Bombay, India
    'GUA': "CIUDAD DE GUATEMALA",  # Ciudad de Guatemala, Guatemala
    'CCU': "CALCUTA",  # Calcuta, India
    'COK': "COCHIN",  # Cochin, India
    'CMB': "COLOMBO",  # Colombo, Sri Lanka
    'LHE': "LAHORE",  # Lahore, Pakistán
    'HKG': "HONG KONG",  # Hong Kong, China
    'KHI': "KARACHI",  # Karachi, Pakistán
    'ZHA': "ZHANGJIAJIE",  # Zhangjiajie, China
    'SFO': "SAN FRANCISCO",  # San Francisco, EE. UU.
    'TBS': "TBILISI",  # Tbilisi, Georgia
    'GVA': "GINEBRA",  # Ginebra, Suiza
    'IAH': "HOUSTON",  # Houston, EE. UU.
    'IKF': "IKARIA",  # Ikaria, Grecia
    'LYR': "LONGYEARBYEN",  # Longyearbyen, Noruega
    'OSL': "OSLO",  # Oslo, Noruega
    'STO': "ESTOCOLMO",  # Estocolmo, Suecia
    'VIE': "VIENA",  # Viena, Austria
    'SHA': "SHANGHAI",  # Shanghái, China
    'KIX': "OSAKA",  # Osaka, Japón
    'CAN': "GUANGZHOU",  # Cantón, China
    'KTM': "KATHMANDU",  # Katmandú, Nepal
    'BKK': "BANGKOK",  # Bangkok, Tailandia
    'MAN': "MANCHESTER",  # Manchester, Reino Unido
    'SGN': "CIUDAD HO CHI MINH",  # Ciudad Ho Chi Minh, Vietnam
    'TPE': "TAIPEI",  # Taipéi, Taiwán
    'YVR': "VANCOUVER",  # Vancouver, Canadá
    'VCE': "VENECIA",  # Venecia, Italia
    'BEY': "BEIRUT",  # Beirut, Líbano
    'GMP': "SEOUL",  # Seúl, Corea del Sur
    'PEK': "PEKÍN",  # Pekín, China
    'CAG': "CAGLIARI",  # Cagliari, Italia
    'BCN': "BARCELONA",  # Barcelona, España
    'KIS': "KISUMU",  # Kisumu, Kenia
    'ORD': "CHICAGO O'HARE",  # Chicago O'Hare, EE. UU.
    'MEX': "CIUDAD DE MÉXICO",  # Ciudad de México, México
    'YUL': "MONTREAL",  # Montreal, Canadá
    'SEA': "SEATTLE",  # Seattle, EE. UU.
    'MRS': "MARSILLA",  # Marsella, Francia
    'NCE': "NIZA",  # Niza, Francia
    'MEL': "MELBOURNE",  # Melbourne, Australia
    'CPT': "CIUDAD DEL CABO",  # Ciudad del Cabo, Sudáfrica
    'FMO': "MÜNSTER/OSNABRÜCK",  # Münster/Osnabrück, Alemania
    'MUC': "MÚNICH",  # Múnich, Alemania
    'FLN': "FLORIANÓPOLIS",  # Florianópolis, Brasil
    'GOA': "GOA",  # Goa, India
    'WLG': "WELLINGTON",  # Wellington, Nueva Zelanda
    'CPH': "COPENHAGUE",  # Copenhague, Dinamarca
    'VLC': "VALENCIA",  # Valencia, España
    'NRT': "NARITA",  # Narita, Tokio, Japón
    'IKF': "IKARIA",  # Ikaria, Grecia
    'JFK': "NUEVA YORK",  # Nueva York, EE. UU.
    'ADD': "ADDIS ABEBA",  # Addis Abeba, Etiopía
    'XIY': "XIAN",  # Xi'an, China
    'SYD': "SÍDNEY",  # Sídney, Australia
    'BJL': "BANJUL",  # Banjul, Gambia
    'BRU': "BRUSELAS",  # Bruselas, Bélgica
    'DFW': "DALLAS",  # Dallas, EE. UU.
    'PMO': "PALERMO",  # Palermo, Italia
    'VFA': "VICTORIA FALLS",  # Victoria Falls, Zimbabue
    'BRE': "BREMEN",  # Bremen, Alemania
}

CITY_TO_AIRPORT_CODES = {city: code for code, city in CITY_AIRPORT_CODES.items()}

class QueryTask(QRunnable):
    class Signals(QObject):
        query_finished = pyqtSignal(object, str)  # Emitirá los datos y un identificador de la tarea
        error_occurred = pyqtSignal(str, str)  # Emitirá el error y un identificador

    def __init__(self, query_func, task_id, *args, **kwargs):
        super().__init__()
        self.signals = self.Signals()
        self.query_func = query_func
        self.task_id = task_id
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            # Ejecutar la función de consulta
            result = self.query_func(*self.args, **self.kwargs)
            self.signals.query_finished.emit(result, self.task_id)
        except Exception as e:
            self.signals.error_occurred.emit(str(e), self.task_id)

class QueryManager(QObject):
    all_tasks_finished = pyqtSignal(dict)  # Emitirá los datos combinados cuando todas las tareas terminen
    task_error = pyqtSignal(str)  # Emitirá si alguna tarea falla

    def __init__(self, total_tasks):
        super().__init__()
        self.total_tasks = total_tasks
        self.results = {}
        self.tasks_completed = 0

    def handle_task_finished(self, result, task_id):
        self.results[task_id] = result
        self.tasks_completed += 1

        # Verificar si todas las tareas han terminado
        if self.tasks_completed == self.total_tasks:
            self.all_tasks_finished.emit(self.results)

    def handle_task_error(self, error, task_id):
        print(f"Error en la tarea {task_id}: {error}")
        self.task_error.emit(f"Tarea {task_id} falló: {error}")

class VisualizacionDatosScreen(QWidget):
    def __init__(self, controller, main_window):
        super().__init__()
        self.controller = controller
        self.main_window = main_window

        # Añadir esta pantalla al stacked_widget del main_window
        self.main_window.visualizacion_datos_index = self.main_window.stacked_widget.addWidget(self)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Botón "Volver"
        self.button_volver = QPushButton("Volver")
        self.button_volver.setFixedWidth(100)
        self.button_volver.clicked.connect(self.volver_al_menu_principal)
        layout.addWidget(self.button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        # ComboBox para seleccionar la ciudad
        self.city_combo_box = QComboBox()
        self.city_combo_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.city_combo_box.addItem("Ciudad")  # Valor predeterminado
        ciudades = self.get_city_list()
        self.city_combo_box.addItems(ciudades)
        self.city_combo_box.currentIndexChanged.connect(self.load_existing_data)
        layout.addWidget(QLabel("Ciudad"))
        layout.addWidget(self.city_combo_box)

        # ComboBox para seleccionar el buque
        self.buque_combo_box = QComboBox()
        self.buque_combo_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.buque_combo_box.addItem("Vessel")  # Valor predeterminado
        self.buque_combo_box.currentIndexChanged.connect(self.load_existing_data)  # Conectar la señal
        layout.addWidget(QLabel("Vessel"))
        layout.addWidget(self.buque_combo_box)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.on_tab = QWidget()
        self.off_tab = QWidget()

        self.tabs.addTab(self.on_tab, "ON")
        self.tabs.addTab(self.off_tab, "OFF")

        self.on_layout = QHBoxLayout()
        self.off_layout = QHBoxLayout()
        self.on_tab.setLayout(self.on_layout)
        self.off_tab.setLayout(self.off_layout)

        self.on_table_view = QTableView()
        self.off_table_view = QTableView()
        self.on_layout.addWidget(self.on_table_view)
        self.off_layout.addWidget(self.off_table_view)

        self.setLayout(layout)
        self.load_buques()

    def get_city_list(self):
        """Obtiene la lista de ciudades asociadas a los buques en la tabla Buque."""
        try:
            session = get_db_session()
            ciudades = session.query(EtaCiudad.puerto).distinct()
            
            ciudades_unicas = sorted({ciudad[0] for ciudad in ciudades if ciudad[0]})
            
            if ciudades_unicas:
                return ciudades_unicas
            else:
                return ["No hay ciudades disponibles"]
        except SQLAlchemyError as e:
            print(f"Error al obtener las ciudades: {e}")
            return ["Error al cargar ciudades"]
        finally:
            session.close()

    def load_buques(self):
        """Carga la lista de buques en el ComboBox, eliminando duplicados."""
        try:
            session = get_db_session()
            # Obtener los nombres de buques únicos
            buques = session.query(Buque.nombre).distinct().all()
            unique_buques = sorted({buque[0] for buque in buques})  # Usar conjunto para eliminar duplicados
            if unique_buques:
                self.buque_combo_box.addItems(unique_buques)
            else:
                self.buque_combo_box.addItem("No hay buques disponibles")
        except SQLAlchemyError as e:
            print(f"Error al obtener los buques: {e}")
            self.buque_combo_box.addItem("Error al cargar buques")
        finally:
            session.close()

    def volver_al_menu_principal(self):
        """Vuelve al menú principal."""
        self.main_window.stacked_widget.setCurrentIndex(0)

    def load_existing_data(self):
        """Carga los datos de buques ON y OFF y los muestra en diferentes pestañas."""
        selected_buque = self.buque_combo_box.currentText()
        if not selected_buque or selected_buque == "No hay buques disponibles":
            return

        try:
            session = get_db_session()

            # Consulta para obtener todos los datos del buque seleccionado
            buque_data = session.query(
                Buque.nombre.label("Vessel"),
                Viaje.estado.label("Estado"),
                Viaje.activo.label("Activo"),
                Buque.empresa.label("Owner"),
                case(
                    (Viaje.estado == "ON", EtaCiudad.date_arrive_cl),
                    (Viaje.estado == "OFF", EtaCiudad.date_first_flight)
                ).label("Fecha_relevante"),
                EtaCiudad.eta.label("ETA Vessel"),
                EtaCiudad.etd.label("ETD Vessel"),
                EtaCiudad.puerto.label("Puerto"),  
                Tripulante.tripulante_id.label("tripulante_id"),
                Tripulante.nombre.label("First name"),
                Tripulante.apellido.label("Last name"),
                Tripulante.sexo.label("Gender"),
                Tripulante.nacionalidad.label("Nacionalidad"),
                Tripulante.posicion.label("Position"),
                Tripulante.pasaporte.label("Pasaporte"),
                Tripulante.fecha_nacimiento.label("DOB"),
                Tripulante.condicion.label("Condition")
            ).join(Viaje, Buque.buque_id == Viaje.buque_id) \
            .join(EtaCiudad, Viaje.eta_id == EtaCiudad.eta_id) \
            .join(Tripulante, Viaje.tripulante_id == Tripulante.tripulante_id) \
            .filter(func.lower(Buque.nombre) == func.lower(selected_buque.strip()))

            # Ejecutar la consulta y obtener los resultados como una lista
            buque_data = buque_data.all()

            # Dividir los datos en ON y OFF
            on_data = [row for row in buque_data if row.Estado == "ON"]
            off_data = [row for row in buque_data if row.Estado == "OFF"]
            
            # Obtener los tripulantes ON para vuelos internacionales
            tripulantes_on_ids = [row.tripulante_id for row in on_data]
            vuelos_on = self.get_international_flights(session, tripulantes_on_ids)
            # Obtener los tripulantes ON para vuelos domésticos
            vuelos_domesticos = self.get_domestic_flights(session, tripulantes_on_ids)
            # Obtener los tripulantes ON para vuelos regionales
            vuelos_regionales = self.get_regional_flights(session, tripulantes_on_ids)
            # Obtener los tripulantes ON para asistencia
            asistencia_data = self.get_asistencia_tripulantes(session, tripulantes_on_ids)
            # Obtener los tripulantes ON para hoteles
            hoteles_data = self.get_hoteles_tripulantes(session, tripulantes_on_ids)
            # Obtener los tripulantes ON para transporte
            transport_data = self.get_transport_data(session, tripulantes_on_ids)
            restaurant_data = self.get_restaurant_data(session, tripulantes_on_ids)

            formatted_on_data = []  
            for row in on_data:
                vuelos = vuelos_on.get(row.tripulante_id, {})
                vuelos_domestico = vuelos_domesticos.get(row.tripulante_id, {})
                vuelos_regional = vuelos_regionales.get(row.tripulante_id, {})
                asistencia = asistencia_data.get(row.tripulante_id, {})
                hoteles = hoteles_data.get(row.tripulante_id, {})
                transportes = transport_data.get(row.tripulante_id, {})
                restaurantes = restaurant_data.get(row.tripulante_id, {})
                
                row_dict = row._asdict()

                for key, value in vuelos.items():
                    row_dict[key] = value
                for key, value in vuelos_domestico.items():
                    row_dict[key] = value
                for key, value in vuelos_regional.items():
                    row_dict[key] = value
                for key, value in asistencia.items():
                    row_dict[key] = value
                for key, value in hoteles.items():
                    row_dict[key] = value
                for key, value in transportes.items():
                    row_dict[key] = value
                for key, value in restaurantes.items():  
                    row_dict[key] = value

                formatted_on_data.append(row_dict)

            # Reemplaza `on_data` con la lista formateada
            on_data = formatted_on_data
            
            tripulantes_off_ids = [row.tripulante_id for row in off_data]
            vuelos_off = self.get_international_flights(session, tripulantes_off_ids)
            # Obtener los tripulantes ON para vuelos domésticos
            vuelos_domesticos_off = self.get_domestic_flights(session, tripulantes_off_ids)
            # Obtener los tripulantes ON para vuelos regionales
            vuelos_regionales_off = self.get_regional_flights(session, tripulantes_off_ids)
            # Obtener los tripulantes ON para asistencia
            asistencia_data_off = self.get_asistencia_tripulantes(session, tripulantes_off_ids)
            # Obtener los tripulantes ON para hoteles
            hoteles_data_off = self.get_hoteles_tripulantes(session, tripulantes_off_ids)
            # Obtener los tripulantes ON para transporte
            transport_data_off = self.get_transport_data(session, tripulantes_off_ids)
            restaurant_data_off = self.get_restaurant_data(session, tripulantes_off_ids)

            formatted_off_data = []  
            for row in off_data:
                vuelos_off = vuelos_off.get(row.tripulante_id, {})
                vuelos_domestico_off = vuelos_domesticos_off.get(row.tripulante_id, {})
                vuelos_regional_off = vuelos_regionales_off.get(row.tripulante_id, {})
                asistencia_off = asistencia_data_off.get(row.tripulante_id, {})
                hoteles_off = hoteles_data_off.get(row.tripulante_id, {})
                transportes_off = transport_data_off.get(row.tripulante_id, {})
                restaurantes_off = restaurant_data_off.get(row.tripulante_id, {})
                
                row_dict = row._asdict()

                for key, value in vuelos.items():
                    row_dict[key] = value
                for key, value in vuelos_domestico_off.items():
                    row_dict[key] = value
                for key, value in vuelos_regional_off.items():
                    row_dict[key] = value
                for key, value in asistencia_off.items():
                    row_dict[key] = value
                # for key, value in hoteles_off.items():
                #     row_dict[key] = value
                # for key, value in transportes_off.items():
                #     row_dict[key] = value
                # for key, value in restaurantes_off.items():  
                #     row_dict[key] = value
                formatted_off_data.append(row_dict)

            # Reemplaza `on_data` con la lista formateada
            off_data = formatted_off_data

            self.show_data_in_tab(on_data, self.on_table_view, [
                "Activo", "Owner", "Vessel", "Date arrive CL", "ETA Vessel", "ETD Vessel",
                "Puerto", "Condition", "OKTB", "Mail PDI", "First name", "Last name", "Gender", "Nacionalidad", "Position",
                "Pasaporte", "DOB",
                "Aerolinea 1", "Aerolinea 2", "Aerolinea 3", "Aerolinea 4",
                "Vuelo Int 1", "Fecha Vuelo Int 1", "Hora Vuelo Int 1",
                "Vuelo Int 2", "Fecha Vuelo Int 2", "Hora Vuelo Int 2",
                "Vuelo Int 3", "Fecha Vuelo Int 3", "Hora Vuelo Int 3",
                "Vuelo Int 4", "Fecha Vuelo Int 4", "Hora Vuelo Int 4",
                "Nro International Flight", "Date International Flight", "Hora International Flight",
                "Nro Domestic Flight", "Date Domestic Flight", "Hora Domestic Flight",
                "Nro Regional Flight", "Date Regional Flight", "Hora Regional Flight",
                "Proveedor SCL", "Asistencia 1", "Proveedor PUQ", "Asistencia 2", "Proveedor WPU", "Asistencia 3",
                "Category", "Hotel 1", "Check in 1", "Check out 1", "Rooms 1", "Nombre Hotel 1",
                "Hotel 2", "Check in 2", "Check out 2", "Rooms 2", "Nombre Hotel 2",
                "Hotel 3", "Check in 3", "Check out 3", "Rooms 3", "Nombre Hotel 3",
                # Columnas de transporte
                "City_in_1", "Place_in_1", "City_end_1", "Place_end_1", "Date_pickup_1", "Hours_pickup_1",
                "City_in_2", "Place_in_2", "City_end_2", "Place_end_2", "Date_pickup_2", "Hours_pickup_2",
                "City_in_3", "Place_in_3", "City_end_3", "Place_end_3", "Date_pickup_3", "Hours_pickup_3",
                "City_in_4", "Place_in_4", "City_end_4", "Place_end_4", "Date_pickup_4", "Hours_pickup_4",
                # Columnas de restaurante
                "Prefer. Aliment", "Servicio Comida 1", "Fecha Desde 1", "Fecha Hasta 1", "Restaurant 1",
                "Servicio Comida 2", "Fecha Desde 2", "Fecha Hasta 2", "Restaurant 2",
                "Servicio Comida 3", "Fecha Desde 3", "Fecha Hasta 3", "Restaurant 3"
            ], "Puerto a embarcar", "ON")

            self.show_data_in_tab(off_data, self.off_table_view, [
                "Activo", "Owner", "Vessel", "Date first flight", "ETA Vessel", "ETD Vessel",
                "Puerto", "Condition", "Carta Desembarco", "Mail PDI", "First name", "Last name", "Gender", "Nacionalidad", "Position",
                "Pasaporte", "DOB",
                "Aerolinea 1", "Aerolinea 2", "Aerolinea 3", "Aerolinea 4", "Nro Regional Flight", "Date Regional Flight", "Hora Regional Flight",
                "Nro Domestic Flight", "Date Domestic Flight", "Hora Domestic Flight",
                "Nro International Flight", "Date International Flight", "Hora International Flight",
                "Proveedor SCL", "Asistencia 1", "Proveedor PUQ", "Asistencia 2", "Proveedor WPU", "Asistencia 3",
                "Category", "Hotel 1", "Check in 1", "Check out 1", "Rooms 1", "Nombre Hotel 1",
                "Hotel 2", "Check in 2", "Check out 2", "Rooms 2", "Nombre Hotel 2",
                "Hotel 3", "Check in 3", "Check out 3", "Rooms 3", "Nombre Hotel 3",
                # Columnas de transporte
                "City_in_1", "Place_in_1", "City_end_1", "Place_end_1", "Date_pickup_1", "Hours_pickup_1",
                "City_in_2", "Place_in_2", "City_end_2", "Place_end_2", "Date_pickup_2", "Hours_pickup_2",
                "City_in_3", "Place_in_3", "City_end_3", "Place_end_3", "Date_pickup_3", "Hours_pickup_3",
                "City_in_4", "Place_in_4", "City_end_4", "Place_end_4", "Date_pickup_4", "Hours_pickup_4",
                # Columnas de restaurante
                "Prefer. Aliment", "Servicio Comida 1", "Fecha Desde 1", "Fecha Hasta 1", "Restaurant 1",
                "Servicio Comida 2", "Fecha Desde 2", "Fecha Hasta 2", "Restaurant 2",
                "Servicio Comida 3", "Fecha Desde 3", "Fecha Hasta 3", "Restaurant 3"
            ], "Puerto a desembarcar", "OFF")


        except SQLAlchemyError as e:
            print(f"Error al cargar datos: {e}")
        finally:
            session.close()

    def show_data_in_tab(self, data, table_view, columns, puerto_label, estado):
        """Convierte los datos a un DataFrame y los muestra en el QTableView."""
        if not data:
            print(f"No hay datos para mostrar en la pestaña {puerto_label}")
            return

        try:
            # Crear un DataFrame directamente desde los datos
            df = pd.DataFrame(data)

            # Renombrar la columna Fecha_relevante
            if "Fecha_relevante" in df.columns:
                if estado == "ON":
                    df.rename(columns={"Fecha_relevante": "Date arrive CL"}, inplace=True)
                elif estado == "OFF":
                    df.rename(columns={"Fecha_relevante": "Date first flight"}, inplace=True)

            # Asegurarse de que el DataFrame tenga todas las columnas especificadas en el orden correcto
            for col in columns:
                if col not in df.columns:
                    df[col] = None  # Agrega columnas faltantes con valores nulos

            df = df[columns]  # Reordena las columnas en el orden especificado

            # Transformar "Activo" de booleano a "SI" o "NO"
            if "Activo" in df.columns:
                df["Activo"] = df["Activo"].map({True: "SI", False: "NO"})

            # Normalizar las fechas
            if "ETA Vessel" in df.columns:
                df["ETA Vessel"] = pd.to_datetime(df["ETA Vessel"], errors="coerce").dt.strftime("%d-%m-%Y")
            if "ETD Vessel" in df.columns:
                df["ETD Vessel"] = pd.to_datetime(df["ETD Vessel"], errors="coerce").dt.strftime("%d-%m-%Y")

            # Crear el modelo y asignarlo al QTableView
            model = PandasModel(df)
            table_view.setModel(model)

            # Configurar estilo y tamaño de columnas
            table_view.resizeColumnsToContents()
            table_view.setAlternatingRowColors(True)
            table_view.setStyleSheet("""
                QTableView {
                    gridline-color: #00272d;
                    background-color: white;
                    alternate-background-color: #f9f9f9;
                    font-size: 14px;
                    font-family: Arial, sans-serif;
                    color: #00272d;
                    selection-background-color: #134647;
                    selection-color: white;
                }
                QHeaderView::section {
                    background-color: #134647;
                    color: white;
                    font-weight: bold;
                }
            """)
        except Exception as e:
            print(f"Error al mostrar los datos en la pestaña {puerto_label}: {e}")

    def get_international_flights(self, session, tripulantes):
        """
        Recupera vuelos internacionales y los estructura por tripulante,
        incluyendo el último vuelo internacional (que llega a Chile)"""
        print(f"Tripulantes recibidos para búsqueda de vuelos: {tripulantes}")  # Depuración inicial
        
        vuelos_data = session.query(
            Tripulante.tripulante_id,
            Vuelo.aerolinea,
            Vuelo.codigo.label("codigo"),
            Vuelo.fecha.label("fecha"),
            Vuelo.hora_salida.label("hora_salida"),
            Vuelo.hora_llegada.label("hora_llegada"),
            Vuelo.aeropuerto_salida.label("origen"),
            Vuelo.aeropuerto_llegada.label("destino"),
        ).join(TripulanteVuelo, Tripulante.tripulante_id == TripulanteVuelo.tripulante_id) \
            .join(Vuelo, TripulanteVuelo.vuelo_id == Vuelo.vuelo_id) \
            .filter(Vuelo.tipo == "INTERNACIONAL", Tripulante.tripulante_id.in_(tripulantes)) \
            .order_by(Tripulante.tripulante_id, Vuelo.fecha).all()

        print(f"Datos de vuelos recuperados: {vuelos_data}")  # Depuración

        # Inicializar el diccionario que contendrá los vuelos formateados
        vuelos_formateados = {tripulante_id: {
            f"Aerolinea {i + 1}": None for i in range(4)  # Aerolíneas 1-4 primero
        } for tripulante_id in tripulantes}

        for tripulante_id in vuelos_formateados:
            vuelos_formateados[tripulante_id].update({
                f"Vuelo Int {i + 1}": None for i in range(4)
            })
            vuelos_formateados[tripulante_id].update({
                f"Fecha Vuelo Int {i + 1}": None for i in range(4)
            })
            vuelos_formateados[tripulante_id].update({
                f"Hora Vuelo Int {i + 1}": None for i in range(4)
            })
            vuelos_formateados[tripulante_id].update({
                "Nro International Flight": None,
                "Date International Flight": None,
                "Hora International Flight": None
            })

        tripulante_indices = {tripulante_id: 0 for tripulante_id in tripulantes}

        for vuelo in vuelos_data:
            tripulante_id = vuelo.tripulante_id
            index = tripulante_indices[tripulante_id]

            # Mapear los códigos de origen y destino
            origen_code = CITY_TO_AIRPORT_CODES.get(vuelo.origen.upper(), vuelo.origen)
            destino_code = CITY_TO_AIRPORT_CODES.get(vuelo.destino.upper(), vuelo.destino)

            if index < 4:  # Asignar hasta 4 vuelos
                vuelos_formateados[tripulante_id][f"Aerolinea {index + 1}"] = vuelo.aerolinea
                vuelos_formateados[tripulante_id][f"Vuelo Int {index + 1}"] = f"{vuelo.codigo} {origen_code}-{destino_code}"
                vuelos_formateados[tripulante_id][f"Fecha Vuelo Int {index + 1}"] = vuelo.fecha.strftime("%d/%m/%y")
                vuelos_formateados[tripulante_id][f"Hora Vuelo Int {index + 1}"] = f"{vuelo.hora_salida.strftime('%H:%M')} {vuelo.hora_llegada.strftime('%H:%M')}"
                tripulante_indices[tripulante_id] += 1

            # Siempre actualizar el último vuelo internacional (máxima fecha)
            vuelos_formateados[tripulante_id]["Nro International Flight"] = f"{vuelo.codigo} {origen_code}-{destino_code}"
            vuelos_formateados[tripulante_id]["Date International Flight"] = vuelo.fecha.strftime("%d/%m/%y")
            vuelos_formateados[tripulante_id]["Hora International Flight"] = f"{vuelo.hora_salida.strftime('%H:%M')} {vuelo.hora_llegada.strftime('%H:%M')}"

        # Depuración final
        print("Vuelos internacionales formateados finalizados:")
        for tripulante_id, vuelos in vuelos_formateados.items():
            print(f"Tripulante {tripulante_id}: {vuelos}")

        return vuelos_formateados

    def get_domestic_flights(self, session, tripulantes):
        """
        Recupera el último vuelo doméstico para cada tripulante,
        """
        print(f"Tripulantes recibidos para búsqueda de vuelos domésticos: {tripulantes}")  # Depuración inicial
        
        vuelos_data = session.query(
            Tripulante.tripulante_id,
            Vuelo.aerolinea,
            Vuelo.codigo.label("codigo"),
            Vuelo.fecha.label("fecha"),
            Vuelo.hora_salida.label("hora_salida"),
            Vuelo.hora_llegada.label("hora_llegada"),
            Vuelo.aeropuerto_salida.label("origen"),
            Vuelo.aeropuerto_llegada.label("destino"),
        ).join(TripulanteVuelo, Tripulante.tripulante_id == TripulanteVuelo.tripulante_id) \
            .join(Vuelo, TripulanteVuelo.vuelo_id == Vuelo.vuelo_id) \
            .filter(Vuelo.tipo == "DOMESTICO", Tripulante.tripulante_id.in_(tripulantes)) \
            .order_by(Tripulante.tripulante_id, Vuelo.fecha).all()

        print(f"Datos de vuelos domésticos recuperados: {vuelos_data}")  # Depuración

        # Inicializar el diccionario para almacenar el último vuelo doméstico por tripulante
        vuelos_formateados = {tripulante_id: {
            "Nro Domestic Flight": None,
            "Date Domestic Flight": None,
            "Hora Domestic Flight": None
        } for tripulante_id in tripulantes}

        # Asignar el último vuelo doméstico para cada tripulante
        for vuelo in vuelos_data:
            tripulante_id = vuelo.tripulante_id
            
            # Obtener los códigos de los aeropuertos (origen y destino)
            origen_code = CITY_TO_AIRPORT_CODES.get(vuelo.origen.upper(), vuelo.origen)
            destino_code = CITY_TO_AIRPORT_CODES.get(vuelo.destino.upper(), vuelo.destino)

            vuelos_formateados[tripulante_id]["Nro Domestic Flight"] = f"{vuelo.codigo} {origen_code}-{destino_code}"
            vuelos_formateados[tripulante_id]["Date Domestic Flight"] = vuelo.fecha.strftime("%d/%m/%y")
            vuelos_formateados[tripulante_id]["Hora Domestic Flight"] = f"{vuelo.hora_salida.strftime('%H:%M')} {vuelo.hora_llegada.strftime('%H:%M')}"

        # Depuración final
        print("Vuelos domésticos formateados finalizados:")
        for tripulante_id, vuelos in vuelos_formateados.items():
            print(f"Tripulante {tripulante_id}: {vuelos}")

        return vuelos_formateados

    def get_regional_flights(self, session, tripulantes):
        """
        Recupera el último vuelo regional para cada tripulante
        """
        print(f"Tripulantes recibidos para búsqueda de vuelos regionales: {tripulantes}")  # Depuración inicial
        
        vuelos_data = session.query(
            Tripulante.tripulante_id,
            Vuelo.aerolinea,
            Vuelo.codigo.label("codigo"),
            Vuelo.fecha.label("fecha"),
            Vuelo.hora_salida.label("hora_salida"),
            Vuelo.hora_llegada.label("hora_llegada"),
            Vuelo.aeropuerto_salida.label("origen"),
            Vuelo.aeropuerto_llegada.label("destino"),
        ).join(TripulanteVuelo, Tripulante.tripulante_id == TripulanteVuelo.tripulante_id) \
            .join(Vuelo, TripulanteVuelo.vuelo_id == Vuelo.vuelo_id) \
            .filter(Vuelo.tipo == "REGIONAL", Tripulante.tripulante_id.in_(tripulantes)) \
            .order_by(Tripulante.tripulante_id, Vuelo.fecha).all()

        print(f"Datos de vuelos regionales recuperados: {vuelos_data}")  # Depuración

        # Inicializar el diccionario para almacenar el último vuelo regional por tripulante
        vuelos_formateados = {tripulante_id: {
            "Nro Regional Flight": None,
            "Date Regional Flight": None,
            "Hora Regional Flight": None
        } for tripulante_id in tripulantes}

        # Asignar el último vuelo regional para cada tripulante
        for vuelo in vuelos_data:
            tripulante_id = vuelo.tripulante_id
            origen_code = CITY_TO_AIRPORT_CODES.get(vuelo.origen.upper(), vuelo.origen)
            destino_code = CITY_TO_AIRPORT_CODES.get(vuelo.destino.upper(), vuelo.destino)

            vuelos_formateados[tripulante_id]["Nro Regional Flight"] = f"{vuelo.codigo} {origen_code}-{destino_code}"
            vuelos_formateados[tripulante_id]["Date Regional Flight"] = vuelo.fecha.strftime("%d/%m/%y")
            vuelos_formateados[tripulante_id]["Hora Regional Flight"] = f"{vuelo.hora_salida.strftime('%H:%M')} {vuelo.hora_llegada.strftime('%H:%M')}"

        # Depuración final
        print("Vuelos regionales formateados finalizados:")
        for tripulante_id, vuelos in vuelos_formateados.items():
            print(f"Tripulante {tripulante_id}: {vuelos}")

        return vuelos_formateados

    def get_asistencia_tripulantes(self, session, tripulantes):
        """
        Recupera información de asistencia y proveedores para los tripulantes.
        """
        print(f"Tripulantes recibidos para búsqueda de asistencia: {tripulantes}")  # Depuración inicial

        # Consulta para recuperar los datos de asistencia y proveedores
        asistencia_data = session.query(
            TripulanteAsistencia.tripulante_id,
            TripulanteAsistencia.necesita_asistencia_scl.label("asistencia_scl"),
            TripulanteAsistencia.proveedor_scl.label("proveedor_scl"),
            TripulanteAsistencia.necesita_asistencia_puq.label("asistencia_puq"),
            TripulanteAsistencia.proveedor_puq.label("proveedor_puq"),
            TripulanteAsistencia.necesita_asistencia_wpu.label("asistencia_wpu"),
            TripulanteAsistencia.proveedor_wpu.label("proveedor_wpu"),
        ).filter(TripulanteAsistencia.tripulante_id.in_(tripulantes)).all()

        print(f"Datos de asistencia recuperados: {asistencia_data}")  # Depuración

        # Inicializar diccionario para almacenar los datos formateados
        asistencia_formateada = {tripulante_id: {
            "Proveedor SCL": None,
            "Asistencia 1": None,
            "Proveedor PUQ": None,
            "Asistencia 2": None,
            "Proveedor WPU": None,
            "Asistencia 3": None
        } for tripulante_id in tripulantes}

        # Formatear los datos
        for asistencia in asistencia_data:
            tripulante_id = asistencia.tripulante_id
            asistencia_formateada[tripulante_id]["Proveedor SCL"] = asistencia.proveedor_scl if asistencia.proveedor_scl else None
            asistencia_formateada[tripulante_id]["Asistencia 1"] = "Asistencia SCL" if asistencia.asistencia_scl else None

            asistencia_formateada[tripulante_id]["Proveedor PUQ"] = asistencia.proveedor_puq if asistencia.proveedor_puq else None
            asistencia_formateada[tripulante_id]["Asistencia 2"] = "Asistencia PUQ" if asistencia.asistencia_puq else None

            asistencia_formateada[tripulante_id]["Proveedor WPU"] = asistencia.proveedor_wpu if asistencia.proveedor_wpu else None
            asistencia_formateada[tripulante_id]["Asistencia 3"] = "Asistencia WPU" if asistencia.asistencia_wpu else None

        # Depuración final
        print("Datos de asistencia formateados:")
        for tripulante_id, asistencia in asistencia_formateada.items():
            print(f"Tripulante {tripulante_id}: {asistencia}")

        return asistencia_formateada

    def get_hoteles_tripulantes(self, session, tripulantes):
        """
        Recupera información de hoteles asignados a los tripulantes.
        Devuelve hasta 3 hoteles formateados para cada tripulante.
        """
        print(f"Tripulantes recibidos para búsqueda de hoteles: {tripulantes}")  # Depuración inicial

        # Consulta para recuperar los datos de los hoteles asignados
        hoteles_data = session.query(
            TripulanteHotel.tripulante_id,
            cast(TripulanteHotel.categoria, Integer).label("categoria"),            
            TripulanteHotel.fecha_entrada.label("check_in"),
            TripulanteHotel.fecha_salida.label("check_out"),
            TripulanteHotel.tipo_habitacion.label("tipo_habitacion"),
            Hotel.nombre.label("nombre_hotel"),
            Hotel.ciudad.label("ciudad_hotel")
        ).join(Hotel, TripulanteHotel.hotel_id == Hotel.hotel_id) \
        .filter(TripulanteHotel.tripulante_id.in_(tripulantes)) \
        .order_by(TripulanteHotel.tripulante_id, TripulanteHotel.fecha_entrada).all()

        print(f"Datos de hoteles recuperados: {hoteles_data}")  # Depuración

        # Inicializar diccionario para almacenar hasta 3 hoteles por tripulante
        hoteles_formateados = {tripulante_id: {
            "Category": None,
            **{f"Hotel {i + 1}": None for i in range(3)},
            **{f"Check in {i + 1}": None for i in range(3)},
            **{f"Check out {i + 1}": None for i in range(3)},
            **{f"Rooms {i + 1}": None for i in range(3)},
            **{f"Nombre Hotel {i + 1}": None for i in range(3)}
        } for tripulante_id in tripulantes}

        # Asignar hasta 3 hoteles para cada tripulante
        tripulante_indices = {tripulante_id: 0 for tripulante_id in tripulantes}

        for hotel in hoteles_data:
            tripulante_id = hotel.tripulante_id
            index = tripulante_indices[tripulante_id]

            if index < 3:  # Limitar a 3 hoteles por tripulante
                hoteles_formateados[tripulante_id]["Category"] = int(hotel.categoria) if hotel.categoria is not None else None
                hoteles_formateados[tripulante_id][f"Hotel {index + 1}"] = f"Hotel {hotel.ciudad_hotel}"
                hoteles_formateados[tripulante_id][f"Check in {index + 1}"] = (
                    hotel.check_in.strftime("%d/%m/%y") if hotel.check_in else None
                )
                hoteles_formateados[tripulante_id][f"Check out {index + 1}"] = (
                    hotel.check_out.strftime("%d/%m/%y") if hotel.check_out else None
                )
                hoteles_formateados[tripulante_id][f"Rooms {index + 1}"] = hotel.tipo_habitacion
                hoteles_formateados[tripulante_id][f"Nombre Hotel {index + 1}"] = hotel.nombre_hotel
                tripulante_indices[tripulante_id] += 1

        # Depuración final
        print("Datos de hoteles formateados:")
        for tripulante_id, hoteles in hoteles_formateados.items():
            print(f"Tripulante {tripulante_id}: {hoteles}")

        return hoteles_formateados
    
    def get_transport_data(self, session, tripulantes):
        """
        Obtiene los datos de transporte para los tripulantes especificados.
        
        Args:
            session: Sesión de SQLAlchemy.
            tripulantes: Lista de IDs de tripulantes.

        Returns:
            dict: Datos de transporte formateados para cada tripulante.
        """
        print(f"Buscando datos de transporte para tripulantes: {tripulantes}")  # Depuración inicial
        
        # Consulta para obtener los datos
        transport_data = session.query(
            TripulanteTransporte.tripulante_id,
            Transporte.city_in,
            Transporte.place_in,
            Transporte.city_end,
            Transporte.place_end,
            TripulanteTransporte.date_pickup,
            TripulanteTransporte.hours_pickup
        ).join(Transporte, TripulanteTransporte.transporte_id == Transporte.transporte_id) \
        .filter(TripulanteTransporte.tripulante_id.in_(tripulantes)) \
        .order_by(TripulanteTransporte.tripulante_id, TripulanteTransporte.date_pickup).all()

        print(f"Datos de transporte recuperados: {transport_data}")  # Depuración

        # Inicializar el diccionario para almacenar datos por tripulante
        formatted_transport_data = {tripulante_id: {
            **{f"City_in_{i+1}": None for i in range(4)},
            **{f"Place_in_{i+1}": None for i in range(4)},
            **{f"City_end_{i+1}": None for i in range(4)},
            **{f"Place_end_{i+1}": None for i in range(4)},
            **{f"Date_pickup_{i+1}": None for i in range(4)},
            **{f"Hours_pickup_{i+1}": None for i in range(4)},
        } for tripulante_id in tripulantes}

        # Indices para cada tripulante para llenar hasta 4 transportes
        tripulante_indices = {tripulante_id: 0 for tripulante_id in tripulantes}

        for transporte in transport_data:
            tripulante_id = transporte.tripulante_id
            index = tripulante_indices[tripulante_id]

            if index < 4:  # Limitar a 4 transportes
                formatted_transport_data[tripulante_id][f"City_in_{index + 1}"] = transporte.city_in
                formatted_transport_data[tripulante_id][f"Place_in_{index + 1}"] = transporte.place_in
                formatted_transport_data[tripulante_id][f"City_end_{index + 1}"] = transporte.city_end
                formatted_transport_data[tripulante_id][f"Place_end_{index + 1}"] = transporte.place_end
                formatted_transport_data[tripulante_id][f"Date_pickup_{index + 1}"] = (
                    transporte.date_pickup.strftime("%d/%m/%y") if transporte.date_pickup else None
                )
                formatted_transport_data[tripulante_id][f"Hours_pickup_{index + 1}"] = (
                    transporte.hours_pickup.strftime("%H:%M") if transporte.hours_pickup else None
                )
                tripulante_indices[tripulante_id] += 1

        # Depuración final
        print("Datos de transporte formateados:")
        for tripulante_id, transportes in formatted_transport_data.items():
            print(f"Tripulante {tripulante_id}: {transportes}")

        return formatted_transport_data

    def get_restaurant_data(self, session, tripulantes):
        """
        Obtiene los datos de preferencias alimenticias y reservas de restaurantes para los tripulantes especificados.

        Args:
            session: Sesión de SQLAlchemy.
            tripulantes: Lista de IDs de tripulantes.

        Returns:
            dict: Datos de restaurante formateados para cada tripulante.
        """
        print(f"Buscando datos de restaurantes para tripulantes: {tripulantes}")  # Depuración inicial
        
        # Consulta para obtener los datos
        restaurant_data = session.query(
            TripulanteRestaurante.tripulante_id,
            TripulanteRestaurante.pref_alimenticia,
            TripulanteRestaurante.tipo_comida,
            TripulanteRestaurante.fecha_reserva,
            Restaurante.nombre.label("nombre_restaurante"),
            Restaurante.ciudad.label("ciudad_restaurante")
        ).join(Restaurante, TripulanteRestaurante.restaurante_id == Restaurante.restaurante_id) \
        .filter(TripulanteRestaurante.tripulante_id.in_(tripulantes)) \
        .order_by(TripulanteRestaurante.tripulante_id, TripulanteRestaurante.fecha_reserva).all()

        print(f"Datos de restaurantes recuperados: {restaurant_data}")  # Depuración

        # Inicializar el diccionario para almacenar datos por tripulante
        formatted_restaurant_data = {tripulante_id: {
            "Prefer. Aliment": None,
            **{f"Servicio Comida {i+1}": None for i in range(3)},
            **{f"Fecha Desde {i+1}": None for i in range(3)},
            **{f"Fecha Hasta {i+1}": None for i in range(3)},
            **{f"Restaurant {i+1}": None for i in range(3)},
        } for tripulante_id in tripulantes}

        # Indices para cada tripulante para llenar hasta 3 reservas
        tripulante_indices = {tripulante_id: 0 for tripulante_id in tripulantes}

        for reserva in restaurant_data:
            tripulante_id = reserva.tripulante_id
            index = tripulante_indices[tripulante_id]

            if formatted_restaurant_data[tripulante_id]["Prefer. Aliment"] is None:
                formatted_restaurant_data[tripulante_id]["Prefer. Aliment"] = reserva.pref_alimenticia

            if index < 3:  # Limitar a 3 reservas
                formatted_restaurant_data[tripulante_id][f"Servicio Comida {index + 1}"] = reserva.tipo_comida
                formatted_restaurant_data[tripulante_id][f"Fecha Desde {index + 1}"] = (
                    reserva.fecha_reserva.strftime("%d-%m-%y") if reserva.fecha_reserva else None
                )
                # Aquí puedes agregar lógica para calcular "Fecha Hasta" si aplica
                formatted_restaurant_data[tripulante_id][f"Fecha Hasta {index + 1}"] = (
                    reserva.fecha_reserva.strftime("%d-%m-%y") if reserva.fecha_reserva else None
                )
                formatted_restaurant_data[tripulante_id][f"Restaurant {index + 1}"] = reserva.nombre_restaurante
                tripulante_indices[tripulante_id] += 1

        # Depuración final
        print("Datos de restaurantes formateados:")
        for tripulante_id, restaurantes in formatted_restaurant_data.items():
            print(f"Tripulante {tripulante_id}: {restaurantes}")

        return formatted_restaurant_data

    class PandasModel(QAbstractTableModel):
        def __init__(self, data: pd.DataFrame):
            super().__init__()
            self._data = data

        def rowCount(self, parent=None):
            return len(self._data)

        def columnCount(self, parent=None):
            return len(self._data.columns)

        def data(self, index, role=Qt.ItemDataRole.DisplayRole):
            if index.isValid():
                if role == Qt.ItemDataRole.DisplayRole:
                    return str(self._data.iloc[index.row(), index.column()])
            return None

        def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
            if role == Qt.ItemDataRole.DisplayRole:
                if orientation == Qt.Orientation.Horizontal:
                    return self._data.columns[section]
                else:
                    return section + 1  # Índice de fila