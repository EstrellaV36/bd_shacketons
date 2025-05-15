from datetime import datetime, timedelta
import re
import pandas as pd
from sqlalchemy.orm import Session
import traceback
from datetime import time
from sqlalchemy import func, and_
from PyQt6.QtWidgets import QMessageBox
from app.models import Buque, Tripulante, Vuelo, EtaCiudad, Viaje, TripulanteVuelo, Hotel, TripulanteHotel, Restaurante, TripulanteRestaurante, Transporte, TripulanteTransporte, TripulanteAsistencia
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter, column_index_from_string

class Viajes:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def viajes_main(self, file_path):
        try:
            column_names_to_extract = ['Activo', 'Maleta perdida', 'Transporte', 'atencion Medica']

            excel_data_on = pd.read_excel(file_path, sheet_name='ON', header=None)

            viajes_on = self.read_selected_columns(excel_data_on, start_row=0, column_names_to_extract=column_names_to_extract)  
            # viajes_on.reset_index(drop=True, inplace=True)

            excel_data_off = pd.read_excel(file_path, sheet_name='OFF', header=None)

            viajes_off = self.read_selected_columns(excel_data_off, start_row=0, column_names_to_extract=column_names_to_extract)  
            # viajes_off.reset_index(drop=True, inplace=True)

            return viajes_on, viajes_off
        except Exception as e:
            raise Exception(f"[Viajes] Error al procesar el archivo: {e}")
        
    def read_selected_columns(self, data, start_row, column_names_to_extract):
        column_names = data.iloc[start_row].tolist()
        column_names = [str(col).strip().lower() for col in column_names]
        data.columns = column_names
        data = data.iloc[start_row + 2:].reset_index(drop=True)  # Eliminar filas de encabezado

        # Validar columnas requeridas
        column_names_to_extract = [col.strip().lower() for col in column_names_to_extract]
        missing_columns = [col for col in column_names_to_extract if col not in data.columns]

        if missing_columns:
            raise ValueError(f"Columnas no encontradas en el archivo: {missing_columns}")

        # Leer los datos
        data_block = []
        current_row = 0  # Ya eliminamos encabezados, así que partimos desde 0

        while current_row < len(data):
            row_data = data.iloc[current_row]
            if row_data[column_names_to_extract].isnull().all():
                data_block.append({col: pd.NA for col in column_names_to_extract})
                current_row += 1
                continue
            data_block.append(row_data[column_names_to_extract].to_dict())
            current_row += 1

        return pd.DataFrame(data_block)

    def _create_viaje(self, file_path, viajes_df, tripulantes_df, buques_df, estado):
        try:
            errors = []
            errors_message = []

            for index, row in tripulantes_df.iterrows():
                if "activo" not in viajes_df.columns:
                    # print(f"[ERROR] Columna 'Activo' no existe en el DataFrame. Verifica el archivo Excel.")
                    continue  # O manejar el error como corresponda

                # print(f"ID = {index} | {viajes_df.loc[index]}")
                activo_valor = viajes_df.loc[index].get("activo")
                # print(f"Valor de activo = {activo_valor}")
                # print(f"[DEBUG] Tipo de activo_valor: {type(activo_valor)} | Valor: {activo_valor}")


                if pd.isna(activo_valor):
                    # print(f"[ERROR] Columna 'Activo' faltante o vacía en fila {index + 3}")
                    # Registrar en errors y errors_message
                    y = get_excel_column_letter(file_path, estado, "Activo")
                    errors.append([index + 3, y])
                    errors_message.append(f"Valor 'Activo' faltante [{index + 3},{y}]")
                    continue
                else:
                    activo_valor_str = str(activo_valor).strip().upper()
                    if activo_valor_str not in ["SI", "NO"]:
                        # Registrar en errors y errors_message
                        y = get_excel_column_letter(file_path, estado, "Activo")
                        errors.append([index + 3, y])
                        errors_message.append(f"Valor no válido en 'Activo' [{index + 3},{y}]")
                        print(f"[ERROR] Valor no válido en 'Activo' en fila {index + 3}: {activo_valor_str} [{index + 3},{y}]")
                        continue
                    else:
                        activo_valor = activo_valor_str  # Confirmado como "SI" o "NO"

                # print(f"El valor de activo es: [{index}] | {activo_valor}")

                # Convertir el valor de 'Activo' a booleano
                activo = True if str(activo_valor).strip().upper() == "SI" else False

                pasaporte_value = tripulantes_df.loc[index]["Pasaporte"]
                if pd.isna(pasaporte_value) or str(pasaporte_value).strip() == "":
                    print(f"[NO PASAPORTE] Tripulante en fila {index + 3} no tiene pasaporte.")
                    continue

                pasaporte = str(pasaporte_value).strip()
                tripulante = self.db_session.query(Tripulante).filter_by(pasaporte=pasaporte).first()

                if tripulante:
                    tripulante_id = tripulante.tripulante_id  # O 'tripulante.id' si así se llama en tu modelo
                    buque_id = tripulante.buque_id  # O 'tripulante.id' si así se llama en tu modelo
                    # print(f"Pasaporte = {pasaporte} | ID = {tripulante_id} | buque_id = {buque_id}")
                else:
                    print(f"[ERROR] Tripulante con pasaporte {pasaporte} no encontrado.")
                    # Aquí puedes registrar el error en errors y errors_message si corresponde
                    pass

                eta_ciudad = self.db_session.query(EtaCiudad).filter_by(tripulante_id=tripulante_id, buque_id=buque_id).first()
                if not eta_ciudad:
                    raise Exception(f"No se encontró EtaCiudad para tripulante ID {tripulante_id} y buque ID {buque_id}")
                
                viaje_existente = self.db_session.query(Viaje).filter_by(
                    tripulante_id=tripulante_id,
                    buque_id=buque_id,
                    eta_id=eta_ciudad.eta_id,
                    estado=estado
                ).first()

                if viaje_existente:
                    # Si el viaje ya existe, actualizar el campo 'activo' si es diferente
                    if viaje_existente.activo != activo:
                        # print(f"El viaje ya existe. Actualizando el campo 'activo' de {viaje_existente.viaje_id} a {activo}")
                        viaje_existente.activo = activo  # Actualizar el estado 'activo'
                        self.db_session.add(viaje_existente)  # Asegurarse de que se guarde el cambio
                        self.db_session.commit()

                    else:
                        #print(f"El viaje para Tripulante ID {tripulante_id}, Buque ID {buque_id}, Estado {estado} ya existe y está activo como {activo}.")
                        continue
                        # Retornamos el viaje existente (sin crear uno nuevo)

                # Si no existe, crear el nuevo viaje
                equipaje_perdido = True if str(viajes_df.loc[index]["maleta perdida"]).strip().upper() == "SI" else False
                asistencia_medica = True if str(viajes_df.loc[index]["atencion medica"]).strip().upper() == "SI" else False

                viaje = Viaje(
                    tripulante_id=tripulante_id,
                    buque_id=buque_id,
                    eta_id=eta_ciudad.eta_id,  # Asignar el ID de EtaCiudad
                    estado=estado,
                    activo=activo,
                    equipaje_perdido=equipaje_perdido,
                    asistencia_medica=asistencia_medica
                )
                self.db_session.add(viaje)
                self.db_session.flush()  # Obtener el ID del viaje recién creado

                # Guardar el viaje y los hoteles
                self.db_session.commit()
                #print(f"Viaje creado para Tripulante ID {tripulante_id} en Buque ID {buque_id} con Estado {estado}")

            return errors, errors_message  # Retornar el viaje recién creado

        except Exception as e:
            self.db_session.rollback()  # Revertir en caso de error
            print(f"Error al crear o actualizar viaje: {e}")
            return errors, errors_message
    
    def _get_hoteles_para_tripulante(self, tripulante_id, viaje_id):
        """
        Obtiene las reservas de hotel asociadas a un tripulante y las asigna a un viaje.
        Filtra las reservas activas según la fecha de entrada y salida.
        """
        try:
            # Recuperar todas las reservas de hotel para el tripulante
            tripulante_hoteles = self.db_session.query(TripulanteHotel).filter_by(
                tripulante_id=tripulante_id
            ).all()

            print(f"Hoteles recuperados para Tripulante ID {tripulante_id}: {len(tripulante_hoteles)} reservas activas encontradas.")

            # Asignar las reservas de hotel al viaje
            for hotel in tripulante_hoteles:
                # Verificamos si el viaje_id es válido
                if viaje_id:
                    hotel.viaje_id = viaje_id  # Asignar el viaje a la reserva de hotel
                    self.db_session.add(hotel)  # Asegurarnos de guardar cualquier cambio

            # Commit para guardar los cambios realizados
            self.db_session.commit()

            return tripulante_hoteles

        except Exception as e:
            print(f"Error al obtener y asignar hoteles para tripulante {tripulante_id}: {e}")
            self.db_session.rollback()  # Revertir cualquier cambio en caso de error
            return []
        
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