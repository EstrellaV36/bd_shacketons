from datetime import datetime, timedelta
import re
import pandas as pd
from sqlalchemy.orm import Session
import traceback
from datetime import time
from sqlalchemy import func, and_
from PyQt6.QtWidgets import QMessageBox
from app.models import Buque, Tripulante, Vuelo, EtaCiudad, Viaje, TripulanteVuelo, Hotel, TripulanteHotel, Restaurante, TripulanteRestaurante, Transporte, TripulanteTransporte, TripulanteAsistencia


class Aerolineas:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def aerolineas_main(self, file_path):
        try:
            aerolineas_columns = ['Aerolinea 1', 'Aerolinea 2', 'Aerolinea 3', 'Aerolinea 4']

            excel_data_on = pd.read_excel(file_path, sheet_name='ON', header=0)

            aerolineas_on = self.read_all_rows(excel_data_on, start_row=2, column_range=slice(17,21), column_names=aerolineas_columns)
            aerolineas_on.reset_index(drop=True, inplace=True)

            excel_data_off = pd.read_excel(file_path, sheet_name='OFF', header=0)

            aerolineas_off = self.read_all_rows(excel_data_off, start_row=2, column_range=slice(17,21), column_names=aerolineas_columns)
            aerolineas_off.reset_index(drop=True, inplace=True)

            return aerolineas_on, aerolineas_off
        except Exception as e:
            raise Exception(f"[Aerolineas] Error al procesar el archivo: {e}")
        
    def read_all_rows(self, data, start_row, column_range, column_names):
        data_block = []
        current_row = start_row

        while current_row < len(data):
            row_data = data.iloc[current_row, column_range]

            # Si la fila no está completamente vacía, la agregamos
            if not row_data.isnull().all():
                data_block.append(row_data)

            current_row += 1

        # Si no se encontraron datos, devolver DataFrame vacío con las columnas esperadas
        if not data_block:
            return pd.DataFrame(columns=column_names)

        # Crear el DataFrame resultante
        result_df = pd.DataFrame(data_block)

        # Asignar nombres de columnas si corresponde
        if column_names:
            if len(column_names) != result_df.shape[1]:
                raise ValueError(
                    f"Length mismatch: Se esperaban {len(column_names)} columnas, pero se detectaron {result_df.shape[1]}"
                )
            result_df.columns = column_names

        return result_df