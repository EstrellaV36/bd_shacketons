from datetime import datetime, timedelta
import re
import pandas as pd
from sqlalchemy.orm import Session
import traceback
from datetime import time
from sqlalchemy import func, and_
from PyQt6.QtWidgets import QMessageBox
from app.models import Buque, Tripulante, Vuelo, EtaCiudad, Viaje, TripulanteVuelo, Hotel, TripulanteHotel, Restaurante, TripulanteRestaurante, Transporte, TripulanteTransporte, TripulanteAsistencia

aerolineas_columns = ['Aerolinea 1', 'Aerolinea 2', 'Aerolinea 3', 'Aerolinea 4']

class Aerolineas:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def aerolineas_main(self, file_path):
        try:
            excel_data_on = pd.read_excel(file_path, sheet_name='ON', header=None)

            aerolineas_on = self.read_all_rows(excel_data_on, start_row=2, column_range=slice(17,21), column_names=aerolineas_columns)
            aerolineas_on.reset_index(drop=True, inplace=True)

            excel_data_off = pd.read_excel(file_path, sheet_name='OFF', header=None)

            aerolineas_off = self.read_all_rows(excel_data_off, start_row=2, column_range=slice(17,21), column_names=aerolineas_columns)
            aerolineas_off.reset_index(drop=True, inplace=True)

            return aerolineas_on, aerolineas_off
        except Exception as e:
            raise Exception(f"[Aerolineas] Error al procesar el archivo: {e}")
        
    def read_all_rows(self, data, start_row, column_range, column_names):
        # Leer todas las filas a partir de una fila específica, incluyendo filas con celdas vacías.
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
            if len(column_names) != result_df.shape[1]:
                raise ValueError(f"Length mismatch: Se esperaban {len(column_names)} columnas, pero se detectaron {result_df.shape[1]}")
            result_df.columns = column_names
        
        return result_df