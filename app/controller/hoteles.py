from datetime import datetime, timedelta
import unicodedata
import calendar
import re
import pandas as pd
from sqlalchemy.orm import Session
import traceback
from datetime import time
from sqlalchemy import func, and_
from PyQt6.QtWidgets import QMessageBox
from app.models import Buque, Tripulante, Vuelo, EtaCiudad, Viaje, TripulanteVuelo, Hotel, TripulanteHotel, Restaurante, TripulanteRestaurante, Transporte, TripulanteTransporte, TripulanteAsistencia
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter, column_index_from_string

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

class Hoteles:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def hoteles_main(self, file_path):
        try:
            excel_data_on = pd.read_excel(file_path, sheet_name='ON', header=None)

            hoteles_on = self._extract_hotels(excel_data_on, start_row=0, state="on")
            hoteles_on.reset_index(drop=True, inplace=True)

            excel_data_off = pd.read_excel(file_path, sheet_name='OFF', header=None)

            hoteles_off = self._extract_hotels(excel_data_off, start_row=0, state="off")
            hoteles_off.reset_index(drop=True, inplace=True)

            #print(hoteles_off)

            return hoteles_on, hoteles_off
        except Exception as e:
            raise Exception(f"[Hoteles] Error al procesar el archivo: {e}")
        
    def _create_hotel(self, file_path, hotel_df, tripulantes_df, state):
        #print(f"Estoy creando hoteles de {state}")
        errors, errors_message = check_and_clean(file_path, hotel_df, state)

        try:
            if hotel_df.empty or tripulantes_df.empty:
                #print("No hay hoteles o tripulantes para procesar.")
                return

            # Extraer información de hoteles
            hoteles_info = self._extraer_hoteles_fechas(hotel_df)

            # Asignar hoteles a tripulantes
            for i, tripulante_data in tripulantes_df.iterrows():
                try:
                    # Validar si el pasaporte está vacío
                    if pd.isna(tripulante_data['Pasaporte']):
                        #print(f"Pasaporte vacío para el tripulante en la fila {i}. Omitiendo...")
                        continue

                    # Buscar el tripulante en la base de datos
                    tripulante = self.db_session.query(Tripulante).filter_by(pasaporte=tripulante_data['Pasaporte']).first()
                    if not tripulante:
                        #print(f"No se encontró tripulante con pasaporte {tripulante_data['Pasaporte']} en la fila {i}.")
                        continue

                    # Obtener la información de hoteles correspondiente al tripulante
                    hotel_entries = hoteles_info.iloc[i] if i < len(hoteles_info) else None
                    if hotel_entries is None:
                        #print(f"No se encontró información de hotel para el tripulante en la fila {i}.")
                        continue

                    valid_entries = [entry for entry in hotel_entries if entry.get('categoria') is not None]

                    if not valid_entries:  # Si no hay entradas válidas, continuar
                        continue

                    for hotel_info in hotel_entries:  # Iterar sobre todos los hoteles asignados al tripulante
                        #print(hotel_info)
                        # if pd.isna(hotel_info['hotel']) or pd.isna(hotel_info['categoria']) or str(hotel_info['hotel']).lower() == 'no':
                        #     #print(f"Hotel vacío o nulo en la fila {i}. Omitiendo...")
                        #     continue
                        if str(hotel_info['nombre_hotel']).lower() == 'no':
                            continue
                        if hotel_info is None or pd.isna(hotel_info['nombre_hotel']):
                            #print(f"Hotel vacío o nulo en la fila {i}. Omitiendo...")
                            continue

                        # Normalizar el nombre del hotel y la ciudad para la búsqueda
                        hotel_nombre_normalizado = self.clean_string(hotel_info['nombre_hotel'])
                        hotel_ciudad_normalizado = self.clean_string(hotel_info['ciudad'])

                        if hotel_ciudad_normalizado == "hotel":
                            #print(f"Hotel inválido detectado: {hotel_ciudad_normalizado}. Omitiendo...")
                            continue

                        # Verificar si el hotel ya existe en la base de datos
                        existing_hotel = self.db_session.query(Hotel).filter(
                            func.lower(Hotel.nombre) == hotel_nombre_normalizado,
                            func.lower(Hotel.ciudad) == hotel_ciudad_normalizado
                        ).first()

                        if not existing_hotel:
                            # Crear nuevo hotel si no existe
                            print(f"Creando nuevo hotel: {hotel_info['nombre_hotel']}, Ciudad: {hotel_info['ciudad']}")
                            hotel = Hotel(
                                nombre=hotel_info['nombre_hotel'].strip(),
                                ciudad=hotel_info['ciudad'].strip(),
                            )
                            self.db_session.add(hotel)
                            self.db_session.flush()  # Obtener el ID del hotel recién creado
                        else:
                            hotel = existing_hotel

                        # Verificar si ya existe la relación entre tripulante y hotel
                        #print(hotel_info['check_in'])
                        existing_tripulante_hotel = self.db_session.query(TripulanteHotel).filter(
                            TripulanteHotel.tripulante_id == tripulante.tripulante_id,
                            TripulanteHotel.hotel_id == hotel.hotel_id,
                            TripulanteHotel.fecha_entrada == hotel_info['check_in'],
                            TripulanteHotel.fecha_salida == hotel_info['check_out']
                        ).first()

                        if existing_tripulante_hotel:
                            #print(f"Ya existe una relación para Tripulante ID {tripulante.tripulante_id} con el Hotel ID {hotel.hotel_id}.")
                            continue  # Omitir creación de nueva relación si ya existe

                        if hotel_info['nombre_hotel'] != 'TBC':
                            x = i+2
                            if hotel_info['check_in'] == None:
                                #y = 37 + (5 * hotel_info['nro']) - 3
                                #letra_columna = self.indice_a_letra_columna(y)
                                #print(f"Se ha producido un error con el check in [{x}, {letra_columna}]")
                                continue
                            if hotel_info['check_out'] == None:
                                #y = 37 + (5 * hotel_info['nro']) - 2
                                #letra_columna = self.indice_a_letra_columna(y)
                                #print(f"Se ha producido un error con el check out [{x}, {letra_columna}]")
                                continue

                        # Crear nueva relación Tripulante-Hotel si no existe
                        #print(f"Creando relación Tripulante-Hotel: Tripulante ID {tripulante.tripulante_id}, Hotel ID {hotel.hotel_id}.")
                        nuevo_tripulante_hotel = TripulanteHotel(
                            tripulante_id=tripulante.tripulante_id,
                            hotel_id=hotel.hotel_id,
                            fecha_entrada=hotel_info['check_in'] if pd.notna(hotel_info['check_in']) else None,
                            fecha_salida=hotel_info['check_out'] if pd.notna(hotel_info['check_out']) else None,
                            tipo_habitacion=hotel_info['habitacion'] if pd.notna(hotel_info['habitacion']) else None,
                            numero_noches=int(hotel_info['numero_noches']) if pd.notna(hotel_info['numero_noches']) else 0,
                            categoria=int(hotel_info['categoria']) if pd.notna(hotel_info['categoria']) else 0,
                            day_room=False  # O ajusta según sea necesario
                        )
                        self.db_session.add(nuevo_tripulante_hotel)

                except Exception as row_error:
                    print(f"[Hotel] Error procesando fila {i}: {row_error}")
                    #print(f"Datos del tripulante en la fila: {tripulante_data.to_dict()}")
                    print(f"Datos de hotel en fila {i}: {hotel_info}")
                    #print(type(hotel_info['check_in']))
                    ###traceback.print_exc()
                    self.db_session.rollback()  # Revertir cambios parciales en la fila actual
                    continue  # Continuar con la siguiente fila

            # Confirmar los cambios en la base de datos
            self.db_session.commit()
            print("Asignación de hoteles completada.")
        except Exception as e:
            self.db_session.rollback()  # Revertir cualquier cambio parcial en caso de error general
            print(f"Error general al asignar hoteles: {e}")
            ###traceback.print_exc()
        
        return errors, errors_message

    def _extraer_hoteles_fechas(self, hotel_df):
        hoteles_info = []

        for _, row in hotel_df.iterrows():
            hotel_entries = []

            found_valid_hotel = False
            
            # Procesar cada hotel en la fila
            for hotel_key in row.index:
                hotel_info = row[hotel_key]

                if isinstance(hotel_info, dict):
                    if pd.isna(hotel_info.get('hotel')):
                        hotel = 'Desconocido'
                    else:
                        hotel = hotel_info.get('hotel')
                    
                    # check_in = pd.to_datetime(hotel_info.get('check_in'), errors='coerce')
                    # check_out = pd.to_datetime(hotel_info.get('check_out'), errors='coerce')

                    # Convertir NaT a None
                    #print(hotel_info.get('check_in'))
                    if not pd.isna(hotel_info.get('check_in')):
                        if isinstance(hotel_info.get('check_in'), datetime):
                            check_in = hotel_info.get('check_in')
                        else:
                            check_in = None
                    else: 
                        check_in = None
                    if not pd.isna(hotel_info.get('check_out')):
                        if isinstance(hotel_info.get('check_out'), datetime):
                            check_out = hotel_info.get('check_out')
                        else:
                            check_out = None
                        
                    else: 
                        check_out = None
                    #check_out = hotel_info.get('check_out') if hotel_info.get('check_out') else None

                    #print(check_in)
                    
                    # Crear un diccionario para la información del hotel
                    hotel_entry = {
                        'nombre_hotel': hotel_info.get('nombre_hotel'),
                        'categoria': hotel_info.get('categoria'),
                        'ciudad': hotel.split()[-1] if 'hotel' in hotel_info else 'Desconocida',
                        'check_in': check_in,
                        'check_out': check_out,
                        'numero_noches': (check_out - check_in).days if check_in and check_out else 0,
                        'habitacion': hotel_info.get('habitacion'),
                        'nro': hotel_info.get('nro')
                    }

                    # Agrega la entrada del hotel a la lista
                    hotel_entries.append(hotel_entry)
                    found_valid_hotel = True
            
            
            # Si se encontraron hoteles válidos, añade la lista de hoteles a la información del tripulante
            if found_valid_hotel:
                # Añadir el primer hotel encontrado como una entrada en el DataFrame
                hoteles_info.append(hotel_entries)
            else:
                # Si no se encontró ningún hotel, añade 'SIN HOTEL'
                hoteles_info.append([{
                    'nombre_hotel': 'SIN HOTEL',
                    'categoria': None,
                    'ciudad': 'Desconocida',
                    'check_in': None,
                    'check_out': None,
                    'numero_noches': 0,
                    'habitacion': None
                }])

        # Expande la lista de hoteles en el DataFrame
        hoteles_df = pd.DataFrame(hoteles_info)
        # Mantiene el índice del DataFrame original
        hoteles_df.index = hotel_df.index

        return hoteles_df

    def _extract_hotels(self, excel_data, start_row, state):
        hotels = []  # Lista para almacenar la información de los hoteles
        
        # Convertir los nombres de las columnas a cadenas y quitar espacios
        hotels_columns = excel_data.loc[start_row].dropna().str.lower().tolist()
        #print(hotels_columns)

        # Iterar sobre cada fila, comenzando desde la fila indicada
        for i in range(start_row + 1, excel_data.shape[0]):
            tripulante_hotels = {}  # Diccionario para almacenar información del tripulante
            hotel_num = 1  # Contador de hoteles
            
            # Variable para verificar si se encontraron hoteles
            found_hotels = False
            
            # Iterar sobre las columnas de hoteles hasta que ya no existan
            while True:
                # Crear los nombres de las columnas esperadas
                category = 'category'
                hotel_col = f'hotel {hotel_num}'
                check_in_col = f'check in {hotel_num}'
                check_out_col = f'check out {hotel_num}'
                rooms = f'rooms {hotel_num}'
                hotel_name = f'nombre hotel {hotel_num}'

                # Verificar si las columnas existen en el DataFrame
                if (category in hotels_columns and hotel_col in hotels_columns and 
                    check_in_col in hotels_columns and check_out_col in hotels_columns and 
                    rooms in hotels_columns and hotel_name in hotels_columns):    
                    
                    col_idx_category = hotels_columns.index(category)
                    col_idx_hotel = hotels_columns.index(hotel_col)
                    col_idx_check_in = hotels_columns.index(check_in_col)
                    col_idx_check_out = hotels_columns.index(check_out_col)
                    col_idx_rooms = hotels_columns.index(rooms)
                    col_idx_hotel_name = hotels_columns.index(hotel_name)

                    # Obtener información del hotel
                    categoria = excel_data.iloc[i, col_idx_category]
                    hotel = excel_data.iloc[i, col_idx_hotel]
                    check_in = excel_data.iloc[i, col_idx_check_in]
                    check_out = excel_data.iloc[i, col_idx_check_out]
                    habitacion = excel_data.iloc[i, col_idx_rooms]
                    nombre_hotel = excel_data.iloc[i, col_idx_hotel_name]

                    #print(check_out)

                    # Si hay información válida en las columnas, agregarla
                    #if pd.notna(categoria) and pd.notna(hotel):
                    tripulante_hotels[f'Hotel {hotel_num}'] = {
                        "categoria": categoria if categoria else None,
                        "hotel": hotel if hotel else None,
                        #"check_in": pd.to_datetime(check_in, errors='coerce') if check_in else None,
                        "check_in": check_in if check_in else None,
                        "check_out": pd.to_datetime(check_out, errors='coerce') if check_out else None,
                        "habitacion": habitacion if habitacion else None,
                        "nombre_hotel": nombre_hotel if nombre_hotel else None,
                        "nro": hotel_num if hotel_num else None
                    }
                    found_hotels = True  # Se encontró al menos un hotel

                    # Incrementar el número de hotel para buscar el siguiente conjunto
                    hotel_num += 1
                else:
                    break  # Detener la búsqueda si no se encuentra una de las columnas

            # Si no se encontraron hoteles, agregar un registro para ese tripulante
            # if not found_hotels:
            #     tripulante_hotels[f'Hotel {hotel_num}'] = {
            #         "categoria": None,
            #         "hotel": "SIN HOTEL",
            #         "check_in": None,
            #         "check_out": None,
            #         "habitacion": None,
            #         "nombre_hotel": "SIN HOTEL",
            #         "nro": None
            #     }

            # Agregar la información del tripulante a la lista de hoteles
            hotels.append(tripulante_hotels)

        # Verificar si se encontraron hoteles
        if len(hotels) == 0:
            print("No se encontraron hoteles en las filas procesadas.")
        else:
            print(f"{len(hotels)} hoteles procesados. ({state})")
            
        return pd.DataFrame(hotels)  # Retornar el DataFrame con la información de hoteles
    
    def indice_a_letra_columna(self, index):
        """Convierte un índice numérico a la letra de columna en Excel."""
        letras = ''
        while index > 0:
            index, remainder = divmod(index - 1, 26)
            letras = chr(65 + remainder) + letras  # A=65 en ASCII
        return letras
    
    def clean_string(self, value):
        return value.strip().replace('\u200b', '').lower() if isinstance(value, str) else value
    
