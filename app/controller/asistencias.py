from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Tripulante, TripulanteAsistencia

asistencia_columns = ['Proveedor SCL', 'Asistencia 1', 'Proveedor PUQ', 'Asistencia 2', 'Proveedor WPU', 'Asistencia 3']

class Asistencias:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def asistencias_main(self, file_path):
        try:
            # Leer datos de ambas hojas: ON y OFF
            excel_data_on = pd.read_excel(file_path, sheet_name='ON', header=None)
            excel_data_off = pd.read_excel(file_path, sheet_name='OFF', header=None)

            # Extraer asistencias de cada hoja
            asistencias_on = self._extract_assist(excel_data_on, start_row=1, column_range=slice(42, 48), column_names=asistencia_columns)
            asistencias_off = self._extract_assist(excel_data_off, start_row=1, column_range=slice(30, 36), column_names=asistencia_columns)

            asistencias_on.reset_index(drop=True, inplace=True)
            asistencias_off.reset_index(drop=True, inplace=True)

            # Normalizar datos de asistencia
            asistencias_on = self._normalize_assistance_dataframe(asistencias_on)
            asistencias_off = self._normalize_assistance_dataframe(asistencias_off)

            print(f"ASISTENCIAS ON: {asistencias_on}")
            print(f"ASISTENCIAS OFF: {asistencias_off}")

            return asistencias_on, asistencias_off
        except Exception as e:
            raise Exception(f"[Asistencias] Error al procesar el archivo: {e}")

    def procesar_asistencias(self, tripulantes_on_df, asistencias_on_df, tripulantes_off_df, asistencias_off_df):
        try:
            print("Procesando asistencias para ON...")
            self._create_asistencias(tripulantes_on_df, asistencias_on_df)

            print("Procesando asistencias para OFF...")
            self._create_asistencias(tripulantes_off_df, asistencias_off_df)

            print("Procesamiento de asistencias completado para ambas hojas.")
        except Exception as e:
            print(f"Error al procesar asistencias: {e}")

    def _create_asistencias(self, tripulantes_df, asistencias_df):
        try:
            if tripulantes_df.empty or asistencias_df.empty:
                print("No hay datos de tripulantes o asistencias para procesar.")
                return

            for (i, tripulante_row), (_, asistencia_row) in zip(tripulantes_df.iterrows(), asistencias_df.iterrows()):
                try:
                    # Validar pasaporte
                    if pd.isna(tripulante_row['Pasaporte']) or not tripulante_row['Pasaporte']:
                        print(f"Pasaporte vacío o nulo en fila {i}. Registro omitido.")
                        continue

                    # Buscar tripulante
                    tripulante = self.db_session.query(Tripulante).filter_by(pasaporte=tripulante_row['Pasaporte']).first()
                    if not tripulante:
                        print(f"No se encontró tripulante con pasaporte {tripulante_row['Pasaporte']} en la fila {i}. Registro omitido.")
                        continue

                    # Extraer y comparar asistencias y proveedores
                    asistencias_lista = [x for x in [
                        asistencia_row['Asistencia 1'], asistencia_row['Asistencia 2'], asistencia_row['Asistencia 3']
                    ]]

                    proveedores_lista = [x for x in [
                        asistencia_row['Proveedor SCL'], asistencia_row['Proveedor PUQ'], asistencia_row['Proveedor WPU']
                    ]]

                    # Verificar si ya existe la asistencia
                    existing_asistencia = self.db_session.query(TripulanteAsistencia).filter_by(
                        tripulante_id=tripulante.tripulante_id
                    ).first()

                    if not existing_asistencia:
                        tripulante_asistencia = TripulanteAsistencia(
                            tripulante_id=tripulante.tripulante_id,
                            necesita_asistencia_scl='asistencia scl' in asistencias_lista,
                            necesita_asistencia_puq='asistencia puq' in asistencias_lista,
                            necesita_asistencia_wpu='asistencia wpu' in asistencias_lista,
                            proveedor_scl=proveedores_lista[0] if 'asistencia scl' in asistencias_lista else None,
                            proveedor_puq=proveedores_lista[1] if 'asistencia puq' in asistencias_lista else None,
                            proveedor_wpu=proveedores_lista[2] if 'asistencia wpu' in asistencias_lista else None
                        )
                        self.db_session.add(tripulante_asistencia)
                        print(f"Asistencia creada para tripulante ID {tripulante.tripulante_id}.")
                    else:
                        existing_asistencia.necesita_asistencia_scl = 'asistencia scl' in asistencias_lista
                        existing_asistencia.necesita_asistencia_puq = 'asistencia puq' in asistencias_lista
                        existing_asistencia.necesita_asistencia_wpu = 'asistencia wpu' in asistencias_lista
                        existing_asistencia.proveedor_scl = proveedores_lista[0] if 'asistencia scl' in asistencias_lista else None
                        existing_asistencia.proveedor_puq = proveedores_lista[1] if 'asistencia puq' in asistencias_lista else None
                        existing_asistencia.proveedor_wpu = proveedores_lista[2] if 'asistencia wpu' in asistencias_lista else None
                        print(f"Asistencia actualizada para tripulante ID {tripulante.tripulante_id}.")

                    self.db_session.commit()

                except Exception as row_error:
                    print(f"Error procesando asistencia en fila {i}: {row_error}")
                    self.db_session.rollback()

        except Exception as e:
            print(f"Error general al crear asistencias: {e}")
            self.db_session.rollback()

    def _extract_assist(self, data, start_row, column_range, column_names):
        try:
            data_block = []
            current_row = start_row

            while current_row < len(data):
                row_data = data.iloc[current_row, column_range]
                data_block.append(row_data)
                current_row += 1

            result_df = pd.DataFrame(data_block)

            if column_names:
                if len(column_names) != result_df.shape[1]:
                    raise ValueError(f"Length mismatch: Se esperaban {len(column_names)} columnas, pero se detectaron {result_df.shape[1]}")
                result_df.columns = column_names

            return result_df

        except Exception as e:
            raise Exception(f"Error al extraer asistencias: {e}")

    def _normalize_assistance_text(self, text):
        """Normaliza el texto de asistencia para manejar diferentes formatos."""
        if isinstance(text, str):
            words = sorted(text.lower().strip().split())
            return ' '.join(words)
        return text

    def _normalize_assistance_dataframe(self, df):
        """Normaliza las columnas relacionadas con las asistencias."""
        for col in ['Asistencia 1', 'Asistencia 2', 'Asistencia 3']:
            df[col] = df[col].apply(self._normalize_assistance_text)
        return df
