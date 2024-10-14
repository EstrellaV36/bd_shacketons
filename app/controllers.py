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
    'EZE': 'BUENOS AIRES',
    'LUN': 'LUN',
    'DOH': 'DOH',
    'PUJ': 'PUJ',
    'LIM': 'LIM'
}

# Definir los nombres de las columnas antes de llamar al método
buque_on_columns = ['Owner', 'Vessel', 'Date arrive CL', 'ETA Vessel', 'ETD Vessel', 'Puerto a embarcar']
buque_off_columns = ['Owner', 'Vessel', 'Date First flight', 'ETA Vessel', 'ETD Vessel', 'Puerto a desembarcar']

tripulante_columns = ['First name', 'Last name', 'Gender', 'Nacionalidad', 'Position', 'Pasaporte', 'DOB']

def buscar_buque_id(nombre_buque, session):
    # Asegúrate de que el campo 'nombre' es el correcto
    buque = session.query(Buque).filter(Buque.nombre.ilike(nombre_buque)).first()  # Usando ilike para coincidencias sin distinción entre mayúsculas y minúsculas

    if buque:
        #print(f"Buque encontrado: {nombre_buque} con ID: {buque.buque_id}")
        return buque.nombre
    else:
        raise ValueError(f"Buque {nombre_buque} no encontrado en la base de datos.")
    
