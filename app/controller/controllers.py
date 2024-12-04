from sqlalchemy.orm import Session
from app.controller.buques import Buques
from app.controller.tripulantes import Tripulantes
from app.controller.aerolineas import Aerolineas
from app.controller.vuelos import Vuelos
from app.controller.asistencias import Asistencias
from app.controller.hoteles import Hoteles
from app.controller.transportes import Transportes
from app.controller.restaurantes import Restaurantes
from app.controller.extras import Extras
from app.controller.viajes import Viajes

CITY_AIRPORT_CODES = {
    'PUQ': "PUNTA ARENAS",
    'SCL': "SANTIAGO",
    'PMC': "PUERTO MONTT",
    'VAP': "VALPARAISO",
    'ZAL': "VALDIVIA",
    'WPU': "PUERTO WILLIAMS",
    'CDG': 'PARIS',
    'NY': 'NUEVA YORK',
    'SPU': 'SPLIT',
    'ZAG': 'ZAGREB',
    'AMS': 'AMSTERDAM',
    'EZE': 'BUENOS AIRES',
    'LUN': "LUSAKA",
    'DOH': "DOHA",
    'PUJ': "PUNTA CANA",
    'LIM': "LIMA",
    'ANF': "ANTOFAGASTA",
    'IQQ': "IQUIQUE",
    'CCP': "CONCEPCIÓN",
    'LSC': "LA SERENA",
    'ARI': "ARICA",
    'IPC': "RAPA NUI",
    'LAX': "LOS ÁNGELES",
    'JFK': "NUEVA YORK",
    'MAD': "MADRID",
    'LHR': "LONDRES",
    'DXB': "DUBÁI",
    'MQP': "MPUMALANGA",
    'JNB': "JOHANNESBURGO",
    'LCA': "LÁRNACA",
    'ZRH': "ZÚRICH",
    'GOX': "GOLFE DE GARABOGAZ",
    'TRV': "THIRUVANANTHAPURAM",
    'PVG': "SHANGHAI",
    'CGK': "YAKARTA",
    'BDS': "BRINDISI",
    'GRU': "SÃO PAULO",
    'NBO': "NAIROBI",
    'ICN': "SEÚL",
    'HRE': "HARARE",
    'OTP': "BUCARESTANT",
    'AKL': "AUCKLAND",
    'FCO': "ROMA",
    'PTY': "PANAMÁ",
    'MNL': "MANILA",
    'IST': "ESTAMBUL",
    'LED': "SAN PETERSBURGO",
    'IMF': "IMPHAL",
    'TDG': "TANDAG",
    'SUB': "SURABAYA",
    'MGA': "MANAGUA",
    'DEL': "DELHI",
    'GEO': "GEORGETOWN",
    'DPS': "DENPASAR",
    'MIA': "MIAMI",
    'SAL': "SAN SALVADOR",
    'MRU': "MAURICIO",
    'JKT': "YAKARTA",
    'SAP': "SAN PEDRO SULA",
    'SOC': "SOLO CITY",
    'MBJ': "MONTEGO BAY",
    'BOM': "BOMBAY",
    'GUA': "CIUDAD DE GUATEMALA",
    'CCU': "CALCUTA",
    'COK': "COCHIN",
    'CMB': "COLOMBO"
}

CITY_TO_AIRPORT_CODES = {city: code for code, city in CITY_AIRPORT_CODES.items()}

