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
from app.controller.constants import CITY_AIRPORT_CODES, CITY_TO_AIRPORT_CODES
import ast

class Hoteles:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def hoteles_main(self, file_path):
        try:
            excel_data_on = pd.read_excel(file_path, sheet_name='ON', header=None)

            hoteles_on = self._extract_hotels(file_path, excel_data_on, start_row=0, state="on")
            hoteles_on.reset_index(drop=True, inplace=True)
            
            # print(f"Los hoteles de on son = {hoteles_on}")

            excel_data_off = pd.read_excel(file_path, sheet_name='OFF', header=None)

            hoteles_off = self._extract_hotels(file_path, excel_data_off, start_row=0, state="off")
            hoteles_off.reset_index(drop=True, inplace=True)

            #print(hoteles_off)

            return hoteles_on, hoteles_off
        except Exception as e:
            raise Exception(f"[Hoteles] Error al procesar el archivo: {e}")
        
    def _create_hotel(self, file_path, hotel_df, tripulantes_df, state):
        #print(f"Estoy creando hoteles de {state}")
        # print(f"Hoteles de ({state}) = {hotel_df}")
        errors, errors_message = check_and_clean(file_path, hotel_df, state)
        # print(f"Entre a create (1) {state}")

        try:
            if hotel_df.empty or tripulantes_df.empty:
                # print("No hay hoteles o tripulantes para procesar.")
                return [], []

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
                    # if pd.isna(hotel_entries.loc[i]['categoria']):
                    #     # print(f"Hotel_entries es = {hotel_entries.loc[i]['categoria']}")
                    #     continue

                    if hotel_entries is None:
                        #print(f"No se encontró información de hotel para el tripulante en la fila {i}.")
                        continue

                    valid_entries = [entry for entry in hotel_entries if isinstance(entry, dict) and entry.get('categoria') is not None]

                    if not valid_entries:  # Si no hay entradas válidas, continuar
                        continue

                    for hotel_info in hotel_entries:  # Iterar sobre todos los hoteles asignados al tripulante
                        if hotel_info is None:
                            continue  # Evita el error si hotel_info es None

                        nombre_hotel = hotel_info.get('nombre_hotel')
                        if pd.isna(nombre_hotel) or str(nombre_hotel).strip().lower() == 'no':
                            print(f"El nombre de hotel es {nombre_hotel}")
                            continue

                        # Normalizar el nombre del hotel y la ciudad para la búsqueda
                        hotel_nombre_normalizado = self.clean_string(nombre_hotel)
                        hotel_ciudad_normalizado = self.clean_string(hotel_info.get('ciudad'))

                        if hotel_ciudad_normalizado == "hotel":
                            continue

                        # Verificar si el hotel ya existe en la base de datos
                        existing_hotel = self.db_session.query(Hotel).filter(
                            func.lower(Hotel.nombre) == hotel_nombre_normalizado,
                            func.lower(Hotel.ciudad) == hotel_ciudad_normalizado
                        ).first()

                        if hotel_ciudad_normalizado != "no":
                            if not existing_hotel:
                                if hotel_nombre_normalizado == "tbc" or hotel_ciudad_normalizado is None:
                                    continue  # Omitir creación

                                print(f"Creando nuevo hotel: {nombre_hotel}, Ciudad: {hotel_info.get('ciudad')}")
                                hotel = Hotel(
                                    nombre=nombre_hotel.strip(),
                                    ciudad=str(hotel_ciudad_normalizado).upper()
                                )
                                self.db_session.add(hotel)
                                self.db_session.flush()
                            else:
                                hotel = existing_hotel

                        existing_tripulante_hotel = self.db_session.query(TripulanteHotel).filter(
                            TripulanteHotel.tripulante_id == tripulante.tripulante_id,
                            TripulanteHotel.hotel_id == hotel.hotel_id,
                            TripulanteHotel.fecha_entrada == hotel_info.get('check_in'),
                            TripulanteHotel.fecha_salida == hotel_info.get('check_out')
                        ).first()

                        if existing_tripulante_hotel:
                            continue  # Relación ya existe

                        if hotel_info.get('nombre_hotel') != 'TBC':
                            if hotel_info.get('check_in') is None or hotel_info.get('check_out') is None:
                                continue  # Evitar crear relación sin fechas válidas

                        nuevo_tripulante_hotel = TripulanteHotel(
                            tripulante_id=tripulante.tripulante_id,
                            hotel_id=hotel.hotel_id,
                            fecha_entrada=hotel_info.get('check_in') if pd.notna(hotel_info.get('check_in')) else None,
                            fecha_salida=hotel_info.get('check_out') if pd.notna(hotel_info.get('check_out')) else None,
                            tipo_habitacion=hotel_info.get('habitacion') if pd.notna(hotel_info.get('habitacion')) else None,
                            numero_noches=int(hotel_info.get('numero_noches')) if pd.notna(hotel_info.get('numero_noches')) else 0,
                            categoria=int(hotel_info.get('categoria')) if pd.notna(hotel_info.get('categoria')) else 0,
                            day_room=False
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
        
        # print(f"Errores de hotel ({state}) = {errors, errors_message}")
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
                    if str(hotel_info.get('hotel')).strip().lower() == "no":
                        hotel_entry = {
                            'nombre_hotel': hotel_info.get('nombre_hotel'),
                            'categoria': hotel_info.get('categoria'),
                            'ciudad': None,
                            'check_in': None,
                            'check_out': None,
                            'numero_noches': None,
                            'habitacion': None,
                            'nro': None
                        }
                        continue

                    if pd.isna(hotel_info.get('hotel')):
                        # hotel = 'Desconocido'
                        hotel = None
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
                    valid_prefixes = ['hotel', 'hostal', 'hostel', 'autogestion']

                    if isinstance(hotel, str) and hotel.lower() not in ['no', 'tbc']:
                        words = hotel.strip().split()
                        if len(words) >= 2 and words[0].lower() in valid_prefixes:
                            ciudad = ' '.join(words[1:])  # La ciudad es lo que queda después del prefijo
                        else:
                            ciudad = None
                    else:
                        ciudad = None

                    habitacion = hotel_info.get('habitacion')
                    if pd.notna(habitacion) and isinstance(habitacion, str):
                        habitacion = habitacion.strip().split()[0].upper()
                    else:
                        habitacion = None

                    hotel_entry = {
                        'nombre_hotel': hotel_info.get('nombre_hotel'),
                        'categoria': hotel_info.get('categoria'),
                        'ciudad': ciudad,
                        'check_in': check_in,
                        'check_out': check_out,
                        'numero_noches': (check_out - check_in).days if check_in and check_out else 0,
                        'habitacion': habitacion,
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

    def _extract_hotels(self, file_path, excel_data, start_row, state):
        hotels = []  # Lista para almacenar la información de los hoteles
        
        # Convertir los nombres de las columnas a cadenas y quitar espacios
        hotels_columns = excel_data.loc[start_row].dropna().str.lower().tolist()
        #print(hotels_columns)

        # Iterar sobre cada fila, comenzando desde la fila indicada
        for i in range(start_row + 2, excel_data.shape[0]):
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
                    if pd.notna(habitacion) and isinstance(habitacion, str):
                        habitacion = habitacion.strip().split()[0].upper()  # Toma solo "Single" o "Doble" en mayúsculas
                    else:
                        habitacion = None
                    nombre_hotel = excel_data.iloc[i, col_idx_hotel_name]

                    #print(check_out)
                    
                    if str(hotel).strip().lower() == "no":
                        tripulante_hotels[f'Hotel {hotel_num}'] = {
                            "categoria": categoria if not pd.isna(categoria) else None,
                            "hotel": hotel,
                            "check_in": None,
                            "check_out": None,
                            "habitacion": None,
                            "nombre_hotel": None,
                            "nro": None
                        }
                    else:
                        tripulante_hotels[f'Hotel {hotel_num}'] = {
                            "categoria": categoria if not pd.isna(categoria) else None,
                            "hotel": hotel if hotel else None,
                            #"check_in": pd.to_datetime(check_in, errors='coerce') if check_in else None,
                            "check_in": check_in if check_in else None,
                            "check_out": pd.to_datetime(check_out, errors='coerce') if check_out else None,
                            "habitacion": habitacion if habitacion else None,
                            "nombre_hotel": nombre_hotel if nombre_hotel else None,
                            "nro": hotel_num if hotel_num else None
                        }

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
    
    def get_column(df, columna, column):
        sheet_name = state
        indices = {key: idx for idx, key in enumerate(df.keys())}
        x = indices[columna] + 1
        if column != "Categoria":
            y = get_excel_column_letter(file_path, sheet_name, f"{column} {x+1}")
        else:
            y = get_excel_column_letter(file_path, sheet_name, "Category")
        return y
    
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
        return unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode('utf-8').strip().lower()

    def precache_column_letters(file_path):
        workbook = load_workbook(file_path)
        column_mapping = {}
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            mapping = {}
            for col in sheet.iter_cols(1, sheet.max_column, 1, 1):
                col_name = col[0].value
                if col_name:
                    mapping[col_name] = get_column_letter(col[0].column)
            column_mapping[sheet_name] = mapping
        return column_mapping

    def get_column_letter_from_column(col_name, column_letter_cache, sheet_name):
        return column_letter_cache.get(sheet_name, {}).get(col_name, '?')

    def check_column(file_path, sheet_name, hoteles_df):
        df = pd.DataFrame(hoteles_df)
        column_letter_cache = precache_column_letters(file_path)

        # print(column_letter_cache, state)

        dynamic_columns = {}
        for col in df.columns:
            for base_col in ['Hotel', 'Check in', 'Check out', 'Rooms', 'Nombre Hotel', 'Categoria']:
                if col.startswith(base_col):
                    dynamic_columns.setdefault(base_col, []).append(col)

        for idx, row in df.iterrows():
            categoria_checked = False  # Reinicia para cada fila

            for base_col, columns in dynamic_columns.items():
                for columna in columns:
                    registro = row[columna]

                    if not isinstance(registro, dict):
                        continue

                    # Validar Categoría solo una vez por fila
                    if not categoria_checked:
                        categoria = registro.get('categoria')
                        if pd.isna(categoria):
                            register_error(idx, 'Category', 'Categoria', "Categoría faltante", column_letter_cache, sheet_name)
                        categoria_checked = True  # Ya validamos la categoría para esta fila

                    hotel_value = registro.get('hotel')
                    if isinstance(hotel_value, str) and hotel_value.lower().strip() in ('no', 'tbc', 'autogestion'):
                        continue  # Saltar la validación de fechas, habitaciones, etc.

                    if pd.isna(hotel_value):
                        register_error(idx, columna, 'Hotel', "Hotel faltante", column_letter_cache, sheet_name)
                        continue

                    if isinstance(hotel_value, str):
                        hotel_parts = hotel_value.split()
                        if hotel_value.lower().strip() not in ('no', 'tbc'):
                            if len(hotel_parts) < 2:
                                register_error(idx, columna, 'Hotel', "Formato incorrecto en nombre de hotel", column_letter_cache, sheet_name)
                            elif hotel_parts[1].upper() in CITY_AIRPORT_CODES:
                                if normalize_string(hotel_parts[0]) not in ['hotel', 'autogestion', 'hostal', 'hostel']:
                                    register_error(idx, columna, 'Hotel', "Debe comenzar con 'hotel', 'autogestión', 'hostal' o 'hostel'", column_letter_cache, sheet_name)
                            else:
                                register_error(idx, columna, 'Hotel', "Ciudad no válida en nombre de hotel", column_letter_cache, sheet_name)

                    skip = False

                    if pd.isna(registro.get('check_in')):
                        correct_check_in_column = columna.replace('Hotel', 'Check in')
                        register_error(idx, correct_check_in_column, 'Check in', "Check in faltante", column_letter_cache, sheet_name)
                        skip = True
                    else:
                        column_letter = check_date(df, registro, idx, columna, 'check_in', 'Check in')
                        if column_letter is not True:
                            correct_check_in_column = columna.replace('Hotel', 'Check in')
                            register_error(idx, correct_check_in_column, 'Check in', "Formato de check in no válido", column_letter_cache, sheet_name)

                    if pd.isna(registro.get('check_out')):
                        correct_check_out_column = columna.replace('Hotel', 'Check out')
                        register_error(idx, correct_check_out_column, 'Check out', "Check out faltante", column_letter_cache, sheet_name)
                        skip = True
                    else:
                        column_letter = check_date(df, registro, idx, columna, 'check_out', 'Check out')
                        if column_letter is not True:
                            correct_check_out_column = columna.replace('Hotel', 'Check out')
                            register_error(idx, correct_check_out_column, 'Check out', "Formato de check out no válido", column_letter_cache, sheet_name)

                    if skip:
                        continue

                    habitacion_value = registro.get('habitacion')
                    if pd.isna(habitacion_value):
                        correct_rooms_column = columna.replace('Hotel', 'Rooms')
                        register_error(idx, correct_rooms_column, 'Rooms', "Room faltante", column_letter_cache, sheet_name)
                    elif isinstance(habitacion_value, str) and habitacion_value.lower() not in ('no', 'tbc'):
                        room_parts = habitacion_value.split()
                        if len(room_parts) > 2:
                            correct_rooms_column = columna.replace('Hotel', 'Rooms')
                            register_error(idx, correct_rooms_column, 'Rooms', "Formato incorrecto en nombre de room", column_letter_cache, sheet_name)
                        elif normalize_string(room_parts[0]) not in ['single', 'doble']:
                            correct_rooms_column = columna.replace('Hotel', 'Rooms')
                            register_error(idx, correct_rooms_column, 'Rooms', "Debe comenzar con 'single' o 'doble'", column_letter_cache, sheet_name)

                    if pd.isna(registro.get('nombre_hotel')):
                        correct_nombre_hotel_column = columna.replace('Hotel', 'Nombre Hotel')
                        register_error(idx, correct_nombre_hotel_column, 'Nombre Hotel', "Nombre de hotel faltante", column_letter_cache, sheet_name)

    def register_error(idx, columna, base_col, msg, column_letter_cache, sheet_name):
        column_letter = get_column_letter_from_column(columna, column_letter_cache, sheet_name)
        errors_to_check.append([idx, columna])
        errors.append([idx + 3, column_letter])
        errors_message.append(f"{msg} [{idx + 3},{column_letter}]")
        # print(f"{idx + 3},{column_letter} | {msg}")

    def get_excel_column_letter(file_path, sheet_name, column_name):
        workbook = load_workbook(file_path)
        sheet = workbook[sheet_name]

        # Buscar la columna por nombre (suponiendo que los nombres están en la primera fila)
        for col in sheet.iter_cols(min_row=1, max_row=1):
            cell_value = col[0].value
            if isinstance(cell_value, str) and cell_value.strip() == column_name:
                return get_column_letter(col[0].column)  # Esto ya maneja bien la base 1

        print(f"[WARNING] Columna '{column_name}' no encontrada en la hoja '{sheet_name}'.")
        return "?"

    def get_cell_value(file_path, sheet_name, row, column):
        # Cargar el archivo de Excel
        workbook = load_workbook(file_path, data_only=True)  # `data_only=True` para obtener el valor calculado en celdas con fórmulas
        sheet = workbook[sheet_name]

        # Obtener el valor de la celda
        cell_value = sheet.cell(row=row, column=column).value

        return cell_value

    def validate_categories(tripulantes_df, column_name_prefix, file_path, state):
        for column in tripulantes_df.columns:
            if column_name_prefix in column:  # Filtra columnas tipo "Hotel 1", "Hotel 2", etc.
                if column == 'categoria':
                    for i, value in tripulantes_df[column].items():
                        # print(f"El value es {value}")
                        if pd.isna(value):
                            print(f"Saltando NaN en fila {i + 3}, columna {column}")

                            # Obtener la letra de la columna en Excel
                            y = get_excel_column_letter(file_path, state, "Category")
                            
                            # Registrar el error en las listas de control
                            errors.append([i + 3, y])
                            errors_message.append(f"Categoría faltante [{i + 3},{y}]")

                            continue  # Saltar a la siguiente iteración

                        try:
                            # Convertir string a dict si es necesario
                            if isinstance(value, str):
                                value = ast.literal_eval(value)
                            
                            # Verificar que sea un diccionario antes de usar .get
                            if isinstance(value, dict):
                                categoria = value.get('categoria', None)
                                
                                # Validar la categoría (ajusta según tus valores permitidos)
                                if categoria not in [1, 2, 3]:
                                    print(f"[ERROR HOTELES] Categoría no existente: {categoria}")
                                    error = categoria
                                    sheet_name = state
                                    x = i + 3  # Ajuste para filas en Excel
                                    y = get_excel_column_letter(file_path, sheet_name, column)
                                    column_number = column_index_from_string(y)
                                    cell_value = get_cell_value(file_path, sheet_name, 1, column_number)

                                    print(f"Error [Hoteles]: Categoría inexistente en la fila {x+3}, columna '{column} ({y})'. Valor: '{error}'")
                                    errors.append([i + 3, y])
                                    errors_message.append(f"Categoría inexistente en {cell_value} [{x + 3},{y}]")
                            else:
                                # Si no es dict ni string evaluable, no se procesa
                                continue

                        except (ValueError, SyntaxError) as e:
                            print(f"[ERROR] No se pudo convertir la celda en la fila {i + 3}, columna {column}. Error: {e}")

    # print(hoteles_df)

    validate_categories(hoteles_df, "Hotel", file_path, state)
    check_column(file_path, state, hoteles_df)
    # print(f"Errores de hotel ({state})= {errors}, {errors_message}")
    return errors, errors_message