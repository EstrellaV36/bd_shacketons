from datetime import datetime, timedelta
import re
import pandas as pd
from sqlalchemy.orm import Session
import traceback
from datetime import time
from sqlalchemy import func, and_
from PyQt6.QtWidgets import QMessageBox
from app.models import Extra, Buque, Tripulante, Vuelo, EtaCiudad, Viaje, TripulanteVuelo, Hotel, TripulanteHotel, Restaurante, TripulanteRestaurante, Transporte, TripulanteTransporte, TripulanteAsistencia

class Extras:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        
    def _create_extra(self, file_path, tripulantes_df, state):
        extra_columns = ['Maleta perdida', 'Transporte', 'Atencion Medica', 'Fecha', 'Ciudad', 'Comentarios']
        excel_data = pd.read_excel(file_path, sheet_name=state, header=None)
        if state == "ON":
            extras = self.read_all_rows(excel_data, start_row=2, column_range=slice(101, 107), column_names=extra_columns)
        elif state == "OFF":
            extras = self.read_all_rows(excel_data, start_row=2, column_range=slice(89, 95), column_names=extra_columns)

        extras = extras.where(pd.notnull(extras), None)

        try:
            if extras.empty or tripulantes_df.empty:
                #print("No hay hoteles o tripulantes para procesar.")
                return

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

                    existing_tripulante_extra_viaje = self.db_session.query(Viaje).filter(
                        Viaje.tripulante_id == tripulante.tripulante_id,
                    ).first()

                    existing_tripulante_extra = self.db_session.query(Extra).filter(
                        Extra.extra_id == tripulante.tripulante_id,
                    ).first()

                    if existing_tripulante_extra_viaje:
                        if str(extras.loc[i]['Maleta perdida'].strip().lower()) == "si":
                            existing_tripulante_extra_viaje.equipaje_perdido = True
                            self.db_session.commit()
                        elif str(extras.loc[i]['Maleta perdida'].strip().lower()) == "no":
                            existing_tripulante_extra_viaje.equipaje_perdido = False
                            self.db_session.commit()

                        print(extras.loc[i]['Atencion Medica'].strip().lower())
                        if str(extras.loc[i]['Atencion Medica'].strip().lower()) == "si":
                            existing_tripulante_extra_viaje.asistencia_medica = True
                            self.db_session.commit()
                        elif str(extras.loc[i]['Atencion Medica'].strip().lower()) == "no":
                            existing_tripulante_extra_viaje.asistencia_medica = False
                            self.db_session.commit()
                    else:
                        #print("No existe su viaje")
                        pass

                    if existing_tripulante_extra:
                        existing_tripulante_extra.comments =extras.loc[i]['Comentarios']  # Actualizar el estado 'activo'
                        self.db_session.add(existing_tripulante_extra)
                    else:
                        extra = Extra(
                            tripulante_id=tripulante.tripulante_id,
                            comments=extras.loc[i]['Comentarios']
                        )
                        self.db_session.add(extra)
                        self.db_session.flush()

                    self.db_session.commit()
                except Exception as e:
                    #print(e)
                    self.db_session.rollback()  # Revertir cambios parciales en la fila actual
                    continue  # Continuar con la siguiente fila

            # Confirmar los cambios en la base de datos
            self.db_session.commit()
            print(f"Asignación de extras {state} completada.")

        except Exception as e:
            self.db_session.rollback()
            print(e)

        self.db_session.commit()
        return extras

    def read_all_rows(self, data, start_row, column_range, column_names):
        # Convertir column_range en una lista si es necesario
        if isinstance(column_range, slice):
            column_range = list(range(column_range.start or 0, column_range.stop or data.shape[1], column_range.step or 1))

        # Leer todas las filas a partir de una fila específica, incluyendo filas con celdas vacías.
        data_block = []
        current_row = start_row

        while current_row < len(data):
            # Leer una fila completa del DataFrame
            row_data = data.iloc[current_row, column_range]

            # Si la fila está completamente vacía, agregar None
            if row_data.isnull().all():
                row_data = [None] * len(column_range)
            else:
                row_data = row_data.tolist()  # Convertir a lista si no está vacía

            # Agregar los datos de la fila al bloque
            data_block.append(row_data)
            current_row += 1

        # Convertir el bloque de datos en un DataFrame
        result_df = pd.DataFrame(data_block)

        # Asignar nombres de columnas si se proporcionan
        if column_names:
            if len(column_names) != result_df.shape[1]:
                raise ValueError(f"Length mismatch: Se esperaban {len(column_names)} columnas, pero se detectaron {result_df.shape[1]}")
            result_df.columns = column_names

        return result_df