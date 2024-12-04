from datetime import datetime, timedelta
import re
import pandas as pd
from sqlalchemy.orm import Session
import traceback
from datetime import time
from sqlalchemy import func, and_
from PyQt6.QtWidgets import QMessageBox
from app.models import Buque, Tripulante, Vuelo, EtaCiudad, Viaje, TripulanteVuelo, Hotel, TripulanteHotel, Restaurante, TripulanteRestaurante, Transporte, TripulanteTransporte, TripulanteAsistencia

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

            return hoteles_on, hoteles_off
        except Exception as e:
            raise Exception(f"[Hoteles] Error al procesar el archivo: {e}")
        
    def _create_hotel(self, hotel_df, tripulantes_df):
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

                    for hotel_info in hotel_entries:  # Iterar sobre todos los hoteles asignados al tripulante
                        #print(hotel_entries)
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
                            #print(f"Creando nuevo hotel: {hotel_info['nombre_hotel']}, Ciudad: {hotel_info['ciudad']}")
                            hotel = Hotel(
                                nombre=hotel_info['nombre_hotel'].strip(),
                                ciudad=hotel_info['ciudad'].strip(),
                            )
                            self.db_session.add(hotel)
                            self.db_session.flush()  # Obtener el ID del hotel recién creado
                        else:
                            hotel = existing_hotel

                        # Verificar si ya existe la relación entre tripulante y hotel
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
                                y = 37 + (5 * hotel_info['nro']) - 3
                                letra_columna = self.indice_a_letra_columna(y)
                                print(f"Se ha producido un error con el check in [{x}, {letra_columna}]")
                                continue
                            if hotel_info['check_out'] == None:
                                y = 37 + (5 * hotel_info['nro']) - 2
                                letra_columna = self.indice_a_letra_columna(y)
                                print(f"Se ha producido un error con el check out [{x}, {letra_columna}]")
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
                    print(f"Datos del tripulante en la fila: {tripulante_data.to_dict()}")
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

    def _extraer_hoteles_fechas(self, hotel_df):
        hoteles_info = []

        for _, row in hotel_df.iterrows():
            hotel_entries = []

            found_valid_hotel = False
            
            # Procesar cada hotel en la fila
            for hotel_key in row.index:
                hotel_info = row[hotel_key]

                if isinstance(hotel_info, dict):
                    check_in = pd.to_datetime(hotel_info.get('check_in'), errors='coerce')
                    check_out = pd.to_datetime(hotel_info.get('check_out'), errors='coerce')

                    # Convertir NaT a None
                    check_in = None if pd.isna(check_in) else check_in
                    check_out = None if pd.isna(check_out) else check_out
                    
                    # Crear un diccionario para la información del hotel
                    hotel_entry = {
                        'nombre_hotel': hotel_info.get('nombre_hotel'),
                        'categoria': hotel_info.get('categoria'),
                        'ciudad': hotel_info.get('hotel').split()[-1] if 'hotel' in hotel_info else 'Desconocida',
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
                    if pd.notna(categoria) and pd.notna(hotel):
                        tripulante_hotels[f'Hotel {hotel_num}'] = {
                            "categoria": categoria,
                            "hotel": hotel,
                            "check_in": pd.to_datetime(check_in, errors='coerce'),
                            "check_out": pd.to_datetime(check_out, errors='coerce'),
                            "habitacion": habitacion,
                            "nombre_hotel": nombre_hotel,
                            "nro": hotel_num
                        }
                        found_hotels = True  # Se encontró al menos un hotel

                    # Incrementar el número de hotel para buscar el siguiente conjunto
                    hotel_num += 1
                else:
                    break  # Detener la búsqueda si no se encuentra una de las columnas

            # Si no se encontraron hoteles, agregar un registro para ese tripulante
            if not found_hotels:
                tripulante_hotels['Hotel 1'] = {
                    "categoria": None,
                    "hotel": "SIN HOTEL",
                    "check_in": None,
                    "check_out": None,
                    "habitacion": None,
                    "nombre_hotel": "SIN HOTEL",
                    "nro": None
                }

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