from datetime import datetime, timedelta
import calendar
import re
import pandas as pd
from sqlalchemy.orm import Session
import traceback
from datetime import time, date
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

class Transportes:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def transportes_main(self, file_path):
        try:
            excel_data_on = pd.read_excel(file_path, sheet_name='ON', header=None)

            transportes_on = self._extract_transports(excel_data_on, start_row=0, state="on")
            transportes_on.reset_index(drop=True, inplace=True)

            excel_data_off = pd.read_excel(file_path, sheet_name='OFF', header=None)

            transportes_off = self._extract_transports(excel_data_off, start_row=0, state="off")
            transportes_off.reset_index(drop=True, inplace=True)

            return transportes_on, transportes_off
        except Exception as e:
            raise Exception(f"[Transportes] Error al procesar el archivo: {e}")

    def _create_transporte(self, file_path, transportes_df, tripulantes_df, state):
        transportes = []  # Lista para almacenar los transportes creados
        errors, errors_message, errors_to_check = check_and_clean(file_path, transportes_df, state)
        #print(errors_to_check)

        try:
            # Verificar que ambos DataFrames no estén vacíos
            if transportes_df.empty or tripulantes_df.empty:
                print("No hay transportes o tripulantes para procesar.")
                return []

            # Iterar sobre cada fila del DataFrame de transportes
            for i, row in transportes_df.iterrows():
                try:
                    # Verificar que la fila de tripulantes tenga un índice válido
                    if i >= len(tripulantes_df):
                        print(f"No hay datos de tripulante para la fila {i}. Omitiendo...")
                        continue

                    # Obtener el tripulante correspondiente a la fila actual
                    tripulante_data = tripulantes_df.iloc[i]
                    if pd.isna(tripulante_data['Pasaporte']):
                        #print(f"Pasaporte vacío para el tripulante en la fila {i}. Omitiendo...")
                        continue

                    tripulante = self.db_session.query(Tripulante).filter_by(pasaporte=tripulante_data['Pasaporte']).first()

                    if not tripulante:
                        print(f"No se encontró tripulante con pasaporte {tripulante_data['Pasaporte']} en la fila {i}. Omitiendo...")
                        continue

                    # Iterar sobre las claves que representan los transportes
                    for transporte_key in row.index:
                        transporte_info = row[transporte_key]  # Obtener el diccionario del transporte

                        if [i, transporte_key] in errors_to_check:
                            #print(f"Omitiendo creación para fila {i}, transporte {transporte_key} debido a errores.")
                            continue

                        # Verificar que haya información para el transporte
                        if pd.notna(transporte_info) and isinstance(transporte_info, dict):                        
                            transporte_info = self._extraer_transportes(transporte_info)

                            for _transporte in transporte_info:
                                try:
                                    # Verificar que el valor de 'City In' no sea 'Desconocido'
                                    if _transporte['City In'] == 'Desconocido' or _transporte['City In'].lower() == 'no':
                                        #print(f"Omitiendo transporte con 'City In' desconocido en la fila {i}: {_transporte}")
                                        continue

                                    # Verificar datos faltantes
                                    if not all(key in _transporte for key in ['City In', 'Place In', 'City End', 'Place End']):
                                        print(f"Datos faltantes en transporte en la fila {i}: {_transporte}")
                                        continue

                                    #print(f"Buscando transporte con: City In: {_transporte['City In']}, Place In: {_transporte['Place In']}, City End: {_transporte['City End']}, Place End: {_transporte['Place End']}")
                                    # Buscar el transporte en la base de datos
                                    transporte = (
                                        self.db_session.query(Transporte)
                                        .filter(
                                            and_(
                                                Transporte.city_in == _transporte['City In'],
                                                Transporte.place_in == _transporte['Place In'],
                                                Transporte.city_end == _transporte['City End'],
                                                Transporte.place_end == _transporte['Place End']
                                            )
                                        )
                                        .first()
                                    )

                                    if not transporte:
                                        print(f"Creando nuevo transporte: {_transporte}")
                                        transporte = Transporte(
                                            city_in=_transporte['City In'],
                                            place_in=_transporte['Place In'],
                                            city_end=_transporte['City End'],
                                            place_end=_transporte['Place End'],
                                        )
                                        self.db_session.add(transporte)
                                        self.db_session.flush()  # Asegurar que el transporte esté disponible en la base de datos
                                        transportes.append(transporte)

                                    # Verificar si ya existe la relación entre tripulante y transporte
                                    tripulante_transporte_existente = self.db_session.query(TripulanteTransporte).filter_by(
                                        tripulante_id=tripulante.tripulante_id,
                                        transporte_id=transporte.transporte_id,
                                    ).first()                                        

                                    #print(f"HOLA {type(hours_pickup)}")
                                    
                                    if not tripulante_transporte_existente and transporte.transporte_id != None:
                                        tripulante_transporte = TripulanteTransporte(
                                            tripulante_id=tripulante.tripulante_id,
                                            transporte_id=transporte.transporte_id,
                                            #date_pickup=_transporte['Date Pickup'] if 'Date Pickup' in _transporte else None,
                                            date_pickup=_transporte['Date Pickup'],
                                            hours_pickup=_transporte['Hours Pickup']
                                        )

                                        self.db_session.add(tripulante_transporte)
                                        self.db_session.flush()
                                        self.db_session.commit()
                                        #print(f"Transporte guardado correctamente: {tripulante_transporte}")

                                    elif tripulante_transporte_existente:
                                        #print(f"Ya existe relación para Tripulante ID {tripulante.tripulante_id} y Transporte ID {transporte.transporte_id}.")
                                        continue
                                    
                                except Exception as transporte_error:
                                    #print(f"Error procesando transporte en fila {i}, transporte: {_transporte} {tripulante.nombre}")
                                    ###traceback.print_exc()
                                    self.db_session.rollback()
                                    continue

                except Exception as fila_error:
                    #print(f"[Transporte] Error procesando fila {i}: {fila_error}")
                    #print(f"Datos del tripulante en la fila: {tripulante_data.to_dict()}")
                    ###traceback.print_exc()
                    self.db_session.rollback()
                    continue

            # Confirmar los cambios en la base de datos
            self.db_session.commit()
            print("Procesamiento de transportes completado.")

        except Exception as e:
            print(f"Error general al crear transportes: {e}")
            ###traceback.print_exc()
            self.db_session.rollback()

        return errors, errors_message  # Retornar la lista de transportes creados

    def _extraer_transportes(self, transporte_info):        
        transportes_info = []

        if Transporte is None or pd.isna(Transporte):
            print("Transporte es NaN o None. Omitiendo...")
            return None
        
        if transporte_info['City In'] != 'Desconocido':
            city_in = transporte_info['City In']
            place_in = transporte_info['Place In']
            city_end = transporte_info['City End']
            place_end = transporte_info['Place End']
            date_pickup = transporte_info['Date Pickup']
            hours_pickup = transporte_info['Hours Pickup']

            transportes_info.append({
                'City In': city_in,
                'Place In': place_in,
                'City End': city_end,
                'Place End': place_end,
                'Date Pickup': date_pickup,
                'Hours Pickup': hours_pickup,
            })
        
        return transportes_info

    def _extract_transports(self, excel_data, start_row, state):
        transports = []

        # Convertir los nombres de las columnas a cadenas y quitar espacios
        transport_columns = excel_data.loc[start_row].dropna().str.lower().tolist()

        # Iterar sobre cada fila, comenzando desde la fila indicada
        for i in range(start_row + 1, excel_data.shape[0]):
            tripulante_transports = {}
            transports_num = 1

            # Iterar sobre las posibles columnas de transportes hasta que ya no existan
            while True:
                city_in_x = f'city_in_{transports_num}'
                place_in_x = f'place_in_{transports_num}'
                city_end_x = f'city_end_{transports_num}'
                place_end_x = f'place_end_{transports_num}'
                date_pickup_x = f'date_pickup_{transports_num}'
                hours_pickup_x = f'hours_pickup_{transports_num}'

                # Verificar si las columnas de transporte y fecha existen
                if city_in_x in transport_columns and place_in_x in transport_columns and city_end_x in transport_columns:
                    col_idx_city_in = transport_columns.index(city_in_x)
                    col_idx_place_in = transport_columns.index(place_in_x)
                    col_idx_city_end = transport_columns.index(city_end_x)
                    col_idx_place_end = transport_columns.index(place_end_x)
                    col_idx_date_pickup = transport_columns.index(date_pickup_x)
                    col_idx_hours_pickup = transport_columns.index(hours_pickup_x)

                    city_in_idx = excel_data.iloc[i, col_idx_city_in] if col_idx_city_in < excel_data.shape[1] else None
                    place_in_idx = excel_data.iloc[i, col_idx_place_in] if col_idx_place_in < excel_data.shape[1] else None
                    city_end_idx = excel_data.iloc[i, col_idx_city_end] if col_idx_city_end < excel_data.shape[1] else None
                    place_end_idx = excel_data.iloc[i, col_idx_place_end] if col_idx_place_end < excel_data.shape[1] else None
                    date_pickup_idx = excel_data.iloc[i, col_idx_date_pickup] if col_idx_date_pickup < excel_data.shape[1] else None
                    hours_pickup_idx = excel_data.iloc[i, col_idx_hours_pickup] if col_idx_hours_pickup < excel_data.shape[1] else None

                    # Asignar valores 'Desconocido' si faltan datos
                    city_in_value = city_in_idx if pd.notna(city_in_idx) else 'Desconocido'
                    place_in_value = place_in_idx if pd.notna(place_in_idx) else 'Desconocido'
                    city_end_value = city_end_idx if pd.notna(city_end_idx) else 'Desconocido'
                    place_end_value = place_end_idx if pd.notna(place_end_idx) else 'Desconocido'
                    date_pickup_value = date_pickup_idx if pd.notna(date_pickup_idx) else None
                    hours_pickup_value = hours_pickup_idx if pd.notna(hours_pickup_idx) else None

                    # Agregar el transporte al diccionario del tripulante
                    tripulante_transports[f'Transporte {transports_num}'] = {
                        "City In": city_in_value,
                        "Place In": place_in_value,
                        "City End": city_end_value,
                        "Place End": place_end_value,
                        "Date Pickup": date_pickup_value,
                        "Hours Pickup": hours_pickup_value
                    }

                    # Incrementar el contador para verificar el siguiente transporte
                    transports_num += 1
                else:
                    # No hay más columnas de transporte y fecha, salir del bucle
                    break

            # Agregar una entrada para el tripulante actual, incluso si no se encontraron transportes
            if not tripulante_transports:
                tripulante_transports[f'Transporte {transports_num}'] = {
                    "City In": 'Desconocido',
                    "Place In": 'Desconocido',
                    "City End": 'Desconocido',
                    "Place End": 'Desconocido',
                    "Date Pickup": 'Desconocido',
                    "Hours Pickup": 'Desconocido'
                }

            # Agregar los transportes del tripulante a la lista final
            transports.append(tripulante_transports)

        # Verificar si se encontraron transportes
        if len(transports) == 0:
            print("No se encontraron transportes en las filas procesadas.")

        # Asegurar que la función retorne la lista de transportes
        return pd.DataFrame(transports)
        
        # Leer todas las filas desde una fila específica hasta que no haya más datos,
        # incluso si las filas tienen valores nulos.
        
        data_block = []
        current_row = start_row

        while current_row < len(data):
            # Leer una fila completa del DataFrame, sin detenerse por nulos
            row_data = data.iloc[current_row, column_range]

            # Agregar los datos de la fila al bloque, incluso si hay nulos
            data_block.append(row_data)
            current_row += 1

        # Convertir el bloque de datos en un DataFrame
        result_df = pd.DataFrame(data_block)
        
        # Asignar nombres de columnas si se proporcionan
        if column_names:
            if len(column_names) != result_df.shape[1]:
                raise ValueError(f"Length mismatch: Se esperaban {len(column_names)} columnas, pero se detectaron {result_df.shape[1]}")
            result_df.columns = column_names
        
        return result_df

