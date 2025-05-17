import pandas as pd
import calendar
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import Buque, Tripulante, Vuelo, EtaCiudad, Viaje
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter, column_index_from_string
from datetime import datetime

class Tripulantes:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def tripulantes_main(self, file_path):
        try:
            tripulante_columns = ['First name', 'Last name', 'Gender', 'Nacionalidad', 'Position', 'Pasaporte', 'DOB']

            excel_data_on = pd.read_excel(file_path, sheet_name='ON', header=None)

            tripulantes_on = self.read_all_rows(excel_data_on, start_row=2, column_range=slice(10, 17), column_names=tripulante_columns)  
            tripulantes_on.reset_index(drop=True, inplace=True)

            excel_data_off = pd.read_excel(file_path, sheet_name='OFF', header=None)

            tripulantes_off = self.read_all_rows(excel_data_off, start_row=2, column_range=slice(10, 17), column_names=tripulante_columns) 
            tripulantes_off.reset_index(drop=True, inplace=True)

            return tripulantes_on, tripulantes_off
        except Exception as e:
            #raise Exception(f"[Tripulantes] Error al procesar el archivo: {e}")
            pass

    def _create_tripulantes(self, file_path, tripulantes_df, buque_df, estado):
        tripulantes = []  # Lista para almacenar los tripulantes creados
        vuelos_tripulante = []  # Lista para almacenar los vuelos asociados a cada tripulante
        errors = []
        errors_message = []
        count_skiped = 0

        errors, errors_message = self.check_and_clean(tripulantes_df, file_path, estado)

        try:
            # Asegurarse de que ambos DataFrames tienen la misma longitud
            if len(tripulantes_df) != len(buque_df):
                raise ValueError("El número de tripulantes no coincide con el número de buques.")

            # Iterar simultáneamente sobre tripulantes_df y buque_df
            for (i, tripulante_row), (_, buque_row) in zip(tripulantes_df.iterrows(), buque_df.iterrows()):
                
                try:
                    tripulante_existente_pasaporte = self.db_session.query(Tripulante).filter(
                        Tripulante.pasaporte == tripulante_row['Pasaporte']
                    ).first()

                    if tripulante_existente_pasaporte:
                        continue

                    # Normalizar los nombres y apellidos para evitar problemas de mayúsculas/minúsculas
                    nombre_normalizado = tripulante_row['First name'].strip().title()
                    apellido_normalizado = tripulante_row['Last name'].strip().title()

                    # Verificar si ya existe un tripulante con el mismo nombre y apellido (independientemente de si tiene pasaporte o no)
                    tripulante_existente = self.db_session.query(Tripulante).filter(
                        Tripulante.nombre == nombre_normalizado,
                        Tripulante.apellido == apellido_normalizado
                    ).first()

                    # Si no existe el tripulante, lo creamos
                    if not tripulante_existente:
                        if pd.isna(tripulante_row['Gender']):
                            # print("[ERROR TRIPULANTE] Género faltante en...")
                            continue

                        tripulante = Tripulante(
                            nombre=nombre_normalizado,
                            apellido=apellido_normalizado,
                            sexo=str(tripulante_row['Gender']).strip(),
                            nacionalidad=tripulante_row['Nacionalidad'],
                            posicion=tripulante_row['Position'],
                            pasaporte=tripulante_row['Pasaporte'] if tripulante_row['Pasaporte'] else None,
                            condicion=buque_row['Condicion'],
                            fecha_nacimiento=pd.to_datetime(tripulante_row['DOB']).date() if not pd.isna(tripulante_row['DOB']) else None,
                            buque_id=self.buscar_buque_id(buque_row['Vessel'], buque_row['Owner'], self.db_session)
                        )
                        self.db_session.add(tripulante)
                        self.db_session.flush()  # Genera el tripulante_id sin hacer commit
                        tripulante_existente = tripulante  # Asignar a la variable existente
                    else:
                        # Si el tripulante ya existe, actualizamos los datos
                        tripulante_existente.sexo = tripulante_row['Gender']
                        tripulante_existente.nacionalidad = tripulante_row['Nacionalidad']
                        tripulante_existente.posicion = tripulante_row['Position']
                        tripulante_existente.condicion = buque_row['Condicion']
                        tripulante_existente.fecha_nacimiento = pd.to_datetime(tripulante_row['DOB']).date() if not pd.isna(tripulante_row['DOB']) else tripulante_existente.fecha_nacimiento
                        tripulante_existente.buque_id = self.buscar_buque_id(buque_row['Vessel'], buque_row['Owner'], self.db_session)

                        # Si el tripulante ya existe y no tiene pasaporte, lo actualizamos con el nuevo pasaporte (si está presente)
                        if tripulante_row['Pasaporte'] and not tripulante_existente.pasaporte:
                            tripulante_existente.pasaporte = tripulante_row['Pasaporte']

                    # Datos de ETA
                    eta_vessel = pd.to_datetime(buque_row['ETA Vessel'], errors='coerce', format="%Y-%m-%d %H:%M:%S")
                    etd_vessel = pd.to_datetime(buque_row['ETD Vessel'], errors='coerce', format="%Y-%m-%d %H:%M:%S")
                    if estado == 'ON':
                        date_arrive_cl = pd.to_datetime(buque_row['Date arrive CL'], errors='coerce', format="%Y-%m-%d %H:%M:%S")
                        
                        # Si la fecha es NaT o None, saltar esta fila
                        if pd.isna(date_arrive_cl):
                            date_arrive_cl = None
                            pass
                    else:
                        date_arrive_cl = None

                    # Normalización de otros campos, como el puerto
                    puerto_name = self.normalize_text(buque_row['Puerto'])

                    eta = EtaCiudad(
                        tripulante_id=tripulante_existente.tripulante_id,
                        buque_id=tripulante_existente.buque_id,
                        puerto=puerto_name,
                        eta=eta_vessel,
                        etd=etd_vessel,
                        date_arrive_cl=(
                            date_arrive_cl if estado == 'ON' and not pd.isna(buque_row['Date arrive CL']) else None
                        ),
                        date_first_flight=(
                            pd.to_datetime(buque_row['Date First flight'], errors='coerce', format="%Y-%m-%d %H:%M:%S")
                            if estado == 'OFF' and not pd.isna(buque_row['Date First flight']) else None
                        )
                    )
                    self.db_session.add(eta)

                    # Confirmar los cambios en la base de datos
                    self.db_session.commit()  # Confirmar el tripulante y la ETA
                    tripulantes.append(tripulante_existente)

                except Exception as row_error:
                    #print(f"[Tripulante] Error procesando fila {i}: {row_error}")
                    # Imprimir el tripulante y el buque relacionados con la fila actual
                    #print(f"Datos del tripulante en fila {i}: {tripulantes_df.iloc[i].to_dict()}")
                    #print(f"Datos del buque en fila {i}: {buque_df.iloc[i].to_dict()}")
                    self.db_session.rollback()  # Revertir cambios en caso de error en la fila
                    continue  # Continuar con la siguiente fila

            print(f"Total de tripulantes creados: {len(tripulantes)}")
            return errors, errors_message

        except Exception as e:
            print(f"Error general al crear tripulantes o encontrar vuelos: {e}")
            self.db_session.rollback()  # Revertir la sesión en caso de error crítico
            return [], []  # Devolver listas vacías en caso de error

    def normalize_text(self, text):
        if isinstance(text, str):
            return text.strip().title()  # Convierte la primera letra en mayúsculas y el resto en minúsculas
        return text  # Si no es una cadena, devuelve el valor original

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
    
    def buscar_buque_id(self, nombre_buque, nombre_empresa, session):
        nombre_buque = nombre_buque.strip()
        buque = session.query(Buque).filter(
            and_(
                Buque.nombre.ilike(nombre_buque),
                Buque.empresa.ilike(nombre_empresa)
            )
        ).first()
        if buque:
            #print(f"Buque encontrado: {nombre_buque} con ID: {buque.buque_id}")
            return buque.buque_id
        else:
            raise ValueError(f"Buque {nombre_buque} no encontrado en la base de datos.")
        
    def buscar_vuelo_id(self, codigo_vuelo, session):
        # Asegúrate de que el campo 'nombre' es el correcto
        vuelo = session.query(Vuelo).filter(Vuelo.codigo.ilike(codigo_vuelo)).first()  # Usando ilike para coincidencias sin distinción entre mayúsculas y minúsculas

        if vuelo:
            #print(f"Vuelo encontrado con el codigo: {vuelo.codigo}")
            return vuelo.codigo
        else:
            raise ValueError(f"Vuelo {vuelo.codigo} no encontrado en la base de datos.")
        
    def check_and_clean(self, tripulantes_df, file_path, state):
        file_path = file_path
        state = state

        errors = []
        errors_message = []

        def clean_value(value):
            if isinstance(value, str):  # Verificar si es una cadena
                return value.strip().replace('/', '-')  # Eliminar espacios en blanco
            return value  # Dejar el valor tal como está si no es cadena

        def is_valid_date(date_str):
            if pd.isna(date_str):
                return False

            # Caso 1: Ya es datetime
            if isinstance(date_str, (pd.Timestamp, datetime)):
                return True

            # Caso 2: Viene como número (formato de fecha de Excel en número de días)
            if isinstance(date_str, (int, float)):
                try:
                    date = pd.to_datetime('1899-12-30') + pd.to_timedelta(float(date_str), unit='D')
                    return True
                except Exception:
                    return False

            # Caso 3: Es un string, intentar con varios formatos
            try:
                pd.to_datetime(date_str, errors='raise', dayfirst=True)
                return True
            except Exception:
                pass  # Si falla, seguimos probando formatos específicos

            # Intentar con formatos definidos manualmente
            formats = ['%d-%m-%y', '%d-%m-%Y', '%d %b %Y']
            for date_format in formats:
                try:
                    pd.to_datetime(date_str, format=date_format, errors='raise')
                    return True
                except Exception:
                    continue

            return False

        def validate_dates(tripulantes_df, column_name, file_path, state):
            # Carga única del archivo y la hoja
            workbook = load_workbook(file_path, data_only=True)
            sheet = workbook[state]

            # Mapeo de nombre de columna a letra de Excel (solo una vez)
            column_map = {col[0].value: get_column_letter(col[0].column) for col in sheet.iter_cols(1, sheet.max_column, 1, 1)}

            y = column_map.get(column_name, '?')
            column_number = column_index_from_string(y) if y != '?' else None
            cell_value = sheet.cell(row=1, column=column_number).value if column_number else '?'

            for i, value in tripulantes_df[column_name].items():
                if not is_valid_date(value):
                    error = tripulantes_df.loc[i, column_name]
                    x = i + 2  # Ajuste de índice

                    if isinstance(value, str) and '-' in value and len(value.split('-')) == 3:
                        print(f"Error [Tripulante]: Fecha inexistente en la fila {x}, columna '{column_name} ({y})'. Valor: '{error}'")
                        errors.append([i + 3, y])
                        errors_message.append(f"Fecha inexistente en {cell_value} [{x},{y}]")
                    elif not pd.isna(value):
                        print(f"Error [Tripulante]: Formato de fecha incorrecto en la fila {x}, columna '{y}'. Valor: '{error}'")
                        errors.append([i + 3, y])
                        errors_message.append(f"Formato de fecha incorrecto en {cell_value} [{x},{y}]")


        def validate_genders(tripulantes_df, column_name, file_path, state):
            # Carga única del archivo y hoja
            workbook = load_workbook(file_path, data_only=True)
            sheet = workbook[state]

            # Obtener el mapeo de nombres de columna a letras de Excel solo una vez
            column_map = {col[0].value: get_column_letter(col[0].column) for col in sheet.iter_cols(1, sheet.max_column, 1, 1)}

            y = column_map.get(column_name, None)
            if y:
                column_number = column_index_from_string(y)
                cell_value = sheet.cell(row=1, column=column_number).value
            else:
                y = '?'
                cell_value = '?'

            for i, value in tripulantes_df[column_name].items():
                gender_value = str(value).strip() if not pd.isna(value) else ''
                if gender_value not in ['F', 'M']:
                    print(f"[ERROR TRIPULANTES] Género no existente: {value}")
                    x = i + 3  # Ajustar índice a la fila de Excel (asumiendo empieza en 1)
                    print(f"Error [Tripulante]: Género inexistente en la fila {x}, columna '{column_name} ({y})'. Valor: '{value}'")
                    errors.append([i+3, y])
                    errors_message.append(f"Género inexistente en {cell_value} [{x},{y}]")

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
        
        def get_cell_value(file_path, sheet_name, row, column):
            # Cargar el archivo de Excel
            workbook = load_workbook(file_path, data_only=True)  # `data_only=True` para obtener el valor calculado en celdas con fórmulas
            sheet = workbook[sheet_name]

            # Obtener el valor de la celda
            cell_value = sheet.cell(row=row, column=column).value

            return cell_value

        tripulantes_df["DOB"] = tripulantes_df["DOB"].apply(clean_value)

        # Validar y notificar errores antes de convertir las fechas
        validate_dates(tripulantes_df, "DOB", file_path, state)

        # Conversión final de DOB permitiendo distintos formatos de fecha
        tripulantes_df["DOB"] = pd.to_datetime(
            tripulantes_df["DOB"], 
            errors='coerce', 
            dayfirst=True
        )

        # Validar géneros después de las fechas
        validate_genders(tripulantes_df, "Gender", file_path, state)

        return errors, errors_message