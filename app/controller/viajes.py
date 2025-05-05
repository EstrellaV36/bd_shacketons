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

            # Verificar si ya existe un viaje con los mismos parámetros (tripulante_id, buque_id, eta_fecha, estado)
            viaje_existente = self.db_session.query(Viaje).filter_by(
                tripulante_id=tripulante_id,
                buque_id=buque_id,
                eta_id=eta_ciudad.eta_id,
                estado=estado
            ).first()

            if viaje_existente:
                # Si el viaje ya existe, actualizar el campo 'activo' si es diferente
                if viaje_existente.activo != activo:
                    # print(f"El viaje ya existe. Actualizando el campo 'activo' de {viaje_existente.viaje_id} a {activo}")
                    viaje_existente.activo = activo  # Actualizar el estado 'activo'
                    self.db_session.add(viaje_existente)  # Asegurarse de que se guarde el cambio
                    self.db_session.commit()

                else:
                    #print(f"El viaje para Tripulante ID {tripulante_id}, Buque ID {buque_id}, Estado {estado} ya existe y está activo como {activo}.")
                    pass
                return viaje_existente  # Retornamos el viaje existente (sin crear uno nuevo)

            # Si no existe, crear el nuevo viaje
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
            tripulante_hoteles = self._get_hoteles_para_tripulante(tripulante_id, viaje.viaje_id)
            if tripulante_hoteles:
                viaje.tripulante_hoteles.extend(tripulante_hoteles)
                # Imprimir los hoteles asignados al viaje
                print(f"Hoteles asignados al viaje {viaje.viaje_id} para Tripulante ID {tripulante_id}:")
                for hotel in tripulante_hoteles:
                    print(f"- Hotel: {hotel.hotel.nombre}, Fecha Entrada: {hotel.fecha_entrada}, Fecha Salida: {hotel.fecha_salida}")
            else:
                print("Tripulante_hotel no existente")

            # Guardar el viaje y los hoteles
            self.db_session.commit()
            #print(f"Viaje creado para Tripulante ID {tripulante_id} en Buque ID {buque_id} con Estado {estado}")
            return viaje  # Retornar el viaje recién creado

        except Exception as e:
            self.db_session.rollback()  # Revertir en caso de error
            print(f"Error al crear o actualizar viaje: {e}")
            return None

    def _create_viajes_from_dataframes(self, tripulantes_on, tripulantes_off, buques_on, buques_off):
        try:
            # Iterar sobre los DataFrames ON

            for index, row in buques_on.iterrows():
                # Buscar el buque en la base de datos por nombre y empresa
                buque = self.db_session.query(Buque).filter_by(nombre=(row["Vessel"]).strip(), empresa=row["Owner"]).first()
                if not buque:
                    print(f"Error: No se encontró el buque con nombre '{row['Vessel']}' y empresa '{row['Owner']}'")
                    continue 

                # Buscar el tripulante en la base de datos por pasaporte o, si es nulo, por nombre y apellido
                pasaporte = tripulantes_on.loc[index, "Pasaporte"]

                if pd.isna(pasaporte):
                    pasaporte = None

                if pasaporte:
                    # Si el pasaporte está presente, buscar por pasaporte
                    tripulante = self.db_session.query(Tripulante).filter_by(pasaporte=pasaporte).first()
                else:
                    # Si el pasaporte es nulo, buscar por nombre y apellido
                    #print(f"Buscando {tripulantes_on.loc[index, "First name"]} {tripulantes_on.loc[index, "Last name"]}")
                    nombre = tripulantes_on.loc[index, "First name"]
                    apellido = tripulantes_on.loc[index, "Last name"]
                    # print(f"Encontrado: {nombre} {apellido}")

                    tripulante = self.db_session.query(Tripulante).filter_by(nombre=nombre, apellido=apellido).first()

                if not tripulante:
                    # Si no se encontró el tripulante por ninguno de los dos métodos
                    #print(f"Error: No se encontró el tripulante con Pasaporte '{pasaporte}' o Nombre '{nombre}' y Apellido '{apellido}'")
                    continue

                # Verificar y asignar la columna 'Activo'
                activo_valor = buques_on.loc[index].get("Activo")
                if pd.isna(activo_valor):
                    print(f"[ERROR] Columna 'Activo' faltante o vacía en fila {index}")
                    continue
                else:
                    activo_valor = activo_valor.upper()

                # print(f"El valor de activo es: [{index}] | {activo_valor}")

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
                # print(f"El valor de activo es: [{index}]{activo_valor}")
                if activo_valor is None:
                    #print(f"Advertencia: Columna 'Activo' faltante o vacía en fila {index}")
                    continue

                # Convertir el valor de 'Activo' a booleano
                activo = True if str(activo_valor).strip().upper() == "SI" else False

                self._create_viaje(tripulante_id=tripulante.tripulante_id, buque_id=buque.buque_id, estado="OFF", activo=activo)

            print("\nViajes creados exitosamente.")
        except Exception as e:
            print(f"Error al crear los viajes: {e}")

    def _get_hoteles_para_tripulante(self, tripulante_id, viaje_id):
        """
        Obtiene las reservas de hotel asociadas a un tripulante y las asigna a un viaje.
        Filtra las reservas activas según la fecha de entrada y salida.
        """
        try:
            # Recuperar todas las reservas de hotel para el tripulante
            tripulante_hoteles = self.db_session.query(TripulanteHotel).filter_by(
                tripulante_id=tripulante_id
            ).all()

            print(f"Hoteles recuperados para Tripulante ID {tripulante_id}: {len(tripulante_hoteles)} reservas activas encontradas.")

            # Asignar las reservas de hotel al viaje
            for hotel in tripulante_hoteles:
                # Verificamos si el viaje_id es válido
                if viaje_id:
                    hotel.viaje_id = viaje_id  # Asignar el viaje a la reserva de hotel
                    self.db_session.add(hotel)  # Asegurarnos de guardar cualquier cambio

            # Commit para guardar los cambios realizados
            self.db_session.commit()

            return tripulante_hoteles

        except Exception as e:
            print(f"Error al obtener y asignar hoteles para tripulante {tripulante_id}: {e}")
            self.db_session.rollback()  # Revertir cualquier cambio en caso de error
            return []