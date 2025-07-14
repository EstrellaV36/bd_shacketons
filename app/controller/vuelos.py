from datetime import datetime, timedelta, time
import calendar
import re
import pandas as pd
from sqlalchemy.orm import Session
from app.models import Tripulante, Vuelo, TripulanteVuelo
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter, column_index_from_string
from app.controller.constants import CITY_AIRPORT_CODES, CITY_TO_AIRPORT_CODES

class Vuelos:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def vuelos_main(self, file_path):
        try:
            # Leer la hoja ON del archivo Excel
            excel_data_on = pd.read_excel(file_path, sheet_name='ON', header=None)        

            vuelos_internacionales_on = self._extract_international_flights(excel_data_on, start_row=0, state="on")
            vuelos_internacionales_on.reset_index(drop=True, inplace=True)  # Reiniciar el índice
            print("Internacional ON done")

            vuelos_domesticos_on = self._extract_flights(excel_data_on, start_row=0, state="DOMESTICO")
            vuelos_domesticos_on.reset_index(drop=True, inplace=True)  # Reiniciar el índice
            print("Domesticos ON done")

            vuelos_regionales_on = self._extract_flights(excel_data_on, start_row=0, state="REGIONAL")
            vuelos_regionales_on.reset_index(drop=True, inplace=True)  # Reiniciar el índice
            print("Regional ON done")

            excel_data_off = pd.read_excel(file_path, sheet_name='OFF', header=None)

            vuelos_internacionales_off = self._extract_flights(excel_data_off, start_row=0, state="INTERNACIONAL")
            vuelos_internacionales_off.reset_index(drop=True, inplace=True)  # Reiniciar el índice
            print("Internacional OFF done")

            vuelos_domesticos_off = self._extract_flights(excel_data_off, start_row=0, state="DOMESTICO")
            vuelos_domesticos_off.reset_index(drop=True, inplace=True)  # Reiniciar el índice
            print("Domesticos OFF done")

            vuelos_regionales_off = self._extract_flights(excel_data_off, start_row=0, state="REGIONAL")
            vuelos_regionales_off.reset_index(drop=True, inplace=True)  # Reiniciar el índice
            print("Regional OFF done")

            # print("Viajes de OFF terminados")

            return vuelos_internacionales_on, vuelos_internacionales_off, vuelos_domesticos_on, vuelos_domesticos_off, vuelos_regionales_on, vuelos_regionales_off
        except Exception as e:
            raise Exception(f"[Vuelos] Error al procesar el archivo: {e}")
        
    def _determinar_tipo_transporte(self, codigo_vuelo):
        codigo = str(codigo_vuelo).upper()
        if codigo.startswith("BUS"):
            return "TERRESTRE"
        elif codigo.startswith("FERRY"):
            return "MARÍTIMO"
        else:
            return "AÉREO"

    def _extraer_ciudades_y_horarios(self, vuelo_info, i, state, tipo):
        try:
            vuelo = vuelo_info.get('vuelo')

            if vuelo is None or pd.isna(vuelo):
                return None  # Vuelo no especificado

            # Si el vuelo es "NO" o "TBC", omitirlo sin error
            if str(vuelo).strip().upper() in ["NO", "TBC"]:
                return None

            # Regex para código de vuelo y aeropuertos
            expresion_vuelo = r'^(.+)\s([A-Z]{3})[-\s]([A-Z]{3})$'
            match = re.match(expresion_vuelo, vuelo)

            if not match:
                return None  # No cumple el formato esperado

            codigo_vuelo = match.group(1).strip()
            aeropuerto_salida = match.group(2)
            aeropuerto_llegada = match.group(3)

            fecha_vuelo = vuelo_info.get('fecha')
            if isinstance(fecha_vuelo, str):
                fecha_vuelo = pd.to_datetime(fecha_vuelo, errors='coerce', dayfirst=True)

            if pd.isna(fecha_vuelo):
                print(f"[ERROR] Fecha de vuelo inválida: {fecha_vuelo} | {codigo_vuelo} | {i}")
                return None

            hora = vuelo_info.get('hora', '')
            dia_siguiente = None  # Asegurar que siempre esté definido

            if isinstance(hora, str):
                hora = hora.strip().replace("–", "-").replace(" ", "-")

                # Formato de dos horas con opcional +1
                match_horas = re.match(r'^(\d{1,2}:\d{2})[-\s](\d{1,2}:\d{2})(\+\d+)?$', hora)

                if match_horas:
                    hora_salida_str = match_horas.group(1)
                    hora_llegada_str = match_horas.group(2)
                    dia_siguiente = match_horas.group(3)

                    hora_salida = datetime.combine(fecha_vuelo.date(), datetime.strptime(hora_salida_str, "%H:%M").time())
                    hora_llegada = datetime.combine(fecha_vuelo.date(), datetime.strptime(hora_llegada_str, "%H:%M").time())

                else:
                    # Caso de una sola hora (ej. 12:00:00), asumir solo hora de llegada
                    match_hora_unica = re.match(r'^(\d{1,2}:\d{2})$', hora)
                    if match_hora_unica:
                        hora_llegada_str = match_hora_unica.group(1)
                        hora_salida = None
                        hora_llegada = datetime.combine(fecha_vuelo.date(), datetime.strptime(hora_llegada_str, "%H:%M").time())
                    else:
                        #if str(hora).strip().upper() not in ["NO", "TBC"]:
                            #print(f"Error en la fila {i+3} | {state} | {tipo} | Hora inválida: {hora}")
                        return None  # No es un formato de hora válido

            elif isinstance(hora, time):
                hora_salida = None
                hora_llegada = datetime.combine(fecha_vuelo.date(), hora)
            else:
                return None

            # Ajuste si hay día siguiente (+1)
            if dia_siguiente:
                numero_de_dias = int(dia_siguiente.lstrip("+"))
                hora_llegada += timedelta(days=numero_de_dias)

            ciudad_salida = CITY_AIRPORT_CODES.get(aeropuerto_salida, "Desconocido")
            ciudad_llegada = CITY_AIRPORT_CODES.get(aeropuerto_llegada, "Desconocido")

            if hora_llegada is None:
                raise ValueError("Hora de llegada no puede ser nula.")

            return {
                'codigo_vuelo': codigo_vuelo,
                'ciudad_salida': ciudad_salida,
                'ciudad_llegada': ciudad_llegada,
                'fecha': fecha_vuelo,
                'hora_salida': hora_salida,
                'hora_llegada': hora_llegada
            }

        except Exception as e:
            print(f"Error al procesar el vuelo: {e} | HORA: {vuelo_info.get('hora')}")
            return None

    def _create_vuelos(self, file_path, vuelos_df, tripulantes_df, state, tipo):
        vuelos = []  # Lista para almacenar los vuelos creados
        errors, errors_message = check_and_clean(file_path, vuelos_df, state, tipo)

        try:
            if vuelos_df.empty or tripulantes_df.empty:
                print("No hay vuelos o tripulantes para procesar.")
                return [], []

            for i, (vuelo_row, tripulante_data) in enumerate(zip(vuelos_df.iterrows(), tripulantes_df.iterrows())):
                vuelo_row = vuelo_row[1]
                tripulante_data = tripulante_data[1]

                if pd.isna(tripulante_data['Pasaporte']):
                    continue

                tripulante = self.db_session.query(Tripulante).filter_by(pasaporte=tripulante_data['Pasaporte']).first()
                if not tripulante:
                    continue

                for vuelo_key in vuelo_row.index:
                    vuelo_info = vuelo_row[vuelo_key]
                    if pd.notna(vuelo_info) and isinstance(vuelo_info, dict) and vuelo_info.get('vuelo') != 'No disponible':
                        vuelo_info = self._extraer_ciudades_y_horarios(vuelo_info, i, state, tipo)
                        if vuelo_info is None or 'codigo_vuelo' not in vuelo_info:
                            continue

                        # Determinar tipo de transporte
                        tipo_transporte = self._determinar_tipo_transporte(vuelo_info['codigo_vuelo'])

                        # Buscar vuelo existente
                        vuelo = self.db_session.query(Vuelo).filter_by(
                            codigo=vuelo_info['codigo_vuelo'],
                            aeropuerto_salida=vuelo_info['ciudad_salida'],
                            aeropuerto_llegada=vuelo_info['ciudad_llegada'],
                            fecha=vuelo_info['fecha'],
                            hora_salida=vuelo_info['hora_salida']
                        ).first()

                        if not vuelo:
                            vuelo = Vuelo(
                                codigo=vuelo_info['codigo_vuelo'],
                                aeropuerto_salida=vuelo_info['ciudad_salida'],
                                aeropuerto_llegada=vuelo_info['ciudad_llegada'],
                                fecha=vuelo_info['fecha'],
                                hora_salida=vuelo_info['hora_salida'],
                                hora_llegada=vuelo_info['hora_llegada'],
                                tipo=tipo,
                                tipo_transporte=tipo_transporte  # Nuevo campo agregado
                            )
                            self.db_session.add(vuelo)
                            self.db_session.flush()
                            self.db_session.commit()
                            vuelos.append(vuelo)
                            # print(f"Vuelo creado {vuelo}")

                        # Asociar tripulante si no existe la relación
                        tripulante_vuelo_existente = self.db_session.query(TripulanteVuelo).filter_by(
                            tripulante_id=tripulante.tripulante_id, vuelo_id=vuelo.vuelo_id
                        ).first()

                        if not tripulante_vuelo_existente:
                            tripulante_vuelo = TripulanteVuelo(
                                tripulante_id=tripulante.tripulante_id,
                                vuelo_id=vuelo.vuelo_id
                            )
                            self.db_session.add(tripulante_vuelo)
                            self.db_session.flush()
                            self.db_session.commit()


                    else:
                        continue

            self.db_session.commit()
        except Exception as e:
            self.db_session.rollback()
            print(f"[ERROR] Error al crear vuelos o asignar tripulantes: {e}")

        return errors, errors_message

    def _extract_international_flights(self, excel_data, start_row, state):
        vuelos = []
        
        # Convertir los nombres de las columnas a cadenas y quitar espacios
        flight_columns = excel_data.loc[start_row].fillna("").astype(str).str.strip().str.lower().tolist()

        # Verificar las columnas con las que estamos trabajando
        #print("Columnas disponibles:", flight_columns)  # Imprimir las columnas para verificar qué se está cargando

        # Iterar sobre cada fila, comenzando desde la fila indicada
        for i in range(start_row + 2, excel_data.shape[0]):
            tripulante_vuelos = {}
            vuelo_num = 1
            
            # Iterar sobre las columnas de vuelos hasta que ya no existan
            while True:
                if state=="on":
                    vuelo_col = f'vuelo int {vuelo_num}'
                    fecha_col = f'fecha vuelo int {vuelo_num}'
                    hora_col = f'hora vuelo int {vuelo_num}'

                    #print(f"Fila {start_row} | i {i}")
                    
                    # Verificar si las columnas existen en el DataFrame
                    if vuelo_col in flight_columns and fecha_col in flight_columns and hora_col in flight_columns:    
                        col_idx_vuelo = flight_columns.index(vuelo_col)
                        col_idx_fecha = flight_columns.index(fecha_col)
                        col_idx_hora = flight_columns.index(hora_col)  
                        # print(f"{vuelo_col} | {fecha_col} | {hora_col}")

                        vuelo = excel_data.iloc[i, col_idx_vuelo]
                        fecha = excel_data.iloc[i, col_idx_fecha]
                        hora = excel_data.iloc[i, col_idx_hora]

                        vuelo = vuelo.strip() if isinstance(vuelo, str) else vuelo
                        fecha = fecha.strip() if isinstance(fecha, str) else fecha
                        hora = hora.strip() if isinstance(hora, str) else hora

                        if type(hora) == str:
                            if hora.replace(" ", "") == "":
                                hora = None
                            else:
                                hora = hora.strip().replace("-", " ")
                                #print(f"LA HORA ES {type(hora)} {hora}")

                        if vuelo not in ["NO", "TBC"] and not pd.isna(vuelo):
                            # print(f"(A) {i} {vuelo} | {fecha} | {hora}")
                            tripulante_vuelos[f'Vuelo {vuelo_num}'] = {
                                "vuelo": vuelo,
                                #"fecha": pd.to_datetime(fecha, errors='coerce'),
                                "fecha": fecha,
                                "hora": hora  # Mantener la hora como string, o usar pd.to_datetime si es necesario
                            }
                        else:
                            if pd.isna(vuelo):
                                # print(f"(B) {i} {vuelo} | {fecha} | {hora}")
                                print(f"[ERROR] Vuelo faltante en...")
                            elif vuelo in ["NO", "TBC"]:
                                # print(f"Vuelo {vuelo} omitido")
                                tripulante_vuelos[f'Vuelo {vuelo_num}'] = {
                                    "vuelo": vuelo if not pd.isna(vuelo) else None,
                                    "fecha": None,
                                    "hora": None
                                }
                                vuelo_num += 1
                                continue

                        # Incrementar el vuelo_num para buscar el siguiente conjunto
                        vuelo_num += 1
                    else:
                        break  # Detener la búsqueda si no se encuentra una de las columnas
                elif state=="off":
                    nro_regional_flight  = 'nro regional flight'
                    date_reg_flight = 'date reg flight'
                    hora_reg_flight = 'hora reg flight'

                    if nro_regional_flight in flight_columns and date_reg_flight in flight_columns and hora_reg_flight in flight_columns: 
                        col_idx_nro = flight_columns.index(nro_regional_flight)
                        col_idx_date = flight_columns.index(date_reg_flight)
                        col_idx_hora = flight_columns.index(hora_reg_flight)

                        nro = excel_data.iloc[i, col_idx_nro]
                        date = excel_data.iloc[i, col_idx_date]
                        hora = excel_data.iloc[i, col_idx_hora]

                        # print(f"{nro} | {state}")

                        if pd.notna(nro) and pd.notna(date) and pd.notna(hora):
                            tripulante_vuelos[f'Vuelo {vuelo_num}'] = {
                                "vuelo": nro,
                                #"date": pd.to_datetime(date, format='%d-%m-%Y', errors='coerce'),
                                "fecha": date,
                                "hora": hora  # Mantener la hora como string, o usar pd.to_datetime si es necesario
                            }
                        elif nro.lower() == "no":
                            tripulante_vuelos[f'Vuelo {vuelo_num}'] = {
                                "vuelo": 'NO',
                                "fecha": None,
                                "hora": None  # Mantener la hora como string, o usar pd.to_datetime si es necesario
                            }
                            vuelo_num += 1
                        else:
                            tripulante_vuelos[f'Vuelo {vuelo_num}'] = {
                                "vuelo": 'Desconocido',
                                "fecha": None,
                                "hora": 'Desconocido'  # Mantener la hora como string, o usar pd.to_datetime si es necesario
                            }
                        vuelo_num += 1
                        # break
                    else:
                        break

            # Solo agregar el vuelo si se encontraron vuelos válidos para el tripulante
            if tripulante_vuelos:
                vuelos.append(tripulante_vuelos)

        # Verificar si se encontraron vuelos
        if len(vuelos) == 0:
            print("No se encontraron vuelos internacionales en las filas procesadas.")
        else:
            print(f"{len(vuelos)} vuelos internacionales procesados. ({state})")
            
        return pd.DataFrame(vuelos)

    def _extract_flights(self, excel_data, start_row, state):
        vuelos = []
        
        # Convertir los nombres de las columnas a cadenas y quitar espacios
        vuelos_columns = excel_data.loc[start_row].dropna().str.lower().tolist()

        # Mapear los estados a los tipos de vuelo correspondientes
        state_columns = {
            "INTERNACIONAL": ['nro international flight', 'date international flight', 'hora international flight'],
            "DOMESTICO": ['nro domestic flight', 'date domestic flight', 'hora domestic flight'],
            "REGIONAL": ['nro regional flight', 'date regional flight', 'hora regional flight']
        }

        # Obtener las columnas correctas para el estado dado
        nro_flight, date_flight, hora_flight = state_columns.get(state, [None, None, None])

        # Verificar si las columnas existen en el DataFrame
        if nro_flight not in vuelos_columns or date_flight not in vuelos_columns or hora_flight not in vuelos_columns:
            print(f"Columnas para {state} no encontradas.")
            return pd.DataFrame()  # Retornar DataFrame vacío si no hay columnas

        # Obtener los índices de las columnas
        col_idx_nro_flight = vuelos_columns.index(nro_flight)
        col_idx_date_flight = vuelos_columns.index(date_flight)
        col_idx_hora_flight = vuelos_columns.index(hora_flight)

        # Iterar sobre cada fila, comenzando desde la fila indicada
        for i in range(start_row + 2, excel_data.shape[0]):
            tripulante_vuelos = {}
            vuelos_num = 1
            
            # Extraer la información de vuelo, permitiendo valores nulos
            nro_flight_value = excel_data.iloc[i, col_idx_nro_flight] if col_idx_nro_flight is not None else None
            date_flight_value = excel_data.iloc[i, col_idx_date_flight] if col_idx_date_flight is not None else None
            hora_flight_value = excel_data.iloc[i, col_idx_hora_flight] if col_idx_hora_flight is not None else None

            # print(f"{state} | {nro_flight_value} | {date_flight_value} | {hora_flight_value}")

            # Incluso si los valores son nulos, agregar los vuelos con 'NaN' o entradas vacías
            if nro_flight_value not in ["NO", "TBC"] and not pd.isna(nro_flight_value):
                tripulante_vuelos[f'Vuelo {vuelos_num}'] = {
                    "vuelo": nro_flight_value if pd.notna(nro_flight_value) else 'No disponible',
                    #"fecha": pd.to_datetime(date_flight_value, errors='coerce') if pd.notna(date_flight_value) else 'No disponible',
                    "fecha": date_flight_value if pd.notna(date_flight_value) else 'No disponible',
                    "hora": hora_flight_value if pd.notna(hora_flight_value) else 'No disponible'
                }
                vuelos_num += 1  # Incrementar el número de vuelo para el siguiente
            else:
                if pd.isna(nro_flight_value):
                    # print(f"(B) {i} {vuelo} | {fecha} | {hora}")
                    tripulante_vuelos[f'Vuelo {vuelos_num}'] = {
                        "vuelo": "NO",
                        "fecha": None,
                        "hora": None
                    }
                    vuelos_num += 1 
                    print(f"[ERROR] Vuelo faltante")
                elif nro_flight_value in ["NO", "TBC"]:
                    # print(f"Vuelo {vuelo} omitido")
                    # print(f"El vuelo es {nro_flight_value}")
                    tripulante_vuelos[f'Vuelo {vuelos_num}'] = {
                        "vuelo": "NO",
                        #"fecha": pd.to_datetime(date_flight_value, errors='coerce') if pd.notna(date_flight_value) else 'No disponible',
                        "fecha": None,
                        "hora": None
                    }
                    vuelos_num += 1  # Incrementar el número de vuelo para el siguiente
                    vuelos.append(tripulante_vuelos)
                    continue

            # Agregar la información del vuelo, aunque sea incompleta
            vuelos.append(tripulante_vuelos)

        # Verificar si se encontraron vuelos
        if len(vuelos) == 0:
            print(f"No se encontraron vuelos {state} en las filas procesadas.")
        
        return pd.DataFrame(vuelos)
    