def check_and_clean(file_path, transportes_df, state):
    errors_to_check = []
    errors = []
    errors_message = []

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
    
    def get_column(df, columna):
        sheet_name = state
        indices = {key: idx for idx, key in enumerate(df.keys())}
        x = indices[columna]
        y = get_excel_column_letter(file_path, sheet_name, f"Date_pickup_{x+1}")
        return y
    
    def get_cell_value(file_path, sheet_name, row, column):
        # Cargar el archivo de Excel
        workbook = load_workbook(file_path, data_only=True)  # `data_only=True` para obtener el valor calculado en celdas con fórmulas
        sheet = workbook[sheet_name]

        # Obtener el valor de la celda
        cell_value = sheet.cell(row=row, column=column).value

        return cell_value

    def check_date():        
        df = pd.DataFrame(transportes_df)
        for columna in transportes_df:
            #print(f"Columna: {columna} | {state}")
            transporte = df[columna].tolist()  # Convertir la columna en una lista
            for idx, registro in enumerate(transporte):  # Iterar sobre los diccionarios
                # Verificar si 'City In' es igual a 'Desconocido'
                if registro.get('City In').lower() != 'no':
                    
                    if isinstance(registro.get('Date Pickup'), str):
                        if looks_like_date(registro.get('Date Pickup')):
                            value = registro.get('Date Pickup')
                            value = clean_value(value)

                            if not is_valid_date(value):
                                print(f"NE | Registro {idx} en '{columna}': Fecha es {value}")
                                sheet_name = state
                                column_letter = get_column(df, columna)
                                column_number = column_index_from_string(column_letter)
                                cell_value = get_cell_value(file_path, sheet_name, 1, column_number)
                                errors_to_check.append([idx, columna])
                                errors.append([idx, column_letter])
                                errors_message.append(f"Fecha inexistente en {cell_value} [{idx+2},{column_letter}]")
                    else:
                        #print(f"{idx} | {registro.get('Date Pickup')}")
                        value = registro.get('Date Pickup')
                        value = clean_value(value)
                        
                        if registro.get('Date Pickup') == None:
                            print(f"ER | Registro {idx+2} en '{columna}': Fecha está vacía")
                            sheet_name = state
                            column_letter = get_column(df, columna)
                            column_number = column_index_from_string(column_letter)
                            cell_value = get_cell_value(file_path, sheet_name, 1, column_number)
                            errors_to_check.append([idx, columna])
                            errors.append([idx, column_letter])
                            errors_message.append(f"Fecha faltante en {cell_value} [{idx+2},{column_letter}]")
                        else:
                            if not is_valid_date(value):
                                print(f"NE | Registro {idx+2} en '{columna}': Fecha es {registro.get('Date Pickup')}")
                                sheet_name = state
                                column_letter = get_column(df, columna)
                                column_number = column_index_from_string(column_letter)
                                cell_value = get_cell_value(file_path, sheet_name, 1, column_number)
                                errors_to_check.append([idx, columna])
                                errors.append([idx, column_letter])
                                errors_message.append(f"Fecha inexistente en {columna} [{idx+2},{column_letter}]")
                else:
                    if registro.get('City In').lower() == 'no':
                        continue
                    else:
                        print(f"Registro {idx+2} en '{columna}': City In está vacío")

    check_date()

    return errors, errors_message, errors_to_check


