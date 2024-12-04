import pandas as pd
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QFileDialog, QCheckBox, QHBoxLayout, QDateEdit
from PyQt6.QtCore import Qt, QDate
from app.database import get_db_session
from app.models import Buque, EtaCiudad, Tripulante, Vuelo, TripulanteVuelo, Transporte, TripulanteTransporte, TripulanteAsistencia, Restaurante, TripulanteRestaurante, Hotel, TripulanteHotel, Viaje
from app.controller.controllers import CITY_AIRPORT_CODES, CITY_TO_AIRPORT_CODES
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Alignment, Font, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime, time, timedelta
from sqlalchemy import func, exists, case, and_
from collections import defaultdict

class AsistenciasScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        session = get_db_session()
        layout = QVBoxLayout(self)

        # Label para mostrar asistencias
        self.label = QLabel("ASISTENCIAS")  # Mover el label aquí para que sea un atributo de la clase
        self.label.setStyleSheet("""
            font-size: 40px;  /* Tamaño de fuente */
            font-weight: bold; /* Negrita */
            color: #00272d;    /* Color del texto */
            text-align: center; /* Centrar el texto horizontalmente */
            margin-bottom: 20px; /* Espacio debajo del título */
        """)

        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)  # Centrar el título
        layout.addSpacing(20)

        # Llenar el combo de ciudades desde la base de datos
        self.combo_ciudades = QComboBox()
        self.combo_ciudades.addItem("Ciudad")  # Agregar un valor por defecto
        ciudades = session.query(Hotel.ciudad).distinct().all()  # Consulta para obtener las ciudades únicas
        for ciudad in ciudades:
            self.combo_ciudades.addItem(ciudad.ciudad)
            #print(ciudad.ciudad)
        layout.addWidget(self.combo_ciudades)

        # Cuadro de selección de tipo tripulante
        self.tipo_tripulante = QComboBox()
        self.tipo_tripulante.addItem("Tipo tripulante")  # Agregar un valor por defecto
        self.tipo_tripulante.addItems(["AMBOS", "ON", "OFF"])  
        layout.addWidget(self.tipo_tripulante)

        # Cuadro de selección de tipo tripulante
        self.combo_proveedor = QComboBox()
        self.combo_proveedor.addItem("Proveedor")  # Agregar un valor por defecto
        self.combo_proveedor.addItems(["C&L", "FBAGS", "SHACK", "WPU"])  
        layout.addWidget(self.combo_proveedor)

        self.check_fecha = QCheckBox("Habilitar filtro por fechas")
        self.check_fecha.setChecked(False)  # Inicialmente deshabilitado
        self.check_fecha.stateChanged.connect(self.actualizar_datos)  # Conectar evento de cambio de estado
        layout.addWidget(self.check_fecha)

        # Layout horizontal para las fechas
        layout_filtro = QHBoxLayout()

        # Selector de fecha de inicio
        self.date_start1 = QDateEdit()
        self.date_start1.setCalendarPopup(True)
        self.date_start1.setDate(QDate.currentDate())
        layout_filtro.addWidget(QLabel("Fecha inicio:"))
        layout_filtro.addWidget(self.date_start1)

        # Selector de fecha de fin
        self.date_end1 = QDateEdit()
        self.date_end1.setCalendarPopup(True)
        self.date_end1.setDate(QDate.currentDate())
        layout_filtro.addWidget(QLabel("Fecha fin:"))
        layout_filtro.addWidget(self.date_end1)

        layout.addLayout(layout_filtro)

        # Tabla para mostrar datos
        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        # Botón para generar el Excel
        button_generar_excel = QPushButton("Generar excel")
        button_generar_excel.clicked.connect(self.generar_excel_con_ciudad)  # Conectar al método de generación de Excel
        layout.addWidget(button_generar_excel)

        # Botón "Volver" para regresar a la pantalla anterior (Generación de Reportes)
        button_volver = QPushButton("Volver")
        button_volver.setFixedWidth(100)
        button_volver.clicked.connect(self.volver_a_opciones_programar)
        layout.addWidget(button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        # Conectar el cambio en el QComboBox a un método
        self.combo_ciudades.currentTextChanged.connect(self.actualizar_datos)
        self.tipo_tripulante.currentTextChanged.connect(self.actualizar_datos)
        self.combo_proveedor.currentTextChanged.connect(self.actualizar_datos)
        self.date_start1.dateChanged.connect(self.actualizar_datos)
        self.date_end1.dateChanged.connect(self.actualizar_datos)

        # Actualizar datos inicialmente
        self.actualizar_datos()

    def generar_excel_con_ciudad(self):
        ciudad_seleccionada = self.combo_ciudades.currentText()  # Obtener la ciudad seleccionada
        tipo_crew = self.tipo_tripulante.currentText()
        proveedor = self.combo_proveedor.currentText()
        fecha_inicio = self.date_start1.date().toString("dd-MM-yyyy")
        fecha_fin = self.date_start1.date().toString("dd-MM-yyyy")
        self.generar_excel(ciudad_seleccionada, tipo_crew, proveedor, fecha_inicio, fecha_fin)  # Llamar a generar_excel con la ciudad seleccionada

    def actualizar_datos(self):
        ciudad_seleccionada = self.combo_ciudades.currentText()  # Obtiene la ciudad seleccionada
        proveedor_seleccionado = self.combo_ciudades.currentText()
        tipo_tripulante = self.tipo_tripulante.currentText()
        if ciudad_seleccionada.lower() != "ciudad":
            self.label.setText(f"ASISTENCIAS EN {ciudad_seleccionada.upper()}")  # Actualiza el label
        else:
            self.label.setText(f"ASISTENCIAS")  # Actualiza el label

        # Cargar datos en la tabla
        self.cargar_datos(ciudad_seleccionada, proveedor_seleccionado, tipo_tripulante)

    def toggle_fechas(self, state):
        enabled = state == Qt.CheckState.Checked  # Verificar si el checkbox está marcado
        self.date_start1.setEnabled(enabled)
        self.date_end1.setEnabled(enabled)
        # Deshabilitar el cuadro emergente si está desmarcado
        self.date_start1.setCalendarPopup(enabled)
        self.date_end1.setCalendarPopup(enabled)

    def cargar_datos(self, ciudad_seleccionada, proveedor_seleccionado, tipo_tripulante):
        session = get_db_session()  # Obtener la sesión de la base de datos

        # Obtener el nombre de la ciudad a partir del código
        codigo_ciudad = ciudad_seleccionada
        ciudad_seleccionada = CITY_AIRPORT_CODES.get(ciudad_seleccionada)
        # Obtener las fechas seleccionadas en QDateEdit
        fecha_inicio = self.date_start1.date().toPyDate()
        fecha_fin = datetime.combine(self.date_end1.date().toPyDate(), time.max)

        # Obtener datos de vuelos de arribo
        arribo_vuelos_query = (
            session.query(
                Buque.empresa.label("Owner"),
                Buque.nombre.label("Vessel"),
                Vuelo.aeropuerto_llegada.label("Aeropuerto_Llegada"),
                EtaCiudad.eta.label("ETA"),
                Vuelo.hora_llegada.label("Hora_Arribo"),
                Tripulante.nombre.label("First_Name"),
                Tripulante.apellido.label("Last_Name"),
                Tripulante.condicion.label("Condition"),
                Viaje.estado.label("Type"),
                Vuelo.codigo.label("Nro_Vuelo_Arribo"),
                Tripulante.tripulante_id,
                Vuelo.fecha.label("Fecha_Vuelo_Arribo")
            )
            .outerjoin(TripulanteVuelo, TripulanteVuelo.tripulante_id == Tripulante.tripulante_id)
            .outerjoin(Viaje, Tripulante.tripulante_id == Viaje.tripulante_id)
            .outerjoin(Vuelo, TripulanteVuelo.vuelo_id == Vuelo.vuelo_id)
            .outerjoin(Buque, Tripulante.buque_id == Buque.buque_id)
            .outerjoin(EtaCiudad, Buque.buque_id == EtaCiudad.buque_id)
            .filter(Vuelo.aeropuerto_llegada == ciudad_seleccionada)
        )

        # Aplicar filtro de ETA por rango de fechas si está habilitado
        if self.check_fecha.isChecked():
            arribo_vuelos_query = arribo_vuelos_query.filter(
                EtaCiudad.eta >= fecha_inicio,
                EtaCiudad.eta <= fecha_fin
            )

        # Ejecutar la consulta
        arribo_vuelos = arribo_vuelos_query.all()
        # Construir un diccionario para almacenar la información de los tripulantes
        tripulantes_info = {}

        vuelos_dict = defaultdict(lambda: {
            "arribo": [],
            "salida": []
        })

        # Agregar la información de vuelos de arribo al diccionario
        for arribo in arribo_vuelos:
            tripulante_id = arribo.tripulante_id
            if tripulante_id not in tripulantes_info:
                tripulantes_info[tripulante_id] = {
                    "Owner": arribo.Owner,
                    "Vessel": arribo.Vessel,
                    "ETA": arribo.ETA,
                    "First_Name": arribo.First_Name,
                    "Last_Name": arribo.Last_Name,
                    "Condition": arribo.Condition,
                    "Type": arribo.Type,
                    "Nro_Vuelo_Arribo": arribo.Nro_Vuelo_Arribo,
                    "Fecha_Vuelo_Arribo": arribo.Fecha_Vuelo_Arribo,
                    "Hora_Arribo": arribo.Hora_Arribo,
                    "Nro_Vuelo_Salida": None,
                    "Fecha_Vuelo_Salida": None,
                    "Hora_Vuelo_Salida": None,
                    "Asistencia": None,
                    "Transportes": None,
                    "Hotel": None,
                    "Habitación": None
                }

            # Agregar vuelo de arribo al diccionario de vuelos
            vuelos_dict[tripulante_id]["arribo"].append({
                "Nro_Vuelo_Arribo": arribo.Nro_Vuelo_Arribo,
                "Fecha_Vuelo_Arribo": arribo.Fecha_Vuelo_Arribo,
                "Hora_Arribo": arribo.Hora_Arribo,
                "Aeropuerto_Llegada": arribo.Aeropuerto_Llegada
            })

        #Esta consulta esta capturando tambien los viajes en bus guardados en "vuelos"
        # Obtener datos de vuelos de salida
        salida_vuelos = (
            session.query(
                Vuelo.aeropuerto_salida.label("Aeropuerto_Salida"),
                Vuelo.hora_salida.label("Hora_Salida"),
                Vuelo.codigo.label("Nro_Vuelo_Salida"),
                Vuelo.fecha.label("Fecha_Vuelo_Salida"),
                Tripulante.tripulante_id,
                Viaje.estado.label("Estado")
            )
            .outerjoin(TripulanteVuelo, TripulanteVuelo.tripulante_id == Tripulante.tripulante_id)
            .outerjoin(Viaje, Tripulante.tripulante_id == Viaje.tripulante_id)
            .outerjoin(Vuelo, TripulanteVuelo.vuelo_id == Vuelo.vuelo_id)
            .filter((Vuelo.aeropuerto_salida) == ciudad_seleccionada)
            .all()
        )

        # Agregar la información de vuelos de salida al diccionario
        for salida in salida_vuelos:
            tripulante_id = salida.tripulante_id
            if tripulante_id in tripulantes_info:
                tripulantes_info[tripulante_id]["Nro_Vuelo_Salida"] = salida.Nro_Vuelo_Salida
                tripulantes_info[tripulante_id]["Fecha_Vuelo_Salida"] = salida.Fecha_Vuelo_Salida
                tripulantes_info[tripulante_id]["Hora_Vuelo_Salida"] = salida.Hora_Salida

                # Agregar vuelo de salida al diccionario de vuelos
                vuelos_dict[tripulante_id]["salida"].append({
                    "Nro_Vuelo_Salida": salida.Nro_Vuelo_Salida,
                    "Fecha_Vuelo_Salida": salida.Fecha_Vuelo_Salida,
                    "Hora_Salida": salida.Hora_Salida,
                    "Aeropuerto_Salida": salida.Aeropuerto_Salida

                })

        # Construir la consulta de transporte
        transporte_necesario = (
            session.query(
                Tripulante.tripulante_id,
                Viaje.estado.label("Estado"),
                Tripulante.nombre.label("First_Name"),
                Tripulante.apellido.label("Last_Name"),
                Tripulante.nacionalidad.label("Nacionalidad"),
                exists().where(
                    (Transporte.city_in == codigo_ciudad) &
                    (Transporte.transporte_id == TripulanteTransporte.transporte_id) &
                    (TripulanteTransporte.tripulante_id == Tripulante.tripulante_id)
                ).label("Tiene_Transporte")
            )
            .join(TripulanteTransporte, Tripulante.tripulante_id == TripulanteTransporte.tripulante_id)
            .join(Viaje, Tripulante.tripulante_id == Viaje.tripulante_id)
            .group_by(Tripulante.tripulante_id, Viaje.estado, Tripulante.nombre, Tripulante.apellido, Tripulante.nacionalidad)
        )

        resultados_transporte = transporte_necesario.all()
        # Agregar la información de transporte al diccionario
        for resultado in resultados_transporte:
            tripulante_id = resultado.tripulante_id
            if tripulante_id in tripulantes_info:
                tripulantes_info[tripulante_id]["Transporte"] = resultado.Tiene_Transporte

        # Inicializar asistencia_data como una consulta vacía
        asistencia_data = None

        # Obtener la información de asistencia y proveedores según la ciudad seleccionada
        if codigo_ciudad == "SCL":
            asistencia_data = (
                session.query(
                    TripulanteAsistencia.tripulante_id,
                    TripulanteAsistencia.necesita_asistencia_scl.label("Necesita_Asistencia"),
                    TripulanteAsistencia.proveedor_scl.label("Proveedor")
                )
            )
        elif codigo_ciudad == "PUQ":
            asistencia_data = (
                session.query(
                    TripulanteAsistencia.tripulante_id,
                    TripulanteAsistencia.necesita_asistencia_puq.label("Necesita_Asistencia"),
                    TripulanteAsistencia.proveedor_puq.label("Proveedor")
                )
            )
        elif codigo_ciudad == "WPU":
            asistencia_data = (
                session.query(
                    TripulanteAsistencia.tripulante_id,
                    TripulanteAsistencia.necesita_asistencia_wpu.label("Necesita_Asistencia"),
                    TripulanteAsistencia.proveedor_wpu.label("Proveedor")
                )
            )

        # Ejecutar la consulta y obtener resultados
        resultados_asistencia = asistencia_data.all() if asistencia_data else []

        # Agregar la información de asistencia al diccionario
        for resultado in resultados_asistencia:
            tripulante_id = resultado.tripulante_id
            if tripulante_id in tripulantes_info:
                # Obtener el valor de asistencia como "Sí" o "No"
                tripulantes_info[tripulante_id]["Asistencia"] = "Sí" if resultado.Necesita_Asistencia else "No"
                tripulantes_info[tripulante_id]["Proveedor"] = resultado.Proveedor if resultado.Proveedor else ""

        comida_requerida = (
            session.query(
                Tripulante.tripulante_id,
                case(
                    (TripulanteRestaurante.tripulante_id.isnot(None), "Sí"),
                    else_="No"
                ).label("Requiere_Comida")
            )
            .outerjoin(TripulanteRestaurante, Tripulante.tripulante_id == TripulanteRestaurante.tripulante_id)
            .outerjoin(Restaurante, TripulanteRestaurante.restaurante_id == Restaurante.restaurante_id)
            .filter(
            (Restaurante.ciudad == codigo_ciudad)  # Filtrar por ciudad
            )
            .group_by(Tripulante.tripulante_id)
            .all()
        )

        # Agregar la información de comidas al diccionario
        for resultado in comida_requerida:
            tripulante_id = resultado.tripulante_id
            if tripulante_id in tripulantes_info:
                tripulantes_info[tripulante_id]["Requiere_Comida"] = resultado.Requiere_Comida
            else:
                # Si el tripulante no está en tripulantes_info, añadirlo con "No"
                pass

        # Si un tripulante no tiene registro de comida, agregar "No"
        for tripulante_id in tripulantes_info.keys():
            if "Requiere_Comida" not in tripulantes_info[tripulante_id]:
                tripulantes_info[tripulante_id]["Requiere_Comida"] = "No"

        # Obtener la información del hotel
        tripulantes_con_hotel = (
            session.query(
                Tripulante.tripulante_id,
                Hotel.nombre.label("Nombre_Hotel"),
                TripulanteHotel.tipo_habitacion,
                TripulanteHotel.fecha_salida,
            )
            .join(TripulanteHotel, TripulanteHotel.tripulante_id == Tripulante.tripulante_id)
            .join(Hotel, TripulanteHotel.hotel_id == Hotel.hotel_id)
            .filter(func.lower(Hotel.ciudad) == codigo_ciudad.lower())
            .all()
        )

        # Agregar la información de hotel y habitación al diccionario
        for resultado in tripulantes_con_hotel:
            tripulante_id = resultado.tripulante_id
            if tripulante_id in tripulantes_info:
                tripulantes_info[tripulante_id]["Hotel"] = resultado.Nombre_Hotel
                tripulantes_info[tripulante_id]["Habitación"] = resultado.tipo_habitacion
            else:
                # Si el tripulante no está en tripulantes_info, añadirlo con la información del hotel y habitación
                tripulantes_info[tripulante_id] = {
                    "Hotel": resultado.Nombre_Hotel,
                    "Habitación": resultado.tipo_habitacion
                }

        # Construir la consulta de transporte
        transporte_pick_up = (
            session.query(
                Tripulante.tripulante_id,
                Transporte.city_in.label("Ciudad_Transporte_in"),
                Transporte.place_in.label("Lugar_Transporte_in"),
                Transporte.city_end.label("Ciudad_Transporte_end"),
                Transporte.place_end.label("Lugar_Transporte_end"),
                TripulanteTransporte.date_pickup.label("Fecha_Pickup"),
                TripulanteTransporte.hours_pickup.label("Hora_Pickup")
            )
            .join(TripulanteTransporte, Tripulante.tripulante_id == TripulanteTransporte.tripulante_id)
            .filter(Transporte.transporte_id == TripulanteTransporte.transporte_id)
        )
        if ciudad_seleccionada != "ciudad":
            transporte_necesario = transporte_necesario.filter(and_(func.lower(Transporte.city_in) == ciudad_seleccionada),
                                                               Transporte.transporte_id == TripulanteTransporte.transporte_id)

        transporte_dict = defaultdict(list)
        for transporte in transporte_pick_up:
            transporte_dict[transporte.tripulante_id].append(transporte)

        # Procesar la información de transporte
        for tripulante_id, transportes in transporte_dict.items():
            vuelos = vuelos_dict.get(tripulante_id, {'arribo': [], 'salida': []})
            
            for transporte in transportes:
                tramo = f"{transporte.Lugar_Transporte_in}-{transporte.Lugar_Transporte_end}"
                if 'ATO-HOTEL' == tramo:  # Transporte hacia el hotel
                    vuelos_llegada = [
                        v for v in vuelos['arribo']
                        if v is not None and v.get('Aeropuerto_Llegada') and ciudad_seleccionada
                        and v['Aeropuerto_Llegada'].lower() == ciudad_seleccionada.lower()
                    ]
                    for vuelo in vuelos_llegada:
                        tripulantes_info[tripulante_id]["Fecha_Pick_Up"] = vuelo["Fecha_Vuelo_Arribo"]
                        tripulantes_info[tripulante_id]["Hora_Pick_Up"] = vuelo['Hora_Arribo'].time()

                elif 'HOTEL-ATO' in tramo:  # Transporte desde el hotel
                    vuelos_salida = [
                        v for v in vuelos['salida']
                        if v is not None and v.get('Aeropuerto_Salida') and v['Aeropuerto_Salida'].lower() == (ciudad_seleccionada.lower() if ciudad_seleccionada else '')
                    ]

                    for vuelo in vuelos_salida:
                        a1 = CITY_TO_AIRPORT_CODES.get(str(vuelo['Aeropuerto_Salida']))
                        a2 = CITY_TO_AIRPORT_CODES.get(str(vuelo.get('Aeropuerto_Llegada', '')))  # Evitar errores si falta 'Aeropuerto_Llegada'

                        # Calcular `a1` correctamente según el contexto
                        if a1 == 'SCL' and a2 == 'PUQ':
                            a1 = f"{a1} Nacional"
                        elif a1 == 'SCL' and a2 != 'PUQ':
                            a1 = f"{a1} Internacional"

                        # Solo calcular `tiempo_a_restar` si es necesario
                        tiempo_a_restar = None  # Inicializar como None para verificar más adelante
                        if a1 == "PUQ":
                            tiempo_a_restar = timedelta(hours=2, minutes=30)
                        elif a1 == "SCL Nacional":
                            tiempo_a_restar = timedelta(hours=2, minutes=30)
                        elif a1 == "SCL Internacional":
                            tiempo_a_restar = timedelta(hours=3, minutes=30)
                        elif a1 == "WPU":
                            tiempo_a_restar = timedelta(hours=1, minutes=30)
                        elif a1 == "KGI":
                            tiempo_a_restar = timedelta(hours=3, minutes=30)

                        # Verifica si `tiempo_a_restar` fue calculado
                        if tiempo_a_restar is not None:
                            # Ajustar el tiempo para calcular la hora de pick-up
                            hora_pick_up = (vuelo['Hora_Salida'] - tiempo_a_restar).time()
                            tripulantes_info[tripulante_id]['Fecha_Pick_Up'] = vuelo['Fecha_Vuelo_Salida']
                            tripulantes_info[tripulante_id]["Hora_Pick_Up"] = hora_pick_up
                        else:
                            # Log o manejar el caso donde no se necesita transporte
                            print(f"No se requiere transporte para el vuelo con salida {vuelo['Nro_Vuelo_Salida']}.")

        # Asegurarse de que todos los tripulantes tengan asignada la información del hotel y habitación
        for tripulante_id in tripulantes_info.keys():
            if "Hotel" not in tripulantes_info[tripulante_id]:
                tripulantes_info[tripulante_id]["Hotel"] = "No"
            if "Habitación" not in tripulantes_info[tripulante_id]:
                tripulantes_info[tripulante_id]["Habitación"] = "No"

        # Filtrar por tipo de tripulante
        if tipo_tripulante != "Tipo tripulante":  # Cambia este valor por el valor por defecto que tengas
            if tipo_tripulante == "AMBOS":
                # Si el tipo de tripulante es "AMBOS", no aplicamos filtro
                pass  
            else:
                tripulantes_info = {
                    tripulante_id: info for tripulante_id, info in tripulantes_info.items()
                    if "Type" in info and info["Type"] == tipo_tripulante
                }
                
                # Depuración: imprimir tripulantes sin el campo "Type"
                for tripulante_id, info in tripulantes_info.items():
                    if "Type" not in info:
                        print(f"El tripulante con ID {tripulante_id} no tiene el campo 'Type' en su información: {info}")
                    elif info["Type"] != tipo_tripulante:
                        print(f"El tripulante con ID {tripulante_id} tiene 'Type' distinto a '{tipo_tripulante}': {info['Type']}")
        
        # Filtrar por proveedor si se ha seleccionado uno
        proveedor_seleccionado = self.combo_proveedor.currentText()  # Obtener proveedor seleccionado
        if proveedor_seleccionado != "Proveedor":  # Comprobar que no sea el valor por defecto
            tripulantes_info = {
                tripulante_id: info for tripulante_id, info in tripulantes_info.items()
                if info.get("Proveedor", "").lower() == proveedor_seleccionado.lower()
            }

        # Filtrar para asegurar que solo queden registros completos
        tripulantes_info = {
            tripulante_id: info for tripulante_id, info in tripulantes_info.items()
            if info.get("First_Name") or info.get("Last_Name") or info.get("Vessel")  # Puedes ajustar según el criterio
        }

        headers = [
            "Owner", "Vessel", "ETA", "First Name", "Last Name", "Condition", "Type", "Proveedor", "Asistencia", "Transporte",
            "Comidas", "Nro Vuelo Arribo", "Fecha Vuelo Arribo", "Hora Arribo",
            "Hotel", "Habitacion", "Date Pick up", "Hora Pick Up",
            "Nro Vuelo Salida", "Fecha Vuelo Salida", "Hora Vuelo Salida"
        ]

        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)
        self.table_widget.setRowCount(0)
    
        # Agregar filas a la tabla
        for tripulante_id, info in tripulantes_info.items():
            row_position = self.table_widget.rowCount()  # Obtener la cantidad de filas actuales
            self.table_widget.insertRow(row_position)  # Insertar una nueva fila

            # Llenar las celdas de la fila con la información del tripulante
            self.table_widget.setItem(row_position, 0, QTableWidgetItem(info.get("Owner", "")))
            self.table_widget.setItem(row_position, 1, QTableWidgetItem(info.get("Vessel", "")))
            self.table_widget.setItem(row_position, 2, QTableWidgetItem(
                info.get("ETA", "").strftime("%d-%m-%Y") if isinstance(info.get("ETA", ""), datetime) else ""
            ))
            self.table_widget.setItem(row_position, 3, QTableWidgetItem(info.get("First_Name", "")))
            self.table_widget.setItem(row_position, 4, QTableWidgetItem(info.get("Last_Name", "")))
            self.table_widget.setItem(row_position, 5, QTableWidgetItem(info.get("Condition", "")))
            self.table_widget.setItem(row_position, 6, QTableWidgetItem(info.get("Type", "")))
            self.table_widget.setItem(row_position, 7, QTableWidgetItem(info.get("Proveedor", "")))
            self.table_widget.setItem(row_position, 8, QTableWidgetItem(info.get("Asistencia", "")))
            self.table_widget.setItem(row_position, 9, QTableWidgetItem(
                "Sí" if info.get("Transporte", False) else "No"
            ))
            self.table_widget.setItem(row_position, 10, QTableWidgetItem(info.get("Requiere_Comida", "")))
            self.table_widget.setItem(row_position, 11, QTableWidgetItem(info.get("Nro_Vuelo_Arribo", "")))
            self.table_widget.setItem(row_position, 12, QTableWidgetItem(
                info.get("Fecha_Vuelo_Arribo", "").strftime("%d-%m-%Y") if isinstance(info.get("Fecha_Vuelo_Arribo", ""), datetime) else ""
            ))
            self.table_widget.setItem(row_position, 13, QTableWidgetItem(
                info.get("Hora_Arribo", "").strftime("%H:%M") if isinstance(info.get("Hora_Arribo", ""), datetime) else ""
            ))
            self.table_widget.setItem(row_position, 14, QTableWidgetItem(info.get("Hotel", "")))
            self.table_widget.setItem(row_position, 15, QTableWidgetItem(info.get("Habitación", "")))
            self.table_widget.setItem(row_position, 16, QTableWidgetItem(
                info.get("Fecha_Pick_Up", "").strftime("%d-%m-%Y") if isinstance(info.get("Fecha_Pick_Up", ""), datetime) else ""
            ))
            # Obtén el valor de "Hora_Pick_Up"
            hora_pick_up_value = info.get("Hora_Pick_Up", None)

            # Inicializa la cadena para almacenar el valor
            hora_pick_up_str = ""

            # Verifica si es un datetime o un time
            if isinstance(hora_pick_up_value, datetime):
                hora_pick_up_str = hora_pick_up_value.strftime("%H:%M")
            elif isinstance(hora_pick_up_value, time):
                hora_pick_up_str = hora_pick_up_value.strftime("%H:%M")

            # Imprime el resultado
            self.table_widget.setItem(row_position, 17, QTableWidgetItem(hora_pick_up_str))  

            self.table_widget.setItem(row_position, 18, QTableWidgetItem(info.get("Nro_Vuelo_Salida", "")))
            self.table_widget.setItem(row_position, 19, QTableWidgetItem(
                info.get("Fecha_Vuelo_Salida", "").strftime("%d-%m-%Y") if isinstance(info.get("Fecha_Vuelo_Salida", ""), datetime) else ""
            ))
            self.table_widget.setItem(row_position, 20, QTableWidgetItem(
                info.get("Hora_Vuelo_Salida", "").strftime("%H:%M") if isinstance(info.get("Hora_Vuelo_Salida", ""), datetime) else ""
            ))


    # Mantén las funciones de formateo separadas
    def format_date(self, value):
        """Convierte un valor datetime a solo la fecha."""
        if isinstance(value, datetime):
            return value.strftime('%d-%m-%Y')
        return str(value)

    def format_time(self, value):
        """Convierte un valor datetime a solo la hora."""
        if isinstance(value, datetime):
            return value.strftime('%H:%M')
        return str(value)

    def generar_excel(self, ciudad_seleccionada, tipo_crew, proveedor, fecha_inicio, fecha_fin):
        # Crear un DataFrame con los datos de la tabla
        data = []
        for row in range(self.table_widget.rowCount()):
            row_data = []
            for column in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, column)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        # Definir los nombres de las columnas
        column_names = ["Owner", "Vessel", "ETA", "First Name", "Last Name", "Condition", "Type", 
                        "Proveedor", "Asistencia", "Transportes", "Comidas", "Nro Vuelo Arribo", 
                        "Fecha Vuelo Arribo", "Hora Arribo", "Hotel", "Habitación", 
                        "Date Pick Up", "Hora Pick Up", "Nro Vuelo Salida", 
                        "Fecha Vuelo Salida", "Hora Vuelo Salida"]

        df = pd.DataFrame(data, columns=column_names)

        # Generar nombre de archivo basado en buque y hotel seleccionados
        file_name_parts = ["asistencia"]
        if ciudad_seleccionada.lower() != "ciudad" and ciudad_seleccionada.lower() not in file_name_parts:
            file_name_parts.append(ciudad_seleccionada)
        if tipo_crew.lower() != "tipo tripulante" and tipo_crew.lower() not in file_name_parts:
            file_name_parts.append(tipo_crew)
        if proveedor.lower() != "proveedor" and proveedor.lower() not in file_name_parts:
            file_name_parts.append(proveedor)

        file_name = "_".join(file_name_parts) + ".xlsx"


        # Guardar en un archivo Excel
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Guardar archivo Excel", 
            file_name,
            "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if file_path:
            wb = Workbook()
            ws = wb.active

            # Título en negrita, subrayado y de tamaño grande, centrado en más columnas
            ws.merge_cells('A1:T1')  # Fusionar más columnas para centrar el título
            title_cell = ws['A1']
            title_cell.value = "Requerimiento asistencias"
            title_cell.font = Font(size=24, bold=True, underline="single")  # Tamaño de fuente más grande
            title_cell.alignment = Alignment(horizontal="center", vertical="center")

            # Mostrar "CIUDAD" solo si es diferente de "Ciudad"
            if ciudad_seleccionada.lower() != "ciudad":
                ws.cell(row=2, column=1, value="CIUDAD").font = Font(bold=True)
                ws.cell(row=2, column=2, value=ciudad_seleccionada)

            # Configurar el valor predeterminado para "TIPO" y "PROVEEDOR" si no están seleccionados
            tipo_crew_text = tipo_crew if tipo_crew.lower() != "tipo tripulante" else "Ambos"
            proveedor_text = proveedor if proveedor.lower() != "proveedor" else "No se seleccionó proveedor"

            # Agregar "TIPO" con el valor de tipo_crew
            ws.cell(row=3, column=1, value="TIPO").font = Font(bold=True)
            ws.cell(row=3, column=2, value=tipo_crew_text)

            # Agregar "PROVEEDOR" con el valor de proveedor
            ws.cell(row=4, column=1, value="PROVEEDOR").font = Font(bold=True)
            ws.cell(row=4, column=2, value=proveedor_text)

            # Verificar si el filtro de fechas está activado y mostrar "ETA Desde" y "ETA Hasta"
            if self.check_fecha.isChecked() and fecha_inicio and fecha_fin:
                ws.cell(row=5, column=1, value="ETA Desde:").font = Font(bold=True)
                ws.cell(row=5, column=2, value=fecha_inicio.strftime("%d-%m-%Y"))
                ws.cell(row=6, column=1, value="ETA Hasta:").font = Font(bold=True)
                ws.cell(row=6, column=2, value=fecha_fin.strftime("%d-%m-%Y"))
            else:
                ws.cell(row=5, column=1, value="ETA No seleccionada").font = Font(bold=True)

            # Estilos de borde, relleno y alineación
            thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
            header_fill = PatternFill(start_color='ADD8E6', end_color='ADD8E6', fill_type='solid')
            data_fill = PatternFill(start_color='FFFF99', end_color='FFFF99', fill_type='solid')

            # Escribir los encabezados de la tabla
            for col_num, col_name in enumerate(column_names, 1):
                cell = ws.cell(row=8, column=col_num)
                cell.value = col_name
                cell.fill = header_fill
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = thin_border

            # Escribir los datos del DataFrame y aplicar borde a las celdas
            for row_num, row_data in enumerate(df.values, start=9):
                for col_num, cell_value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_num, column=col_num)
                    cell.value = cell_value
                    cell.fill = data_fill
                    cell.border = thin_border

            # Ajustar el ancho de las columnas basándonos en los datos del DataFrame
            for col_num, column in enumerate(df.columns, 1):
                max_length = max(df[column].astype(str).apply(len).max(), len(column)) + 2
                ws.column_dimensions[get_column_letter(col_num)].width = max_length

            # Guardar el archivo Excel
            wb.save(file_path)

    def volver_a_opciones_programar(self):
        self.main_window.stacked_widget.setCurrentIndex(self.main_window.opciones_programar_index)