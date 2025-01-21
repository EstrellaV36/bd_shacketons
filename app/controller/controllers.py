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
import pandas as pd

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
            self.asistencias_on, self.asistencias_off = self.asistencias_processor.asistencias_main(file_path)
            # Procesa las asistencias para ambos conjuntos de datos
            self.asistencias_processor.procesar_asistencias(self.tripulantes_on, self.asistencias_on, self.tripulantes_off, self.asistencias_off)

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
            self.extras_processor._create_extra(file_path, self.tripulantes_on, "ON")
            self.extras_processor._create_extra(file_path, self.tripulantes_off, "OFF")
            
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


            # Combinar todos los datos en un solo DataFrame para ON y OFF
            full_data_on = pd.concat(
                [
                    self.buques_on,
                    self.tripulantes_on,
                    self.aerolineas_on,
                    self.vuelos_internacionales_on.add_suffix("_Internacional"),
                    self.vuelos_domesticos_on.add_suffix("_Domestico"),
                    self.vuelos_regionales_on.add_suffix("_Regional"),
                    self.asistencias_on,
                    self.hoteles_on,
                    self.transportes_on,
                    self.restaurantes_on,
                    #self.extras_on,
                ],
                axis=1,
            )

            full_data_off = pd.concat(
                [
                    self.buques_off,
                    self.tripulantes_off,
                    self.aerolineas_off,
                    self.vuelos_internacionales_off.add_suffix("_Internacional"),
                    self.vuelos_domesticos_off.add_suffix("_Domestico"),
                    self.vuelos_regionales_off.add_suffix("_Regional"),
                    self.asistencias_off,
                    self.hoteles_off,
                    self.transportes_off,
                    self.restaurantes_off,
                    #self.extras_off,
                ],
                axis=1,
            )
            
            full_data_on, full_data_off = self.process_all_to_show(full_data_on, full_data_off)

            return full_data_on, full_data_off, self.errors_on, self.errors_off, self.errors_on_message, self.errors_off_message
        except Exception as e:
            raise Exception(f"[Controller] Error al procesar el archivo: {e}")
        
    def process_all_to_show(self, df_on, df_off):
        # Limpiar los nombres de las columnas en df_on
        df_on.columns = df_on.columns.str.strip()

        ###PROCESAMIENTO DE VUELOS ON#####
        # Procesar vuelos internacionales
        vuelo_international_columns = [col for col in df_on.columns if col.startswith('Vuelo') and '_Domestico' not in col and '_Regional' not in col]
        self._process_vuelos(df_on, vuelo_international_columns, "Vuelo Int", "Nro International Flight", "Date International Flight", "Hora International Flight")

        # Procesar vuelos domésticos
        vuelo_domestic_columns = [col for col in df_on.columns if '_Domestico' in col]
        self._process_single_flight(df_on, vuelo_domestic_columns, "Nro Domestic Flight", "Date Domestic Flight", "Hora Domestic Flight")

        # Procesar vuelos regionales
        vuelo_regional_columns = [col for col in df_on.columns if '_Regional' in col]
        self._process_single_flight(df_on, vuelo_regional_columns, "Nro Regional Flight", "Date Regional Flight", "Hora Regional Flight")

        #Procesamiento hoteles ON
        df_on = self.process_hotels(df_on)

        # Limpiar los nombres de las columnas en df_off
        df_off.columns = df_off.columns.str.strip()
        # print("Columnas originales del DataFrame (OFF):")
        # print(df_off.columns.tolist())
        
        ### PROCESAMIENTO DE VUELOS OFF #####
        # Procesar vuelos regionales (salida de Chile)
        vuelo_regional_columns_off = [col for col in df_off.columns if '_Regional' in col]
        self._process_single_flight(df_off, vuelo_regional_columns_off, "Nro Regional Flight", "Date Regional Flight", "Hora Regional Flight")
   
        # Procesar vuelos domésticos (salida de Chile)
        vuelo_domestic_columns_off = [col for col in df_off.columns if '_Domestico' in col]
        self._process_single_flight(df_off, vuelo_domestic_columns_off, "Nro Domestic Flight", "Date Domestic Flight", "Hora Domestic Flight")

        # Procesar vuelos internacionales (salida de Chile)
        vuelo_international_columns_off = [col for col in df_off.columns if col.startswith('Vuelo') and '_Domestico' not in col and '_Regional' not in col]
        self._process_single_flight(df_off, vuelo_international_columns_off, "Nro International Flight", "Date International Flight", "Hora International Flight")

        # Reordenar las columnas para asegurar que el orden sea consistente
        self._reorder_columns_off(df_off)
        
        return df_on, df_off

    def _process_vuelos(self, df, vuelo_columns, vuelo_prefix, nro_flight_col, date_flight_col, hora_flight_col):
        for vuelo_col in vuelo_columns:
            try:
                # Descomponer la columna en un DataFrame con subcolumnas
                vuelo_df = df[vuelo_col].apply(
                    lambda x: pd.Series(x) if isinstance(x, dict) else pd.Series({"vuelo": None, "fecha": None, "hora": None})
                )
                # Formatear las fechas para que estén sin hora
                vuelo_df['fecha'] = pd.to_datetime(vuelo_df['fecha'], errors='coerce').dt.date

                # Crear nombres de columnas
                vuelo_number = vuelo_columns.index(vuelo_col) + 1  # Usar índice para nombrar los vuelos correctamente
                vuelo_df.columns = [
                    f"{vuelo_prefix} {vuelo_number}",
                    f"Fecha {vuelo_prefix} {vuelo_number}",
                    f"Hora {vuelo_prefix} {vuelo_number}",
                ]

                # Insertar las nuevas columnas en la posición correcta
                col_index = df.columns.get_loc(vuelo_col)
                for i, new_col in enumerate(vuelo_df.columns):
                    df.insert(col_index + i + 1, new_col, vuelo_df[new_col])

                # Eliminar la columna original
                df.drop(columns=[vuelo_col], inplace=True)
            except Exception as e:
                print(f"Error al procesar '{vuelo_col}': {e}")

        # Procesar el último vuelo no vacío
        nro_flight = []
        date_flight = []
        hora_flight = []

        for _, row in df.iterrows():
            last_flight = None
            last_flight_date = None
            last_flight_time = None

            # Iterar sobre los vuelos disponibles
            for i in range(1, len(vuelo_columns) + 1):
                vuelo_col = f"{vuelo_prefix} {i}"
                fecha_col = f"Fecha {vuelo_prefix} {i}"
                hora_col = f"Hora {vuelo_prefix} {i}"

                # Verificar si la columna actual no está vacía
                if pd.notna(row.get(vuelo_col)):
                    last_flight = row[vuelo_col]
                    last_flight_date = row[fecha_col]
                    last_flight_time = row[hora_col]

            # Almacenar el último vuelo no vacío
            nro_flight.append(last_flight)
            date_flight.append(last_flight_date)
            hora_flight.append(last_flight_time)

        # Insertar las nuevas columnas inmediatamente después de los vuelos procesados
        try:
            last_vuelo_col = f"Hora {vuelo_prefix} {len(vuelo_columns)}"
            insert_position = df.columns.get_loc(last_vuelo_col) + 1
            df.insert(insert_position, nro_flight_col, nro_flight)
            df.insert(insert_position + 1, date_flight_col, date_flight)
            df.insert(insert_position + 2, hora_flight_col, hora_flight)
        except Exception as e:
            print(f"Error al insertar las columnas de último vuelo ({vuelo_prefix}): {e}")


    def _process_single_flight(self, df, vuelo_columns, nro_flight_col, date_flight_col, hora_flight_col):
        # Asumimos que solo hay un vuelo por procesar y sus columnas están en `vuelo_columns`
        if not vuelo_columns:
            print(f"No se encontraron columnas para {nro_flight_col}.")
            return

        # Extraer la única columna de vuelo (asumimos que hay solo una)
        vuelo_col = vuelo_columns[0]

        try:
            # Dividir la columna en subcolumnas
            vuelo_df = df[vuelo_col].apply(
                lambda x: pd.Series(x) if isinstance(x, dict) else pd.Series({"vuelo": None, "fecha": None, "hora": None})
            )
            # Formatear las fechas para que estén sin hora
            vuelo_df['fecha'] = pd.to_datetime(vuelo_df['fecha'], errors='coerce').dt.date
            vuelo_df.columns = [nro_flight_col, date_flight_col, hora_flight_col]

            # Insertar las nuevas columnas en el lugar correcto
            col_index = df.columns.get_loc(vuelo_col)
            for i, new_col in enumerate(vuelo_df.columns):
                df.insert(col_index + i + 1, new_col, vuelo_df[new_col])

            # Eliminar la columna original
            df.drop(columns=[vuelo_col], inplace=True)

            # Reemplazar valores "No disponible" con valores vacíos
            df[[nro_flight_col, date_flight_col, hora_flight_col]] = df[[nro_flight_col, date_flight_col, hora_flight_col]].replace("No disponible", None)
        except Exception as e:
            print(f"Error al procesar '{vuelo_col}': {e}")

    def _reorder_columns_off(self, df):
        # Definir el orden esperado de todas las columnas
        column_order = [
            "Activo", "Owner", "Vessel", "Date First Flight", "ETA Vessel", "ETD Vessel", "Puerto a desembarcar",
            "Condition", "Carta Desembarco", "Mail PDI", "First name", "Last name", "Gender", "Nacionalidad", 
            "Position", "Pasaporte", "DOB", "Aerolinea 1", "Aerolinea 2", "Aerolinea 3", "Aerolinea 4",
            "Nro Regional Flight", "Date Regional Flight", "Hora Regional Flight",
            "Nro Domestic Flight", "Date Domestic Flight", "Hora Domestic Flight",
            "Nro International Flight", "Date International Flight", "Hora International Flight",
            "Proveedor SCL", "Asistencia 1", "Proveedor PUQ", "Asistencia 2", "Proveedor WPU", "Asistencia 3",
        ]

        # Reordenar las columnas del DataFrame según el orden definido
        existing_columns = [col for col in column_order if col in df.columns]  # Filtrar solo las columnas que existen en el DataFrame
        remaining_columns = [col for col in df.columns if col not in column_order]  # Columnas que no están en el orden definido

        # Reordenar las columnas y mantener las adicionales al final
        df = df[existing_columns + remaining_columns]
        return df

    def process_hotels(self, df):
        # Detectar columnas de hoteles 
        # #FUNCION EN PROCESO AUN NO FUNCIONA BIEN
        hotel_columns = [col for col in df.columns if col.startswith('Hotel')]

        category = None  # Variable para almacenar la categoría (se mostrará una sola vez)

        for hotel_col in hotel_columns:
            try:
                if hotel_col not in df.columns:
                    print(f"Error: La columna '{hotel_col}' no existe en el DataFrame.")
                    continue

                # Descomponer la columna en subcolumnas
                hotel_df = df[hotel_col].apply(
                    lambda x: pd.Series({
                        "categoria": x.get("categoria") if isinstance(x, dict) else None,
                        "hotel": x.get("hotel") if isinstance(x, dict) else None,
                        "check_in": pd.to_datetime(x.get("check_in"), errors='coerce').date() if isinstance(x, dict) else None,
                        "check_out": pd.to_datetime(x.get("check_out"), errors='coerce').date() if isinstance(x, dict) else None,
                        "habitacion": x.get("habitacion") if isinstance(x, dict) else None,
                        "nombre_hotel": x.get("nombre_hotel") if isinstance(x, dict) else None,
                    }) if isinstance(x, dict) else pd.Series({
                        "categoria": None, "hotel": None, "check_in": None,
                        "check_out": None, "habitacion": None, "nombre_hotel": None
                    })
                )

                # Extraer y almacenar la categoría una vez
                if category is None and "categoria" in hotel_df:
                    category = hotel_df['categoria']
                    if "Category" in df.columns:
                        df.drop(columns=["Category"], inplace=True)  # Eliminar columna previa si existe
                    df.insert(0, "Category", category)  # Insertar la categoría al inicio del DataFrame

                # Renombrar las subcolumnas (sin incluir "categoria")
                hotel_number = hotel_columns.index(hotel_col) + 1
                hotel_df = hotel_df.drop(columns=["categoria"], errors='ignore')  # Eliminar columna innecesaria
                hotel_df.columns = [
                    f"Hotel {hotel_number}",
                    f"Check in {hotel_number}",
                    f"Check out {hotel_number}",
                    f"Rooms {hotel_number}",
                    f"Nombre Hotel {hotel_number}",
                ]

                # Asegurarnos de eliminar columnas existentes con el mismo nombre
                for col in hotel_df.columns:
                    if col in df.columns:
                        df.drop(columns=[col], inplace=True)

                # Insertar las nuevas columnas en el lugar correcto
                col_index = df.columns.get_loc(hotel_col)
                for i, new_col in enumerate(hotel_df.columns):
                    df.insert(col_index + i + 1, new_col, hotel_df[new_col])

                # Eliminar la columna original
                df.drop(columns=[hotel_col], inplace=True)
            except Exception as e:
                print(f"Error al procesar '{hotel_col}': {e}")
                continue

        return df