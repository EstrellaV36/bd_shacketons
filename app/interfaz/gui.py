import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QStackedWidget, QVBoxLayout, QWidget, QLabel, QSizePolicy
from PyQt6.QtCore import Qt
from app.interfaz.carga_masiva import CargaMasivaScreen
from app.interfaz.visualizacion_datos import VisualizacionDatosScreen
from app.interfaz.generacion_reportes import GeneracionReportesScreen
from app.database import get_db_session
from app.controllers import Controller

class BasicApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión Crew Shacketon's Way")
        self.setGeometry(100, 100, 1200, 800)
        
        db_session = get_db_session()
        self.controller = Controller(db_session)

        # UI setup
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Create and add screens
        self.create_main_menu()

        # Create generic screens before other screens
        self.hotel_widget = self.create_generic_screen("Hotel")
        self.transporte_widget = self.create_generic_screen("Transporte")
        self.restaurant_widget = self.create_generic_screen("Restaurant")

        # Instantiate other screens
        self.carga_masiva_screen = CargaMasivaScreen(self.controller, self)
        self.visualizacion_datos_screen = VisualizacionDatosScreen(
            self.controller, self, self.carga_masiva_screen,
            self.hotel_widget, self.transporte_widget, self.restaurant_widget
        )
        self.generacion_reportes_screen = GeneracionReportesScreen(self)

        # Add screens to stacked_widget
        self.stacked_widget.addWidget(self.carga_masiva_screen)
        self.stacked_widget.addWidget(self.visualizacion_datos_screen)
        self.stacked_widget.addWidget(self.generacion_reportes_screen)

    def create_main_menu(self):
        main_menu_widget = QWidget()
        layout = QVBoxLayout(main_menu_widget)

        # Añadir un espacio arriba para centrar los botones verticalmente
        layout.addStretch()

        button_carga_masiva = QPushButton("Carga masiva")
        button_carga_masiva.setFixedWidth(200)
        button_carga_masiva.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        button_carga_masiva.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.carga_masiva_screen))
        layout.addWidget(button_carga_masiva, alignment=Qt.AlignmentFlag.AlignHCenter)

        button_visualizacion_datos = QPushButton("Visualización de los datos")
        button_visualizacion_datos.setFixedWidth(200)
        button_visualizacion_datos.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        button_visualizacion_datos.clicked.connect(self.open_visualizacion_datos)
        layout.addWidget(button_visualizacion_datos, alignment=Qt.AlignmentFlag.AlignHCenter)

        button_generacion_reportes = QPushButton("Generación de reportes")
        button_generacion_reportes.setFixedWidth(200)
        button_generacion_reportes.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        button_generacion_reportes.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.generacion_reportes_screen))
        layout.addWidget(button_generacion_reportes, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Añadir un espacio abajo para centrar los botones verticalmente
        layout.addStretch()

        self.stacked_widget.addWidget(main_menu_widget)

    # Método para crear pantallas genéricas con el botón "Volver"
    def create_generic_screen(self, title):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Añadir un botón "Volver" que lleva al menú principal
        button_volver = QPushButton("Volver")
        button_volver.setFixedWidth(100)
        button_volver.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        label = QLabel(title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.stacked_widget.addWidget(widget)
        return widget

    def open_visualizacion_datos(self):
        # Asegurarse de que el menú flotante esté completamente cerrado antes de ingresar a "Visualización de Datos"
        self.visualizacion_datos_screen.close_menu()  # Método para cerrar el menú flotante

        # Configura el índice actual a la categoría "Tripulante" y muestra la pantalla
        self.visualizacion_datos_screen.menu_list.setCurrentRow(0)
        self.visualizacion_datos_screen.change_tab(0)

        # Cambiar a la pantalla de visualización de datos
        self.stacked_widget.setCurrentWidget(self.visualizacion_datos_screen)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = BasicApp()
    main_window.show()
    sys.exit(app.exec())
