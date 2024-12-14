from datetime import datetime, timedelta
import re
import pandas as pd
from sqlalchemy.orm import Session
import traceback
from datetime import time
from sqlalchemy import func, and_
from PyQt6.QtWidgets import QMessageBox
from app.models import Buque, Tripulante, Vuelo, EtaCiudad, Viaje, TripulanteVuelo, Hotel, TripulanteHotel, Restaurante, TripulanteRestaurante, Transporte, TripulanteTransporte, TripulanteAsistencia

class Restaurantes:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def restaurantes_main(self, file_path):
        try:
            excel_data_on = pd.read_excel(file_path, sheet_name='ON', header=None)

            restaurantes_on = self._extract_restaurants(excel_data_on, start_row=0, state="on")
            restaurantes_on.reset_index(drop=True, inplace=True)

            excel_data_off = pd.read_excel(file_path, sheet_name='OFF', header=None)

            restaurantes_off = self._extract_restaurants(excel_data_off, start_row=0, state="off")
            restaurantes_off.reset_index(drop=True, inplace=True)

            return restaurantes_on, restaurantes_off
        except Exception as e:
            raise Exception(f"[Restaurantes] Error al procesar el archivo: {e}")

    def _create_restaurantes(self, restaurantes_df, tripulantes_df):        
        try:
            for index in range(len(tripulantes_df)):
                restaurante_row = restaurantes_df.iloc[index]

                # Obtener el pasaporte del tripulante basado en la fila actual
                pasaporte_tripulante = tripulantes_df.iloc[index]['Pasaporte']  # Asegúrate de que esta columna exista
                tripulante = self.db_session.query(Tripulante).filter_by(pasaporte=pasaporte_tripulante).first()

                # Comprobar si se encontró el tripulante
                if not tripulante:
                    #print(f"Tripulante no encontrado para el pasaporte: {pasaporte_tripulante}, continuando...")  # Línea de depuración
                    continue

                # Obtener preferencia alimenticia de cada restaurante
                # preferencia_alimenticia_set = [
                #     restaurante_row[f'Restaurante {i}']['Preferencia']
                #     for i in range(1, len(restaurantes_df))
                #     if f'Restaurante {i}' in restaurante_row and restaurante_row[f'Restaurante {i}'] is not None
                # ]
                # print(f"Tripulante ID: {tripulante.tripulante_id}, Preferencias Alimenticias: {preferencia_alimenticia_set}")  # Línea de depuración

                #print(restaurante_row[f'Restaurante {1}']['Preferencia'])
                preferencia_alimenticia = restaurante_row[f'Restaurante {1}']['Preferencia']

                # Obtener los nombres de los restaurantes a partir del DataFrame
                #print(restaurante_row[f'Restaurante {1}'])
                nombre_restaurantes = [
                    restaurante_row[f'Restaurante {i}']['Restaurante']
                    for i in range(1, len(restaurantes_df))
                    if f'Restaurante {i}' in restaurante_row and restaurante_row[f'Restaurante {i}'] is not None
                ]
                #print(f"Nombres de Restaurantes: {nombre_restaurantes}")  # Línea de depuración para los restaurantes

                                # Procesar cada servicio de comida
                # Asegurarse de que no se accede fuera de rango en los nombres de los restaurantes
                for i in range(1, 4):  # Solo 3 restaurantes
                    if i - 1 < len(nombre_restaurantes):  # Verifica si el índice existe
                        nombre_restaurante = nombre_restaurantes[i - 1]
                    else:
                        continue  # Si no existe, saltar al siguiente ciclo


                    servicio_comida = restaurante_row[f'Restaurante {i}']['Servicio Comida']
                    if pd.isna(servicio_comida):
                        #print(f"No hay servicio de comida en {nombre_restaurantes[i-1]}, continuando...")  # Línea de depuración
                        continue

                    fecha_desde = restaurante_row[f'Restaurante {i}']['Fecha desde']
                    if pd.isna(fecha_desde):
                        #print(f"No hay servicio de comida en {nombre_restaurantes[i-1]}, continuando...")  # Línea de depuración
                        continue

                    # Extraer ciudad y tipo de comida
                    ciudad_tipo = servicio_comida.split(" ")  # Separar "PUQ Cena" en ["PUQ", "Cena"]
                    ciudad = ciudad_tipo[0] if len(ciudad_tipo) > 0 else None
                    tipo_comida = ciudad_tipo[1] if len(ciudad_tipo) > 1 else None
                    #print(f"{tripulante.tripulante_id} | Servicio Comida en {nombre_restaurantes[i-1]}: Ciudad = {ciudad}, Tipo de Comida = {tipo_comida}, Fecha desde = {fecha_desde}")  # Línea de depuración

                    # Crear o recuperar el restaurante
                    nombre_restaurante = nombre_restaurantes[i - 1]
                    #restaurante = self.db_session.query(Restaurante).filter_by(nombre=nombre_restaurante).first()
                    restaurante = (
                        self.db_session.query(Restaurante)
                        .filter(
                            and_(
                                Restaurante.nombre == nombre_restaurante,
                                Restaurante.ciudad == ciudad
                            )
                        )
                        .first()
                    )
                    
                    if not restaurante:
                        #print(f"Creando nuevo restaurante: {nombre_restaurante} en {ciudad}")  # Línea de depuración
                        restaurante = Restaurante(nombre=nombre_restaurante, ciudad=ciudad)
                        self.db_session.add(restaurante)
                        self.db_session.flush()  # Asegúrate de que el ID se genere antes de continuar

                    tripulante_restaurante = (
                        self.db_session.query(TripulanteRestaurante)
                        .filter(
                            and_(
                                TripulanteRestaurante.tripulante_id == tripulante.tripulante_id,
                                TripulanteRestaurante.restaurante_id == restaurante.restaurante_id,
                                TripulanteRestaurante.fecha_reserva == fecha_desde,
                                TripulanteRestaurante.tipo_comida == tipo_comida
                            )
                        )
                        .first()
                    )

                    #print(tripulante_restaurante)

                    if not tripulante_restaurante:
                        # Asignar preferencia alimenticia al tripulante si no se ha establecido
                        if restaurante is not None:  # Crea la relación entre el tripulante y el restaurante
                            relacion = TripulanteRestaurante(
                                tripulante_id=tripulante.tripulante_id,
                                restaurante_id=restaurante.restaurante_id,
                                fecha_reserva=fecha_desde,
                                tipo_comida=tipo_comida,
                                pref_alimenticia = preferencia_alimenticia if preferencia_alimenticia is not None else 'NORMAL' ##Todos con dieta normal a menos que se diga lo contrario
                            )
                            self.db_session.add(relacion)
                            self.db_session.flush()

            # Guardar cambios en la base de datos
            self.db_session.commit()

        except Exception as e:
            print(f"[RESTAURANTE _create] Error al guardar en la base de datos: {e}")
            ###traceback.print_exc()
            self.db_session.rollback()  # Asegúrate de revertir la sesión en caso de error

    def _extract_restaurants(self, excel_data, start_row, state):
        restaurants = []
        
        # Convertir los nombres de las columnas a cadenas y quitar espacios
        restaurant_columns = excel_data.loc[start_row].dropna().str.lower().tolist()

        # Iterar sobre cada fila, comenzando desde la fila indicada
        for i in range(start_row + 1, excel_data.shape[0]):
            tripulante_restaurants = {}
            restaurants_num = 1
            
            # Iterar sobre las columnas de restaurantes hasta que ya no existan
            while True:
                prefer_alimento = "prefer. aliment"
                servicio_comida = f'servicio comida {restaurants_num}'
                fecha_desde = f'fecha desde {restaurants_num}'
                fecha_hasta = f'fecha hasta {restaurants_num}'
                restaurante = f'restaurant {restaurants_num}'
                        
                # Verificar si las columnas existen en el DataFrame
                if (prefer_alimento in restaurant_columns and
                    servicio_comida in restaurant_columns and
                    fecha_desde in restaurant_columns and
                    fecha_hasta in restaurant_columns and
                    restaurante in restaurant_columns):
                    
                    col_idx_prefer_alimento = restaurant_columns.index(prefer_alimento)
                    col_idx_servicio_comida = restaurant_columns.index(servicio_comida)
                    col_idx_fecha_desde = restaurant_columns.index(fecha_desde)
                    col_idx_fecha_hasta = restaurant_columns.index(fecha_hasta)
                    col_idx_restaurante = restaurant_columns.index(restaurante)

                    # Obtener los valores, asignando nulo si no hay información
                    prefer_alimento_idx = excel_data.iloc[i, col_idx_prefer_alimento] if pd.notna(excel_data.iloc[i, col_idx_prefer_alimento]) else None
                    servicio_comida_idx = excel_data.iloc[i, col_idx_servicio_comida] if pd.notna(excel_data.iloc[i, col_idx_servicio_comida]) else None
                    fecha_desde_idx = excel_data.iloc[i, col_idx_fecha_desde] if pd.notna(excel_data.iloc[i, col_idx_fecha_desde]) else None
                    fecha_hasta_idx = excel_data.iloc[i, col_idx_fecha_hasta] if pd.notna(excel_data.iloc[i, col_idx_fecha_hasta]) else None
                    restaurante_idx = excel_data.iloc[i, col_idx_restaurante] if pd.notna(excel_data.iloc[i, col_idx_restaurante]) else None

                    # Agregar la información incluso si algunos campos son nulos
                    tripulante_restaurants[f'Restaurante {restaurants_num}'] = {
                        "Preferencia": prefer_alimento_idx,
                        "Servicio Comida": servicio_comida_idx,
                        "Fecha desde": fecha_desde_idx,
                        "Fecha hasta": fecha_hasta_idx,
                        "Restaurante": restaurante_idx
                    }

                    # Incrementar el restaurante_num para buscar el siguiente conjunto
                    restaurants_num += 1
                else:
                    break  # Detener la búsqueda si no se encuentra una de las columnas

            # Solo agregar el restaurante si se encontraron datos para el tripulante
            if tripulante_restaurants:
                restaurants.append(tripulante_restaurants)

        # Verificar si se encontraron restaurantes
        if len(restaurants) == 0:
            print("No se encontraron restaurantes en las filas procesadas.")
        else:
            print(f"{len(restaurants)} restaurantes procesados. ({state})")

        return pd.DataFrame(restaurants)