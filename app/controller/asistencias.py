from datetime import datetime, timedelta
import re
import pandas as pd
from sqlalchemy.orm import Session
import traceback
from datetime import time
from sqlalchemy import func, and_
from PyQt6.QtWidgets import QMessageBox
from app.models import Buque, Tripulante, Vuelo, EtaCiudad, Viaje, TripulanteVuelo, Hotel, TripulanteHotel, Restaurante, TripulanteRestaurante, Transporte, TripulanteTransporte, TripulanteAsistencia

asistencia_columns = ['Proveedor SCL', 'Asistencia 1', 'Proveedor PUQ', 'Asistencia 2', 'Proveedor WPU', 'Asistencia 3']

class Asistencias:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def asistencias_main(self, file_path):
        try:
            excel_data_on = pd.read_excel(file_path, sheet_name='ON', header=None)

            asistencias_on = self._extract_assist(excel_data_on, start_row=1, column_range=slice(42,48), column_names=asistencia_columns)
            asistencias_on.reset_index(drop=True, inplace=True)  # Reiniciar el índice

            return asistencias_on
        except Exception as e:
            raise Exception(f"[Asistencias] Error al procesar el archivo: {e}")

    def _create_asistencias(self, tripulantes_df, asistencias_df):
        try:
            # Verificar que ambos DataFrames no estén vacíos
            if tripulantes_df.empty or asistencias_df.empty:
                print("No hay datos de tripulantes o asistencias para procesar.")
                return

            # Iterar simultáneamente sobre tripulantes_df y asistencias_df
            for (i, tripulante_row), (_, asistencia_row) in zip(tripulantes_df.iterrows(), asistencias_df.iterrows()):
                try:
                    # Validar que el pasaporte no sea nulo
                    if pd.isna(tripulante_row['Pasaporte']) or not tripulante_row['Pasaporte']:
                        #print(f"Pasaporte vacío o nulo en fila {i}. Registro omitido: {tripulante_row.to_dict()}")
                        continue

                    # Buscar el tripulante en la base de datos
                    tripulante = self.db_session.query(Tripulante).filter_by(pasaporte=tripulante_row['Pasaporte']).first()
                    if not tripulante:
                        print(f"No se encontró tripulante con pasaporte {tripulante_row['Pasaporte']} en la fila {i}. Registro omitido.")
                        continue

                    # Extraer los valores de asistencia y proveedores
                    asistencias_lista = [
                        asistencia_row.get('Asistencia 1'),
                        asistencia_row.get('Asistencia 2'),
                        asistencia_row.get('Asistencia 3')
                    ]
                    proveedores_lista = [
                        asistencia_row.get('Proveedor SCL'),
                        asistencia_row.get('Proveedor PUQ'),
                        asistencia_row.get('Proveedor WPU')
                    ]

                    # Verificar si ya existe una entrada de TripulanteAsistencia
                    existing_asistencia = self.db_session.query(TripulanteAsistencia).filter_by(
                        tripulante_id=tripulante.tripulante_id
                    ).first()

                    if not existing_asistencia:
                        #print(f"Creando asistencias para tripulante ID {tripulante.tripulante_id}.")
                        tripulante_asistencia = TripulanteAsistencia(
                            tripulante_id=tripulante.tripulante_id,
                            necesita_asistencia_scl='Asistencia SCL' in asistencias_lista,
                            necesita_asistencia_puq='Asistencia PUQ' in asistencias_lista,
                            necesita_asistencia_wpu='Asistencia WPU' in asistencias_lista,
                            proveedor_scl=proveedores_lista[0] if 'Asistencia SCL' in asistencias_lista else None,
                            proveedor_puq=proveedores_lista[1] if 'Asistencia PUQ' in asistencias_lista else None,
                            proveedor_wpu=proveedores_lista[2] if 'Asistencia WPU' in asistencias_lista else None
                        )
                        self.db_session.add(tripulante_asistencia)
                    else:
                        #print(f"Asistencias ya existen para tripulante ID {tripulante.tripulante_id}. Omitiendo...")
                        continue
                    # Confirmar los cambios para esta fila
                    self.db_session.commit()

                except Exception as row_error:
                    print(f"[Asistencias] Error procesando asistencia en fila {i}: {row_error}")
                    print(f"Datos del tripulante en fila {i}: {tripulante_row.to_dict()}")
                    print(f"Datos de asistencia en fila {i}: {asistencia_row.to_dict()}")
                    self.db_session.rollback()  # Revertir cambios en caso de error en la fila
                    continue  # Continuar con la siguiente fila

            print("Procesamiento de asistencias completado.")
        except Exception as e:
            print(f"Error general al crear asistencias: {e}")
            ###traceback.print_exc()
            self.db_session.rollback()  # Revertir la sesión en caso de error crítico

    def _extract_assist(self, data, start_row, column_range, column_names):
        # Leer todas las filas desde una fila específica hasta que no haya más datos,
        # incluso si las filas tienen valores nulos.
        
        data_block = []
        current_row = start_row

        while current_row < len(data):
            # Leer una fila completa del DataFrame, sin detenerse por nulos
            row_data = data.iloc[current_row, column_range]

            # Agregar los datos de la fila al bloque, incluso si hay nulos
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