def buscar_vuelo_id(codigo_vuelo, session):
    # Asegúrate de que el campo 'nombre' es el correcto
    vuelo = session.query(Vuelo).filter(Vuelo.codigo.ilike(codigo_vuelo)).first()  # Usando ilike para coincidencias sin distinción entre mayúsculas y minúsculas

    if vuelo:
        print(f"Buque encontrado con el codigo: {vuelo.codigo}")
        return vuelo.codigo
    else:
        raise ValueError(f"Buque {vuelo.codigo} no encontrado en la base de datos.")

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
            hoteles_on.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            #Procesar vuelos ON
            vuelos_on = self._extract_flights(excel_data_on, start_row=0, state="on")
            vuelos_on.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            #Procesar asistencias ON
            asistencias_on = self._extract_assists(excel_data_on, start_row=0, state="on")
            asistencias_on.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            #Procesar transportes ON
            transportes_on = self._extract_transports(excel_data_on, start_row=0, state="on")
            transportes_on.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            #Procesar restaurantes ON
            restaurantes_on = self._extract_restaurants(excel_data_on, start_row=0, state="on")
            restaurantes_on.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            #Procesar extras ON
            extras_on = self._extract_extras(excel_data_on, start_row=0, state="on")
            extras_on.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            # Leer la hoja OFF del archivo Excel
            excel_data_off = pd.read_excel(file_path, sheet_name='OFF', header=None)

            # Extraer los datos de los buque OFF (desde fila 22, índice 21)
            buque_off = self.read_all_rows(excel_data_off, start_row=1, column_range=slice(0, 6), column_names=buque_off_columns)
            buque_off.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            # Extraer los datos de tripulantes OFF (fila 22)
            tripulantes_off = self.read_all_rows(excel_data_off, start_row=1, column_range=slice(9, 16), column_names=tripulante_columns) 
            tripulantes_off.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            # Procesar vuelos internacionales OFF
            #vuelos_internacionales_off = self._extract_international_flights(excel_data_off, start_row=0, state="off")
            #vuelos_internacionales_off.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            #Procesar hoteles OFF
            hoteles_off = self._extract_hotels(excel_data_off, start_row=0, state="off")
            hoteles_off.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            #Procesar vuelos OFF
            vuelos_off = self._extract_flights(excel_data_off, start_row=0, state="off")
            vuelos_off.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            #Procesar asistencias OFF
            asistencias_off = self._extract_assists(excel_data_off, start_row=0, state="off")
            asistencias_off.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            #Procesar transporte OFF
            transportes_off = self._extract_transports(excel_data_off, start_row=0, state="off")
            transportes_off.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            #Procesar restaurantes OFF
            restaurantes_off = self._extract_restaurants(excel_data_off, start_row=0, state="off")
            restaurantes_off.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            #Procesar extras OFF
            extras_off = self._extract_extras(excel_data_off, start_row=0, state="off")
            extras_off.reset_index(drop=True, inplace=True)  # Reiniciar el índice

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
            #self.vuelos_internacionales_off = vuelos_internacionales_off
            self.hoteles_on = hoteles_on
            self.hoteles_off = hoteles_off
            self.vuelos_on = vuelos_on
            self.vuelos_off = vuelos_off
            self.asistencias_on = asistencias_on
            self.asistencias_off = asistencias_off
            self.transportes_on = transportes_on
            self.transportes_off = transportes_off
            self.restaurantes_on = restaurantes_on
            self.restaurantes_off = restaurantes_off
            self.extras_on = extras_on
            self.extras_off = extras_off

            #pd.set_option('display.max_columns', None)  # Para mostrar todas las columnas
            #pd.set_option('display.max_rows', None)     # Para mostrar todas las filas
            #pd.set_option('display.max_colwidth', None)

            #print(self.hoteles_on.get('Hotel 1'))  # Esto te mostrará las claves del diccionario
            #print(extras_off)

            # Crear buques ON y OFF
            self._create_buque(self.buque_on)
            self._create_buque(self.buque_off)

            # Crear tripulantes ON y OFF
            tripulantes = []
            tripulantes += self._create_tripulantes(tripulantes_on, self.buque_on)
            tripulantes += self._create_tripulantes(tripulantes_off, self.buque_off)

            # Crear vuelos ON y OFF
            vuelos_on = self._create_vuelos(self.vuelos_internacionales_on, self.tripulantes_on, state='on')
            #vuelos_off = self._create_vuelos(self.vuelos_internacionales_off, self.tripulantes_off, state='off')

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
        
        if len(partes) < 2:
            #print("ENTRE")
            raise ValueError(f"Formato de vuelo inválido: {vuelo_info[vuelo]}")

        codigo_vuelo = partes[0]  # 'AF178' o 'KL702'
        aeropuertos = partes[1]  # 'CDG' o 'SCL'
        aeropuerto_salida, aeropuerto_llegada = aeropuertos.split("-")
        #aeropuerto_llegada = partes[2]  # 'JFK' o 'AMS'
        
        #print(f"{codigo_vuelo} | {aeropuerto_salida} | {aeropuerto_llegada}")

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

        #print(f"{codigo_vuelo} | {ciudad_salida} | {ciudad_llegada} | {fecha_vuelo} | {hora_salida} | {hora_llegada}")
        
        return {
            'codigo_vuelo': codigo_vuelo,
            'ciudad_salida': ciudad_salida,
            'ciudad_llegada': ciudad_llegada,
            'fecha': fecha_vuelo,  # Retornar como objeto Timestamp
            'hora_salida': hora_salida,  # Retornar como objeto datetime
            'hora_llegada': hora_llegada   # Retornar como objeto datetime
        }

    def _create_tripulantes(self, tripulantes_df, buque_df):
        tripulantes = []  # Lista para almacenar los tripulantes creados
        vuelos_tripulante = []  # Lista para almacenar los vuelos asociados a cada tripulante
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
                    )
                    self.db_session.add(tripulante)
                    self.db_session.commit()  # Confirmar la creación del tripulante

                    tripulante_id = tripulante.tripulante_id
                
                tripulantes.append(tripulante_existente if tripulante_existente else tripulante)  # Agregar a la lista

                #vuelo_id = buscar_vuelo_id(codigo_vuelo, self.db_session)    

                # Agregar todos los vuelos de 'on' y 'off' a la lista de vuelos del tripulante
                """
                for vuelo in vuelos_on + vuelos_off:
                    vuelos_tripulante.append({
                        'tripulante_id': tripulante_id,
                        'vuelo_id': vuelo['vuelo_id']
                    })"""

            # Retornar la lista de tripulantes y vuelos asociados
            return tripulantes, vuelos_tripulante
        except Exception as e:
            print(f"Error al crear tripulantes o encontrar vuelos: {e}")
            self.db_session.rollback()  # Revertir la sesión en caso de error
            return [], []  # Devolver listas vacías en caso de error

    def _create_buque(self, buques_df):
        try:
            # Renombrar las columnas si es necesario
            if 'Puerto a embarcar' in buques_df.columns:
                buques_df.rename(columns={'Puerto a embarcar': 'Puerto'}, inplace=True)

            if 'Puerto a desembarcar' in buques_df.columns:
                buques_df.rename(columns={'Puerto a desembarcar': 'Puerto'}, inplace=True)

            for _, row in buques_df.iterrows():
                # Verificar si el buque ya existe por nombre en la base de datos
                buque_existente = self.db_session.query(Buque).filter(Buque.nombre == row['Vessel'].strip()).first()
                #print(f"{Buque.nombre} == {row['Vessel']}")

                if buque_existente:
                    #print(f"Buque {buque_existente.nombre} ya existente")
                    
                    # Verificar si ya existe una ETA similar para este buque
                    eta_existente = self.db_session.query(EtaCiudad).filter_by(
                        buque_id=buque_existente.buque_id,
                        ciudad=row['Puerto'],
                        eta=pd.to_datetime(row['ETA Vessel']),
                        etd=pd.to_datetime(row['ETD Vessel'])
                    ).first()

                    if not eta_existente:
                        # Si no existe una ETA igual, agregarla
                        nueva_eta = EtaCiudad(
                            buque=buque_existente,
                            ciudad=row['Puerto'],
                            eta=pd.to_datetime(row['ETA Vessel']),
                            etd=pd.to_datetime(row['ETD Vessel'])
                        )
                        buque_existente.etas.append(nueva_eta)
                        self.db_session.add(nueva_eta)
                        #print(f"Nueva ETA añadida a buque existente: {buque_existente.nombre}")

                else:
                    # Crear un nuevo buque si no existe
                    nuevo_buque = Buque(
                        nombre=row['Vessel'],
                        empresa=row['Owner'] if pd.notna(row['Owner']) else "Empresa Desconocida",
                        ciudad=row['Puerto'] if pd.notna(row['Puerto']) else "Ciudad Desconocida"
                    )
                    self.db_session.add(nuevo_buque)
                    self.db_session.commit()  # Confirmar la creación del nuevo buque
                    #print(f"Nuevo buque creado: {nuevo_buque.nombre}")

                    # Añadir la ETA al nuevo buque
                    nueva_eta = EtaCiudad(
                        buque=nuevo_buque,
                        ciudad=row['Puerto'],
                        eta=pd.to_datetime(row['ETA Vessel']),
                        etd=pd.to_datetime(row['ETD Vessel'])
                    )
                    nuevo_buque.etas.append(nueva_eta)
                    self.db_session.add(nueva_eta)
                    #print(f"ETA añadida al nuevo buque: {nuevo_buque.nombre}")

                # Confirmar todos los cambios al final
                self.db_session.commit()

        except Exception as e:
            self.db_session.rollback()  # Revertir cambios en caso de error
            raise Exception(f"Error al crear o actualizar buques: {e}")

        return "Proceso completado exitosamente"
        
    def _create_vuelos(self, vuelos_df, tripulantes_df, state):
        vuelos = []  # Lista para almacenar los vuelos creados
        try:
            # Iterar sobre cada fila del DataFrame de vuelos
            for i, row in vuelos_df.iterrows():
                #print("ENTRE")
                #print(f"Row {i}: {row.to_dict()}")  # Imprimir el contenido de la fila

                # Obtener el tripulante correspondiente a la fila actual
                tripulante_data = tripulantes_df.iloc[i+1]
                tripulante = self.db_session.query(Tripulante).filter_by(pasaporte=tripulante_data['Pasaporte']).first()
                
                if not tripulante:
                    print(f"No se encontró tripulante con pasaporte {tripulante_data['Pasaporte']} en la fila {i}.")
                    continue

                # Iterar sobre las claves que representan los vuelos
                for vuelo_key in row.index:
                    vuelo_info = row[vuelo_key]  # Obtener el diccionario del vuelo
                    #print(vuelo_info)

                    # Verifica que haya información para el vuelo
                    if pd.notna(vuelo_info):  # Solo procesar si hay información
                        
                        # Llamar a la función _extraer_ciudades_y_horarios
                        vuelo_info = self._extraer_ciudades_y_horarios(vuelo_info, state)
                        #print(vuelo_info) 
                        # Verificar que vuelo_info no sea None antes de continuar
                        if vuelo_info is None:
                            #print(f"Omitiendo vuelo {vuelo_key} en la fila {i} debido a datos faltantes.")
                            continue

                        # Crear o buscar el vuelo en la base de datos
                        vuelo = self.db_session.query(Vuelo).filter_by(codigo=vuelo_info['codigo_vuelo']).first()
                        #print(f"{vuelo.codigo} | {vuelo_info['codigo_vuelo']}")
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
                            #print(f"Vuelo {vuelo.codigo} creado desde {vuelo.aeropuerto_salida} a {vuelo.aeropuerto_llegada}.")

                        print(f"{vuelo}")
                        # Verificar si ya existe una asociación en TripulanteVuelo
                        tripulante_vuelo_existente = self.db_session.query(TripulanteVuelo).filter_by(
                            tripulante_id=tripulante.tripulante_id, vuelo_id=vuelo.vuelo_id
                        ).first()

                        if not tripulante_vuelo_existente:
                            # Asociar el tripulante al vuelo en la tabla intermedia TripulanteVuelo
                            tripulante_vuelo = TripulanteVuelo(
                                tripulante_id=tripulante.tripulante_id,
                                vuelo_id=vuelo.vuelo_id
                            )
                            self.db_session.add(tripulante_vuelo)
                            self.db_session.commit()
                            #print(f"Tripulante {tripulante.nombre} {tripulante.apellido} asignado al vuelo {vuelo.codigo}.")

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
            print(f"{len(vuelos)} vuelos internacionales procesados. ({state})")
            
        return pd.DataFrame(vuelos)
    
    def _extract_hotels(self, excel_data, start_row, state):
        hotels = []
        
        # Convertir los nombres de las columnas a cadenas y quitar espacios
        hotels_columns = excel_data.loc[start_row].dropna().str.lower().tolist()

        # Verificar las columnas con las que estamos trabajando
        #print("Columnas disponibles:", hotels_columns)  # Imprimir las columnas para verificar qué se está cargando

        # Iterar sobre cada fila, comenzando desde la fila indicada
        for i in range(start_row + 1, excel_data.shape[0]):
            tripulante_hotels = {}
            hotel_num = 1
            
            # Iterar sobre las columnas de vuelos hasta que ya no existan
            while True:
                category = 'silver categoria'
                hotel_col = f'hotel {hotel_num}'
                check_in_col = f'check in {hotel_num}'
                check_out_col = f'check out {hotel_num}'
                rooms = f'rooms {hotel_num}'
                hotel_name = f'nombre hotel {hotel_num}'

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
                    if pd.notna(categoria) and pd.notna(hotel):
                        tripulante_hotels[f'Hotel {hotel_num}'] = {
                            "categoria": categoria,
                            "hotel": hotel,
                            "check_in": pd.to_datetime(check_in, errors='coerce'),
                            "check_out": pd.to_datetime(check_out, errors='coerce'),
                            "habitacion": habitacion,
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
        #else:
            #print(f"{len(hotels)} hoteles procesados. ({state})")
            
            
        return pd.DataFrame(hotels)
    
    def _extract_flights(self, excel_data, start_row, state):
        vuelos = []
        
        # Convertir los nombres de las columnas a cadenas y quitar espacios
        vuelos_columns = excel_data.loc[start_row].dropna().str.lower().tolist()

        # Verificar las columnas con las que estamos trabajando
        #print("Columnas disponibles:", vuelos_columns)  # Imprimir las columnas para verificar qué se está cargando

        # Iterar sobre cada fila, comenzando desde la fila indicada
        for i in range(start_row + 1, excel_data.shape[0]):
            tripulante_vuelos = {}
            vuelos_num = 1
            
            # Iterar sobre las columnas de vuelos hasta que ya no existan
            while True:
                nro_int_flight = 'nro international flight'
                date_int_flight = 'date international flight'
                hora_int_flight = 'hora international flight'

                nro_domestic_flight = 'nro domestic flight'
                date_domestic_flight = 'date domestic flight'
                hora_domestic_flight = 'hora domestic flight'

                nro_regional_flight = 'nro regional flight'
                date_regional_flight = 'date regional flight'
                hora_regional_flight = 'hora regional flight'

                #print(f"Fila {start_row} | i {i}")
                #print(f"{category} | {hotel_col} | {check_in_col} | {check_out_col} | {rooms} | {hotel_name}")
                    
                # Verificar si las columnas existen en el DataFrame
                if (nro_int_flight in vuelos_columns and date_int_flight in vuelos_columns and hora_int_flight in vuelos_columns) or (nro_domestic_flight in vuelos_columns and date_domestic_flight in vuelos_columns and hora_domestic_flight in vuelos_columns) or (nro_regional_flight in vuelos_columns and date_regional_flight in vuelos_columns and hora_regional_flight in vuelos_columns):
                    col_idx_nro_int_flight = vuelos_columns.index(nro_int_flight)
                    col_idx_date_int_flight = vuelos_columns.index(date_int_flight)
                    col_idx_hora_int_flight = vuelos_columns.index(hora_int_flight)

                    col_idx_nro_domestic_flight = vuelos_columns.index(nro_domestic_flight)
                    col_idx_date_domestic_flight = vuelos_columns.index(date_domestic_flight)
                    col_idx_hora_domestic_flight = vuelos_columns.index(hora_domestic_flight)

                    col_idx_nro_regional_flight = vuelos_columns.index(nro_regional_flight)
                    col_idx_date_regional_flight = vuelos_columns.index(date_regional_flight)
                    col_idx_hora_regional_flight = vuelos_columns.index(hora_regional_flight)
                    #print(f"{vuelo_col} | {fecha_col} | {hora_col}")
                    #print(f"{category} | {hotel_col} | {check_in_col} | {check_out_col} | {rooms} | {hotel_name}")

                    nro_inter_flight = excel_data.iloc[i, col_idx_nro_int_flight]
                    date_inter_flight = excel_data.iloc[i, col_idx_date_int_flight]
                    hora_inter_flight = excel_data.iloc[i, col_idx_hora_int_flight]

                    nro_domestic_flight = excel_data.iloc[i, col_idx_nro_domestic_flight]
                    date_domestic_flight = excel_data.iloc[i, col_idx_date_domestic_flight]
                    hora_domestic_flight = excel_data.iloc[i, col_idx_hora_domestic_flight]

                    nro_regional_flight = excel_data.iloc[i, col_idx_nro_regional_flight]
                    date_regional_flight = excel_data.iloc[i, col_idx_date_regional_flight]
                    hora_regional_flight = excel_data.iloc[i, col_idx_hora_regional_flight]

                    #print(nro_inter_flight)

                    # Si hay información válida en las columnas, agregarla
                    if pd.notna(nro_inter_flight) or pd.notna(nro_domestic_flight) or pd.notna(nro_regional_flight):
                        tripulante_vuelos[f'Vuelo {vuelos_num}'] = {
                            "nro internat flight": nro_inter_flight,
                            "date internat flight": pd.to_datetime(date_inter_flight, errors='coerce'),
                            "hora internat flight": hora_inter_flight,
                            "nro dom flight": nro_domestic_flight,
                            "date dom flight": pd.to_datetime(date_domestic_flight, errors='coerce'),
                            "hora dom flight": hora_domestic_flight,
                            "nro reg flight": nro_regional_flight,
                            "date reg flight": pd.to_datetime(date_regional_flight, errors='coerce', dayfirst=True),
                            "hora reg flight": hora_regional_flight
                        }

                    # Incrementar el vuelo_num para buscar el siguiente conjunto
                    vuelos_num += 1
                    break
                else:
                    break  # Detener la búsqueda si no se encuentra una de las columnas

            # Solo agregar el vuelo si se encontraron vuelos válidos para el tripulante
            if tripulante_vuelos:
                vuelos.append(tripulante_vuelos)

        # Verificar si se encontraron vuelos
        if len(vuelos) == 0:
            print("No se encontraron vuelos en las filas procesadas.")
        #else:
            #print(f"{len(vuelos)} vuelos procesados. ({state})")
            
        return pd.DataFrame(vuelos)
    
    def _extract_assists(self, excel_data, start_row, state):
        assists = []
        
        # Convertir los nombres de las columnas a cadenas y quitar espacios
        assist_columns = excel_data.loc[start_row].dropna().str.lower().tolist()

        # Verificar las columnas con las que estamos trabajando
        #print("Columnas disponibles:", vuelos_columns)  # Imprimir las columnas para verificar qué se está cargando

        # Iterar sobre cada fila, comenzando desde la fila indicada
        for i in range(start_row + 1, excel_data.shape[0]):
            tripulante_assists = {}
            assist_num = 1
            
            # Iterar sobre las columnas de vuelos hasta que ya no existan
            while True:
                assist = f'asistencia {assist_num}'
                #print(assist)
                    
                # Verificar si las columnas existen en el DataFrame
                if assist in assist_columns:
                    col_idx_assist = assist_columns.index(assist)

                    assist_idx = excel_data.iloc[i, col_idx_assist]

                    #print(nro_inter_flight)

                    # Si hay información válida en las columnas, agregarla
                    if pd.notna(assist_idx):
                        tripulante_assists[f'Asistencia {assist_num}'] = {
                            "asistencia": assist_idx,
                        }

                    # Incrementar el vuelo_num para buscar el siguiente conjunto
                    assist_num += 1
                else:
                    break  # Detener la búsqueda si no se encuentra una de las columnas

            # Solo agregar el vuelo si se encontraron vuelos válidos para el tripulante
            if tripulante_assists:
                assists.append(tripulante_assists)

        # Verificar si se encontraron vuelos
        if len(assists) == 0:
            print("No se encontraron asistencias en las filas procesadas.")
        #else:
            #print(f"{len(assists)} asistencias procesadas. ({state})")
            
        return pd.DataFrame(assists)
    
    def _extract_transports(self, excel_data, start_row, state):
        transports = []
        
        # Convertir los nombres de las columnas a cadenas y quitar espacios
        transport_columns = excel_data.loc[start_row].dropna().str.lower().tolist()

        # Verificar las columnas con las que estamos trabajando
        #print("Columnas disponibles:", vuelos_columns)  # Imprimir las columnas para verificar qué se está cargando

        # Iterar sobre cada fila, comenzando desde la fila indicada
        for i in range(start_row + 1, excel_data.shape[0]):
            tripulante_transports = {}
            transports_num = 1
            
            # Iterar sobre las columnas de vuelos hasta que ya no existan
            while True:
                transporte = f'transporte {transports_num}'
                date_pick_up = f'date pick up {transports_num}'
                #print(assist)
                    
                # Verificar si las columnas existen en el DataFrame
                if transporte in transport_columns and date_pick_up in transport_columns:
                    col_idx_transport = transport_columns.index(transporte)
                    col_idx_date_pick_up = transport_columns.index(date_pick_up)

                    transport_idx = excel_data.iloc[i, col_idx_transport]
                    date_pick_up_idx = excel_data.iloc[i, col_idx_date_pick_up]

                    #print(nro_inter_flight)

                    # Si hay información válida en las columnas, agregarla
                    if pd.notna(transport_idx) and pd.notna(date_pick_up_idx):
                        tripulante_transports[f'Transporte {transports_num}'] = {
                            "Transporte": transport_idx,
                            "Date Pick Up": date_pick_up_idx
                        }

                    # Incrementar el vuelo_num para buscar el siguiente conjunto
                    transports_num += 1
                else:
                    break  # Detener la búsqueda si no se encuentra una de las columnas

            # Solo agregar el vuelo si se encontraron vuelos válidos para el tripulante
            if tripulante_transports:
                transports.append(tripulante_transports)

        # Verificar si se encontraron vuelos
        if len(transports) == 0:
            print("No se encontraron transporte en las filas procesadas.")
        #else:
            #print(f"{len(transports)} transportes procesados. ({state})")
            
        return pd.DataFrame(transports)
    
    def _extract_restaurants(self, excel_data, start_row, state):
        restaurants = []
        
        # Convertir los nombres de las columnas a cadenas y quitar espacios
        restaurant_columns = excel_data.loc[start_row].dropna().str.lower().tolist()

        # Verificar las columnas con las que estamos trabajando
        #print("Columnas disponibles:", vuelos_columns)  # Imprimir las columnas para verificar qué se está cargando

        # Iterar sobre cada fila, comenzando desde la fila indicada
        for i in range(start_row + 1, excel_data.shape[0]):
            tripulante_restaurants = {}
            restaurants_num = 1
            
            # Iterar sobre las columnas de vuelos hasta que ya no existan
            while True:
                prefer_alimento = "prefer. aliment"
                servicio_comida = f'servicio comida {restaurants_num}'
                fecha_desde = f'fecha desde {restaurants_num}'
                fecha_hasta = f'fecha hasta {restaurants_num}'
                restaurante = f'restaurant {restaurants_num}'
                #print(assist)
                    
                # Verificar si las columnas existen en el DataFrame
                if prefer_alimento in restaurant_columns and servicio_comida in restaurant_columns and fecha_desde in restaurant_columns and fecha_hasta in restaurant_columns and restaurante in restaurant_columns:
                    col_idx_prefer_alimento = restaurant_columns.index(prefer_alimento)
                    col_idx_servicio_comida = restaurant_columns.index(servicio_comida)
                    col_idx_fecha_desde = restaurant_columns.index(fecha_desde)
                    col_idx_fecha_hasta = restaurant_columns.index(fecha_hasta)
                    col_idx_restaurante = restaurant_columns.index(restaurante)

                    prefer_alimento_idx = excel_data.iloc[i, col_idx_prefer_alimento]
                    servicio_comida_idx = excel_data.iloc[i, col_idx_servicio_comida]
                    fecha_desde_idx = excel_data.iloc[i, col_idx_fecha_desde]
                    fecha_hasta_idx = excel_data.iloc[i, col_idx_fecha_hasta]
                    restaurante_idx = excel_data.iloc[i, col_idx_restaurante]

                    # Si hay información válida en las columnas, agregarla
                    if pd.notna(prefer_alimento_idx) or (pd.notna(servicio_comida_idx) and pd.notna(fecha_desde_idx) and pd.notna(fecha_hasta_idx) and pd.notna(restaurante_idx)):
                        tripulante_restaurants[f'Restaurante {restaurants_num}'] = {
                            "Preferencia": prefer_alimento_idx,
                            "Servicio Comida": servicio_comida_idx,
                            "Fecha desde": fecha_desde_idx,
                            "Fecha hasta": fecha_hasta_idx,
                            "Restaurante": restaurante_idx
                        }

                    # Incrementar el vuelo_num para buscar el siguiente conjunto
                    restaurants_num += 1
                else:
                    break  # Detener la búsqueda si no se encuentra una de las columnas

            # Solo agregar el vuelo si se encontraron vuelos válidos para el tripulante
            if tripulante_restaurants:
                restaurants.append(tripulante_restaurants)

        # Verificar si se encontraron vuelos
        if len(restaurants) == 0:
            print("No se encontraron restaurantes en las filas procesadas.")
        else:
            print(f"{len(restaurants)} restaurantes procesados. ({state})")
            
        return pd.DataFrame(restaurants)
    
    def _extract_extras(self, excel_data, start_row, state):
        extras = []
        
        # Convertir los nombres de las columnas a cadenas y quitar espacios
        extras_columns = excel_data.loc[start_row].dropna().str.lower().tolist()

        # Verificar las columnas con las que estamos trabajando
        #print("Columnas disponibles:", extras_columns)  # Imprimir las columnas para verificar qué se está cargando

        # Iterar sobre cada fila, comenzando desde la fila indicada
        for i in range(start_row + 1, excel_data.shape[0]):
            tripulante_extras = {}
            extras_num = 1
            
            # Iterar sobre las columnas de vuelos hasta que ya no existan
            while True:
                maleta_perdida = "maleta perdida"
                transporte = "transporte"
                atencion_medica = "atencion medica"
                fecha = "fecha"
                ciudad = "ciudad"
                #print(assist)}
                    
                # Verificar si las columnas existen en el DataFrame
                if maleta_perdida in extras_columns and transporte in extras_columns and atencion_medica in extras_columns and fecha in extras_columns and ciudad in extras_columns:
                    col_idx_maleta_perdida = extras_columns.index(maleta_perdida)
                    col_idx_transporte = extras_columns.index(transporte)
                    col_idx_atencion_medica = extras_columns.index(atencion_medica)
                    col_idx_fecha = extras_columns.index(fecha)
                    col_idx_ciudad = extras_columns.index(ciudad)

                    maleta_perdida_idx = excel_data.iloc[i, col_idx_maleta_perdida]
                    transporte_idx = excel_data.iloc[i, col_idx_transporte]
                    atencion_medica_idx = excel_data.iloc[i, col_idx_atencion_medica]
                    fecha_idx = excel_data.iloc[i, col_idx_fecha]
                    ciudad_idx = excel_data.iloc[i, col_idx_ciudad]

                    # Si hay información válida en las columnas, agregarla
                    if pd.notna(maleta_perdida_idx) or pd.notna(transporte_idx) or pd.notna(atencion_medica_idx) or pd.notna(fecha_idx) or pd.notna(ciudad_idx):
                        tripulante_extras[f'Extras {extras_num}'] = {
                            "Maleta perdida": maleta_perdida_idx,
                            "Transporte": transporte_idx,
                            "Atención médica": atencion_medica_idx,
                            "Fecha": fecha_idx,
                            "Ciudad": ciudad_idx
                        }

                    # Incrementar el vuelo_num para buscar el siguiente conjunto
                    extras_num += 1
                    break
                else:
                    break  # Detener la búsqueda si no se encuentra una de las columnas

            # Solo agregar el vuelo si se encontraron vuelos válidos para el tripulante
            if tripulante_extras:
                extras.append(tripulante_extras)

        # Verificar si se encontraron vuelos
        if len(extras) == 0:
            print("No se encontraron extras en las filas procesadas.")
        #else:
            #print(f"{len(extras)} extras procesados. ({state})")
            
        return pd.DataFrame(extras)

    def read_all_rows(self, data, start_row, column_range, column_names):
        #Leer todas las filas a partir de una fila específica, incluyendo filas con celdas vacías.
        
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