import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import Buque, Tripulante, Vuelo, EtaCiudad, Viaje
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

class Tripulantes:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def tripulantes_main(self, file_path):
        try:
            tripulante_columns = ['First name', 'Last name', 'Gender', 'Nacionalidad', 'Position', 'Pasaporte', 'DOB']

            excel_data_on = pd.read_excel(file_path, sheet_name='ON', header=None)

            tripulantes_on = self.read_all_rows(excel_data_on, start_row=1, column_range=slice(10, 17), column_names=tripulante_columns)  
            tripulantes_on.reset_index(drop=True, inplace=True)

            self.check_and_clean(tripulantes_on, file_path, "ON")

            excel_data_off = pd.read_excel(file_path, sheet_name='OFF', header=None)

            tripulantes_off = self.read_all_rows(excel_data_off, start_row=1, column_range=slice(10, 17), column_names=tripulante_columns) 
            tripulantes_off.reset_index(drop=True, inplace=True)

            self.check_and_clean(tripulantes_off, file_path, "OFF")

            return tripulantes_on, tripulantes_off
        except Exception as e:
            raise Exception(f"[Tripulantes] Error al procesar el archivo: {e}")

    def _create_tripulantes(self, tripulantes_df, buque_df, estado):
        tripulantes = []  # Lista para almacenar los tripulantes creados
        vuelos_tripulante = []  # Lista para almacenar los vuelos asociados a cada tripulante

        try:
            # Asegurarse de que ambos DataFrames tienen la misma longitud
            if len(tripulantes_df) != len(buque_df):
                raise ValueError("El número de tripulantes no coincide con el número de buques.")

            # Iterar simultáneamente sobre tripulantes_df y buque_df
            for (i, tripulante_row), (_, buque_row) in zip(tripulantes_df.iterrows(), buque_df.iterrows()):
                try:
                    # Normalizar los nombres y apellidos para evitar problemas de mayúsculas/minúsculas
                    nombre_normalizado = tripulante_row['First name'].strip().title()
                    apellido_normalizado = tripulante_row['Last name'].strip().title()

                    # Validación de datos importantes
                    if pd.isna(tripulante_row['Pasaporte']) or not tripulante_row['Pasaporte']:
                        # Si el pasaporte está vacío, verificar por nombre, apellido e ID
                        print(f"Pasaporte vacío en fila {i}. Verificando por nombre, apellido e ID.")
                        
                        # Realizamos la búsqueda normalizada
                        tripulante_existente = self.db_session.query(Tripulante).filter(
                            Tripulante.nombre == nombre_normalizado,
                            Tripulante.apellido == apellido_normalizado,
                        ).first()
                    else:
                        # Buscar si el tripulante ya existe por pasaporte
                        tripulante_existente = self.db_session.query(Tripulante).filter_by(pasaporte=tripulante_row['Pasaporte']).first()

                    # Si no se encuentra el tripulante, lo creamos
                    if not tripulante_existente:
                        tripulante = Tripulante(
                            nombre=nombre_normalizado,  # Usamos el nombre normalizado
                            apellido=apellido_normalizado,  # Usamos el apellido normalizado
                            sexo=tripulante_row['Gender'],
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

                    # Datos de ETA
                    eta_vessel = pd.to_datetime(buque_row['ETA Vessel'], errors='coerce', format="%Y-%m-%d %H:%M:%S")
                    etd_vessel = pd.to_datetime(buque_row['ETD Vessel'], errors='coerce', format="%Y-%m-%d %H:%M:%S")
                    date_arrive_cl = pd.to_datetime(buque_row['Date arrive CL'], errors='coerce', format="%Y-%m-%d %H:%M:%S") if estado == 'ON' else None

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
                    print(f"[Tripulante] Error procesando fila {i}: {row_error}")
                    # Imprimir el tripulante y el buque relacionados con la fila actual
                    print(f"Datos del tripulante en fila {i}: {tripulantes_df.iloc[i].to_dict()}")
                    print(f"Datos del buque en fila {i}: {buque_df.iloc[i].to_dict()}")
                    self.db_session.rollback()  # Revertir cambios en caso de error en la fila
                    continue  # Continuar con la siguiente fila

            return tripulantes, vuelos_tripulante

        except Exception as e:
            print(f"Error general al crear tripulantes o encontrar vuelos: {e}")
            ###traceback.print_exc()
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

        def clean_value(value):
            if isinstance(value, str):  # Verificar si es una cadena
                print(f"Limpiando valor: {value}")
                print(f"Resultado valor: {value.strip()}")
                return value.strip()  # Eliminar espacios en blanco
            return value  # Dejar el valor tal como está si no es cadena
        
        def validate_dates(tripulantes_df, column_name, file_path, state):
            for i, value in tripulantes_df[column_name].items():
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

        tripulantes_df["DOB"] = tripulantes_df["DOB"].apply(clean_value)

        tripulantes_df["DOB"] = pd.to_datetime(tripulantes_df["DOB"], format='%d/%m/%y', errors='coerce')
        
        validate_dates(tripulantes_df, "DOB", file_path, state)