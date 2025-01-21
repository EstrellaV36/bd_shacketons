from datetime import datetime, timedelta
import re
import pandas as pd
from sqlalchemy.orm import Session
import traceback
from datetime import time
from sqlalchemy import func, and_
from PyQt6.QtWidgets import QMessageBox
from app.models import Buque, Tripulante, Vuelo, EtaCiudad, Viaje, TripulanteVuelo, Hotel, TripulanteHotel, Restaurante, TripulanteRestaurante, Transporte, TripulanteTransporte, TripulanteAsistencia

class Extras:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def extras_main(self, file_path):
        try:
            print("[Extras] Leyendo hoja 'ON'")
            excel_data_on = pd.read_excel(file_path, sheet_name='ON', header=None)

            extras_on = self._extract_extras(excel_data_on, start_row=0, state="on")
            extras_on.reset_index(drop=True, inplace=True)

            print("[Extras] Leyendo hoja 'OFF'")
            excel_data_off = pd.read_excel(file_path, sheet_name='OFF', header=None)

            extras_off = self._extract_extras(excel_data_off, start_row=0, state="off")
            extras_off.reset_index(drop=True, inplace=True)

            return extras_on, extras_off
        except Exception as e:
            print("[Extras] Error durante el procesamiento:", e)
            traceback.print_exc()
            raise Exception(f"[Extras] Error al procesar el archivo: {e}")

    def _create_extra(self, file_path, tripulantes_df, state):
        extra_columns = ['Maleta perdida', 'Transporte', 'Atencion Medica', 'Fecha', 'Ciudad']
        excel_data = pd.read_excel(file_path, sheet_name=state, header=None)
        if state == "ON":
            extras = self.read_all_rows(excel_data, start_row=1, column_range=slice(101, 106), column_names=extra_columns)
        elif state == "OFF":
            extras = self.read_all_rows(excel_data, start_row=1, column_range=slice(89, 94), column_names=extra_columns)

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

                    existing_tripulante_extra = self.db_session.query(Viaje).filter(
                        Viaje.tripulante_id == tripulante.tripulante_id,
                    ).first()

                    if existing_tripulante_extra:
                        if str(extras.loc[i]['Maleta perdida'].strip().lower()) == "si":
                            existing_tripulante_extra.equipaje_perdido = True
                            self.db_session.commit()
                        elif str(extras.loc[i]['Maleta perdida'].strip().lower()) == "no":
                            existing_tripulante_extra.equipaje_perdido = False
                            self.db_session.commit()

                        print(extras.loc[i]['Atencion Medica'].strip().lower())
                        if str(extras.loc[i]['Atencion Medica'].strip().lower()) == "si":
                            existing_tripulante_extra.asistencia_medica = True
                            self.db_session.commit()
                        elif str(extras.loc[i]['Atencion Medica'].strip().lower()) == "no":
                            existing_tripulante_extra.asistencia_medica = False
                            self.db_session.commit()
                        
                    else:
                        #print("No existe su viaje")
                        continue

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
    
    def _extract_extras(self, excel_data, start_row, state):
        extras = []

        # Convertir los nombres de las columnas a cadenas y quitar espacios
        try:
            extras_columns = excel_data.loc[start_row].dropna().str.lower().tolist()
            #print(f"[Extras Extract] Columnas detectadas ({state}): {extras_columns}")
        except Exception as e:
            #print(f"[Extras Extract] Error al leer nombres de columnas en ({state}): {e}")
            return pd.DataFrame()

        # Iterar sobre cada fila, comenzando desde la fila indicada
        for i in range(start_row + 1, excel_data.shape[0]):
            #print(f"[Extras Extract] Procesando fila {i} en estado {state}")
            try:
                maleta_perdida = "maleta perdida"
                transporte = "transporte"
                atencion_medica = "atencion medica"
                fecha = "fecha"
                ciudad = "ciudad"

                # Verificar si las columnas existen en el DataFrame
                if (maleta_perdida in extras_columns and
                    transporte in extras_columns and
                    atencion_medica in extras_columns and
                    fecha in extras_columns and
                    ciudad in extras_columns):

                    col_idx_maleta_perdida = extras_columns.index(maleta_perdida)
                    col_idx_transporte = extras_columns.index(transporte)
                    col_idx_atencion_medica = extras_columns.index(atencion_medica)
                    col_idx_fecha = extras_columns.index(fecha)
                    col_idx_ciudad = extras_columns.index(ciudad)

                    # Obtener los valores, asignando nulo si no hay información
                    maleta_perdida_idx = excel_data.iloc[i, col_idx_maleta_perdida] if pd.notna(excel_data.iloc[i, col_idx_maleta_perdida]) else None
                    transporte_idx = excel_data.iloc[i, col_idx_transporte] if pd.notna(excel_data.iloc[i, col_idx_transporte]) else None
                    atencion_medica_idx = excel_data.iloc[i, col_idx_atencion_medica] if pd.notna(excel_data.iloc[i, col_idx_atencion_medica]) else None
                    fecha_idx = excel_data.iloc[i, col_idx_fecha] if pd.notna(excel_data.iloc[i, col_idx_fecha]) else None
                    ciudad_idx = excel_data.iloc[i, col_idx_ciudad] if pd.notna(excel_data.iloc[i, col_idx_ciudad]) else None

                    # Agregar la información a la lista de extras
                    extras.append({
                        "Maleta Perdida": maleta_perdida_idx,
                        "Transporte": transporte_idx,
                        "Atencion medica": atencion_medica_idx,
                        "Fecha": fecha_idx,
                        "Ciudad": ciudad_idx
                    })
                    #print(f"[Extras Extract] Fila {i} procesada: {extras[-1]}")
                else:
                    #print(f"[Extras Extract] Columnas necesarias no encontradas en fila {i}. Saliendo del bucle.")
                    continue
            except Exception as e:
                print(f"[Extras Extract] Error al procesar fila {i}: {e}")
                continue

        # Verificar si se encontraron extras
        if len(extras) == 0:
            print(f"[Extras Extract] No se encontraron extras en las filas procesadas ({state}).")
        else:
            print(f"[Extras Extract] {len(extras)} extras procesados ({state}).")

        return pd.DataFrame(extras)