def check_and_clean(file_path, vuelos_df, state, tipo):
    errors_to_check = []

    # print(f"El tipo es {tipo}")

    errors = []
    errors_message = []

    column_letters_excel = {}

    def preload_column_letters():
        workbook = load_workbook(file_path)
        sheet = workbook[state]
        for col in sheet.iter_cols(1, sheet.max_column, 1, 1):
            header = col[0].value
            if header:
                header_normalized = header.strip().lower()
                column_letters_excel[header_normalized] = get_column_letter(col[0].column)

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
    
    def get_column(df, columna, tipo_dato="fecha"):
        indices = {key: idx for idx, key in enumerate(df.keys())}
        x = indices[columna]

        if tipo == "INTERNACIONAL":
            if tipo_dato == "fecha":
                header_name = f"Fecha Vuelo Int {x+1}"
            elif tipo_dato == "hora":
                header_name = f"Hora Vuelo Int {x+1}"
            else:
                return "?"
        elif tipo == "DOMESTICO":
            header_name = "Date Domestic Flight" if tipo_dato == "fecha" else "Hora Domestic Flight"
        elif tipo == "REGIONAL":
            header_name = "Date Regional Flight" if tipo_dato == "fecha" else "Hora Regional Flight"
        else:
            return "?"

        return column_letters_excel.get(header_name.strip().lower(), "?")
    
    def is_valid_hour(hora_str):
        if isinstance(hora_str, str):
            hora_str = hora_str.strip().replace("–", "-").replace("—", "-")
            hora_str = re.sub(r'\s+', ' ', hora_str)  # reemplaza múltiples espacios por uno

            # Formato simple "HH:MM"
            if re.match(r'^\d{1,2}:\d{2}$', hora_str):
                return True
            # Formato "HH:MM-HH:MM"
            if re.match(r'^\d{1,2}:\d{2}-\d{1,2}:\d{2}$', hora_str):
                return True
            # Formato "HH:MM HH:MM+1"
            if re.match(r'^\d{1,2}:\d{2} \d{1,2}:\d{2}\+\d+$', hora_str):
                return True
            if re.match(r'^\d{1,2}:\d{2}-\d{1,2}:\d{2}$', hora_str):
                return True
            # Formato con +1, como "HH:MM+1"
            if re.match(r'^\d{1,2}:\d{2}\+\d+$', hora_str):
                return True
            # Formato completo: "HH:MM-HH:MM+1"
            if re.match(r'^\d{1,2}:\d{2}-\d{1,2}:\d{2}\+\d+$', hora_str):
                return True
            # Formato "HH:MM HH:MM"
            if re.match(r'^\d{1,2}:\d{2} \d{1,2}:\d{2}$', hora_str):
                return True
            return False

        elif isinstance(hora_str, time):
            return True

        return False

    def check_date():        
        df = pd.DataFrame(vuelos_df)

        for columna in vuelos_df:
            #print(f"Columna: {columna} | {state} | {tipo}")
            vuelo = df[columna].tolist()  # Convertir la columna en una lista
            for idx, registro in enumerate(vuelo):  # Iterar sobre los diccionarios
                if pd.isna(registro):
                    continue
                elif str(registro.get('vuelo')).lower() != 'no':
                    if str(registro.get('vuelo')).lower() == 'tbc':
                        continue

                    if isinstance(registro.get('fecha'), str):
                        if looks_like_date(registro.get('fecha')):
                            value = registro.get('fecha')
                            value = clean_value(value)

                            if not is_valid_date(value):
                                print(f"NE 1 {state} | Registro {idx+3} en '{columna}': Vuelo es {value}")
                                column_letter = get_column(df, columna)
                                column_number = column_index_from_string(column_letter)
                                cell_value = sheet_loaded.cell(row=1, column=column_number).value
                                errors_to_check.append([idx+3, columna])
                                errors.append([idx+3, column_letter])
                                errors_message.append(f"Fecha inexistente en {cell_value} [{idx+3},{column_letter}]")
                    else:
                        #print(f"{idx} | {registro.get('Date Pickup')}")
                        value = registro.get('fecha')
                        value = clean_value(value)
                        
                        if registro.get('fecha') == None or pd.isna(registro.get('fecha')):
                            if str(registro.get('vuelo')).lower() != 'no' and not pd.isna(registro.get('vuelo')):
                                print(f"ER {state} | Registro {idx+3} en '{columna}': Vuelo es {registro.get('vuelo')}")
                                column_letter = get_column(df, columna)
                                column_number = column_index_from_string(column_letter)
                                cell_value = sheet_loaded.cell(row=1, column=column_number).value
                                errors_to_check.append([idx+3, columna])
                                errors.append([idx+3, column_letter])
                                errors_message.append(f"Formato incorrecto en {cell_value} [{idx+3},{column_letter}]")
                                continue

                            #print(f"{type(registro.get('vuelo'))} | {registro.get('vuelo')}")
                            #print(f"ER | Registro {idx+2} en '{columna}': Vuelo es {registro.get('fecha')}")
                            print(f"ER {state} | Registro {idx+3} en '{columna}': Vuelo está vacío")
                            column_letter = get_column(df, columna)
                            column_number = column_index_from_string(column_letter)
                            cell_value = sheet_loaded.cell(row=1, column=column_number).value
                            errors_to_check.append([idx+3, columna])
                            errors.append([idx+3, column_letter])
                            errors_message.append(f"Dato faltante en {cell_value} [{idx+3},{column_letter}]")
                        else:
                            if not is_valid_date(value):
                                print(f"NE 2 {state} | Registro {idx+3} en '{columna}': Vuelo es {registro.get('fecha')}")
                                column_letter = get_column(df, columna)
                                column_number = column_index_from_string(column_letter)
                                cell_value = sheet_loaded.cell(row=1, column=column_number).value
                                errors_to_check.append([idx+3, columna])
                                errors.append([idx+3, column_letter])
                                errors_message.append(f"Fecha inexistente en {cell_value} [{idx+3},{column_letter}]")

                    
                    if isinstance(registro.get('hora'), str):
                        hora_valor = registro.get('hora')
                        if not is_valid_hour(hora_valor) and hora_valor != "TBC":
                            column_letter = get_column(df, columna, tipo_dato="hora")

                            if column_letter == "?":
                                print(f"[ERROR] No se encontró el header para columna '{columna}' en tipo '{tipo}'")
                                continue  # o raise, dependiendo del flujo

                            column_number = column_index_from_string(column_letter)
                            cell_value = sheet_loaded.cell(row=1, column=column_number).value
                            errors_to_check.append([idx+3, columna])
                            errors.append([idx+3, column_letter])
                            errors_message.append(f"Hora inválida en {cell_value} [{idx+3},{column_letter}]")
                else:
                    if str(registro.get('vuelo')).lower() != 'tbc' and str(registro.get('vuelo')).lower() != 'no':
                        print(f"{state} | Registro {idx+3} en '{columna}': Vuelo es {registro.get('vuelo')}")
                    # if registro.get('vuelo').lower() == 'no':
                    #     continue
                    # else:
                    #     print(f"Registro {idx+2} en '{columna}': Vuelo está vacío")

    preload_column_letters()
    workbook = load_workbook(file_path, data_only=True)
    sheet_loaded = workbook[state]

    check_date()

    return errors, errors_message