from datetime import datetime
import pandas as pd
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QComboBox, QLabel, QTableView,
    QPushButton, QSizePolicy, QTabWidget, QHBoxLayout
)
from PyQt6.QtCore import Qt
from sqlalchemy.sql import func
from app.interfaz.pandas_model import PandasModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import case
from app.database import get_db_session
from app.models import Buque, EtaCiudad, Tripulante, Viaje, Vuelo, TripulanteVuelo, Restaurante, TripulanteRestaurante, Transporte, TripulanteTransporte, Hotel, TripulanteHotel, Buque, TripulanteAsistencia

from PyQt6.QtCore import QAbstractTableModel

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
        self.button_volver.setStyleSheet("""
            font-size: 16px;  /* Tamaño de la letra */
            padding: 0px;    /* Elimina el espacio interno */
            line-height: 18px; /* Asegura que el texto no se corte verticalmente */
            text-align: center; /* Centra el texto */
        """)
        self.button_volver.setFixedWidth(80)
        self.button_volver.setFixedHeight(40)
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

            formatted_on_data = []  # Nueva lista para almacenar los datos formateados
            for row in on_data:
                vuelos = vuelos_on.get(row.tripulante_id, {})
                vuelos_domestico = vuelos_domesticos.get(row.tripulante_id, {})
                vuelos_regional = vuelos_regionales.get(row.tripulante_id, {})  # Añadir vuelos regionales
                row_dict = row._asdict()
                for key, value in vuelos.items():
                    row_dict[key] = value
                for key, value in vuelos_domestico.items():
                    row_dict[key] = value
                for key, value in vuelos_regional.items():
                    row_dict[key] = value  # Agregar vuelos regionales al diccionario
                formatted_on_data.append(row_dict)

                        # Reemplaza `on_data` con la lista formateada
            on_data = formatted_on_data

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
                "Nro Regional Flight", "Date Regional Flight", "Hora Regional Flight"  # Nuevas columnas
            ], "Puerto a embarcar", "ON")

            self.show_data_in_tab(off_data, self.off_table_view, [
                "Activo", "Owner", "Vessel", "Date first flight", "ETA Vessel", "ETD Vessel",
                "Puerto", "Condition", "Carta Desembarco", "Mail PDI", "First name", "Last name", "Gender", "Nacionalidad", "Position",
                "Pasaporte", "DOB",
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