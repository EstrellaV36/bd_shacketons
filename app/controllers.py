from datetime import datetime
import re
import pandas as pd
from sqlalchemy.orm import Session
import traceback
from sqlalchemy import func
from PyQt6.QtWidgets import QMessageBox
from app.models import Buque, Tripulante, Vuelo, EtaCiudad, Viaje, TripulanteVuelo, Hotel, TripulanteHotel, Transporte, TripulanteTransporte

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
    'LUN': "LUSAKA",  # Kenneth Kaunda International Airport
    'DOH': "DOHA",    # Hamad International Airport
    'PUJ': "PUNTA CANA",  # Punta Cana International Airport
    'LIM': "LIMA",     # Jorge Chávez International Airport
    'ANF': "ANTOFAGASTA",
    'IQQ': "IQUIQUE",
    'CCP': "CONCEPCIÓN",
    'LSC': "LA SERENA",
    'ARI': "ARICA",
    'IPC': "RAPA NUI",
    'LAX': "LOS ÁNGELES",
    'JFK': "NUEVA YORK",  # John F. Kennedy International Airport
    'MAD': "MADRID",  # Adolfo Suárez Madrid–Barajas Airport
    'LHR': "LONDRES",
    'DXB': "DUBÁI",
    'MQP': "MPUMALANGA",  # Mpumalanga International Airport
    'JNB': "JOHANNESBURGO",  # O.R. Tambo International Airport
    'LCA': "LÁRNACA",  # Larnaca International Airport
    'ZRH': "ZÚRICH",  # Zurich Airport
    'GOX': "GOLFE DE GARABOGAZ",  # Golfe de Garabogaz Airport
    'TRV': "THIRUVANANTHAPURAM",  # Trivandrum International Airport
    'PVG': "SHANGHAI",  # Shanghai Pudong International Airport
    'CGK': "YAKARTA",  # Soekarno-Hatta International Airport
    'BDS': "BRINDISI",  # Brindisi Airport
    'GRU': "SÃO PAULO",  # São Paulo/Guarulhos–Governador André Franco Montoro International Airport
    'NBO': "NAIROBI",  # Jomo Kenyatta International Airport
    'ICN': "SEÚL",  # Incheon International Airport
    'HRE': "HARARE",  # Harare International Airport
    'OTP': "BUCARESTANT",  # Henri Coandă International Airport
    'AKL': "AUCKLAND",  # Auckland Airport
    'FCO': "ROMA",  # Aeropuerto Internacional Leonardo da Vinci
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
        print(f"Vuelo encontrado con el codigo: {vuelo.codigo}")
        return vuelo.codigo
    else:
        raise ValueError(f"Vuelo {vuelo.codigo} no encontrado en la base de datos.")

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

            #Procesar hoteles OFF
            hoteles_off = self._extract_hotels(excel_data_off, start_row=0, state="off")
            hoteles_off.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            #Procesar vuelos internacionales OFF
            vuelos_internacionales_off = self._extract_international_flights(excel_data_on, start_row=0, state="on")
            vuelos_internacionales_off.reset_index(drop=True, inplace=True)  # Reiniciar el índice

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

            #print(f"Hotel ON: {hoteles_on.head()}")
            # Almacenar los datos
            self.tripulantes_on = tripulantes_on
            self.tripulantes_off = tripulantes_off
            self.buque_on = buque_on
            self.buque_off = buque_off
            self.vuelos_internacionales_on = vuelos_internacionales_on
            self.vuelos_internacionales_off = vuelos_internacionales_off
            self.hoteles_on = hoteles_on
            self.hoteles_off = hoteles_off
            self.asistencias_on = asistencias_on
            self.asistencias_off = asistencias_off
            self.transportes_on = transportes_on
            self.transportes_off = transportes_off
            self.restaurantes_on = restaurantes_on
            self.restaurantes_off = restaurantes_off
            self.extras_on = extras_on
            self.extras_off = extras_off

            # Crear buques ON y OFF
            self._create_buque(self.buque_on)
            self._create_buque(self.buque_off)

            # Crear tripulantes ON y OFF
            tripulantes = []
            tripulantes += self._create_tripulantes(tripulantes_on, self.buque_on, self.asistencias_on)
            tripulantes += self._create_tripulantes(tripulantes_off, self.buque_off, self.asistencias_off)

            # Crear vuelos ON y OFF
            self._create_vuelos(self.vuelos_internacionales_on, self.tripulantes_on, state='on')
            self._create_vuelos(self.vuelos_internacionales_off, self.tripulantes_off, state='off')

            self._create_hotel(self.hoteles_on, self.tripulantes_on)

            self._create_transporte(self.transportes_on, self.tripulantes_on)
            self._create_transporte(self.transportes_off, self.tripulantes_off)

            return self.buque_on, self.buque_off, self.tripulantes_on, self.tripulantes_off

        except Exception as e:
            raise Exception(f"Error al procesar el archivo: {e}")

    def _create_transporte(self, transportes_df, tripulantes_df):
        transportes = []  # Lista para almacenar los vuelos creados
        try:
            # Verificar que ambos DataFrames no estén vacíos
            if transportes_df.empty or tripulantes_df.empty:
                print("No hay vuelos o tripulantes para procesar.")
                return []

            x=1
            # Iterar sobre cada fila del DataFrame de vuelos
            for i, row in transportes_df.iterrows():
                # Verificar que la fila de tripulantes tenga un índice válido
                if i >= len(tripulantes_df):
                    #print(f"No hay datos de tripulante para la fila {i}.")
                    continue

                # Obtener el tripulante correspondiente a la fila actual
                tripulante_data = tripulantes_df.iloc[i]

                if pd.isna(tripulante_data['Pasaporte']):
                    print(f"Pasaporte vacío para el tripulante en la fila {i}. Omitiendo...")
                    continue

                tripulante = self.db_session.query(Tripulante).filter_by(pasaporte=tripulante_data['Pasaporte']).first()
                
                if not tripulante:
                    print(f"No se encontró tripulante con pasaporte {tripulante_data['Pasaporte']} en la fila {i}.")
                    continue

                # Iterar sobre las claves que representan los vuelos
                for transporte_key in row.index:
                    transporte_info = row[transporte_key]  # Obtener el diccionario del vuelo

                    # Verificar que haya información para el vuelo
                    if pd.notna(transporte_info) and isinstance(transporte_info, dict):  # Solo procesar si hay información y es un diccionario                        
                        transporte_info = self._extraer_transportes(transporte_info)

                        for _transporte in transporte_info:
                            # Verificar que el valor de 'tramo' no sea 'Desconocido'
                            if _transporte['tramo'] != 'Desconocido':
                                if transporte_info is None or 'tramo' not in _transporte:
                                    print(f"Omitiendo transporte {transporte_info} en la fila {i} debido a datos faltantes.")
                                    continue

                                transporte = self.db_session.query(Transporte).filter_by(nombre=_transporte['tramo']).first()
                                
                                if not transporte:
                                    transporte = Transporte(
                                        nombre=_transporte['tramo'],
                                        ciudad="A",
                                    )
                                    self.db_session.add(transporte)
                                    self.db_session.flush()  # Asegurar que el vuelo esté disponible en la base de datos
                                    transportes.append(transporte)  # Agregar el vuelo a la lista de vuelos

                                tripulante_transporte_existente = self.db_session.query(TripulanteTransporte).filter_by(
                                    tripulante_id=tripulante.tripulante_id,
                                    transporte_id=transporte.transporte_id,
                                ).first()

                                if not tripulante_transporte_existente:
                                    ciudad = _transporte['ciudad']
                                    lugar_inicio = _transporte['lugar_inicio']
                                    lugar_final = _transporte['lugar_final']
                                    fecha = _transporte['fecha']
                                    # Asociar el tripulante al vuelo en la tabla intermedia TripulanteVuelo
                                    tripulante_vuelo = TripulanteTransporte(
                                        tripulante_id=tripulante.tripulante_id,
                                        transporte_id=transporte.transporte_id,
                                        ciudad=ciudad,
                                        lugar_inicio=lugar_inicio,
                                        lugar_final=lugar_final,
                                        fecha=fecha
                                    )
                                    self.db_session.add(tripulante_vuelo)
                                    self.db_session.flush()
                    else:
                        continue

            self.db_session.commit()

        except Exception as e:
            print(f"Error al crear vuelos o asignar tripulantes: {e}")
            traceback.print_exc()  # Esto imprime el traceback completo para depurar
            self.db_session.rollback()  # Revertir la sesión en caso de error

        return transportes  # Retornar la lista de vuelos creados

    def _extraer_transportes(self, transporte_info):        
        transportes_info = []

        if Transporte is None or pd.isna(Transporte):
            print("Transporte es NaN o None. Omitiendo...")
            return None
        
        if transporte_info['Transporte'] != 'Desconocido':
            tramo = transporte_info['Transporte']
            ciudad, resto = tramo.split(" ", 1)
            lugar_inicio, lugar_final = resto.split("-", 1)
            fecha = transporte_info['Date Pick Up']

            transportes_info.append({
                'tramo': tramo,
                'ciudad': ciudad,
                'lugar_inicio': lugar_inicio,
                'lugar_final': lugar_final,
                'fecha': fecha
            })
        
        return transportes_info

    def _extraer_ciudades_y_horarios(self, vuelo_info, tipo_vuelo):        
        vuelo = vuelo_info['vuelo']

        # Verifica si el vuelo es NaN o None
        if vuelo is None or pd.isna(vuelo):
            print("Vuelo es NaN o None. Omitiendo...")
            return None  # O puedes lanzar un error, dependiendo de cómo manejes esto

        # Dividir la cadena del vuelo en partes
        partes = vuelo.split()
        
        if len(partes) < 2:
            raise ValueError(f"Formato de vuelo inválido: {vuelo_info[vuelo]}")

        codigo_vuelo = partes[0]  # 'AF178' o 'KL702'
        aeropuertos = partes[1]  # 'CDG' o 'SCL'
        aeropuerto_salida, aeropuerto_llegada = aeropuertos.split("-")

        # Obtener la fecha y las horas como objetos datetime
        fecha_vuelo = vuelo_info['fecha']  # Se espera que sea un objeto Timestamp
        hora_salida, hora_llegada = vuelo_info['hora'].split('-')

        # Eliminar espacios en blanco antes de convertir a datetime
        hora_salida = hora_salida.strip()
        hora_llegada = hora_llegada.strip()

        # Verifica si la hora de llegada contiene un '+1' y ajusta la hora
        if '+1' in hora_llegada:
            hora_llegada = hora_llegada.replace('+1', '').strip()  # Eliminar '+1' de la hora de llegada
            # Aquí no se modifica la fecha_vuelo, solo se ajusta la hora_llegada

        # Convertir las horas de salida y llegada a objetos datetime
        hora_salida = datetime.combine(fecha_vuelo.date(), datetime.strptime(hora_salida, "%H:%M").time())
        
        # Convertir la hora de llegada
        hora_llegada = datetime.combine(fecha_vuelo.date(), datetime.strptime(hora_llegada, "%H:%M").time())
        
        # Si la hora de llegada era originalmente pasada la medianoche, ajusta para mostrarlo como un día más
        if '+1' in vuelo_info['hora']:
            hora_llegada += pd.Timedelta(days=1)  # Esto es solo para el cálculo, pero puedes ajustar el formato al mostrarlo.

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
    
    def _create_tripulantes(self, tripulantes_df, buque_df, asistencias_df):
        tripulantes = []  # Lista para almacenar los tripulantes creados
        vuelos_tripulante = []  # Lista para almacenar los vuelos asociados a cada tripulante
        try:
            # Asegurarse de que ambos DataFrames tienen la misma longitud
            if len(tripulantes_df) != len(buque_df):
                raise ValueError("El número de tripulantes no coincide con el número de buques.")

            # Iterar sobre cada fila del DataFrame de tripulantes
            for i, row in tripulantes_df.iterrows():
                # Comprobar si el índice i está dentro de buque_df
                if i >= len(buque_df):
                    raise IndexError(f"Índice fuera de rango: {i} no está en buque_df.")

                # Obtener el nombre del buque correspondiente
                nombre_buque = buque_df.loc[i]['Vessel']
                buque_id = buscar_buque_id(nombre_buque, self.db_session)

                # Buscar si el tripulante ya existe en la base de datos por pasaporte
                tripulante_existente = self.db_session.query(Tripulante).filter_by(pasaporte=row['Pasaporte']).first()

                if tripulante_existente:
                    continue
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

                    tripulante_existente = tripulante  # Asignar el nuevo tripulante a la variable existente

                # Asignar asistencias al tripulante
                asistencias_tripulante = asistencias_df.iloc[i]  # Obtener la fila de asistencias correspondiente

                # Extraer los valores de asistencia como una lista
                asistencias_lista = [asistencia['asistencia'] for asistencia in asistencias_tripulante]

                # Asignar booleanos según la presencia de cada asistencia
                tripulante_existente.necesita_asistencia_scl = 'Asistencia SCL' in asistencias_lista
                tripulante_existente.necesita_asistencia_puq = 'Asistencia PUQ' in asistencias_lista
                tripulante_existente.necesita_asistencia_wpu = 'Asistencia WPU' in asistencias_lista

                # Confirmar los cambios en la base de datos
                self.db_session.commit()

                tripulantes.append(tripulante_existente)  # Agregar a la lista

            # Retornar la lista de tripulantes y vuelos asociados
            return tripulantes, vuelos_tripulante
        except Exception as e:
            print(f"Error al crear tripulantes o encontrar vuelos: {e}")
            self.db_session.rollback()  # Revertir la sesión en caso de error
            return [], []  # Devolver listas vacías en caso de error

    def _create_buque(self, buques_df):
        try:
            if 'Puerto a embarcar' in buques_df.columns:
                buques_df.rename(columns={'Puerto a embarcar': 'Puerto'}, inplace=True)

            if 'Puerto a desembarcar' in buques_df.columns:
                buques_df.rename(columns={'Puerto a desembarcar': 'Puerto'}, inplace=True)

            for _, row in buques_df.iterrows():
                # Normalizar el nombre del buque
                vessel_name = row['Vessel'].strip().lower()

                # Verificar si el buque ya existe
                buque_existente = self.db_session.query(Buque).filter(func.lower(Buque.nombre) == vessel_name).first()

                if buque_existente:
                    #print(f"Buque {buque_existente.nombre} ya existente")

                    # Normalizar las fechas ETA y ETD truncando los microsegundos
                    eta_fecha = pd.to_datetime(row['ETA Vessel']).replace(microsecond=0)
                    etd_fecha = pd.to_datetime(row['ETD Vessel']).replace(microsecond=0)

                    # Verificar si ya existe una ETA similar para este buque
                    eta_existente = self.db_session.query(EtaCiudad).filter_by(
                        buque_id=buque_existente.buque_id,
                        ciudad=row['Puerto']
                    ).filter(
                        func.date(EtaCiudad.eta) == eta_fecha.date(),
                        func.date(EtaCiudad.etd) == etd_fecha.date()
                    ).first()

                    if eta_existente:
                        #print(f"ETA ya existente para buque {buque_existente.nombre} en {row['Puerto']} con ETA {eta_existente.eta} y ETD {eta_existente.etd}")
                        continue
                    else:
                        # Si no existe una ETA igual, agregarla
                        nueva_eta = EtaCiudad(
                            buque=buque_existente,
                            ciudad=row['Puerto'],
                            eta=eta_fecha,
                            etd=etd_fecha
                        )
                        buque_existente.etas.append(nueva_eta)
                        self.db_session.add(nueva_eta)
                        self.db_session.flush()  # Asegurar que la nueva ETA esté en la BD
                        #print(f"Nueva ETA añadida a buque existente: {buque_existente.nombre}, ETA: {nueva_eta.eta}, ETD: {nueva_eta.etd}")
                else:
                    # Crear un nuevo buque
                    nuevo_buque = Buque(
                        nombre=row['Vessel'].strip(),
                        empresa=row['Owner'] if pd.notna(row['Owner']) else "Empresa Desconocida",
                        ciudad=row['Puerto'] if pd.notna(row['Puerto']) else "Ciudad Desconocida"
                    )
                    self.db_session.add(nuevo_buque)
                    self.db_session.flush()  # Generar el ID del nuevo buque

                    # Añadir la ETA al nuevo buque
                    nueva_eta = EtaCiudad(
                        buque=nuevo_buque,
                        ciudad=row['Puerto'],
                        eta=pd.to_datetime(row['ETA Vessel']).replace(microsecond=0),
                        etd=pd.to_datetime(row['ETD Vessel']).replace(microsecond=0)
                    )
                    nuevo_buque.etas.append(nueva_eta)
                    self.db_session.add(nueva_eta)
                    self.db_session.flush()  # Asegurar que la nueva ETA esté en la BD
                    #print(f"Nuevo buque creado: {nuevo_buque.nombre}, ETA: {nueva_eta.eta}, ETD: {nueva_eta.etd}")

            # Confirmar todos los cambios al final
            self.db_session.commit()

        except Exception as e:
            self.db_session.rollback()  # Revertir cambios en caso de error
            raise Exception(f"Error al crear o actualizar buques: {e}")

        return "Proceso completado exitosamente"

    def _create_vuelos(self, vuelos_df, tripulantes_df, state):
        vuelos = []  # Lista para almacenar los vuelos creados
        try:
            # Verificar que ambos DataFrames no estén vacíos
            if vuelos_df.empty or tripulantes_df.empty:
                print("No hay vuelos o tripulantes para procesar.")
                return []

            # Iterar sobre cada fila del DataFrame de vuelos
            for i, row in vuelos_df.iterrows():
                # Verificar que la fila de tripulantes tenga un índice válido
                if i >= len(tripulantes_df):
                    #print(f"No hay datos de tripulante para la fila {i}.")
                    continue

                # Obtener el tripulante correspondiente a la fila actual
                tripulante_data = tripulantes_df.iloc[i]

                if pd.isna(tripulante_data['Pasaporte']):
                    print(f"Pasaporte vacío para el tripulante en la fila {i}. Omitiendo...")
                    continue

                tripulante = self.db_session.query(Tripulante).filter_by(pasaporte=tripulante_data['Pasaporte']).first()
                
                if not tripulante:
                    print(f"No se encontró tripulante con pasaporte {tripulante_data['Pasaporte']} en la fila {i}.")
                    continue

                #print(f"Tripulante {tripulante.nombre} encontrado para procesar vuelos.")

                # Iterar sobre las claves que representan los vuelos
                for vuelo_key in row.index:
                    vuelo_info = row[vuelo_key]  # Obtener el diccionario del vuelo
                    #print(vuelo_info)

                    # Verificar que haya información para el vuelo
                    if pd.notna(vuelo_info) and isinstance(vuelo_info, dict):  # Solo procesar si hay información y es un diccionario                        
                        vuelo_info = self._extraer_ciudades_y_horarios(vuelo_info, state)

                        if vuelo_info is None or 'codigo_vuelo' not in vuelo_info:
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
                            self.db_session.flush()  # Asegurar que el vuelo esté disponible en la base de datos
                            vuelos.append(vuelo)  # Agregar el vuelo a la lista de vuelos

                        #print(f"Vuelo {vuelo.codigo} encontrado o creado.")

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
                            self.db_session.flush()  # Confirmar la asociación sin hacer commit completo
                            #print(f"Tripulante {tripulante.nombre} asignado al vuelo {vuelo.codigo}.")
                    else:
                        #print(f"No hay información para {vuelo_key} en la fila {i}.")
                        continue

            # Confirmar todos los cambios al final
            self.db_session.commit()

        except Exception as e:
            print(f"Error al crear vuelos o asignar tripulantes: {e}")
            traceback.print_exc()  # Esto imprime el traceback completo para depurar
            self.db_session.rollback()  # Revertir la sesión en caso de error

        return vuelos  # Retornar la lista de vuelos creados
    
    def _extraer_hoteles_fechas(self, hotel_df):
        hoteles_info = []  # Lista para almacenar la información de los hoteles

        # Iterar sobre cada fila del DataFrame de hoteles
        for i, row in hotel_df.iterrows():
            # Iterar sobre las claves que representan los hoteles
            for hotel_key in row.index:
                hotel_info = row[hotel_key]  # Obtener la información del hotel

                if isinstance(hotel_info, dict):  # Solo procesar si es un diccionario
                    # Asignar valores
                    
                    hotel_nombre = hotel_info['nombre_hotel'] if pd.notna(hotel_info['nombre_hotel']) else 'Desconocido'
                    categoria = hotel_info['categoria']
                    
                    # Extraer el código de la ciudad del nombre del hotel
                    ciudad_codigo = hotel_info['hotel'].split()[-1]  # Suponiendo que el formato es "Hotel [CÓDIGO]"
                    ciudad = CITY_AIRPORT_CODES.get(ciudad_codigo, 'Desconocida')  # Obtener ciudad del diccionario

                    # Obtener las fechas de check-in y check-out
                    check_in = hotel_info.get('check_in', None)
                    check_out = hotel_info.get('check_out', None)

                    # Calcular número de noches
                    if pd.notna(check_in) and pd.notna(check_out):
                        num_noches = (pd.to_datetime(check_out) - pd.to_datetime(check_in)).days
                    else:
                        num_noches = 0  # O definir un valor por defecto si es necesario

                    # Acceder al tipo de habitación desde hotel_info
                    tipo_habitacion = hotel_info.get('habitacion', None)  # Extraer tipo de habitación
                    #print(tipo_habitacion)  # Para ver el valor de la habitación extraída

                    # Almacenar la información del hotel en la lista
                    hoteles_info.append({
                        'nombre_hotel': hotel_nombre,
                        'categoria': categoria,
                        'ciudad': ciudad,
                        'check_in': check_in,
                        'check_out': check_out,
                        'numero_noches': num_noches,
                        'habitacion': tipo_habitacion  # Añadir el tipo de habitación
                    })
                elif pd.isna(hotel_info) or (isinstance(hotel_info, str) and hotel_info.strip() == "SIN HOTEL"):
                    # Manejar el caso "SIN HOTEL"
                    hoteles_info.append({
                        'nombre_hotel': 'SIN HOTEL',
                        'categoria': None,
                        'ciudad': 'Desconocida',
                        'check_in': None,
                        'check_out': None,
                        'numero_noches': 0,
                        'habitacion': None  # Por defecto en este caso
                    })

        return hoteles_info  # Retornar la lista con la información de los hoteles

    def _create_hotel(self, hotel_df, tripulantes_df):
        hotels = []  # Lista para almacenar los hoteles creados
        try:
            # Verificar que ambos DataFrames no estén vacíos
            if hotel_df.empty or tripulantes_df.empty:
                print("No hay hoteles o tripulantes para procesar.")
                return hotels  # Retornar la lista vacía en caso de no haber datos

            # Extraer la información de los hoteles utilizando la nueva función
            hoteles_info = self._extraer_hoteles_fechas(hotel_df)

            # Iterar sobre cada fila del DataFrame de hoteles
            for i, row in hotel_df.iterrows():
                #print(f"Procesando fila {i} del DataFrame de hoteles:")
                # Verificar que la fila de tripulantes tenga un índice válido
                if i >= len(tripulantes_df):
                    continue

                # Obtener el tripulante correspondiente a la fila actual
                tripulante_data = tripulantes_df.iloc[i]
                if pd.isna(tripulante_data['Pasaporte']):
                    print(f"Pasaporte vacío para el tripulante en la fila {i}. Omitiendo...")
                    continue

                tripulante = self.db_session.query(Tripulante).filter_by(pasaporte=tripulante_data['Pasaporte']).first()
                if not tripulante:
                    print(f"No se encontró tripulante con pasaporte {tripulante_data['Pasaporte']} en la fila {i}.")
                    continue

                #print(hoteles_info)

                # Iterar sobre la información extraída de los hoteles
                for hotel_info in hoteles_info:
                    hotel_nombre = hotel_info['nombre_hotel']
                    categoria = hotel_info['categoria']
                    ciudad = hotel_info['ciudad']
                    check_in = hotel_info['check_in']
                    check_out = hotel_info['check_out']
                    num_noches = hotel_info['numero_noches']
                    tipo_habitacion = hotel_info.get('habitacion')  # Recuperar el tipo de habitación

                    # Verificar si el hotel ya existe
                    existing_hotel = self.db_session.query(Hotel).filter_by(nombre=hotel_nombre, ciudad=ciudad).first()

                    if existing_hotel:
                        hotel = existing_hotel
                        #print(f"  Hotel existente encontrado: {hotel}")
                    else:
                        # Crear el objeto Hotel
                        hotel = Hotel(
                            nombre=hotel_nombre,
                            ciudad=ciudad,
                        )
                        # Añadir el hotel a la sesión
                        self.db_session.add(hotel)
                        self.db_session.flush()  # Asegúrate de que el hotel tiene un ID antes de asignarlo
                        print(f"  Hotel creado: {hotel}")

                    # Verificar si hay un "To Be Confirmed" y si las fechas y el hotel están cambiando
                    tripulante_hotel = self.db_session.query(TripulanteHotel).filter_by(
                        tripulante_id=tripulante.tripulante_id,
                        hotel_id=hotel.hotel_id
                    ).first()

                    if tripulante_hotel:
                        # Actualizar si es un hotel TBC
                        if tripulante_hotel.hotel_id == existing_hotel.hotel_id and existing_hotel.nombre == "TBC":
                            tripulante_hotel.hotel_id = hotel.hotel_id
                            tripulante_hotel.fecha_entrada = check_in
                            tripulante_hotel.fecha_salida = check_out
                            tripulante_hotel.tipo_habitacion = tipo_habitacion
                            tripulante_hotel.numero_noches = num_noches
                            #print(f"  Relación Tripulante-Hotel actualizada: {tripulante_hotel}")
                    else:
                        # Verificar que los IDs son válidos antes de crear la relación
                        fecha_entrada = check_in if pd.notna(check_in) else None
                        fecha_salida = check_out if pd.notna(check_out) else None

                        if tripulante.tripulante_id is not None and hotel.hotel_id is not None:
                            # Crear la relación en TripulanteHotel
                            tripulante_hotel = TripulanteHotel(
                                tripulante_id=tripulante.tripulante_id,
                                hotel_id=hotel.hotel_id,
                                fecha_entrada=fecha_entrada,
                                fecha_salida=fecha_salida,
                                tipo_habitacion=tipo_habitacion,  # Asignar el tipo de habitación
                                numero_noches=num_noches,
                                categoria=categoria if pd.notna(categoria) else None,
                                day_room=False
                            )

                            # Añadir la relación a la sesión
                            self.db_session.add(tripulante_hotel)
                            #print(f"  Relación Tripulante-Hotel creada: {tripulante_hotel}")

            # Confirmar los cambios en la base de datos
            self.db_session.commit()
            #print("Todos los cambios han sido confirmados en la base de datos.")

        except Exception as e:
            print(f"Error al crear hoteles o asignar tripulantes: {e}")
            traceback.print_exc()  # Esto imprime el traceback completo para depurar
            self.db_session.rollback()  # Revertir los cambios en caso de error

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

        # Iterar sobre cada fila, comenzando desde la fila indicada
        for i in range(start_row + 1, excel_data.shape[0]):
            tripulante_hotels = {}
            hotel_num = 1
            
            # Iterar sobre las columnas de hoteles hasta que ya no existan
            while True:
                category = 'silver categoria'
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

                    categoria = excel_data.iloc[i, col_idx_category]
                    hotel = excel_data.iloc[i, col_idx_hotel]
                    check_in = excel_data.iloc[i, col_idx_check_in]
                    check_out = excel_data.iloc[i, col_idx_check_out]
                    habitacion = excel_data.iloc[i, col_idx_rooms]
                    nombre_hotel = excel_data.iloc[i, col_idx_hotel_name]
                    #print(f"Fila {i}: habitacion = {habitacion}")
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

                    # Incrementar el número de hotel para buscar el siguiente conjunto
                    hotel_num += 1
                else:
                    break  # Detener la búsqueda si no se encuentra una de las columnas

            # Asegurarse de agregar al tripulante incluso si no tiene hoteles
            if not tripulante_hotels:  # Si el diccionario está vacío, agregar un mensaje
                tripulante_hotels['SIN HOTEL'] = {
                    "categoria": 'SIN HOTEL',
                    "hotel": 'SIN HOTEL',
                    "check_in": None,
                    "check_out": None,
                    "habitacion": None,
                    "nombre_hotel": 'SIN HOTEL'
                }

            hotels.append(tripulante_hotels)

        # Verificar si se encontraron hoteles
        if len(hotels) == 0:
            print("No se encontraron hoteles en las filas procesadas.")
        else:
            print(f"{len(hotels)} hoteles procesados. ({state})")
            
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

        # Iterar sobre cada fila, comenzando desde la fila indicada
        for i in range(start_row + 1, excel_data.shape[0]):
            tripulante_assists = {}
            assist_num = 1
            
            # Iterar sobre las columnas de vuelos hasta que ya no existan
            while True:
                assist = f'asistencia {assist_num}'
                    
                # Verificar si las columnas existen en el DataFrame
                if assist in assist_columns:
                    col_idx_assist = assist_columns.index(assist)

                    assist_idx = excel_data.iloc[i, col_idx_assist]

                    # Si hay información válida en las columnas, agregarla
                    if pd.notna(assist_idx):
                        tripulante_assists[f'Asistencia {assist_num}'] = {
                            "asistencia": assist_idx,
                        }
                    else:
                        # Si el campo está vacío, agregar un valor predeterminado
                        tripulante_assists[f'Asistencia {assist_num}'] = {
                            "asistencia": "NO",  # o cualquier valor que consideres apropiado
                        }

                    # Incrementar el vuelo_num para buscar el siguiente conjunto
                    assist_num += 1
                else:
                    break  # Detener la búsqueda si no se encuentra una de las columnas

            # Agregar el tripulante_assists, incluso si está vacío
            assists.append(tripulante_assists)

        # Verificar si se encontraron asistencias
        if len(assists) == 0:
            print("No se encontraron asistencias en las filas procesadas.")
            
        return pd.DataFrame(assists)

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
                transporte = f'transporte {transports_num}'
                date_pick_up = f'date pick up {transports_num}'

                # Verificar si las columnas de transporte y fecha existen
                if transporte in transport_columns and date_pick_up in transport_columns:
                    col_idx_transport = transport_columns.index(transporte)
                    col_idx_date_pick_up = transport_columns.index(date_pick_up)

                    transport_idx = excel_data.iloc[i, col_idx_transport] if col_idx_transport < excel_data.shape[1] else None
                    date_pick_up_idx = excel_data.iloc[i, col_idx_date_pick_up] if col_idx_date_pick_up < excel_data.shape[1] else None

                    # Asignar valores 'Desconocido' si faltan datos
                    transport_value = transport_idx if pd.notna(transport_idx) else 'Desconocido'
                    date_pick_up_value = date_pick_up_idx if pd.notna(date_pick_up_idx) else 'Desconocido'

                    # Agregar el transporte al diccionario del tripulante
                    tripulante_transports[f'Transporte {transports_num}'] = {
                        "Transporte": transport_value,
                        "Date Pick Up": date_pick_up_value
                    }

                    # Incrementar el contador para verificar el siguiente transporte
                    transports_num += 1
                else:
                    # No hay más columnas de transporte y fecha, salir del bucle
                    break

            # Agregar una entrada para el tripulante actual, incluso si no se encontraron transportes
            if not tripulante_transports:
                # Si no se encontraron transportes, agregar un valor por defecto
                tripulante_transports[f'Transporte {transports_num}'] = {
                    "Transporte": 'Desconocido',
                    "Date Pick Up": 'Desconocido'
                }

            # Agregar los transportes del tripulante a la lista final
            transports.append(tripulante_transports)
        
        """x=2
        for transport in transports:
            print(f"{transport['Transporte 3']} {x}")
            x+=1"""

        # Verificar si se encontraron transportes
        if len(transports) == 0:
            print("No se encontraron transportes en las filas procesadas.")
            
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