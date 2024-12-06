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

    def process_excel_file(self, file_path, update_progress_callback):
        try:
            ### BUQUES ###
            self.buques_on, self.buques_off = self.buques_processor.buques_main(file_path)
            self.buques_processor._create_buque(self.buques_on)
            self.buques_processor._create_buque(self.buques_off)
            update_progress_callback(10)  # 10% después de procesar los buques

            ### TRIPULANTES ###
            self.tripulantes_on, self.tripulantes_off = self.tripulantes_processor.tripulantes_main(file_path)
            self.tripulantes_processor._create_tripulantes(self.tripulantes_on, self.buques_on, "ON")
            self.tripulantes_processor._create_tripulantes(self.tripulantes_off, self.buques_off, "OFF")
            update_progress_callback(20)  # 20% después de procesar los tripulantes

            # ### AEROLINEAS ###
            # self.aerolineas_on, self.aerolineas_off = self.aerolineas_processor.aerolineas_main(file_path)
            # update_progress_callback(30)  # 30% después de procesar aerolíneas

            # ### VUELOS ###
            # self.vuelos_internacionales_on, self.vuelos_internacionales_off, self.vuelos_domesticos_on, self.vuelos_domesticos_off, self.vuelos_regionales_on, self.vuelos_regionales_off = self.vuelos_processor.vuelos_main(file_path)
            # update_progress_callback(50)  # 50% después de procesar vuelos

            # ### ASISTENCIAS ###
            # self.asistencias_on = self.asistencias_processor.asistencias_main(file_path)
            # update_progress_callback(60)  # 60% después de procesar asistencias

            # ### HOTELES ###
            # self.hoteles_on, self.hoteles_off = self.hoteles_processor.hoteles_main(file_path)
            # update_progress_callback(70)  # 70% después de procesar hoteles

            # ### TRANSPORTES ###
            # self.transportes_on, self.transportes_off = self.transportes_processor.transportes_main(file_path)
            # update_progress_callback(80)  # 80% después de procesar transportes

            # ### RESTAURANTES ###
            # self.restaurantes_on, self.restaurantes_off = self.restaurantes_processor.restaurantes_main(file_path)
            # update_progress_callback(90)  # 90% después de procesar restaurantes

            # ### EXTRAS ###
            # self.extras_on, self.extras_off = self.extras_processor.extras_main(file_path)
            # update_progress_callback(95)  # 95% después de procesar extras

            # ### VIAJES ###
            # self.viaje_processor._create_viajes_from_dataframes(self.tripulantes_on, self.tripulantes_off, self.buques_on, self.buques_off)
            # update_progress_callback(100)  # 100% después de procesar viajes

            return self.buques_on, self.buques_off, self.tripulantes_on, self.tripulantes_off
        except Exception as e:
            raise Exception(f"[Controller] Error al procesar el archivo: {e}")
