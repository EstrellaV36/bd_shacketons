import re
import pandas as pd
from sqlalchemy.orm import Session
from PyQt6.QtWidgets import QMessageBox
from app.models import Buque, Tripulante, Vuelo, EtaCiudad, Viaje

CITY_AIRPORT_CODES = {
    "PUNTA ARENAS": "PUQ",
    "SANTIAGO": "SCL",
    "PUERTO MONTT": "PMC",
    "VALPARAISO": "VAP",
    "VALDIVIA": "ZAL",
    "PUERTO WILLIAMS": "WPU",
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
            vuelos_internacionales_on = self._extract_international_flights(excel_data_on, start_row=0)

            # Leer la hoja OFF del archivo Excel
            excel_data_off = pd.read_excel(file_path, sheet_name='OFF', header=None)

            # Extraer los datos de los buque OFF (desde fila 22, índice 21)
            buque_off = self.read_all_rows(excel_data_off, start_row=1, column_range=slice(0, 6), column_names=buque_off_columns)
            buque_off.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            # Extraer los datos de tripulantes OFF (fila 22)
            tripulantes_off = self.read_all_rows(excel_data_off, start_row=1, column_range=slice(9, 16), column_names=tripulante_columns) 
            tripulantes_off.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            # Procesar vuelos internacionales OFF
            vuelos_internacionales_off = self._extract_international_flights(excel_data_off, start_row=0)

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

            # Crear buques
            self._create_buque(self.buque_on)
            self._create_buque(self.buque_off)

            # Imprimir los datos extraídos para depuración
            #print("\nDatos de buque ON:")
            #print(buque_on.head())
            #print("\nDatos de buque OFF:")
            #print(buque_off.head())

            #print("\nDatos de tripulantes ON:")
            #print(tripulantes_on.head())
            #print("\nDatos de tripulantes OFF:")
            #print(tripulantes_off.head())

            # Imprimir datos de vuelos internacionales ON y OFF
            print("\nVuelos Internacionales ON:")
            print(vuelos_internacionales_on.head())
            print("\nVuelos Internacionales OFF:")
            print(vuelos_internacionales_off.head())

            # Crear tripulantes ON y OFF
            tripulantes = []
            tripulantes += self._create_tripulantes(tripulantes_on, self.buque_on, "ON")
            tripulantes += self._create_tripulantes(tripulantes_off, self.buque_off, "OFF")
        
            return self.buque_on, self.buque_off, self.tripulantes_on, self.tripulantes_off

        except Exception as e:
            raise Exception(f"Error al procesar el archivo: {e}")
        
    def _extract_international_flights(self, excel_data, start_row):
        vuelos = []
        
        # Convertir los nombres de las columnas a cadenas y quitar espacios
        flight_columns = excel_data.loc[start_row].dropna().tolist()

        # Verificar las columnas con las que estamos trabajando
        print("Columnas disponibles:", flight_columns)  # Imprimir las columnas para verificar qué se está cargando

        # Iterar sobre cada fila, comenzando desde la fila indicada
        for i in range(start_row + 1, excel_data.shape[0]):
            tripulante_vuelos = {}
            vuelo_num = 1
            
            # Iterar sobre las columnas de vuelos hasta que ya no existan
            while True:
                vuelo_col = f'Vuelo Int {vuelo_num}'
                fecha_col = f'Fecha Vuelo Int {vuelo_num}'
                hora_col = f'Hora Vuelo Int {vuelo_num}'

                print(f"Fila {start_row} | i {i}")
                
                # Verificar si las columnas existen en el DataFrame
                if vuelo_col in flight_columns and fecha_col in flight_columns and hora_col in flight_columns:    
                    col_idx_vuelo = flight_columns.index(vuelo_col)
                    col_idx_fecha = flight_columns.index(fecha_col)
                    col_idx_hora = flight_columns.index(hora_col)  
                    #print(f"{vuelo_col} | {fecha_col} | {hora_col}")

                    vuelo = excel_data.iloc[i, col_idx_vuelo]
                    fecha = excel_data.iloc[i, col_idx_fecha]
                    hora = excel_data.iloc[i, col_idx_hora]

                    # Obtener los valores correspondientes
                    #vuelo = excel_data.loc[i, vuelo_col]
                    #fecha = excel_data.loc[i, fecha_col]
                    #hora = excel_data.loc[i, hora_col]

                    print(f"{vuelo} | {fecha} | {hora}")

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
            
            # Solo agregar el vuelo si se encontraron vuelos válidos para el tripulante
            if tripulante_vuelos:
                vuelos.append(tripulante_vuelos)

        # Verificar si se encontraron vuelos
        if len(vuelos) == 0:
            print("No se encontraron vuelos internacionales en las filas procesadas.")
        else:
            print(f"{len(vuelos)} vuelos internacionales procesados.")
            
        return pd.DataFrame(vuelos)

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

    def _create_tripulantes(self, tripulantes_df, buque_df, estado):
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
                        estado=estado  # (ON u OFF)
                    )
                    self.db_session.add(tripulante)
                    self.db_session.commit()  # Confirmar la creación del tripulante

                    tripulante_id = tripulante.tripulante_id
                    print(f"Tripulante {tripulante.nombre} {tripulante.apellido} creado con ID: {tripulante_id}.")

                # Crear un nuevo viaje para el tripulante
                self._create_viaje(tripulante_id, buque_id)
                
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
        
    def _process_tripulantes_sheet(self, df, estado):
        if df is not None:
            for _, row in df.iterrows():
                # Si la fila es completamente vacía, omitirla
                if row.isna().all():
                    continue

                # Buscar o crear 'Buque'
                nombre_buque = row['Vessel'].strip().upper() if pd.notna(row['Vessel']) else None
                if not nombre_buque:
                    continue  # Si el nombre del buque es inválido, omitir

                nave = self.db_session.query(Buque).filter_by(nombre=nombre_buque).first()
                if not nave:
                    # Si no existe, crear un nuevo buque
                    nave = Buque(
                        nombre=nombre_buque,
                        compañia="Compañía Desconocida",  # Puedes modificar esto según la lógica deseada
                        ciudad="Ciudad Desconocida"
                    )
                    self.db_session.add(nave)
                    self.db_session.commit()

                # Buscar o crear 'Tripulante'
                pasaporte = row['Passport number'].strip() if pd.notna(row['Passport number']) else None
                if not pasaporte:
                    continue  # Si el pasaporte es inválido, omitir

                tripulante = self.db_session.query(Tripulante).filter_by(pasaporte=pasaporte).first()
                if tripulante:
                    tripulante = self._update_tripulante(tripulante, row, nave.buque_id, estado)
                else:
                    tripulante = self._create_tripulante(row, nave.buque_id, estado)
                    self.db_session.add(tripulante)

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

    def assign_flights_to_tripulantes(self):
        try:
            # Assign 'ON' flights
            self._assign_flights(self.on_flights)
            # Assign 'OFF' flights
            self._assign_flights(self.off_flights)
            self.db_session.commit()
        except Exception as e:
            self.db_session.rollback()
            raise Exception(f"Error al asignar vuelos: {e}")

    def _assign_flights(self, flights_df):
        if flights_df is not None:
            for _, row in flights_df.iterrows():
                tripulante = self.db_session.query(Tripulante).filter_by(pasaporte=row['Passport'].strip()).first()
                if tripulante:
                    print(f"Tripulante encontrado: {tripulante.nombre} {tripulante.apellido}")

                    # Verificar si el vuelo ya existe para el tripulante
                    vuelo_existente = self.db_session.query(Vuelo).filter_by(
                        codigo=row['Flight'],
                        tripulante_id=tripulante.tripulante_id
                    ).first()
                    
                    if not vuelo_existente:
                        vuelo = Vuelo(
                            codigo=row['Flight'],
                            aeropuerto_salida=row['Departure airport'],
                            hora_salida=pd.to_datetime(f"{row['Departure date']} {row['Departure time']}"),
                            aeropuerto_llegada=row['Arrival airport'],
                            hora_llegada=pd.to_datetime(f"{row['Arrival date']} {row['Arrival time']}"),
                            tripulante_id=tripulante.tripulante_id,
                        )
                        self.db_session.add(vuelo)

                        # Añadir la validación antes de crear el registro de ETA
                        eta_existente = self.db_session.query(EtaCiudad).filter_by(
                            tripulante_id=tripulante.tripulante_id,
                            ciudad=row['Arrival airport']
                        ).first()

                        if not eta_existente:
                            eta_ciudad = EtaCiudad(
                                tripulante_id=tripulante.tripulante_id,
                                ciudad=row['Arrival airport'],
                                eta=pd.to_datetime(f"{row['Arrival date']} {row['Arrival time']}")
                            )
                            print(f"ETA asignado: {eta_ciudad.eta} para {tripulante.nombre} en {eta_ciudad.ciudad}")
                            self.db_session.add(eta_ciudad)
                        else:
                            print(f"ETA ya existe para el tripulante: {tripulante.nombre} en la ciudad: {eta_existente.ciudad}")
                    else:
                        print(f"Vuelo ya existe para el tripulante: {tripulante.nombre}")
                else:
                    print(f"No se encontró tripulante para el pasaporte: {row['Passport']}")

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