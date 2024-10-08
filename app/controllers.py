from datetime import datetime
import re
import pandas as pd
from sqlalchemy.orm import Session
from PyQt6.QtWidgets import QMessageBox
from app.models import Buque, Tripulante, Vuelo, EtaCiudad, Viaje, TripulanteVuelo

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
    'EZE': 'BUENOS AIRES'
}

# Definir los nombres de las columnas antes de llamar al método
buque_on_columns = ['Owner', 'Vessel', 'Date arrive CL', 'ETA Vessel', 'ETD Vessel', 'Puerto a embarcar']
buque_off_columns = ['Owner', 'Vessel', 'Date First Flight', 'ETA Vessel', 'ETD Vessel', 'Puerto a desembarcar']

tripulante_columns = ['First name', 'Last name', 'Gender', 'Nacionalidad', 'Position', 'Pasaporte', 'DOB']

def buscar_buque_id(nombre_buque, session):
    # Asegúrate de que el campo 'nombre' es el correcto
    buque = session.query(Buque).filter(Buque.nombre.ilike(nombre_buque)).first()  # Usando ilike para coincidencias sin distinción entre mayúsculas y minúsculas

    if buque:
        #print(f"Buque encontrado: {nombre_buque} con ID: {buque.buque_id}")
        return buque.buque_id
    else:
        raise ValueError(f"Buque {nombre_buque} no encontrado en la base de datos.")
                    

