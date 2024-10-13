import pandas as pd
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QFileDialog
from PyQt6.QtCore import Qt
from app.database import get_db_session
from app.models import Buque, EtaCiudad, Tripulante, Vuelo, TripulanteVuelo # Asegúrate de que estos modelos se importen correctamente
from app.controllers import CITY_AIRPORT_CODES
from sqlalchemy import func


class GeneracionReportesScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Añadir un botón "Volver" al menú principal
        self.button_volver = QPushButton("Volver")
        self.button_volver.setFixedWidth(100)
        self.button_volver.clicked.connect(self.volver_al_menu_principal)
        layout.addWidget(self.button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        # Crear un layout horizontal para los botones
        layout_botones = QHBoxLayout()
        layout_botones.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Botones
        button_informar = QPushButton("Informar")
        button_informar.setFixedSize(120, 40)
        layout_botones.addWidget(button_informar)

        button_programar = QPushButton("Programar")
        button_programar.setFixedSize(120, 40)
        button_programar.clicked.connect(self.mostrar_asistencias)
        layout_botones.addWidget(button_programar)

        button_liquidar = QPushButton("Liquidar")
        button_liquidar.setFixedSize(120, 40)
        layout_botones.addWidget(button_liquidar)

        button_cuadrar_proveedor = QPushButton("Cuadrar Proveedor")
        button_cuadrar_proveedor.setFixedSize(120, 40)
        layout_botones.addWidget(button_cuadrar_proveedor)

        # Añadir el layout de botones al layout principal
        layout.addLayout(layout_botones)

    def mostrar_asistencias(self):
        asistencias_screen = AsistenciasScreen(self.main_window)
        self.main_window.stacked_widget.addWidget(asistencias_screen)
        self.main_window.stacked_widget.setCurrentWidget(asistencias_screen)

    def volver_al_menu_principal(self):
        self.main_window.stacked_widget.setCurrentIndex(0)  # Regresar al menú principal

class AsistenciasScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Cuadro de selección de ciudad dentro de AsistenciasScreen
        self.combo_ciudades = QComboBox()
        self.combo_ciudades.addItems(["SCL", "PUQ", "WPU"])  # Agrega las ciudades al combo box
        layout.addWidget(self.combo_ciudades)

        # Label para mostrar asistencias
        self.label = QLabel()  # Mover el label aquí para que sea un atributo de la clase
        layout.addWidget(self.label)

        # Tabla para mostrar datos
        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        # Botón para generar el Excel
        button_generar_excel = QPushButton("Generar Excel")
        button_generar_excel.clicked.connect(self.generar_excel_con_ciudad)  # Conectar al método de generación de Excel
        layout.addWidget(button_generar_excel)

        # Botón "Volver" para regresar a la pantalla anterior (Generación de Reportes)
        button_volver = QPushButton("Volver")
        button_volver.setFixedWidth(100)
        button_volver.clicked.connect(self.volver_a_reportes)
        layout.addWidget(button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        # Conectar el cambio en el QComboBox a un método
        self.combo_ciudades.currentTextChanged.connect(self.actualizar_datos)

        # Actualizar datos inicialmente
        self.actualizar_datos()
        
    def generar_excel_con_ciudad(self):
        ciudad_seleccionada = self.combo_ciudades.currentText()  # Obtener la ciudad seleccionada
        self.generar_excel(ciudad_seleccionada)  # Llamar a generar_excel con la ciudad seleccionada

    def actualizar_datos(self):
        ciudad_seleccionada = self.combo_ciudades.currentText()  # Obtiene la ciudad seleccionada
        self.label.setText(f"Asistencias en {ciudad_seleccionada}")  # Actualiza el label

        # Cargar datos en la tabla
        self.cargar_datos(ciudad_seleccionada)

    def cargar_datos(self, ciudad_seleccionada):
        session = get_db_session()  # Obtener la sesión de la base de datos

        # Obtener el nombre de la ciudad a partir del código
        ciudad_seleccionada = CITY_AIRPORT_CODES.get(ciudad_seleccionada).lower()  # Convertir a minúsculas

        # Obtener datos de vuelos de arribo
        arribo_vuelos = (
            session.query(
                Buque.nombre.label("Vessel"),
                Vuelo.aeropuerto_llegada.label("Aeropuerto_Llegada"),
                EtaCiudad.eta.label("ETA"),  
                Vuelo.hora_llegada.label("Hora_Arribo"),
                Tripulante.nombre.label("First_Name"),
                Tripulante.apellido.label("Last_Name"),
                Tripulante.estado.label("Type"),
                Vuelo.codigo.label("Nro_Vuelo_Arribo"),
                Vuelo.fecha.label("Fecha_Vuelo_Arribo")  # Asegúrate de que este campo exista
            )
            .outerjoin(TripulanteVuelo, TripulanteVuelo.tripulante_id == Tripulante.tripulante_id)
            .outerjoin(Vuelo, TripulanteVuelo.vuelo_id == Vuelo.vuelo_id)
            .outerjoin(Buque, Tripulante.buque_id == Buque.buque_id) 
            .outerjoin(EtaCiudad, Buque.buque_id == EtaCiudad.buque_id)  # Asegúrate de que Buque tenga un buque_id
            .filter(func.lower(Vuelo.aeropuerto_llegada) == ciudad_seleccionada)  
            .all()
        )
        # Obtener datos de vuelos de salida
        salida_vuelos = (
            session.query(
                Buque.nombre.label("Vessel"),
                Vuelo.aeropuerto_salida.label("Aeropuerto Salida"),
                EtaCiudad.eta.label("ETA"),  
                Vuelo.hora_salida.label("Hora_Salida"),
                Tripulante.nombre.label("First_Name"),
                Tripulante.apellido.label("Last_Name"),
                Tripulante.estado.label("Type"),
                Vuelo.codigo.label("Nro_Vuelo_Salida"),
                Vuelo.fecha.label("Fecha_Vuelo_Salida")  # Asegúrate de que este campo exista

            )
            .outerjoin(TripulanteVuelo, TripulanteVuelo.tripulante_id == Tripulante.tripulante_id)
            .outerjoin(Vuelo, TripulanteVuelo.vuelo_id == Vuelo.vuelo_id)
            .outerjoin(Buque, Tripulante.buque_id == Buque.buque_id)  # Ajuste aquí
            .outerjoin(EtaCiudad, Buque.buque_id == EtaCiudad.buque_id)  # Asegúrate de que Buque tenga un buque_id
            .filter(func.lower(Vuelo.aeropuerto_salida) == ciudad_seleccionada)  
            .all()
        )
        # Limpiar la tabla
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(11)  # Número de columnas
        self.table_widget.setHorizontalHeaderLabels(
            ["Vessel", "ETA", "First Name", "Last Name", "Type",
            "Nro Vuelo Arribo", "Fecha Vuelo Arribo", "Hora Arribo",
            "Nro Vuelo Salida", "Fecha Vuelo Salida", "Hora Vuelo Salida"]
        )

        # Combinar y llenar la tabla
        for arribo in arribo_vuelos:
            # Buscar un vuelo de salida correspondiente
            salida = next((s for s in salida_vuelos if s.First_Name == arribo.First_Name and s.Last_Name == arribo.Last_Name), None)

            self.table_widget.insertRow(self.table_widget.rowCount())
            self.table_widget.setItem(self.table_widget.rowCount() - 1, 0, QTableWidgetItem(str(arribo.Vessel)))
            self.table_widget.setItem(self.table_widget.rowCount() - 1, 1, QTableWidgetItem(str(arribo.ETA)))  # Usar la fecha de recalada
            self.table_widget.setItem(self.table_widget.rowCount() - 1, 2, QTableWidgetItem(str(arribo.First_Name)))
            self.table_widget.setItem(self.table_widget.rowCount() - 1, 3, QTableWidgetItem(str(arribo.Last_Name)))
            self.table_widget.setItem(self.table_widget.rowCount() - 1, 4, QTableWidgetItem(str(arribo.Type)))
            self.table_widget.setItem(self.table_widget.rowCount() - 1, 5, QTableWidgetItem(str(arribo.Nro_Vuelo_Arribo)))
            self.table_widget.setItem(self.table_widget.rowCount() - 1, 6, QTableWidgetItem(str(arribo.Fecha_Vuelo_Arribo)))
            self.table_widget.setItem(self.table_widget.rowCount() - 1, 7, QTableWidgetItem(str(arribo.Hora_Arribo)))

            # Si hay un vuelo de salida, añadirlo a la fila
            if salida:
                self.table_widget.setItem(self.table_widget.rowCount() - 1, 8, QTableWidgetItem(str(salida.Nro_Vuelo_Salida)))
                self.table_widget.setItem(self.table_widget.rowCount() - 1, 9, QTableWidgetItem(str(salida.Fecha_Vuelo_Salida)))
                self.table_widget.setItem(self.table_widget.rowCount() - 1, 10, QTableWidgetItem(str(salida.Hora_Salida)))
            else:
                # Dejar los campos vacíos si no hay vuelo de salida
                self.table_widget.setItem(self.table_widget.rowCount() - 1, 8, QTableWidgetItem(""))
                self.table_widget.setItem(self.table_widget.rowCount() - 1, 9, QTableWidgetItem(""))
                self.table_widget.setItem(self.table_widget.rowCount() - 1, 10, QTableWidgetItem(""))

        # También puedes agregar los vuelos de salida si no están en arribo
        for salida in salida_vuelos:
            # Si no se ha agregado un vuelo de arribo correspondiente
            if not any(arr.First_Name == salida.First_Name and arr.Last_Name == salida.Last_Name for arr in arribo_vuelos):
                self.table_widget.insertRow(self.table_widget.rowCount())
                self.table_widget.setItem(self.table_widget.rowCount() - 1, 0, QTableWidgetItem(str(salida.Vessel)))
                self.table_widget.setItem(self.table_widget.rowCount() - 1, 1, QTableWidgetItem(""))  # No hay ETA aquí
                self.table_widget.setItem(self.table_widget.rowCount() - 1, 2, QTableWidgetItem(str(salida.First_Name)))
                self.table_widget.setItem(self.table_widget.rowCount() - 1, 3, QTableWidgetItem(str(salida.Last_Name)))
                self.table_widget.setItem(self.table_widget.rowCount() - 1, 4, QTableWidgetItem(str(salida.Type)))
                self.table_widget.setItem(self.table_widget.rowCount() - 1, 5, QTableWidgetItem(""))
                self.table_widget.setItem(self.table_widget.rowCount() - 1, 6, QTableWidgetItem(""))
                self.table_widget.setItem(self.table_widget.rowCount() - 1, 7, QTableWidgetItem(""))
                self.table_widget.setItem(self.table_widget.rowCount() - 1, 8, QTableWidgetItem(str(salida.Nro_Vuelo_Salida)))
                self.table_widget.setItem(self.table_widget.rowCount() - 1, 9, QTableWidgetItem(str(salida.Fecha_Vuelo_Salida)))
                self.table_widget.setItem(self.table_widget.rowCount() - 1, 10, QTableWidgetItem(str(salida.Hora_Salida)))


    def generar_excel(self, ciudad_seleccionada):
        # Crear un DataFrame con los datos de la tabla
        data = []
        for row in range(self.table_widget.rowCount()):
            row_data = []
            for column in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, column)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        # Definir los nombres de las columnas
        column_names = [
            "Vessel", "ETA", "First Name", "Last Name", "Type",
            "Nro Vuelo Arribo", "Fecha Vuelo Arribo", "Hora Arribo",
            "Nro Vuelo Salida", "Fecha Vuelo Salida", "Hora Vuelo Salida"
        ]

        # Convertir a DataFrame
        df = pd.DataFrame(data, columns=column_names)

        # Construir el nombre del archivo Excel
        file_name = f'asistencia_{ciudad_seleccionada}.xlsx'
        
        # Guardar en un archivo Excel
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Guardar archivo Excel", 
            file_name,  # Usar el nombre del archivo predefinido
            "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if file_path:
            df.to_excel(file_path, index=False)

    def volver_a_reportes(self):
        self.main_window.stacked_widget.setCurrentIndex(self.main_window.stacked_widget.currentIndex() - 1)