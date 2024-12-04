from datetime import datetime
import pandas as pd
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QComboBox, QLabel, QTableView,
    QPushButton, QSizePolicy, QTabWidget, QHBoxLayout
)
from PyQt6.QtCore import Qt
from sqlalchemy.sql import func
from app.interfaz.pandas_model import PandasModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import case
from app.database import get_db_session
from app.models import Buque, EtaCiudad, Tripulante, Viaje, Vuelo, TripulanteVuelo, Restaurante, TripulanteRestaurante, Transporte, TripulanteTransporte, Hotel, TripulanteHotel, Buque, TripulanteAsistencia


class VisualizacionDatosScreen(QWidget):
    def __init__(self, controller, main_window):
        super().__init__()
        self.controller = controller
        self.main_window = main_window

        # Añadir esta pantalla al stacked_widget del main_window
        self.main_window.visualizacion_datos_index = self.main_window.stacked_widget.addWidget(self)

        self.setup_ui()

    def setup_ui(self):
        session = get_db_session()
        layout = QVBoxLayout(self)

        # Botón "Volver"
        self.button_volver = QPushButton("Volver")
        self.button_volver.setFixedWidth(100)
        self.button_volver.clicked.connect(self.volver_al_menu_principal)
        layout.addWidget(self.button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        # ComboBox para seleccionar la ciudad
        self.city_combo_box = QComboBox()
        self.city_combo_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.city_combo_box.addItem("Ciudad")
        ciudades = session.query(Buque.ciudad).distinct().all()  # Consulta para obtener las ciudades únicas
        for ciudad in ciudades:
            self.city_combo_box.addItem(ciudad.ciudad)
        layout.addWidget(self.city_combo_box)

        self.city_combo_box.currentIndexChanged.connect(self.load_existing_data)
        layout.addWidget(QLabel("Ciudad"))
        layout.addWidget(self.city_combo_box)

        self.buque_combo_box = QComboBox()
        self.buque_combo_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.buque_combo_box.addItem("Vessel")
        buques = session.query(Buque.nombre).distinct().all()  # Consulta para obtener los nombres de los buques
        for buque in buques:
            self.buque_combo_box.addItem(buque.nombre)
        layout.addWidget(self.buque_combo_box)

        self.buque_combo_box.currentIndexChanged.connect(self.load_existing_data)  # Conectar la señal
        layout.addWidget(QLabel("Vessel"))
        layout.addWidget(self.buque_combo_box)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.on_tab = QWidget()
        self.off_tab = QWidget()

        self.tabs.addTab(self.on_tab, "ON")
        self.tabs.addTab(self.off_tab, "OFF")

        self.on_layout = QHBoxLayout()
        self.off_layout = QHBoxLayout()
        self.on_tab.setLayout(self.on_layout)
        self.off_tab.setLayout(self.off_layout)

        self.on_table_view = QTableView()
        self.off_table_view = QTableView()
        self.on_layout.addWidget(self.on_table_view)
        self.off_layout.addWidget(self.off_table_view)

        self.setLayout(layout)

    def volver_al_menu_principal(self):
        """Vuelve al menú principal."""
        self.main_window.stacked_widget.setCurrentIndex(0)

    def load_existing_data(self):
        """Carga los datos de buques ON y OFF y los muestra en diferentes pestañas."""
        selected_buque = self.buque_combo_box.currentText()
        selected_city = self.city_combo_box.currentText()

        # Validar si hay un buque seleccionado y la ciudad no es el valor predeterminado
        if not selected_buque or selected_buque == "No hay buques disponibles":
            return
        if not selected_city or selected_city == "Ciudad":
            selected_city = None  # No aplicar filtro de ciudad si es el valor predeterminado

        try:
            session = get_db_session()

            # Construir consulta básica
            query = session.query(
                Buque.nombre.label("Vessel"),
                Viaje.estado.label("Estado"),
                Viaje.activo.label("Activo"),
                Buque.empresa.label("Owner"),
                case(
                    (Viaje.estado == "ON", EtaCiudad.date_arrive_cl),
                    (Viaje.estado == "OFF", EtaCiudad.date_first_flight)
                ).label("Fecha relevante"),
                EtaCiudad.eta.label("ETA Vessel"),
                EtaCiudad.etd.label("ETD Vessel"),
                EtaCiudad.ciudad.label("Puerto"),  
                Tripulante.nombre.label("First name"),
                Tripulante.apellido.label("Last name"),
                Tripulante.condicion.label("Condition")
            ).join(Viaje, Buque.buque_id == Viaje.buque_id) \
            .join(EtaCiudad, Viaje.eta_id == EtaCiudad.eta_id) \
            .join(Tripulante, Viaje.tripulante_id == Tripulante.tripulante_id) \
            .filter(func.lower(Buque.nombre) == func.lower(selected_buque.strip()))
            
            # Aplicar filtro de ciudad si está seleccionado
            if selected_city:
                query = query.filter(func.lower(EtaCiudad.ciudad) == func.lower(selected_city.strip()))

            # Ejecutar la consulta
            buque_data = query.all()

            # Dividir los datos en ON y OFF
            on_data = [row for row in buque_data if row.Estado == "ON"]
            off_data = [row for row in buque_data if row.Estado == "OFF"]

            # Mostrar datos en las pestañas
            self.show_data_in_tab(on_data, self.on_table_view, [
                "Activo", "Owner", "Vessel", "Date arrive CL", "ETA Vessel", "ETD Vessel",
                "Puerto", "Condition", "First name", "Last name"
            ], "Puerto a embarcar")
            self.show_data_in_tab(off_data, self.off_table_view, [
                "Activo", "Owner", "Vessel", "Date first flight", "ETA Vessel", "ETD Vessel",
                "Puerto", "Condition", "First name", "Last name"
            ], "Puerto a desembarcar")

        except SQLAlchemyError as e:
            print(f"Error al cargar datos: {e}")
        finally:
            session.close()


    def show_data_in_tab(self, data, table_view, headers, puerto_label):
        """Muestra los datos en un QTableView dentro de una pestaña."""
        if data:
            # Convertir la lista de resultados a un DataFrame
            formatted_data = []
            for row in data:
                formatted_row = {}
                for col in headers:
                    value = getattr(row, col, None)
                    # Formatear fecha para ETA y ETD
                    if col in ["ETA Vessel", "ETD Vessel"] and isinstance(value, datetime):
                        value = value.strftime('%Y-%m-%d')
                    # Convertir "Activo" a "SI" o "NO"
                    if col == "Activo":
                        value = "SI" if value else "NO"
                    formatted_row[col] = value
                formatted_data.append(formatted_row)

            df = pd.DataFrame(formatted_data, columns=headers)

            # Cambiar el encabezado de 'Puerto' dinámicamente
            df.rename(columns={"Puerto": puerto_label}, inplace=True)

            model = PandasModel(df)
            table_view.setModel(model)
            table_view.resizeColumnsToContents()
        else:
            # Mostrar tabla vacía
            empty_model = PandasModel(pd.DataFrame(columns=headers))
            table_view.setModel(empty_model)