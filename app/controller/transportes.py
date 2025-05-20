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
from app.controller.constants import CITY_AIRPORT_CODES, CITY_TO_AIRPORT_CODES

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

            pd.set_option('display.max_rows', None)         # Muestra todas las filas
            pd.set_option('display.max_columns', None)      # Muestra todas las columnas
            pd.set_option('display.max_colwidth', None)     # Muestra contenido completo de cada celda
            pd.set_option('display.expand_frame_repr', False)
            print(f"Transportes OFF = {transportes_off["Transporte 1"]}")

            return transportes_on, transportes_off
        except Exception as e:
            raise Exception(f"[Transportes] Error al procesar el archivo: {e}")

    def _create_transporte(self, file_path, transportes_df, tripulantes_df, state):
        transportes = []
        errors, errors_message, errors_to_check = check_and_clean(file_path, transportes_df, state)

        try:
            if transportes_df.empty or tripulantes_df.empty:
                print("No hay transportes o tripulantes para procesar.")
                return []

            for i, row in transportes_df.iterrows():
                try:
                    if i >= len(tripulantes_df):
                        continue

                    tripulante_data = tripulantes_df.iloc[i]
                    if pd.isna(tripulante_data['Pasaporte']):
                        continue

                    tripulante = self.db_session.query(Tripulante).filter_by(
                        pasaporte=tripulante_data['Pasaporte']
                    ).first()

                    if not tripulante:
                        continue

                    for transporte_key in row.index:
                        transporte_info = row[transporte_key]

                        if [i, transporte_key] in errors_to_check:
                            continue

                        if pd.notna(transporte_info) and isinstance(transporte_info, dict):
                            transporte_info = self._extraer_transportes(transporte_info)

                            for _transporte in transporte_info:
                                try:
                                    if _transporte['City In'] in ['Desconocido', 'NO']:
                                        continue

                                    if not all(k in _transporte for k in ['City In', 'Place In', 'City End', 'Place End']):
                                        continue

                                    transporte = self.db_session.query(Transporte).filter_by(
                                        city_in=_transporte['City In'],
                                        place_in=_transporte['Place In'],
                                        city_end=_transporte['City End'],
                                        place_end=_transporte['Place End']
                                    ).first()

                                    if not transporte:
                                        transporte = Transporte(
                                            city_in=_transporte['City In'],
                                            place_in=_transporte['Place In'],
                                            city_end=_transporte['City End'],
                                            place_end=_transporte['Place End']
                                        )
                                        self.db_session.add(transporte)
                                        self.db_session.flush()
                                        self.db_session.commit()
                                        transportes.append(transporte)

                                    tripulante_transporte_existente = self.db_session.query(TripulanteTransporte).filter_by(
                                        tripulante_id=tripulante.tripulante_id,
                                        transporte_id=transporte.transporte_id
                                    ).first()

                                    if not tripulante_transporte_existente:
                                        # ✅ Conversión segura de hours_pickup
                                        hours_pickup_raw = _transporte.get('Hours Pickup')
                                        if isinstance(hours_pickup_raw, str):
                                            try:
                                                hours_pickup_obj = datetime.strptime(hours_pickup_raw.strip(), "%H:%M").time()
                                            except ValueError:
                                                print(f"[ERROR] Hora inválida en fila {i}: {hours_pickup_raw}. Se asigna None.")
                                                hours_pickup_obj = None
                                        elif isinstance(hours_pickup_raw, time):
                                            hours_pickup_obj = hours_pickup_raw
                                        else:
                                            hours_pickup_obj = None

                                        # ✅ Conversión segura de date_pickup
                                        date_pickup_raw = _transporte.get('Date Pickup')
                                        if isinstance(date_pickup_raw, str):
                                            try:
                                                date_pickup_obj = datetime.strptime(date_pickup_raw.strip(), "%d-%m-%Y").date()
                                            except ValueError:
                                                try:
                                                    date_pickup_obj = datetime.strptime(date_pickup_raw.strip(), "%d-%m-%y").date()
                                                except ValueError:
                                                    print(f"[ERROR] Fecha inválida en fila {i}: {date_pickup_raw}. Se asigna None.")
                                                    date_pickup_obj = None
                                        elif isinstance(date_pickup_raw, datetime):
                                            date_pickup_obj = date_pickup_raw.date()
                                        elif isinstance(date_pickup_raw, date):
                                            date_pickup_obj = date_pickup_raw
                                        else:
                                            date_pickup_obj = None

                                        tripulante_transporte = TripulanteTransporte(
                                            tripulante_id=tripulante.tripulante_id,
                                            transporte_id=transporte.transporte_id,
                                            date_pickup=date_pickup_obj,
                                            hours_pickup=hours_pickup_obj
                                        )

                                        self.db_session.add(tripulante_transporte)
                                        self.db_session.flush()
                                        self.db_session.commit()
                                        # print(f"[OK] Relación creada: Tripulante {tripulante.tripulante_id} - Transporte {transporte.transporte_id}")

                                except Exception as e:
                                    self.db_session.rollback()
                                    print(f"[ERROR transporte interno] Fila {i}, error: {e}")
                                    continue

                except Exception as fila_error:
                    self.db_session.rollback()
                    print(f"[ERROR fila] Fila {i}, error: {fila_error}")
                    continue

            self.db_session.commit()
            print("Procesamiento de transportes completado.")

        except Exception as e:
            self.db_session.rollback()
            print(f"[ERROR general] {e}")

        return errors, errors_message

    def _extraer_transportes(self, transporte_info):        
        transportes_info = []

        if Transporte is None or pd.isna(Transporte):
            print("Transporte es NaN o None. Omitiendo...")
            return None
        
        if transporte_info['City In'] != 'Desconocido':
            city_in = str(transporte_info['City In']).strip()
            place_in = str(transporte_info['Place In']).strip()
            city_end = str(transporte_info['City End']).strip()
            place_end = str(transporte_info['Place End']).strip()
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
        for i in range(start_row + 2, excel_data.shape[0]):
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
                    city_in_value = city_in_idx if pd.notna(city_in_idx) else None
                    place_in_value = place_in_idx if pd.notna(place_in_idx) else None
                    city_end_value = city_end_idx if pd.notna(city_end_idx) else None
                    place_end_value = place_end_idx if pd.notna(place_end_idx) else None
                    date_pickup_value = date_pickup_idx if pd.notna(date_pickup_idx) else None
                    hours_pickup_value = self.limpiar_hora(hours_pickup_idx)

                    # Agregar el transporte al diccionario del tripulante
                    if not pd.isna(city_in_value):
                        if str(city_in_value.lower()) != "no":
                            tripulante_transports[f'Transporte {transports_num}'] = {
                                "City In": city_in_value,
                                "Place In": place_in_value,
                                "City End": city_end_value,
                                "Place End": place_end_value,
                                "Date Pickup": date_pickup_value,
                                "Hours Pickup": hours_pickup_value
                            }
                        else:
                            tripulante_transports[f'Transporte {transports_num}'] = {
                                "City In": "NO",
                                "Place In": None,
                                "City End": None,
                                "Place End": None,
                                "Date Pickup": None,
                                "Hours Pickup": None
                            }
                    else:
                        tripulante_transports[f'Transporte {transports_num}'] = {
                                "City In": None,
                                "Place In": None,
                                "City End": None,
                                "Place End": None,
                                "Date Pickup": None,
                                "Hours Pickup": None
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
    
    def limpiar_hora(self, valor):
        if isinstance(valor, datetime):
            return valor.time()
        elif isinstance(valor, time):
            return valor
        elif isinstance(valor, str):
            try:
                return datetime.strptime(valor.strip(), "%H:%M").time()
            except ValueError:
                return None
        return None
        
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

    workbook = load_workbook(file_path, data_only=True)
    sheet = workbook[state]

    column_letter_cache = {
        col[0].value.strip(): get_column_letter(col[0].column)
        for col in sheet.iter_cols(1, sheet.max_column, 1, 1)
        if col[0].value
    }

    def clean_value(value):
        return value.strip().replace('/', '-') if isinstance(value, str) else value

    def is_valid_date(date_value):
        if isinstance(date_value, (datetime, date)):
            return True  # Es un objeto de fecha válido, no hace falta más validación

        # Si es string, intenta convertirlo
        formats = ['%d-%m-%y', '%d-%m-%Y']
        for date_format in formats:
            try:
                date_parsed = pd.to_datetime(date_value, format=date_format, errors='raise')
                return date_parsed.day <= calendar.monthrange(date_parsed.year, date_parsed.month)[1]
            except Exception:
                continue
        return False

    def is_valid_time(time_str):
        return bool(re.match(r'^\d{2}:\d{2}(:\d{2})?$', str(time_str).strip()))

    def clean_time_format(time_str):
        if not time_str:
            return None
        parts = str(time_str).strip().split(':')
        if len(parts) >= 2:
            return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}"
        return None

    def looks_like_date(value):
        return isinstance(value, str) and re.match(r'^\d{2}-\d{2}-\d{2,4}$', value) is not None

    def get_column_letter_for_field(transporte_actual, field):
        transporte_number = transporte_actual.split()[-1]
        col_name = f"{field}_{transporte_number}"
        return column_letter_cache.get(col_name, "?")

    df = pd.DataFrame(transportes_df)

    for columna in transportes_df:
        transporte_data = df[columna].tolist()
        for idx, registro in enumerate(transporte_data):
            if not isinstance(registro, dict):
                continue

            city_in = registro.get('City In')
            if pd.isna(city_in) or str(city_in).strip() == "":
                column_letter = get_column_letter_for_field(columna, 'City_in')
                errors_to_check.append([idx, columna])
                errors.append([idx + 3, column_letter])
                errors_message.append(f"City In faltante [{idx + 3},{column_letter}]")
                continue

            if str(city_in).lower().strip() == 'no':
                continue

            # --- Date Pickup ---
            date_pickup = registro.get('Date Pickup')
            column_letter_date = get_column_letter_for_field(columna, 'Date_pickup')

            # 📌 Si es fórmula o referencia, obtener el valor calculado desde openpyxl
            if isinstance(date_pickup, str) and date_pickup.startswith('='):
                cell_address = f"{column_letter_date}{idx + 3}"
                cell = sheet[cell_address]
                date_pickup = cell.value  # Obtener el valor real
                registro['Date Pickup'] = date_pickup

            if pd.isna(date_pickup) or str(date_pickup).strip() == "":
                errors_to_check.append([idx, columna])
                errors.append([idx + 3, column_letter_date])
                errors_message.append(f"Fecha faltante [{idx + 3},{column_letter_date}]")
            elif isinstance(date_pickup, str):
                cleaned_date = clean_value(date_pickup)
                if looks_like_date(cleaned_date) and not is_valid_date(cleaned_date):
                    # print(f"[ERROR DATE PICK UP] = {date_pickup} | {idx+3} 1")

                    errors_to_check.append([idx, columna])
                    errors.append([idx + 3, column_letter_date])
                    errors_message.append(f"Fecha inexistente [{idx + 3},{column_letter_date}]")
            elif not isinstance(date_pickup, (datetime, date)) and not is_valid_date(str(date_pickup)):
                # print(f"[ERROR DATE PICK UP] = {date_pickup} | {idx+3},{column_letter_date}| 2")

                errors_to_check.append([idx, columna])
                errors.append([idx + 3, column_letter_date])
                errors_message.append(f"Fecha inexistente [{idx + 3},{column_letter_date}]")

            # --- Hours Pickup ---
            hours_pickup = registro.get('Hours Pickup')
            column_letter_hour = get_column_letter_for_field(columna, 'Hours_pickup')

            if isinstance(hours_pickup, str) and hours_pickup.startswith('='):
                cell_address = f"{column_letter_hour}{idx + 3}"
                cell = sheet[cell_address]
                hours_pickup = cell.value
                registro['Hours Pickup'] = hours_pickup

            if pd.isna(hours_pickup) or str(hours_pickup).strip() == "":
                errors_to_check.append([idx, columna])
                errors.append([idx + 3, column_letter_hour])
                errors_message.append(f"Hora faltante [{idx + 3},{column_letter_hour}]")
            else:
                cleaned_time = clean_time_format(hours_pickup)
                if not is_valid_time(cleaned_time):
                    errors_to_check.append([idx, columna])
                    errors.append([idx + 3, column_letter_hour])
                    errors_message.append(f"Hora inválida [{idx + 3},{column_letter_hour}]")
                else:
                    registro['Hours Pickup'] = cleaned_time  # Guarda limpio en formato HH:MM

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