def check_and_clean(file_path, hoteles_df, state):
    errors_to_check = []
    errors = []
    errors_message = []

    #print(f"El dict de {state} es {hoteles_df}")

    def clean_value(value):
        if isinstance(value, str):  # Verificar si es una cadena
            return value.strip().replace('/', '-')  # Eliminar espacios en blanco
        return value  # Dejar el valor tal como está si no es cadena
    
    def is_valid_date(date_str):
        formats = ['%d-%m-%y', '%d-%m-%Y']  # Lista de formatos posibles
        for date_format in formats:
            try:
                date = pd.to_datetime(date_str, format=date_format, errors='raise')
                day, month, year = date.day, date.month, date.year
                last_day_of_month = calendar.monthrange(year, month)[1]
                if day <= last_day_of_month:
                    return True
            except Exception:
                continue  # Intentar con el siguiente formato
        #print(f"Fecha no válida: {date_str}")
        return False
    
    def looks_like_date(value):
        if isinstance(value, str):
            # Usa una expresión regular para filtrar fechas con el formato esperado
            return re.match(r'^\d{2}-\d{2}-\d{2,4}$', value) is not None
        return False
    
    def get_excel_column_letter(file_path, sheet_name, column_name):
            # Cargar el archivo y la hoja
            workbook = load_workbook(file_path)
            sheet = workbook[sheet_name]
            
            # Buscar la columna por nombre (suponiendo que los nombres están en la primera fila)
            for col in sheet.iter_cols(1, sheet.max_column, 1, 1):  # Iterar solo en la primera fila
                if col[0].value == column_name:
                    # Devolver la letra de la columna
                    return get_column_letter(col[0].column)
            
            raise ValueError(f"Columna con nombre '{column_name}' no encontrada en el archivo.")
    
    def get_column(df, columna, column):
        sheet_name = state
        indices = {key: idx for idx, key in enumerate(df.keys())}
        x = indices[columna]
        y = get_excel_column_letter(file_path, sheet_name, f"{column} {x+1}")
        return y
    
    def get_cell_value(file_path, sheet_name, row, column):
        # Cargar el archivo de Excel
        workbook = load_workbook(file_path, data_only=True)  # `data_only=True` para obtener el valor calculado en celdas con fórmulas
        sheet = workbook[sheet_name]

        # Obtener el valor de la celda
        cell_value = sheet.cell(row=row, column=column).value

        return cell_value
    
    def check_date(df, registro, idx, columna, column, x):
        #print(registro.get(f'{column}'))
        #print(registro)
        if isinstance(registro.get(f'{column}'), str):
            if looks_like_date(registro.get(f'{column}')):
                value = registro.get(f'{column}')
                value = clean_value(value)

                if not is_valid_date(value):
                    ##print(f"NE 1 {state} | Registro {idx+2} en '{columna}': Vuelo es {value}")
                    column_letter = get_column(df, columna, x)
                    return column_letter
                else:
                    #print("Fecha válida")
                    return True
        else:
            #print(f"{idx} | {registro.get('Date Pickup')}")
            value = registro.get(f'{column}')
            value = clean_value(value)
            
            if registro.get(f'{column}') == None or pd.isna(registro.get(f'{column}')):
                if str(registro.get('vuelo')).lower() != 'no' and not pd.isna(registro.get('vuelo')):
                    ##print(f"ER {state} | Registro {idx+2} en '{columna}': Vuelo es {registro.get('vuelo')}")
                    column_letter = get_column(df, columna, x)
                    return column_letter

                #print(f"{type(registro.get('vuelo'))} | {registro.get('vuelo')}")
                #print(f"ER | Registro {idx+2} en '{columna}': Vuelo es {registro.get('fecha')}")
                ##print(f"ER {state} | Registro {idx+2} en '{columna}': Vuelo está vacío")
                column_letter = get_column(df, columna, x)
                return column_letter
            else:
                if not is_valid_date(value):
                    ##print(f"NE 2 {state} | Registro {idx+2} en '{columna}': Vuelo es {registro.get(f'{column}')}")
                    column_letter = get_column(df, columna, x)
                    return column_letter
                else:
                    ##print("Fecha válida")
                    return True
                
    def normalize_string(s):
        return unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode('utf-8').lower()

    def check_column():
        df = pd.DataFrame(hoteles_df)
        #print(df)
        for columna in hoteles_df:
            #print(f"Columna: {columna} | {state} | {tipo}")
            hotel = df[columna].tolist()  # Convertir la columna en una lista
            for idx, registro in enumerate(hotel):  # Iterar sobre los diccionarios
                #print(registro)
                skip = False
                if not pd.isna(registro.get('categoria')):
                    #print(f"{idx} {state} | {columna} | Categoria es {str(registro.get('categoria'))}")

                    if str(registro.get('hotel')).lower() == 'no':
                        #print(f"{idx} skipeado | {columna}  {registro.get('hotel')}")
                        continue
                    else:
                        if pd.isna(registro.get('hotel')):
                            sheet_name = state
                            column_letter = get_column(df, columna, 'Hotel')
                            column_number = column_index_from_string(column_letter)
                            cell_value = get_cell_value(file_path, sheet_name, 1, column_number)
                            errors_to_check.append([idx+2, columna])
                            errors.append([idx+2, column_letter])
                            errors_message.append(f"Dato faltante en {cell_value} [{idx+2},{column_letter}]")
                            print(f"{idx+2},{column_letter} {state} {columna} | Error hotel vacío")         
                            continue
                        else:
                            if isinstance(registro.get('hotel'), str):  # Asegurarse de que sea una cadena antes de dividir
                                hotel = registro.get('hotel')
                                if hotel.lower() not in ('no', 'tbc'):
                                    hotel_parts = hotel.split()
                                    if len(hotel_parts) < 2:
                                        sheet_name = state
                                        column_letter = get_column(df, columna, 'Hotel')
                                        column_number = column_index_from_string(column_letter)
                                        cell_value = get_cell_value(file_path, sheet_name, 1, column_number)
                                        errors_to_check.append([idx, columna])
                                        errors.append([idx, column_letter])
                                        errors_message.append(f"Formato incorrecto  en {cell_value} [{idx+2},{column_letter}]")
                                        print(f"{idx+2},{column_letter} | Formato incorrecto en el nombre del hotel: '{hotel}'")
                                    else:
                                        if hotel_parts[1].upper() in CITY_AIRPORT_CODES:
                                            if normalize_string(hotel_parts[0]) not in ['hotel', 'autogestion']:
                                                sheet_name = state
                                                column_letter = get_column(df, columna, 'Hotel')
                                                column_number = column_index_from_string(column_letter)
                                                cell_value = get_cell_value(file_path, sheet_name, 1, column_number)
                                                errors_to_check.append([idx, columna])
                                                errors.append([idx, column_letter])   
                                                errors_message.append(f"Debe comenzar con 'hotel' o 'autogestión' en {cell_value} [{idx+2},{column_letter}]")
                                                print(f"{idx+2},{column_letter} | La primera palabra debe ser 'hotel' o 'autogestión': '{hotel}'")     
                                        else:
                                            sheet_name = state
                                            column_letter = get_column(df, columna, 'Hotel')
                                            column_number = column_index_from_string(column_letter)
                                            cell_value = get_cell_value(file_path, sheet_name, 1, column_number)
                                            errors_to_check.append([idx, columna])
                                            errors.append([idx, column_letter])
                                            errors_message.append(f"Ciudad no válida en {cell_value} [{idx+2},{column_letter}]")
                                            print(f"{idx+2},{column_letter} | La segunda palabra debe ser una ciudad válida '{hotel}'")
                                else:
                                    if hotel.lower() in ('no', 'tbc'):
                                        continue
                                    print(f"{idx+2},{column_letter} | El valor de 'hotel' debe ser una cadena, pero se recibió: {type(hotel).__name__}")

                            if pd.isna(registro.get('check_in')):
                                sheet_name = state
                                column_letter = get_column(df, columna, 'Check in')
                                column_number = column_index_from_string(column_letter)
                                cell_value = get_cell_value(file_path, sheet_name, 1, column_number)
                                errors_to_check.append([idx+2, columna])
                                errors.append([idx+2, column_letter])
                                skip = True
                                errors_message.append(f"Check in faltante en {cell_value} [{idx+2},{column_letter}]")
                                print(f"{idx+2},{column_letter} {state} {columna} | Error check in vacío")
                            else:
                                sheet_name = state
                                column_letter = check_date(df, registro, idx, columna, 'check_in', 'Check in')
                                if column_letter != True:
                                    column_number = column_index_from_string(column_letter)
                                    cell_value = get_cell_value(file_path, sheet_name, 1, column_number)
                                    errors_to_check.append([idx+2, columna])
                                    errors.append([idx+2, column_letter])
                                    errors_message.append(f"Formato de check in no válido en {columna} [{idx+2},{column_letter}]")
                                    print(f"{idx+2},{column_letter} {state} {columna} | Error en formato de check in")

                            if pd.isna(registro.get('check_out')):
                                sheet_name = state
                                column_letter = get_column(df, columna, 'Check out')
                                column_number = column_index_from_string(column_letter)
                                cell_value = get_cell_value(file_path, sheet_name, 1, column_number)
                                errors_to_check.append([idx+2, columna])
                                errors.append([idx+2, column_letter])
                                errors_message.append(f"Check out faltante en {cell_value} [{idx+2},{column_letter}]")
                                skip = True
                                print(f"{idx+2},{column_letter} {state} {columna} | Error check out vacío")
                            else:
                                sheet_name = state
                                column_letter = check_date(df, registro, idx, columna, 'check_out', 'Check out')
                                if column_letter != True:
                                    column_number = column_index_from_string(column_letter)
                                    cell_value = get_cell_value(file_path, sheet_name, 1, column_number)
                                    errors_to_check.append([idx+2, columna])
                                    errors.append([idx+2, column_letter])
                                    errors_message.append(f"Formato de check out no válido en {cell_value} [{idx+2},{column_letter}]")
                                    print(f"{idx+2},{column_letter} {state} {columna} | Error en formato de check out")

                            if not pd.isna(registro.get('habitacion')):
                                room = registro.get('habitacion')
                                if room.lower() not in ('no', 'tbc'):
                                    room_parts = room.split()
                                    if len(room_parts) > 2:
                                        sheet_name = state
                                        column_letter = get_column(df, columna, 'Rooms')
                                        column_number = column_index_from_string(column_letter)
                                        cell_value = get_cell_value(file_path, sheet_name, 1, column_number)
                                        errors_to_check.append([idx, columna])
                                        errors.append([idx, column_letter])
                                        errors_message.append(f"Formato incorrecto en {cell_value} [{idx+2},{column_letter}]")
                                        print(f"{idx+2},{column_letter} | Formato incorrecto en el nombre del room: '{room}'")
                                    else:
                                        # Verificar que la primera palabra sea 'room' o 'autogestión'
                                        if normalize_string(room_parts[0]) not in ['single', 'doble']:
                                            sheet_name = state
                                            column_letter = get_column(df, columna, 'Rooms')
                                            column_number = column_index_from_string(column_letter)
                                            cell_value = get_cell_value(file_path, sheet_name, 1, column_number)
                                            errors_to_check.append([idx, columna])
                                            errors.append([idx, column_letter])
                                            errors_message.append(f"Debe comenzar con 'single' o 'doble' en {cell_value} [{idx+2},{column_letter}]")
                                            print(f"{idx+2},{column_letter} | La primera palabra debe ser 'single' o 'doble': '{room}'")
                            else:
                                sheet_name = state
                                column_letter = get_column(df, columna, 'Rooms')
                                column_number = column_index_from_string(column_letter)
                                cell_value = get_cell_value(file_path, sheet_name, 1, column_number)
                                errors_to_check.append([idx, columna])
                                errors.append([idx, column_letter])
                                errors_message.append(f"Room faltante en {cell_value} [{idx+2},{column_letter}]")
                                print(f"{idx+2},{column_letter} {columna} {state} | El valor de 'room' está vacío")

                            if pd.isna(registro.get('nombre_hotel')):
                                sheet_name = state
                                column_letter = get_column(df, columna, 'Nombre Hotel')
                                column_number = column_index_from_string(column_letter)
                                cell_value = get_cell_value(file_path, sheet_name, 1, column_number)
                                errors_to_check.append([idx, columna])
                                errors.append([idx, column_letter])
                                errors_message.append(f"Nombre de hotel faltante en {cell_value} [{idx+2},{column_letter}]")
                                print(f"{idx+2},{column_letter} {columna} {state} | El valor de 'nombre_hotel' está vacío")

                            if skip:
                                continue

                else:
                    #print(f"Error en {registro}") ### MENSAJE DE ERROR PARA CUANDO NO TIENE LA CATEGORIA
                    sheet_name = state
                    column_letter = get_column(df, columna, 'Categoria')
                    column_number = column_index_from_string(column_letter)
                    cell_value = get_cell_value(file_path, sheet_name, 1, column_number)
                    errors_to_check.append([idx, columna])
                    errors.append([idx, column_letter])
                    errors_message.append(f"Falta la categoría en {cell_value} [{idx+2},{column_letter}]")
                    print(f"{idx+2},{column_letter} {state} {columna} | Error falta categoría") ### MENSAJE DE ERROR PARA CUANDO NO TIENE LA CATEGORIA
                    continue

    check_column()
    return errors, errors_message