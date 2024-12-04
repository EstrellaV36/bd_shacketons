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
            excel_data_on = pd.read_excel(file_path, sheet_name='ON', header=None)

            extras_on = self._extract_extras(excel_data_on, start_row=0, state="on")
            extras_on.reset_index(drop=True, inplace=True)

            excel_data_off = pd.read_excel(file_path, sheet_name='OFF', header=None)

            extras_off = self._extract_extras(excel_data_off, start_row=0, state="off")
            extras_off.reset_index(drop=True, inplace=True)

            return extras_on, extras_off
        except Exception as e:
            raise Exception(f"[Extras] Error al procesar el archivo: {e}")

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
        # if len(extras) == 0:
        #     print("No se encontraron extras en las filas procesadas.")
        #else:
            #print(f"{len(extras)} extras procesados. ({state})")
            
        return pd.DataFrame(extras)
