# app/controllers.py
import re
import pandas as pd
from app.database import SessionLocal
from app.models import Buque, Tripulante, Vuelo, EtaCiudad
from PyQt6.QtWidgets import QMessageBox

class Controller:
    def __init__(self):
        pass

    def get_city_list(self):
        return ["Punta Arenas", "Santiago", "Puerto Montt", "Valparaíso", "Valdivia", 'Puerto Williams']

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
        session = SessionLocal()
        try:
            # Process 'ON' tripulantes
            self._process_tripulantes_sheet(session, on_sheets.get('Pasajeros y Pasaportes ON', None), 'ON')
            # Process 'OFF' tripulantes
            self._process_tripulantes_sheet(session, off_sheets.get('Pasajeros y Pasaportes OFF', None), 'OFF')
            session.commit()
        except Exception as e:
            session.rollback()
            raise Exception(f"Error al guardar en la base de datos: {e}")
        finally:
            session.close()

    def _process_tripulantes_sheet(self, session, df, estado):
        if df is not None:
            for _, row in df.iterrows():
                if pd.isna(row['Vessel']) or pd.isna(row['First name']) or pd.isna(row['Last name']):
                    continue  # Skip incomplete records

                # Buscar o crear 'Buque'
                nave = session.query(Buque).filter_by(nombre=row['Vessel'].strip().upper()).first()
                if not nave:
                    nave = Buque(nombre=row['Vessel'].strip(), compañia="Compañía Desconocida", ciudad="Ciudad Desconocida")
                    session.add(nave)
                    session.commit()

                # Fetch or create 'Tripulante'
                tripulante = session.query(Tripulante).filter_by(pasaporte=row['Passport number']).first()
                if tripulante:
                    tripulante = self._update_tripulante(tripulante, row, nave.buque_id, estado)
                else:
                    tripulante = self._create_tripulante(row, nave.buque_id, estado)
                    session.add(tripulante)

    def _update_tripulante(self, tripulante, row, buque_id, estado):
        tripulante.nombre = row['First name']
        tripulante.apellido = row['Last name']
        tripulante.sexo = row.get('Gender')
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
            pasaporte=row.get('Passport number'),
            fecha_nacimiento=pd.to_datetime(row.get('Date of birth')).date() if not pd.isna(row.get('Date of birth')) else None,
            buque_id=buque_id,
            estado=estado
        )
        print(f"Tripulante {tripulante.nombre} agregado")

        return tripulante

    def assign_flights_to_tripulantes(self):
        session = SessionLocal()
        try:
            # Assign 'ON' flights
            self._assign_flights(session, self.on_flights)
            # Assign 'OFF' flights
            self._assign_flights(session, self.off_flights)
            session.commit()
        except Exception as e:
            session.rollback()
            raise Exception(f"Error al asignar vuelos: {e}")
        finally:
            session.close()

    def _assign_flights(self, session, flights_df):
        if flights_df is not None:
            for _, row in flights_df.iterrows():
                tripulante = session.query(Tripulante).filter_by(pasaporte=row['Passport'].strip()).first()
                if tripulante:
                    print(f"Tripulante encontrado: {tripulante.nombre} {tripulante.apellido}")
                    vuelo = Vuelo(
                        codigo=row['Flight'],
                        aeropuerto_salida=row['Departure airport'],
                        hora_salida=pd.to_datetime(f"{row['Departure date']} {row['Departure time']}"),
                        aeropuerto_llegada=row['Arrival airport'],
                        hora_llegada=pd.to_datetime(f"{row['Arrival date']} {row['Arrival time']}"),
                        tripulante_id=tripulante.tripulante_id,
                    )
                    session.add(vuelo)
                    # Create ETA record
                    eta_ciudad = EtaCiudad(
                        tripulante_id=tripulante.tripulante_id,
                        ciudad=row['Arrival airport'],
                        eta=pd.to_datetime(f"{row['Arrival date']} {row['Arrival time']}")
                    )
                    print(f"ETA asignado: {eta_ciudad.eta} para {tripulante.nombre} en {eta_ciudad.ciudad}")
                    session.add(eta_ciudad)
                else:
                    print(f"No se encontró tripulante para el pasaporte: {row['Passport']}")

    def get_tripulantes_by_city(self, city):
        session = SessionLocal()
        try:
            tripulantes = session.query(Tripulante).join(Vuelo).filter(Vuelo.aeropuerto_llegada == city).all()
            return tripulantes
        except Exception as e:
            raise Exception(f"Error al obtener tripulantes por ciudad: {e}")
        finally:
            session.close()

    def load_existing_data(self):
        session = SessionLocal()
        try:
            # Load 'ON' tripulantes
            tripulantes_on = session.query(Tripulante).filter_by(estado='ON').all()
            df_on = pd.DataFrame([{
                'Vessel': trip.buque.nombre,
                'First name': trip.nombre,
                'Last name': trip.apellido,
                'Gender': trip.sexo,
                'Nationality': trip.nacionalidad,
                'Passport number': trip.pasaporte,
                'Date of birth': trip.fecha_nacimiento
            } for trip in tripulantes_on])

            # Load 'OFF' tripulantes
            tripulantes_off = session.query(Tripulante).filter_by(estado='OFF').all()
            df_off = pd.DataFrame([{
                'Vessel': trip.buque.nombre,
                'First name': trip.nombre,
                'Last name': trip.apellido,
                'Gender': trip.sexo,
                'Nationality': trip.nacionalidad,
                'Passport number': trip.pasaporte,
                'Date of birth': trip.fecha_nacimiento
            } for trip in tripulantes_off])

            return df_on, df_off
        except Exception as e:
            raise Exception(f"Error al cargar datos existentes: {e}")
        finally:
            session.close()
