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
            self.errors_buques_on, self.errors_buques_on_message = self.buques_processor._create_buque(file_path, self.buques_on, "ON")
            update_progress_callback(5)
            self.errors_buques_off, self.errors_buques_off_message = self.buques_processor._create_buque(file_path, self.buques_off, "OFF")
            update_progress_callback(10)  # 10% después de procesar los buques

            ### TRIPULANTES ###
            self.tripulantes_on, self.tripulantes_off = self.tripulantes_processor.tripulantes_main(file_path)

            self.errors_tripulantes_on, self.errors_tripulantes_on_message = self.tripulantes_processor._create_tripulantes(file_path, self.tripulantes_on, self.buques_on, "ON")
            update_progress_callback(15)
            self.errors_tripulantes_off, self.errors_tripulantes_off_message = self.tripulantes_processor._create_tripulantes(file_path, self.tripulantes_off, self.buques_off, "OFF")
            update_progress_callback(20)  # 20% después de procesar los tripulantes

            ### AEROLINEAS ###
            self.aerolineas_on, self.aerolineas_off = self.aerolineas_processor.aerolineas_main(file_path)
            update_progress_callback(30)  # 30% después de procesar aerolíneas
            # FALTA GUARDARLOS EN LA DB

            ### VUELOS ###
            self.vuelos_internacionales_on, self.vuelos_internacionales_off, self.vuelos_domesticos_on, self.vuelos_domesticos_off, self.vuelos_regionales_on, self.vuelos_regionales_off = self.vuelos_processor.vuelos_main(file_path)

            self.errors_vuelos_internacionales_on, self.errors_vuelos_internacionales_on_message = self.vuelos_processor._create_vuelos(file_path, self.vuelos_internacionales_on, self.tripulantes_on, 'ON', 'INTERNACIONAL')
            self.errors_vuelos_internacionales_off, self.errors_vuelos_internacionales_off_message = self.vuelos_processor._create_vuelos(file_path, self.vuelos_internacionales_off, self.tripulantes_off, 'OFF', 'INTERNACIONAL')
            update_progress_callback(40)
            self.errors_vuelos_domesticos_on, self.errors_vuelos_domesticos_on_message = self.vuelos_processor._create_vuelos(file_path, self.vuelos_domesticos_on, self.tripulantes_on, 'ON', 'DOMESTICO')
            self.errors_vuelos_domesticos_off, self.errors_vuelos_domesticos_off_message = self.vuelos_processor._create_vuelos(file_path, self.vuelos_domesticos_off, self.tripulantes_off, 'OFF', 'DOMESTICO')
            update_progress_callback(45)  # 50% después de procesar vuelos
            self.errors_vuelos_regionales_on, self.errors_vuelos_regionales_on_message = self.vuelos_processor._create_vuelos(file_path, self.vuelos_regionales_on, self.tripulantes_on, 'ON', 'REGIONAL')
            self.errors_vuelos_regionales_off, self.errors_vuelos_regionales_off_message = self.vuelos_processor._create_vuelos(file_path, self.vuelos_regionales_off, self.tripulantes_off, 'OFF', 'REGIONAL')            
            update_progress_callback(50)  # 50% después de procesar vuelos

            #print(self.vuelos_internacionales_on)

            ### ASISTENCIAS ###
            self.asistencias_on = self.asistencias_processor.asistencias_main(file_path)

            self.asistencias_processor._create_asistencias(self.tripulantes_on, self.asistencias_on)
            update_progress_callback(60)  # 60% después de procesar asistencias

            ### HOTELES ###
            self.hoteles_on, self.hoteles_off = self.hoteles_processor.hoteles_main(file_path)

            self.errors_hoteles_on, self.errors_hoteles_on_message = self.hoteles_processor._create_hotel(file_path, self.hoteles_on, self.tripulantes_on, "ON")
            update_progress_callback(65)
            self.errors_hoteles_off, self.errors_hoteles_off_message = self.hoteles_processor._create_hotel(file_path, self.hoteles_off, self.tripulantes_off, "OFF")
            update_progress_callback(70)  # 70% después de procesar hoteles

            ### TRANSPORTES ###
            self.transportes_on, self.transportes_off = self.transportes_processor.transportes_main(file_path)

            self.errors_transportes_on, self.errors_transportes_on_message = self.transportes_processor._create_transporte(file_path, self.transportes_on, self.tripulantes_on, "ON")
            update_progress_callback(75)
            self.errors_transportes_off, self.errors_transportes_off_message = self.transportes_processor._create_transporte(file_path, self.transportes_off, self.tripulantes_off, "OFF")
            update_progress_callback(80)  # 80% después de procesar transportes

            ### RESTAURANTES ###
            self.restaurantes_on, self.restaurantes_off = self.restaurantes_processor.restaurantes_main(file_path)
            
            self.restaurantes_processor._create_restaurantes(self.restaurantes_on, self.tripulantes_on)
            update_progress_callback(85)
            self.restaurantes_processor._create_restaurantes(self.restaurantes_off, self.tripulantes_off)
            update_progress_callback(90)  # 90% después de procesar restaurantes

            ### EXTRAS ###
            self.extras_on, self.extras_off = self.extras_processor.extras_main(file_path)
            
            ### FALTA GUARDARLOS EN LA DB
            update_progress_callback(95)  # 95% después de procesar extras

            ### VIAJES ###
            self.viaje_processor._create_viajes_from_dataframes(self.tripulantes_on, self.tripulantes_off, self.buques_on, self.buques_off)
            update_progress_callback(100)  # 100% después de procesar viajes

            ### ERRORES ###
            self.errors_on = []
            self.errors_off = []
            self.errors_on_message = []
            self.errors_off_message = []

            self.errors_on.extend(self.errors_buques_on)
            self.errors_off.extend(self.errors_buques_off)
            self.errors_on_message.extend(self.errors_buques_on_message)
            self.errors_off_message.extend(self.errors_buques_off_message)

            self.errors_on.extend(self.errors_tripulantes_on)
            self.errors_off.extend(self.errors_tripulantes_off)
            self.errors_on_message.extend(self.errors_tripulantes_on_message)
            self.errors_off_message.extend(self.errors_tripulantes_off_message)

            self.errors_on.extend(self.errors_vuelos_internacionales_on)
            self.errors_off.extend(self.errors_vuelos_internacionales_off)
            self.errors_on_message.extend(self.errors_vuelos_internacionales_on_message)
            self.errors_off_message.extend(self.errors_vuelos_internacionales_off_message)
            self.errors_on.extend(self.errors_vuelos_regionales_on)
            self.errors_off.extend(self.errors_vuelos_regionales_off)
            self.errors_on_message.extend(self.errors_vuelos_regionales_on_message)
            self.errors_off_message.extend(self.errors_vuelos_regionales_off_message)
            self.errors_on.extend(self.errors_vuelos_domesticos_on)
            self.errors_off.extend(self.errors_vuelos_domesticos_off)
            self.errors_on_message.extend(self.errors_vuelos_domesticos_on_message)
            self.errors_off_message.extend(self.errors_vuelos_domesticos_off_message)

            self.errors_on.extend(self.errors_hoteles_on)
            self.errors_off.extend(self.errors_hoteles_off)
            self.errors_on_message.extend(self.errors_hoteles_on_message)
            self.errors_off_message.extend(self.errors_hoteles_off_message)

            self.errors_on.extend(self.errors_transportes_on)
            self.errors_off.extend(self.errors_transportes_off)
            self.errors_on_message.extend(self.errors_transportes_on_message)
            self.errors_off_message.extend(self.errors_transportes_off_message)

            # self.errors_on_transportes = self.vuelos_processor.check_and_clean(self.vuelos_internacionales_on, file_path, "ON")
            # self.errors_off_transportes = self.vuelos_processor.check_and_clean(self.vuelos_internacionales_off, file_path, "OFF")

            #self.errors_on.extend(self.errors_on_buques)
            #self.errors_on.extend(self.errors_on_tripulantes)
            #self.errors_off.extend(self.errors_off_buques)
            #self.errors_off.extend(self.errors_off_tripulantes)

            #print(f"Errores en ON = {self.errors_on}")
            #print(f"Errores en OFF = {self.errors_off}")

            return self.buques_on, self.buques_off, self.tripulantes_on, self.tripulantes_off, self.errors_on, self.errors_off, self.errors_on_message, self.errors_off_message
        except Exception as e:
            raise Exception(f"[Controller] Error al procesar el archivo: {e}")