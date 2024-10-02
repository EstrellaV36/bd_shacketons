import re
import pandas as pd
from sqlalchemy.orm import Session
from PyQt6.QtWidgets import QMessageBox
from app.models import Buque, Tripulante, Vuelo, EtaCiudad

CITY_AIRPORT_CODES = {
    "PUNTA ARENAS": "PUQ",
    "SANTIAGO": "SCL",
    "PUERTO MONTT": "PMC",
    "VALPARAISO": "VAP",
    "VALDIVIA": "ZAL",
    "PUERTO WILLIAMS": "WPU",
}

class Controller:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_city_list(self):
        return ["Punta Arenas", "Santiago", "Puerto Montt", "Valparaiso", "Valdivia", 'Puerto Williams']

    def process_excel_file(self, file_path):
        try:
            excel_data = pd.read_excel(file_path, sheet_name=None)
            # Filter sheets ending with 'ON' or 'OFF'
            on_sheets = {
                name: df for name, df in excel_data.items()
                if re.search(r'\bON\b$', name, re.IGNORECASE)
            }
            off_sheets = {
                name: df for name, df in excel_data.items()
                if re.search(r'\bOFF\b$', name, re.IGNORECASE)
            }
            # Store flight sheets separately
            self.on_flights = excel_data.get('Itinerarios de Vuelo ON', None)
            self.off_flights = excel_data.get('Itinerarios de Vuelo OFF', None)
            return on_sheets, off_sheets
        except Exception as e:
            raise Exception(f"Error al procesar el archivo: {e}")

    def save_tripulantes_to_db(self, on_sheets, off_sheets):
        try:
            # Process 'ON' tripulantes
            success_on = self._process_tripulantes_sheet(on_sheets.get('Pasajeros y Pasaportes ON', None), 'ON')
            if not success_on:
                raise ValueError("Error al procesar tripulantes ON.")

            # Process 'OFF' tripulantes
            success_off = self._process_tripulantes_sheet(off_sheets.get('Pasajeros y Pasaportes OFF', None), 'OFF')
            if not success_off:
                raise ValueError("Error al procesar tripulantes OFF.")

            # Si todos los registros se procesaron correctamente, guardar los cambios
            self.db_session.commit()
        except Exception as e:
            self.db_session.rollback()
            raise Exception(f"Error al guardar en la base de datos: {e}")

    def _process_tripulantes_sheet(self, df, estado):
        if df is not None:
            for _, row in df.iterrows():
                if pd.isna(row['Vessel']) or pd.isna(row['First name']) or pd.isna(row['Last name']):
                    continue  # Skip incomplete records

                # Buscar o crear 'Buque'
                nombre_buque = row['Vessel'].strip().upper()  # Normalizar el nombre
                nave = self.db_session.query(Buque).filter_by(nombre=nombre_buque).first()
                if not nave:
                    # Si no existe, crear un nuevo buque
                    nave = Buque(
                        nombre=nombre_buque,
                        compañia="Compañía Desconocida",  # O usa el valor correcto si está disponible
                        ciudad="Ciudad Desconocida"  # O usa el valor correcto si está disponible
                    )
                    self.db_session.add(nave)
                    self.db_session.commit()

                # Buscar o crear 'Tripulante'
                tripulante = self.db_session.query(Tripulante).filter_by(pasaporte=row['Passport number']).first()
                if tripulante:
                    tripulante = self._update_tripulante(tripulante, row, nave.buque_id, estado)
                    if tripulante is None:
                        # Si la actualización falla, no continuar con el guardado y salir del método o del bucle
                        return False  # Retorna False para indicar que hubo un error
                else:
                    tripulante = self._create_tripulante(row, nave.buque_id, estado)
                    self.db_session.add(tripulante)

        return True  # Retorna True si no hubo errores


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

    def _create_tripulante(self, row, buque_id, estado):
        tripulante = Tripulante(
            nombre=row['First name'],
            apellido=row['Last name'],
            sexo=row.get('Gender'),
            nacionalidad=row.get('Nationality'),
            pasaporte=row['Passport number'],
            fecha_nacimiento=pd.to_datetime(row.get('Date of birth')).date() if not pd.isna(row.get('Date of birth')) else None,
            buque_id=buque_id,
            estado=estado
        )
        print(f"Tripulante {tripulante.nombre} agregado")

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
