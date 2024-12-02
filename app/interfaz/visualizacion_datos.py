import pandas as pd
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QComboBox, QLabel, QTableView,
    QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt
from app.interfaz.pandas_model import PandasModel
from sqlalchemy.exc import SQLAlchemyError
from app.database import get_db_session
from app.models import Buque, EtaCiudad, Tripulante, Vuelo, TripulanteVuelo, Restaurante, TripulanteRestaurante, Transporte, TripulanteTransporte, Hotel, TripulanteHotel, Buque, TripulanteAsistencia


class VisualizacionDatosScreen(QWidget):
    def __init__(self, controller, main_window):
        super().__init__()
        self.controller = controller
        self.main_window = main_window

        # Añadir esta pantalla al stacked_widget del main_window
        self.main_window.visualizacion_datos_index = self.main_window.stacked_widget.addWidget(self)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Botón "Volver"
        self.button_volver = QPushButton("Volver")
        self.button_volver.setFixedWidth(100)
        self.button_volver.clicked.connect(self.volver_al_menu_principal)
        layout.addWidget(self.button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        # ComboBox para seleccionar la ciudad
        self.city_combo_box = QComboBox()
        self.city_combo_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.city_combo_box.addItems(self.controller.get_city_list())
        self.city_combo_box.currentIndexChanged.connect(self.load_existing_data)
        
        # ComboBox para seleccionar el buque
        self.buque_combo_box = QComboBox()
        self.buque_combo_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.load_buques()  # Llenar los buques en el combo box
        layout.addWidget(QLabel("Vessel"))
        layout.addWidget(self.buque_combo_box)

        # Tabla para mostrar los datos
        self.visualizacion_table_view = QTableView()
        layout.addWidget(self.visualizacion_table_view)

        # Establecer el diseño principal
        self.setLayout(layout)

    def load_buques(self):
        try:
            session = get_db_session()  # Invoca la función para obtener la sesión correctamente
            buques = session.query(Buque.nombre).all()
            if buques:
                self.buque_combo_box.addItems([buque[0] for buque in buques])  # Agregar los nombres al combo box
            else:
                self.buque_combo_box.addItem("No hay buques disponibles")
        except SQLAlchemyError as e:
            print(f"Error al obtener los buques: {e}")
            self.buque_combo_box.addItem("Error al cargar buques")
        finally:
            session.close()

    def volver_al_menu_principal(self):
        """Vuelve al menú principal."""
        self.main_window.stacked_widget.setCurrentIndex(0)

    def load_existing_data(self):
        """Carga datos basados en la ciudad seleccionada."""
        selected_city = self.city_combo_box.currentText()
        if not selected_city:
            return

        # Obtener datos desde el controlador
        data = self.controller.get_data_by_city(selected_city)
        if data is not None and not data.empty:
            # Cargar datos en la tabla
            model = PandasModel(data)
            self.visualizacion_table_view.setModel(model)
        else:
            # Mostrar un mensaje si no hay datos
            empty_model = PandasModel(pd.DataFrame(columns=["Sin datos disponibles"]))
            self.visualizacion_table_view.setModel(empty_model)