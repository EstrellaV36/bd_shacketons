import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models import Buque
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

class Buques:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def buques_main(self, file_path):
        try:
            buques_on_columns = ['Activo', 'Owner', 'Vessel', 'Date arrive CL', 'ETA Vessel', 'ETD Vessel', 'Puerto a embarcar', 'Condicion']
            buques_off_columns = ['Activo', 'Owner', 'Vessel', 'Date First flight', 'ETA Vessel', 'ETD Vessel', 'Puerto a desembarcar', 'Condicion']

            excel_data_on = pd.read_excel(file_path, sheet_name='ON', header=None)

            buques_on = self.read_all_rows(excel_data_on, start_row=1, column_range=slice(0, 8), column_names=buques_on_columns) 
            buques_on.reset_index(drop=True, inplace=True)

            self.check_and_clean(buques_on, file_path, "ON")

            excel_data_off = pd.read_excel(file_path, sheet_name='OFF', header=None)

            buques_off = self.read_all_rows(excel_data_off, start_row=1, column_range=slice(0, 8), column_names=buques_off_columns)
            buques_off.reset_index(drop=True, inplace=True)

            self.check_and_clean(buques_off, file_path, "OFF")

            return buques_on, buques_off
        except Exception as e:
            raise Exception(f"[Buques] Error al procesar el archivo: {e}")
    
    def _create_buque(self, buques_df):
        try:
            if 'Puerto a embarcar' in buques_df.columns:
                buques_df.rename(columns={'Puerto a embarcar': 'Puerto'}, inplace=True)

            if 'Puerto a desembarcar' in buques_df.columns:
                buques_df.rename(columns={'Puerto a desembarcar': 'Puerto'}, inplace=True)

            for _, row in buques_df.iterrows():
                # Normalizar el nombre del buque
                vessel_name = row['Vessel'].strip().lower()
                empresa_name = row['Owner'].strip().lower()

                # Verificar si el buque ya existe
                buque_existente = self.db_session.query(Buque).filter(and_(func.lower(Buque.nombre) == vessel_name),
                                                                      func.lower(Buque.empresa) == empresa_name).first()

                if not buque_existente:
                    nuevo_buque = Buque(
                        nombre=row['Vessel'].strip(),
                        empresa=row['Owner'] if pd.notna(row['Owner']) else "Empresa Desconocida",
                        ciudad=row['Puerto'] if pd.notna(row['Puerto']) else "Ciudad Desconocida"
                    )
                    self.db_session.add(nuevo_buque)
                    self.db_session.flush()  # Generar el ID del nuevo buque
                
                # Confirmar todos los cambios al final
                self.db_session.commit()

        except Exception as e:
            self.db_session.rollback()  # Revertir cambios en caso de error
            raise Exception(f"Error al crear o actualizar buques: {e}")

        return "Proceso completado exitosamente"

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
    
    def check_and_clean(self, buques_df, file_path, state):
        # Aplicar a toda la columna y limpiar valores tipo str
        file_path = file_path
        state = state
        def clean_value(value):
            if isinstance(value, str):  # Verificar si es una cadena
                print(f"Limpiando valor: {value}")
                print(f"Resultado valor: {value.strip()}")
                return value.strip()  # Eliminar espacios en blanco
            return value  # Dejar el valor tal como está si no es cadena
        
        def validate_dates(buques_df, column_name, file_path, state):
            for i, value in buques_df[column_name].items():
                if pd.isna(value):  # Verificar si el valor es NaT (equivalente a NaN para fechas)
                    sheet_name = state
                    column_name = column_name

                    x = i + 2
                    y = get_excel_column_letter(file_path, sheet_name, column_name)
                    print(f"Error: Fecha inválida en la fila {x}, columna '{y}'. Valor: {value}")

        def get_excel_column_letter(file_path, sheet_name, column_name):
            # Cargar el archivo y la hoja
            workbook = load_workbook(file_path)
            sheet = workbook[sheet_name]
            
            # Buscar la columna por nombre (suponiendo que los nombres están en la primera fila)
            for col in sheet.iter_cols(1, sheet.max_column, 1, 1):  # Iterar solo en la primera fila
                if col[0].value == column_name:
                    # Devolver la letra de la columna
                    return get_column_letter(col[0].column)
            
            raise ValueError(f"Columna con nombre '{column_name}' no encontrada en el archivo.")

        buques_df["ETA Vessel"] = buques_df["ETA Vessel"].apply(clean_value)
        buques_df["ETD Vessel"] = buques_df["ETD Vessel"].apply(clean_value)

        buques_df['ETA Vessel'] = pd.to_datetime(buques_df['ETA Vessel'], format='%d/%m/%y', errors='coerce')
        buques_df['ETD Vessel'] = pd.to_datetime(buques_df['ETD Vessel'], format='%d/%m/%y', errors='coerce')
        
        validate_dates(buques_df, "ETA Vessel", file_path, state)
        validate_dates(buques_df, "ETD Vessel", file_path, state)

    