class Controller:
    def __init__(self, db_session: Session):
        db_session = db_session
        self.buques_processor = Buques(db_session)
        self.tripulantes_processor = Tripulantes(db_session)
        self.aerolineas_processor = Aerolineas(db_session)
        self.vuelos_processor = Vuelos(db_session)
        self.asistencias_processor = Asistencias(db_session)
        self.hoteles_processor = Hoteles(db_session)
        self.transportes_processor = Transportes(db_session)
        self.restaurantes_processor = Restaurantes(db_session)
        self.extras_processor = Extras(db_session)
        self.viaje_processor = Viajes(db_session)

    def process_excel_file(self, file_path):
        try:
            ### BUQUES ###
            self.buques_on, self.buques_off = self.buques_processor.buques_main(file_path)
            self.buques_processor._create_buque(self.buques_on)
            self.buques_processor._create_buque(self.buques_off)

            ### TRIPULANTES ###

            self.tripulantes_on, self.tripulantes_off = self.tripulantes_processor.tripulantes_main(file_path)
            self.tripulantes_processor._create_tripulantes(self.tripulantes_on, self.buques_on, "ON")
            self.tripulantes_processor._create_tripulantes(self.tripulantes_off, self.buques_off, "OFF")

            ### AEROLINEAS ###

            self.aerolineas_on, self.aerolineas_off = self.aerolineas_processor.aerolineas_main(file_path)
            # FALTA GUARDARLOS EN LA DB

            ### VUELOS ###

            self.vuelos_internacionales_on, self.vuelos_internacionales_off, self.vuelos_domesticos_on, self.vuelos_domesticos_off, self.vuelos_regionales_on, self.vuelos_regionales_off = self.vuelos_processor.vuelos_main(file_path)
            self.vuelos_processor._create_vuelos(self.vuelos_internacionales_on, self.tripulantes_on, 'ON', 'INTERNACIONAL')
            self.vuelos_processor._create_vuelos(self.vuelos_internacionales_off, self.tripulantes_off, 'OFF', 'INTERNACIONAL')
            self.vuelos_processor._create_vuelos(self.vuelos_domesticos_on, self.tripulantes_on, 'ON', 'DOMESTICO')
            self.vuelos_processor._create_vuelos(self.vuelos_domesticos_off, self.tripulantes_off, 'OFF', 'DOMESTICO')
            self.vuelos_processor._create_vuelos(self.vuelos_regionales_on, self.tripulantes_on, 'ON', 'REGIONAL')
            self.vuelos_processor._create_vuelos(self.vuelos_regionales_off, self.tripulantes_off, 'OFF', 'REGIONAL')

            ### ASISTENCIAS ###

            self.asistencias_on = self.asistencias_processor.asistencias_main(file_path)
            self.asistencias_processor._create_asistencias(self.tripulantes_on, self.asistencias_on)

            ### HOTELES ###

            self.hoteles_on, self.hoteles_off = self.hoteles_processor.hoteles_main(file_path)
            self.hoteles_processor._create_hotel(self.hoteles_on, self.tripulantes_on)
            self.hoteles_processor._create_hotel(self.hoteles_off, self.tripulantes_off)

            ### TRANSPORTES ###

            self.transportes_on, self.transportes_off = self.transportes_processor.transportes_main(file_path)
            self.transportes_processor._create_transporte(self.transportes_on, self.tripulantes_on)
            self.transportes_processor._create_transporte(self.transportes_off, self.tripulantes_off)

            ### RESTAURANTES ###

            self.restaurantes_on, self.restaurantes_off = self.restaurantes_processor.restaurantes_main(file_path)
            self.restaurantes_processor._create_restaurantes(self.restaurantes_on, self.tripulantes_on)
            self.restaurantes_processor._create_restaurantes(self.restaurantes_off, self.tripulantes_off)

            ### EXTRAS ###

            self.extras_on, self.extras_off = self.extras_processor.extras_main(file_path)
            # FALTA GUARDARLOS EN LA DB

            ### VIAJES ###

            self.viaje_processor._create_viajes_from_dataframes(self.tripulantes_on, self.tripulantes_off, self.buques_on, self.buques_off)

            return self.buques_on, self.buques_off, self.tripulantes_on, self.tripulantes_off
        except Exception as e:
            raise Exception(f"[Controller] Error al procesar el archivo: {e}")
