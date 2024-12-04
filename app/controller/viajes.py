from datetime import datetime, timedelta
import re
import pandas as pd
from sqlalchemy.orm import Session
import traceback
from datetime import time
from sqlalchemy import func, and_
from PyQt6.QtWidgets import QMessageBox
from app.models import Buque, Tripulante, Vuelo, EtaCiudad, Viaje, TripulanteVuelo, Hotel, TripulanteHotel, Restaurante, TripulanteRestaurante, Transporte, TripulanteTransporte, TripulanteAsistencia

class Viajes:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _create_viaje(self, tripulante_id, buque_id, estado, activo):
        try:
            # Buscar el registro EtaCiudad correspondiente
            eta_ciudad = self.db_session.query(EtaCiudad).filter_by(tripulante_id=tripulante_id, buque_id=buque_id).first()
            if not eta_ciudad:
                raise Exception(f"No se encontró EtaCiudad para tripulante ID {tripulante_id} y buque ID {buque_id}")

            # Crear el viaje asignando el tripulante y buque
            viaje = Viaje(
                tripulante_id=tripulante_id,
                buque_id=buque_id,
                eta_id=eta_ciudad.eta_id,  # Asignar el ID de EtaCiudad
                estado=estado,
                activo=activo
            )
            self.db_session.add(viaje)
            self.db_session.flush()  # Obtener el ID del viaje recién creado

            # Asignar los hoteles existentes al viaje
            tripulante_hoteles = self._get_hoteles_para_tripulante(tripulante_id, estado)
            if tripulante_hoteles:
                viaje.tripulante_hoteles.extend(tripulante_hoteles)
                #print(f"Hoteles asignados al viaje {viaje.viaje_id} para Tripulante ID {tripulante_id}")

            self.db_session.commit()    
            #print(f"Viaje creado para Tripulante: {tripulante_id} en Buque ID: {buque_id} eta_id: {eta_ciudad.eta_id}")
        except Exception as e:
            self.db_session.rollback()  # Revertir en caso de error
            #print(f"Error al crear viaje: {e}")

    def _create_viajes_from_dataframes(self, tripulantes_on, tripulantes_off, buques_on, buques_off):
        try:
            # Iterar sobre los DataFrames ON
            for index, row in buques_on.iterrows():
                # Buscar el buque en la base de datos por nombre y empresa
                buque = self.db_session.query(Buque).filter_by(nombre=row["Vessel"], empresa=row["Owner"]).first()
                if not buque:
                    #print(f"Error: No se encontró el buque con nombre '{row['Vessel']}' y empresa '{row['Owner']}'")
                    continue 

                # Buscar el tripulante en la base de datos por pasaporte
                pasaporte = tripulantes_on.loc[index, "Pasaporte"]
                tripulante = self.db_session.query(Tripulante).filter_by(pasaporte=pasaporte).first()
                if not tripulante:
                    #print(f"Error: No se encontró el tripulante con pasaporte '{pasaporte}'")
                    continue 

                # Verificar y asignar la columna 'Activo'
                activo_valor = buques_on.loc[index].get("Activo")
                if activo_valor is None:
                    #print(f"Advertencia: Columna 'Activo' faltante o vacía en fila {index}")
                    continue

                # Convertir el valor de 'Activo' a booleano
                activo = True if str(activo_valor).strip().upper() == "SI" else False

                self._create_viaje(tripulante_id=tripulante.tripulante_id, buque_id=buque.buque_id, estado="ON", activo=activo)

            # Iterar sobre los DataFrames OFF
            for index, row in buques_off.iterrows():
                # Buscar el buque en la base de datos por nombre y empresa
                buque = self.db_session.query(Buque).filter_by(nombre=row["Vessel"], empresa=row["Owner"]).first()
                if not buque:
                    #print(f"Error: No se encontró el buque con nombre '{row['Vessel']}' y empresa '{row['Owner']}'")
                    continue

                # Buscar el tripulante en la base de datos por pasaporte
                pasaporte = tripulantes_off.loc[index, "Pasaporte"]
                tripulante = self.db_session.query(Tripulante).filter_by(pasaporte=pasaporte).first()
                if not tripulante:
                    #print(f"Error: No se encontró el tripulante con pasaporte '{pasaporte}'")
                    continue

                # Verificar y asignar la columna 'Activo'
                activo_valor = buques_off.loc[index].get("Activo")
                if activo_valor is None:
                    #print(f"Advertencia: Columna 'Activo' faltante o vacía en fila {index}")
                    continue

                # Convertir el valor de 'Activo' a booleano
                activo = True if str(activo_valor).strip().upper() == "SI" else False

                self._create_viaje(tripulante_id=tripulante.tripulante_id, buque_id=buque.buque_id, estado="OFF", activo=activo)

            print("\nViajes creados exitosamente.")
        except Exception as e:
            print(f"Error al crear los viajes: {e}")

    def _get_hoteles_para_tripulante(self, tripulante_id, estado):
        """
        Obtiene los hoteles asociados a un tripulante según el estado (ON u OFF),
        utilizando el índice para determinar la correspondencia.
        """
        try:
            hoteles_df = self.hoteles_on if estado == "ON" else self.hoteles_off
            hoteles = []

            for i, row in hoteles_df.iterrows():
                # Usar el índice para obtener la relación
                tripulante = self.tripulantes_on.iloc[i] if estado == "ON" else self.tripulantes_off.iloc[i]

                # Buscar el hotel en la base de datos
                hotel = self.db_session.query(Hotel).filter_by(
                    nombre=row["nombre_hotel"],
                    ciudad=row["ciudad"]
                ).first()

                if hotel:
                    hoteles.append(hotel)
                    print(f"Hotel encontrado: {hotel.nombre} para el tripulante ID: {tripulante_id}")
                else:
                    print(f"Hotel no encontrado: {row['nombre_hotel']} en {row['ciudad']}")

            return hoteles
        except Exception as e:
            #print(f"Error al obtener hoteles para tripulante {tripulante_id}: {e}")
            return []