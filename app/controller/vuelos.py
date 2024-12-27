from datetime import datetime, timedelta, time
import calendar
import re
import pandas as pd
from sqlalchemy.orm import Session
from app.models import Tripulante, Vuelo, TripulanteVuelo
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

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

class Vuelos:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def vuelos_main(self, file_path):
        try:
            # Leer la hoja ON del archivo Excel
            excel_data_on = pd.read_excel(file_path, sheet_name='ON', header=None)

            vuelos_internacionales_on = self._extract_international_flights(excel_data_on, start_row=0, state="on")
            vuelos_internacionales_on.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            vuelos_domesticos_on = self._extract_flights(excel_data_on, start_row=0, state="DOMESTICO")
            vuelos_domesticos_on.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            vuelos_regionales_on = self._extract_flights(excel_data_on, start_row=0, state="REGIONAL")
            vuelos_regionales_on.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            excel_data_off = pd.read_excel(file_path, sheet_name='OFF', header=None)

            vuelos_internacionales_off = self._extract_flights(excel_data_off, start_row=0, state="INTERNACIONAL")
            vuelos_internacionales_off.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            vuelos_domesticos_off = self._extract_flights(excel_data_off, start_row=0, state="DOMESTICO")
            vuelos_domesticos_off.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            vuelos_regionales_off = self._extract_flights(excel_data_off, start_row=0, state="REGIONAL")
            vuelos_regionales_off.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            return vuelos_internacionales_on, vuelos_internacionales_off, vuelos_domesticos_on, vuelos_domesticos_off, vuelos_regionales_on, vuelos_regionales_off
        except Exception as e:
            raise Exception(f"[Vuelos] Error al procesar el archivo: {e}")

    def _extraer_ciudades_y_horarios(self, vuelo_info, i):        
        try:
            vuelo = vuelo_info['vuelo']

            # Verifica si el vuelo es NaN o None
            if vuelo is None or pd.isna(vuelo):
                #print("Vuelo es NaN o None. Omitiendo...")
                return None  

            # Utilizar una expresión regular para capturar el código de vuelo y los aeropuertos
            expresion_vuelo = r'^(.+)\s([A-Z]{3})[-\s]([A-Z]{3})$'  # Acepta '-' o ' ' como separador
            match = re.match(expresion_vuelo, vuelo)

            if match:
                codigo_vuelo = match.group(1).strip()  # Código de vuelo (puede ser solo letras o con número)
                aeropuerto_salida = match.group(2)     # Ciudad de origen
                aeropuerto_llegada = match.group(3)    # Ciudad de destino
            else:
                return None

            # Obtener la fecha del vuelo
            fecha_vuelo = vuelo_info['fecha']  # Se espera que sea un objeto Timestamp

            # Verificar si 'hora' es una cadena o un objeto datetime.time
            hora = vuelo_info.get('hora', '')
            #print(f"la fecha es 1: {fecha_vuelo} ({type(fecha_vuelo)})")
            #print(f"la hora es 1: {hora} ({type(hora)})")
            if isinstance(hora, str):
                # Reemplazar caracteres no estándar y limpiar espacios
                hora = hora.strip()
                hora = hora.replace("–", "-").replace(" ", "-").strip()

                # Detectar y corregir si los horarios están concatenados sin espacio
                match_horas_concatenadas = re.match(r'^(\d{1,2}:\d{2})(\d{1,2}:\d{2})(\+1)?$', hora)
                if match_horas_concatenadas:
                    hora = f"{match_horas_concatenadas.group(1)} {match_horas_concatenadas.group(2)}"
                    if match_horas_concatenadas.group(3):
                        hora += "+1"
                    #print(f"Hora reparada automáticamente: '{hora}'")

                match_horas = re.match(r'^(\d{1,2}:\d{2})[-\s](\d{1,2}:\d{2})(\+1)?$', hora)
                #if not match_horas:
                    #if isinstance(hora, str) and hora != "TBC":
                        #print(hora)
                        #hora_llegada, hora_salida = match_horas.split('-')
                    #else:
                        #print(f"Formato de hora inválido: '{hora}'")
                        #return None
                
                hora_salida = match_horas.group(1)
                hora_llegada = match_horas.group(2)
                dia_siguiente = match_horas.group(3)  # Detectar si hay '+1'

                hora_salida = datetime.combine(fecha_vuelo.date(), datetime.strptime(hora_salida, "%H:%M").time())
                hora_llegada = datetime.combine(fecha_vuelo.date(), datetime.strptime(hora_llegada, "%H:%M").time())
            # elif isinstance(hora, datetime.time):
            #     print(f"Hora ya es un objeto datetime.time: {hora}")
            #     hora_salida = hora
            #     hora_llegada = None
            elif isinstance(hora, time):
                #print(f"la hora es 2: {hora}")
                hora_salida = None
                hora_llegada = hora
                hora_llegada = datetime.combine(fecha_vuelo.date(), hora)
            else:
                print("Error en esta parte")
                #print(f"Error en la fila {i+2}")

            # Convertir horas a objetos datetime
            # print("Intentando convertir hora de salida y llegada a datetime...")
            #print(f"{hora_llegada} | {hora_salida}")

            # Ajustar fecha de llegada si contiene '+1'
            if dia_siguiente:
                hora_llegada += timedelta(days=1)
                # print(f"Hora llegada ajustada por día siguiente: {hora_llegada}")

            # Buscar las ciudades en el diccionario de aeropuertos
            ciudad_salida = CITY_AIRPORT_CODES.get(aeropuerto_salida, "Desconocido")
            ciudad_llegada = CITY_AIRPORT_CODES.get(aeropuerto_llegada, "Desconocido")
            # print(f"Ciudad salida: {ciudad_salida}, Ciudad llegada: {ciudad_llegada}")

            if hora_llegada is None:
                raise ValueError("Hora de llegada no puede ser nula.")

            #print("Retornando")

            # Retornar el resultado
            return {
                'codigo_vuelo': codigo_vuelo,
                'ciudad_salida': ciudad_salida,
                'ciudad_llegada': ciudad_llegada,
                'fecha': fecha_vuelo, 
                'hora_salida': hora_salida, 
                'hora_llegada': hora_llegada  
            }

        except Exception as e:
            print(f"Error al procesar el vuelo: {e} | HORA : {vuelo_info['hora']} {vuelo_info.loc['hora']}")
            ###traceback.print_exc()  # Imprime el seguimiento completo del error
            # print("=== Depuración final ===")
            # print(f"Datos actuales de vuelo_info: {vuelo_info}")
            return None

    def _create_vuelos(self, file_path, vuelos_df, tripulantes_df, state, tipo):
        vuelos = []  # Lista para almacenar los vuelos creados
        errors, errors_message = check_and_clean(file_path, vuelos_df, state, tipo)

        try:
            if vuelos_df.empty or tripulantes_df.empty:
                #print("No hay vuelos o tripulantes para procesar.")
                return []

            # Iterar sobre cada fila de los dataframes correspondientes de vuelos y tripulantes
            for i, (vuelo_row, tripulante_data) in enumerate(zip(vuelos_df.iterrows(), tripulantes_df.iterrows())):
                vuelo_row = vuelo_row[1]  # Acceder a la serie de la fila
                tripulante_data = tripulante_data[1]  # Acceder a la serie de la fila

                if pd.isna(tripulante_data['Pasaporte']):
                    continue

                tripulante = self.db_session.query(Tripulante).filter_by(pasaporte=tripulante_data['Pasaporte']).first()

                if not tripulante:
                    #print(f"No se encontró tripulante con pasaporte {tripulante_data['Pasaporte']} en la fila {i}.")
                    continue

                # Iterar sobre los vuelos correspondientes a este tripulante (en la misma fila)
                for vuelo_key in vuelo_row.index:
                    vuelo_info = vuelo_row[vuelo_key]  # Obtener la información del vuelo de la fila de vuelos
                    # Verificar que haya información válida sobre el vuelo
                    if pd.notna(vuelo_info) and isinstance(vuelo_info, dict) and vuelo_info.get('vuelo') != 'No disponible':
                        #print(i)
                        vuelo_info = self._extraer_ciudades_y_horarios(vuelo_info, i)

                        #print(f"Vuelo info es: {vuelo_info}")

                        if vuelo_info is None or 'codigo_vuelo' not in vuelo_info:
                            #print(f"Omitiendo vuelo {vuelo_key} en la fila {i} debido a datos faltantes. {vuelo_info}")
                            continue

                        # Buscar el vuelo por código y fecha
                        vuelo = self.db_session.query(Vuelo).filter_by(
                            codigo=vuelo_info['codigo_vuelo'],
                            aeropuerto_salida=vuelo_info['ciudad_salida'],
                            aeropuerto_llegada=vuelo_info['ciudad_llegada'],
                            fecha=vuelo_info['fecha'],
                            hora_salida=vuelo_info['hora_salida']
                        ).first()

                        #print(f"HORA LLEGADA: {vuelo_info['hora_llegada']}")

                        if not vuelo:
                            # Crear el vuelo si no existe
                            vuelo = Vuelo(
                                codigo=vuelo_info['codigo_vuelo'],
                                aeropuerto_salida=vuelo_info['ciudad_salida'],
                                aeropuerto_llegada=vuelo_info['ciudad_llegada'],
                                fecha=vuelo_info['fecha'],
                                hora_salida=vuelo_info['hora_salida'],
                                hora_llegada=vuelo_info['hora_llegada'],
                                tipo=tipo
                            )
                            self.db_session.add(vuelo)
                            self.db_session.flush()  # Asegurar que el vuelo esté disponible en la base de datos
                            vuelos.append(vuelo)  # Agregar el vuelo a la lista de vuelos
                            #print(f"Vuelo creado {vuelo}")

                        # Verificar si ya existe una asociación entre el tripulante y el vuelo
                        tripulante_vuelo_existente = self.db_session.query(TripulanteVuelo).filter_by(
                            tripulante_id=tripulante.tripulante_id, vuelo_id=vuelo.vuelo_id
                        ).first()

                        if not tripulante_vuelo_existente:
                            # Asociar el tripulante al vuelo si no existe la asociación
                            tripulante_vuelo = TripulanteVuelo(
                                tripulante_id=tripulante.tripulante_id,
                                vuelo_id=vuelo.vuelo_id
                            )
                            self.db_session.add(tripulante_vuelo)
                            self.db_session.flush()  # Confirmar la asociación sin hacer commit completo

                    else:
                        # No hay información válida para este vuelo en la fila
                        continue

            # Confirmar todos los cambios al final
            self.db_session.commit()
        except Exception as e:
            #print(f"Error al crear vuelos o asignar tripulantes: {e}")
            self.db_session.rollback()

        return errors, errors_message

    def _extract_international_flights(self, excel_data, start_row, state):
        vuelos = []
        
        # Convertir los nombres de las columnas a cadenas y quitar espacios
        flight_columns = excel_data.loc[start_row].dropna().str.lower().tolist()
        #print(flight_columns)

        # Verificar las columnas con las que estamos trabajando
        #print("Columnas disponibles:", flight_columns)  # Imprimir las columnas para verificar qué se está cargando

        # Iterar sobre cada fila, comenzando desde la fila indicada
        for i in range(start_row + 1, excel_data.shape[0]):
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
                        #print(f"{vuelo_col} | {fecha_col} | {hora_col}")

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

                        #print(f"{i} {vuelo} | {fecha} | {hora}")

                        tripulante_vuelos[f'Vuelo {vuelo_num}'] = {
                            "vuelo": vuelo,
                            #"fecha": pd.to_datetime(fecha, errors='coerce'),
                            "fecha": fecha,
                            "hora": hora  # Mantener la hora como string, o usar pd.to_datetime si es necesario
                        }

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

                        if pd.notna(nro) and pd.notna(date) and pd.notna(hora):
                            tripulante_vuelos[f'Vuelo {vuelo_num}'] = {
                                "vuelo": nro,
                                #"date": pd.to_datetime(date, format='%d-%m-%Y', errors='coerce'),
                                "fecha": date,
                                "hora": hora  # Mantener la hora como string, o usar pd.to_datetime si es necesario
                            }
                        else:
                            tripulante_vuelos[f'Vuelo {vuelo_num}'] = {
                                "vuelo": 'Desconocido',
                                "fecha": None,
                                "hora": 'Desconocido'  # Mantener la hora como string, o usar pd.to_datetime si es necesario
                            }

                        break
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
        for i in range(start_row + 1, excel_data.shape[0]):
            tripulante_vuelos = {}
            vuelos_num = 1
            
            # Extraer la información de vuelo, permitiendo valores nulos
            nro_flight_value = excel_data.iloc[i, col_idx_nro_flight] if col_idx_nro_flight is not None else None
            date_flight_value = excel_data.iloc[i, col_idx_date_flight] if col_idx_date_flight is not None else None
            hora_flight_value = excel_data.iloc[i, col_idx_hora_flight] if col_idx_hora_flight is not None else None

            # Incluso si los valores son nulos, agregar los vuelos con 'NaN' o entradas vacías
            tripulante_vuelos[f'Vuelo {vuelos_num}'] = {
                "vuelo": nro_flight_value if pd.notna(nro_flight_value) else 'No disponible',
                #"fecha": pd.to_datetime(date_flight_value, errors='coerce') if pd.notna(date_flight_value) else 'No disponible',
                "fecha": date_flight_value if pd.notna(date_flight_value) else 'No disponible',
                "hora": hora_flight_value if pd.notna(hora_flight_value) else 'No disponible'
            }
            vuelos_num += 1  # Incrementar el número de vuelo para el siguiente

            # Agregar la información del vuelo, aunque sea incompleta
            vuelos.append(tripulante_vuelos)

        # Verificar si se encontraron vuelos
        if len(vuelos) == 0:
            print(f"No se encontraron vuelos {state} en las filas procesadas.")
        
        return pd.DataFrame(vuelos)
    