# def process_time(value, field_name, state, tripulante, transporte_key, row, i, indice_a_letra_columna):
#     errors = []

#     if isinstance(value, str):
#         try:
#             # Intenta convertir a `time` si es una cadena en formato HH:MM
#             print(value)
#             return datetime.strptime(value, "%H:%M").time()
#         except ValueError:
#             print(f"{i} | {value}")
#             if value.upper() == "TBC":
#                 return None
#             error = value
#             j = row.index.get_loc(transporte_key)
#             x = i + 2
#             z = 64 if state == "ON" else 52
#             a = 5 if field_name == 'Date Pickup' else 6 if field_name == 'Hours Pickup' else None
#             y = z + (6 * j) + a
#             letra_columna = indice_a_letra_columna(y)
#             print(f"Se ha producido un error en el tripulante {tripulante.nombre} para el {transporte_key} ({field_name}: {error}) [{state} | {x},{letra_columna}]")
#             errors.append(i)
#             return errors
#     elif isinstance(value, datetime):
#         # Extrae solo la hora si es un `datetime`
#         return value.date()
#     elif isinstance(value, time):
#         # Si ya es de tipo `time`, simplemente devuélvelo
#         return value
#     elif isinstance(value, date):
#         # Si es de tipo `date`, devuélvelo como está
#         return value
#     else:
#         if value == None:
#             errors.append(i)
#             return errors
#         # Si el valor no es manejable, retorna `None`
#         #print(f"Tipo de dato inesperado para {field_name}: {type(value)}")
#         else:
#             return None