class Controller:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_city_list(self):
        return ["Punta Arenas", "Santiago", "Puerto Montt", "Valparaiso", "Valdivia", 'Puerto Williams']

    def process_excel_file(self, file_path):
        try:
            # Leer la hoja ON del archivo Excel
            excel_data_on = pd.read_excel(file_path, sheet_name='ON', header=None)

            # Extraer los datos de los buque ON (desde fila 14, índice 13)
            buque_on = self.read_all_rows(excel_data_on, start_row=1, column_range=slice(0, 6), column_names=buque_on_columns) 
            buque_on.reset_index(drop=True, inplace=True)  # Reiniciar el índice
            
            # Extraer los datos de tripulantes ON (fila 14)
            tripulantes_on = self.read_all_rows(excel_data_on, start_row=1, column_range=slice(9, 16), column_names=tripulante_columns)  
            tripulantes_on.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            # Procesar vuelos internacionales ON
            vuelos_internacionales_on = self._extract_international_flights(excel_data_on, start_row=0, state="on")
            vuelos_internacionales_on.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            #Procesar hoteles ON
            hoteles_on = self._extract_hotels(excel_data_on, start_row=0, state="on")

            # Leer la hoja OFF del archivo Excel
            excel_data_off = pd.read_excel(file_path, sheet_name='OFF', header=None)

            # Extraer los datos de los buque OFF (desde fila 22, índice 21)
            buque_off = self.read_all_rows(excel_data_off, start_row=1, column_range=slice(0, 6), column_names=buque_off_columns)
            buque_off.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            # Extraer los datos de tripulantes OFF (fila 22)
            tripulantes_off = self.read_all_rows(excel_data_off, start_row=1, column_range=slice(9, 16), column_names=tripulante_columns) 
            tripulantes_off.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            # Procesar vuelos internacionales OFF
            vuelos_internacionales_off = self._extract_international_flights(excel_data_off, start_row=0, state="off")
            vuelos_internacionales_off.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            #Procesar hoteles
            hoteles_off = self._extract_hotels(excel_data_off, start_row=0, state="on")

            # Verificar que los DataFrames no estén vacíos
            if buque_on.empty or buque_off.empty:
                raise ValueError("Los datos de buque ON o OFF están vacíos.")
            
            if tripulantes_on.empty and tripulantes_off.empty:
                raise ValueError("Los datos de tripulantes ON y OFF están vacíos.")

            # Almacenar los datos
            self.tripulantes_on = tripulantes_on
            self.tripulantes_off = tripulantes_off
            self.buque_on = buque_on
            self.buque_off = buque_off
            self.vuelos_internacionales_on = vuelos_internacionales_on
            self.vuelos_internacionales_off = vuelos_internacionales_off
            self.hoteles_on = hoteles_on
            self.hoteles_off = hoteles_off

            # Crear buques
            self._create_buque(self.buque_on)
            self._create_buque(self.buque_off)

            # Imprimir datos de vuelos internacionales ON y OFF
            #print("\nVuelos Internacionales ON:")
            #print(vuelos_internacionales_on.head())
            #print("\nVuelos Internacionales OFF:")
            #print(vuelos_internacionales_off.head())

            # Crear tripulantes ON y OFF
            tripulantes = []
            tripulantes += self._create_tripulantes(tripulantes_on, self.buque_on, "ON")
            tripulantes += self._create_tripulantes(tripulantes_off, self.buque_off, "OFF")

            #Crear vuelos
            self._create_vuelos(self.vuelos_internacionales_on, self.tripulantes_on, state='on')
            self._create_vuelos(self.vuelos_internacionales_off, self.tripulantes_off, state='off')

            # Imprimir los datos extraídos para depuración
            #print("\nDatos de buque ON:")
            #print(buque_on.head())
            #print("\nDatos de buque OFF:")
            #print(buque_off.head())

            #print("\nDatos de tripulantes ON:")
            #print(tripulantes_on.head())
            #print("\nDatos de tripulantes OFF:")
            #print(tripulantes_off.head())


            """
            print("\nHoteles ON:")
            print(hoteles_on.head())
            print("\nHoteles OFF:")
            print(hoteles_off.head())
            """


            return self.buque_on, self.buque_off, self.tripulantes_on, self.tripulantes_off

        except Exception as e:
            raise Exception(f"Error al procesar el archivo: {e}")

    def _extraer_ciudades_y_horarios(self, vuelo_info, tipo_vuelo):
        # Dependiendo del tipo de vuelo, se ajusta el acceso a las claves
        if tipo_vuelo == 'on':
            vuelo = vuelo_info['vuelo']
        elif tipo_vuelo == 'off':
            vuelo = vuelo_info['nro']
        else:
            raise ValueError("Tipo de vuelo no válido. Debe ser 'on' o 'off'.")

        # Verifica si el vuelo es NaN o None
        if vuelo is None or pd.isna(vuelo):
            print("Vuelo es NaN o None. Omitiendo...")
            return None  # O puedes lanzar un error, dependiendo de cómo manejes esto

        # Dividir la cadena del vuelo en partes
        partes = vuelo.split()
        
        if len(partes) < 3:
            raise ValueError(f"Formato de vuelo inválido: {vuelo_info[vuelo]}")

        codigo_vuelo = partes[0]  # 'AF178' o 'KL702'
        aeropuerto_salida = partes[1]  # 'CDG' o 'SCL'
        aeropuerto_llegada = partes[2]  # 'JFK' o 'AMS'
        
        # Obtener la fecha y las horas como objetos datetime
        if tipo_vuelo == 'on':
            fecha_vuelo = vuelo_info['fecha']  # Se espera que sea un objeto Timestamp
            hora_salida, hora_llegada = vuelo_info['hora'].split('-')
        elif tipo_vuelo == 'off':
            fecha_vuelo = vuelo_info['date']  # Se espera que sea un objeto Timestamp
            hora_salida, hora_llegada = vuelo_info['hora'].split('-')

        # Eliminar espacios en blanco antes de convertir a datetime
        hora_salida = hora_salida.strip()
        hora_llegada = hora_llegada.strip()

        # Verifica si la hora de llegada contiene un '+1' y ajusta la fecha
        if '+1' in hora_llegada:
            fecha_vuelo += pd.Timedelta(days=1)  # Agregar un día a la fecha de vuelo
            hora_llegada = hora_llegada.replace('+1', '').strip()  # Eliminar '+1' de la hora de llegada

        # Convertir las horas de salida y llegada a objetos datetime
        hora_salida = datetime.combine(fecha_vuelo.date(), datetime.strptime(hora_salida, "%H:%M").time())
        hora_llegada = datetime.combine(fecha_vuelo.date(), datetime.strptime(hora_llegada, "%H:%M").time())

        # Buscar las ciudades en el diccionario de aeropuertos
        ciudad_salida = CITY_AIRPORT_CODES.get(aeropuerto_salida, "Desconocido")
        ciudad_llegada = CITY_AIRPORT_CODES.get(aeropuerto_llegada, "Desconocido")
        
        return {
            'codigo_vuelo': codigo_vuelo,
            'ciudad_salida': ciudad_salida,
            'ciudad_llegada': ciudad_llegada,
            'fecha': fecha_vuelo,  # Retornar como objeto Timestamp
            'hora_salida': hora_salida,  # Retornar como objeto datetime
            'hora_llegada': hora_llegada   # Retornar como objeto datetime
        }

    def _create_tripulantes(self, tripulantes_df, buque_df, vuelos_df, state):        
        tripulantes = []  # Lista para almacenar los tripulantes creados
        try:
            # Asegurarse de que ambos DataFrames tienen la misma longitud
            if len(tripulantes_df) != len(buque_df):
                raise ValueError("El número de tripulantes no coincide con el número de buques.")

            # Iterar sobre cada fila del DataFrame de tripulantes
            for i, row in tripulantes_df.iterrows():
                # Comprobar si el índice i está dentro del rango de buque_df
                if i >= len(buque_df):
                    raise IndexError(f"Índice fuera de rango: {i} no está en buque_df.")

                # Obtener el nombre del buque correspondiente
                nombre_buque = buque_df.loc[i]['Vessel']

                # Buscar el buque ID usando la función buscar_buque_id
                buque_id = buscar_buque_id(nombre_buque, self.db_session)

                # Buscar si el tripulante ya existe en la base de datos por pasaporte
                tripulante_existente = self.db_session.query(Tripulante).filter_by(pasaporte=row['Pasaporte']).first()

                if tripulante_existente:
                    #print(f"Tripulante {tripulante_existente.nombre} {tripulante_existente.apellido} ya existe.")
                    tripulante_id = tripulante_existente.tripulante_id

                else:
                    # Si el tripulante no existe, lo creamos
                    tripulante = Tripulante(
                        nombre=row['First name'],
                        apellido=row['Last name'],
                        sexo=row['Gender'],
                        nacionalidad=row['Nacionalidad'],
                        posicion=row['Position'],
                        pasaporte=row['Pasaporte'],
                        fecha_nacimiento=pd.to_datetime(row['DOB']).date() if not pd.isna(row['DOB']) else None,
                        buque_id=buque_id,
                        estado=state  # (ON u OFF)
                    )
                    self.db_session.add(tripulante)
                    self.db_session.commit()  # Confirmar la creación del tripulante

                    tripulante_id = tripulante.tripulante_id
                    print(f"Tripulante {tripulante.nombre} {tripulante.apellido} creado con ID: {tripulante_id}.")

                # Crear un nuevo viaje para el tripulante
                #self._create_viaje(tripulante_id, buque_id)
                
                tripulantes.append(tripulante_existente if tripulante_existente else tripulante)  # Agregar a la lista

            return tripulantes  # Devolver la lista de tripulantes

        except Exception as e:
            self.db_session.rollback()  # Revertir cambios en caso de error
            raise Exception(f"Error al crear tripulantes: {e}")

    def _create_buque(self, buques_df):
        buques = []  # Lista para almacenar los buques creados
        try:
            if 'Puerto a embarcar' in buques_df.columns:
                buques_df.rename(columns={'Puerto a embarcar': 'Puerto'}, inplace=True)

            # Renombrar la columna 'Puerto a desembarcar' a 'Puerto' si existe
            if 'Puerto a desembarcar' in buques_df.columns:
                buques_df.rename(columns={'Puerto a desembarcar': 'Puerto'}, inplace=True)

            for _, row in buques_df.iterrows():
                # Verificar si el buque ya existe por nombre
                buque_existente = self.db_session.query(Buque).filter_by(nombre=row['Vessel']).first()
                if buque_existente:
                    #print(f"Buque {buque_existente.nombre} ya existe. Usando ID: {buque_existente.buque_id}")
                    buques.append(buque_existente)
                    continue  # Saltar la creación del buque si ya existe

                buque = Buque(
                    nombre=row['Vessel'],
                    empresa=row['Owner'] if pd.notna(row['Owner']) else "Empresa Desconocida",
                    ciudad=row['Puerto'] if pd.notna(row['Puerto']) else "Ciudad Desconocida"
                )
                
                # Crear las ETAs asociadas al buque
                eta = EtaCiudad(
                    buque=buque,
                    ciudad=row['Puerto'],
                    eta=pd.to_datetime(row['ETA Vessel']),
                    etd=pd.to_datetime(row['ETD Vessel'])
                )
                
                print(f"Buque {buque.nombre} agregado con ETA {eta.eta} y ETD {eta.etd}")

                # Agregar el buque y la eta a las listas
                buques.append(buque)
                buque.etas.append(eta)  # Añadir la eta a la relación del buque
            
            # Aquí se agregan los buques a la sesión de la base de datos
            self.db_session.add_all(buques)
            self.db_session.commit()  # Confirmar los cambios

        except Exception as e:
            self.db_session.rollback()  # Revertir cambios en caso de error
            raise Exception(f"Error al crear buques: {e}")

        return buques  # Devolver la lista de buques
        
    def _create_vuelos(self, vuelos_df, tripulantes_df, state):
        vuelos = []  # Lista para almacenar los vuelos creados
        try:
            # Iterar sobre cada fila del DataFrame de vuelos
            for i, row in vuelos_df.iterrows():
                print(f"Row {i}: {row.to_dict()}")  # Imprimir el contenido de la fila

                # Obtener el tripulante correspondiente a la fila actual
                tripulante_data = tripulantes_df.iloc[i]
                tripulante = self.db_session.query(Tripulante).filter_by(pasaporte=tripulante_data['Pasaporte']).first()
                
                if not tripulante:
                    print(f"No se encontró tripulante con pasaporte {tripulante_data['Pasaporte']} en la fila {i}.")
                    continue

                # Iterar sobre las claves que representan los vuelos
                for vuelo_key in row.index:
                    vuelo_info = row[vuelo_key]  # Obtener el diccionario del vuelo

                    # Verifica que haya información para el vuelo
                    if pd.notna(vuelo_info):  # Solo procesar si hay información
                        # Llamar a la función _extraer_ciudades_y_horarios
                        vuelo_info = self._extraer_ciudades_y_horarios(vuelo_info, state)
                        # Verificar que vuelo_info no sea None antes de continuar
                        if vuelo_info is None:
                            print(f"Omitiendo vuelo {vuelo_key} en la fila {i} debido a datos faltantes.")
                            continue

                        # Crear o buscar el vuelo en la base de datos
                        vuelo = self.db_session.query(Vuelo).filter_by(codigo=vuelo_info['codigo_vuelo']).first()
                        if not vuelo:
                            vuelo = Vuelo(
                                codigo=vuelo_info['codigo_vuelo'],
                                aeropuerto_salida=vuelo_info['ciudad_salida'],
                                aeropuerto_llegada=vuelo_info['ciudad_llegada'],
                                fecha=vuelo_info['fecha'],
                                hora_salida=vuelo_info['hora_salida'],
                                hora_llegada=vuelo_info['hora_llegada'],
                            )
                            self.db_session.add(vuelo)
                            vuelos.append(vuelo)  # Agregar el vuelo a la lista de vuelos
                            self.db_session.commit()  # Confirmar la creación del vuelo
                            print(f"Vuelo {vuelo.codigo} creado desde {vuelo.aeropuerto_salida} a {vuelo.aeropuerto_llegada}.")
                        else:
                            print(f"Vuelo {vuelo.codigo} ya existe en la base de datos.")

                        # Asociar el tripulante al vuelo en la tabla intermedia TripulanteVuelo
                        tripulante_vuelo = TripulanteVuelo(
                            tripulante_id=tripulante.tripulante_id,
                            vuelo_id=vuelo.vuelo_id
                        )
                        self.db_session.add(tripulante_vuelo)
                        self.db_session.commit()
                        print(f"Tripulante {tripulante.nombre} {tripulante.apellido} asignado al vuelo {vuelo.codigo}.")

                    else:
                        print(f"No hay información para {vuelo_key} en la fila {i}.")

        except Exception as e:
            print(f"Error al crear vuelos o asignar tripulantes: {e}")
            self.db_session.rollback()  # Revertir la sesión en caso de error

        return vuelos  # Retornar la lista de vuelos creados

    def _create_viaje(self, tripulante_id, buque_id, equipaje_perdido=False, asistencia_medica=False):
        try:
            # Crear el viaje asignando el tripulante y buque
            viaje = Viaje(
                tripulante_id=tripulante_id,
                buque_id=buque_id,
                equipaje_perdido=equipaje_perdido,
                asistencia_medica=asistencia_medica
            )
            self.db_session.add(viaje)
            self.db_session.commit()
            #print(f"Viaje creado para Tripulante: {tripulante_id} en Buque ID: {buque_id}")
        except Exception as e:
            self.db_session.rollback()  # Revertir en caso de error
            raise Exception(f"Error al crear viaje: {e}")
        
    def _extract_international_flights(self, excel_data, start_row, state):
        vuelos = []
        
        # Convertir los nombres de las columnas a cadenas y quitar espacios
        flight_columns = excel_data.loc[start_row].dropna().tolist()

        # Verificar las columnas con las que estamos trabajando
        #print("Columnas disponibles:", flight_columns)  # Imprimir las columnas para verificar qué se está cargando

        # Iterar sobre cada fila, comenzando desde la fila indicada
        for i in range(start_row + 1, excel_data.shape[0]):
            tripulante_vuelos = {}
            vuelo_num = 1
            
            # Iterar sobre las columnas de vuelos hasta que ya no existan
            while True:
                if state=="on":
                    vuelo_col = f'Vuelo Int {vuelo_num}'
                    fecha_col = f'Fecha Vuelo Int {vuelo_num}'
                    hora_col = f'Hora Vuelo Int {vuelo_num}'

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

                        #print(f"{vuelo} | {fecha} | {hora}")

                        # Si hay información válida en las columnas, agregarla
                        if pd.notna(vuelo) and pd.notna(fecha) and pd.notna(hora):
                            tripulante_vuelos[f'Vuelo {vuelo_num}'] = {
                                "vuelo": vuelo,
                                "fecha": pd.to_datetime(fecha, errors='coerce'),
                                "hora": hora  # Mantener la hora como string, o usar pd.to_datetime si es necesario
                            }

                        # Incrementar el vuelo_num para buscar el siguiente conjunto
                        vuelo_num += 1
                    else:
                        break  # Detener la búsqueda si no se encuentra una de las columnas
                elif state=="off":
                    nro_regional_flight  = 'Nro Regional Flight'
                    date_reg_flight = 'Date Reg Flight'
                    hora_reg_flight = 'Hora Reg Flight'

                    if nro_regional_flight in flight_columns and date_reg_flight in flight_columns and hora_reg_flight in flight_columns: 
                        col_idx_nro = flight_columns.index(nro_regional_flight)
                        col_idx_date = flight_columns.index(date_reg_flight)
                        col_idx_hora = flight_columns.index(hora_reg_flight)

                        nro = excel_data.iloc[i, col_idx_nro]
                        date = excel_data.iloc[i, col_idx_date]
                        hora = excel_data.iloc[i, col_idx_hora]

                        if pd.notna(nro) and pd.notna(date) and pd.notna(hora):
                            tripulante_vuelos[f'Vuelo {vuelo_num}'] = {
                                "nro": nro,
                                "date": pd.to_datetime(date, format='%d-%m-%Y', errors='coerce'),
                                "hora": hora  # Mantener la hora como string, o usar pd.to_datetime si es necesario
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
            print(f"{len(vuelos)} vuelos internacionales procesados.")
            
        return pd.DataFrame(vuelos)
    
    def _extract_hotels(self, excel_data, start_row, state):
        hotels = []
        
        # Convertir los nombres de las columnas a cadenas y quitar espacios
        hotels_columns = excel_data.loc[start_row].dropna().tolist()

        # Verificar las columnas con las que estamos trabajando
        #print("Columnas disponibles:", hotels_columns)  # Imprimir las columnas para verificar qué se está cargando

        # Iterar sobre cada fila, comenzando desde la fila indicada
        for i in range(start_row + 1, excel_data.shape[0]):
            tripulante_hotels = {}
            hotel_num = 1
            
            # Iterar sobre las columnas de vuelos hasta que ya no existan
            while True:
                category = 'Silver Categoria'
                hotel_col = f'Hotel{hotel_num}'
                check_in_col = f'Check in{hotel_num}'
                check_out_col = f'Check out{hotel_num}'
                rooms = f'Rooms{hotel_num}'
                hotel_name = f'Nombre Hotel{hotel_num}'

                #print(f"Fila {start_row} | i {i}")
                #print(f"{category} | {hotel_col} | {check_in_col} | {check_out_col} | {rooms} | {hotel_name}")
                    
                # Verificar si las columnas existen en el DataFrame
                if category in hotels_columns and hotel_col in hotels_columns and check_in_col in hotels_columns and check_out_col in hotels_columns and rooms in hotels_columns and hotel_name in hotels_columns:    
                    col_idx_category = hotels_columns.index(category)
                    col_idx_hotel = hotels_columns.index(hotel_col)
                    col_idx_check_in = hotels_columns.index(check_in_col)
                    col_idx_check_out = hotels_columns.index(check_out_col)
                    col_idx_rooms = hotels_columns.index(rooms)
                    col_idx_hotel_name = hotels_columns.index(hotel_name)
                    #print(f"{vuelo_col} | {fecha_col} | {hora_col}")
                    #print(f"{category} | {hotel_col} | {check_in_col} | {check_out_col} | {rooms} | {hotel_name}")

                    categoria = excel_data.iloc[i, col_idx_category]
                    hotel = excel_data.iloc[i, col_idx_hotel]
                    check_in = excel_data.iloc[i, col_idx_check_in]
                    check_out = excel_data.iloc[i, col_idx_check_out]
                    habitacion = excel_data.iloc[i, col_idx_rooms]
                    nombre_hotel = excel_data.iloc[i, col_idx_hotel_name]

                    # Si hay información válida en las columnas, agregarla
                    if pd.notna(categoria) and pd.notna(hotel) and pd.notna(check_in) and pd.notna(check_out) and pd.notna(habitacion) and pd.notna(nombre_hotel):
                        tripulante_hotels[f'Hotel {hotel_num}'] = {
                            "categoria": categoria,
                            "hotel": hotel,
                            "check_in": pd.to_datetime(check_in, errors='coerce'),
                            "check_out": pd.to_datetime(check_out, errors='coerce'),
                            "habitacion": hotel,
                            "nombre_hotel": nombre_hotel 
                        }

                    # Incrementar el vuelo_num para buscar el siguiente conjunto
                    hotel_num += 1
                else:
                    break  # Detener la búsqueda si no se encuentra una de las columnas

            # Solo agregar el vuelo si se encontraron vuelos válidos para el tripulante
            if tripulante_hotels:
                hotels.append(tripulante_hotels)

        # Verificar si se encontraron vuelos
        if len(hotels) == 0:
            print("No se encontraron hoteles en las filas procesadas.")
        else:
            print(f"{len(hotels)} hoteles procesados.")
            
        return pd.DataFrame(hotels)

    def read_all_rows(self, data, start_row, column_range, column_names):
        """
        Leer todas las filas a partir de una fila específica, 
        incluyendo filas con celdas vacías.
        """
        
        data_block = []
        current_row = start_row

        while current_row < len(data):
            # Leer una fila completa del DataFrame
            row_data = data.iloc[current_row, column_range]

            # Verificar si todas las columnas de la fila están vacías
            if row_data.isnull().all():
                break  # Detener si la fila está completamente vacía
            
            # Agregar los datos de la fila al bloque
            data_block.append(row_data)
            current_row += 1

        # Convertir el bloque de datos en un DataFrame
        result_df = pd.DataFrame(data_block)
        
        # Asignar nombres de columnas si se proporcionan
        if column_names:
            result_df.columns = column_names
        
        return result_df

    def _update_tripulante(self, tripulante, row, buque_id, estado):
        tripulante.nombre = row['First name']
        tripulante.apellido = row['Last name']

        gender = row.get('Gender')
        if gender and len(gender) == 1:
            tripulante.sexo = gender
        else:
            print(f"Valor inválido para 'Gender': {gender}. Debe ser un solo carácter.") 
            return None  # O puedes optar por no retornar el tripulante si el valor es inválido
        
        tripulante.nacionalidad = row.get('Nationality')
        tripulante.fecha_nacimiento = pd.to_datetime(row.get('Date of birth')).date() if not pd.isna(row.get('Date of birth')) else None
        tripulante.buque_id = buque_id
        tripulante.estado = estado
        print(f"Tripulante {tripulante.nombre} actualizado")
        return tripulante

    def load_existing_data(self, selected_city: str, start_date: str, end_date: str):
        try:
            # Convertir el nombre de la ciudad al código correspondiente
            selected_city_code = CITY_AIRPORT_CODES.get(selected_city.upper(), None)
            
            if selected_city_code is None:
                print(f"Código de ciudad no encontrado para: {selected_city}")
                return pd.DataFrame(), pd.DataFrame()

            # Convertir las fechas a formato datetime
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)

            # Cargar tripulantes 'ON' y 'OFF' sin filtrar por ciudad
            tripulantes_on = self.db_session.query(Tripulante).filter_by(estado='ON').all()
            tripulantes_off = self.db_session.query(Tripulante).filter_by(estado='OFF').all()

            # Cargar ETA para tripulantes filtrando por ciudad y rango de fechas
            eta_records = self.db_session.query(EtaCiudad).filter(
                EtaCiudad.ciudad == selected_city_code,
                EtaCiudad.eta.between(start_date, end_date)
            ).all()

            # Extraer tripulante_ids de los registros de EtaCiudad
            tripulante_ids_eta = {eta.tripulante_id for eta in eta_records}

            # Filtrar tripulantes 'ON' y 'OFF' por los tripulante_ids en eta
            tripulantes_on_filtered = [trip for trip in tripulantes_on if trip.tripulante_id in tripulante_ids_eta]
            tripulantes_off_filtered = [trip for trip in tripulantes_off if trip.tripulante_id in tripulante_ids_eta]

            # Imprimir los tripulantes filtrados
            print(f"Tripulantes 'ON' filtrados en {selected_city}: {len(tripulantes_on_filtered)}")
            print(f"Tripulantes 'OFF' filtrados en {selected_city}: {len(tripulantes_off_filtered)}")

            # Cargar vuelos relacionados con tripulantes 'ON' y 'OFF'
            vuelos_on = self.db_session.query(Vuelo).filter(Vuelo.tripulante_id.in_([trip.tripulante_id for trip in tripulantes_on_filtered])).all()
            vuelos_off = self.db_session.query(Vuelo).filter(Vuelo.tripulante_id.in_([trip.tripulante_id for trip in tripulantes_off_filtered])).all()

            # Filtrar vuelos y ETAs por tripulantes 'ON' y 'OFF'
            eta_vuelo_df_on = pd.DataFrame([{
                'First name': trip.nombre,
                'Last name': trip.apellido,
                'Flight code': vuelo.codigo,
                'City': eta.ciudad,
                'ETA': eta.eta
            } for trip in tripulantes_on_filtered for vuelo in vuelos_on for eta in eta_records 
            if trip.tripulante_id == eta.tripulante_id])

            eta_vuelo_df_off = pd.DataFrame([{
                'First name': trip.nombre,
                'Last name': trip.apellido,
                'Flight code': vuelo.codigo,
                'City': eta.ciudad,
                'ETA': eta.eta
            } for trip in tripulantes_off_filtered for vuelo in vuelos_off for eta in eta_records 
            if trip.tripulante_id == eta.tripulante_id])

            # Imprimir los dataframes generados
            print(f"DataFrame de tripulantes 'ON':\n{eta_vuelo_df_on}")
            print(f"DataFrame de tripulantes 'OFF':\n{eta_vuelo_df_off}")

            return eta_vuelo_df_on, eta_vuelo_df_off
        except Exception as e:
            raise Exception(f"Error al cargar datos existentes: {e}")