def check_and_clean(file_path, vuelos_df, state, tipo):
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

    def check_date():        
        df = pd.DataFrame(vuelos_df)
        for columna in vuelos_df:
            #print(f"Columna: {columna} | {state} | {tipo}")
            vuelo = df[columna].tolist()  # Convertir la columna en una lista
            for idx, registro in enumerate(vuelo):  # Iterar sobre los diccionarios
                if str(registro.get('vuelo')).lower() != 'no':
                    if str(registro.get('vuelo')).lower() == 'tbc':
                        continue

                    if isinstance(registro.get('fecha'), str):
                        if looks_like_date(registro.get('fecha')):
                            value = registro.get('fecha')
                            value = clean_value(value)

                            if not is_valid_date(value):
                                print(f"NE 1 {state} | Registro {idx+2} en '{columna}': Vuelo es {value}")
                                column_letter = get_column(df, columna)
                                errors_to_check.append([idx+2, columna])
                                errors.append([idx+2, column_letter])
                                errors_message.append(f"Fecha inexistente [{idx+2},{column_letter}]")
                    else:
                        #print(f"{idx} | {registro.get('Date Pickup')}")
                        value = registro.get('fecha')
                        value = clean_value(value)
                        
                        if registro.get('fecha') == None or pd.isna(registro.get('fecha')):
                            if str(registro.get('vuelo')).lower() != 'no' and not pd.isna(registro.get('vuelo')):
                                print(f"ER {state} | Registro {idx+2} en '{columna}': Vuelo es {registro.get('vuelo')}")
                                column_letter = get_column(df, columna)
                                errors_to_check.append([idx+2, columna])
                                errors.append([idx+2, column_letter])
                                errors_message.append(f"Formato incorrecto [{idx+2},{column_letter}]")
                                continue

                            #print(f"{type(registro.get('vuelo'))} | {registro.get('vuelo')}")
                            #print(f"ER | Registro {idx+2} en '{columna}': Vuelo es {registro.get('fecha')}")
                            print(f"ER {state} | Registro {idx+2} en '{columna}': Vuelo está vacío")
                            column_letter = get_column(df, columna)
                            errors_to_check.append([idx+2, columna])
                            errors.append([idx+2, column_letter])
                            errors_message.append(f"Dato faltante [{idx+2},{column_letter}]")
                        else:
                            if not is_valid_date(value):
                                print(f"NE 2 {state} | Registro {idx+2} en '{columna}': Vuelo es {registro.get('fecha')}")
                                column_letter = get_column(df, columna)
                                errors_to_check.append([idx+2, columna])
                                errors.append([idx+2, column_letter])
                                errors_message.append(f"Fecha inexistente [{idx+2},{column_letter}]")
                else:
                    if str(registro.get('vuelo')).lower() != 'tbc' and str(registro.get('vuelo')).lower() != 'no':
                        print(f"{state} | Registro {idx+2} en '{columna}': Vuelo es {registro.get('vuelo')}")
                    # if registro.get('vuelo').lower() == 'no':
                    #     continue
                    # else:
                    #     print(f"Registro {idx+2} en '{columna}': Vuelo está vacío")
            
    check_date()
    return errors, errors_message