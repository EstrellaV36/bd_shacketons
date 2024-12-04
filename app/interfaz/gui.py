import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QStackedWidget, QVBoxLayout, QWidget, QLabel, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from app.interfaz.carga_masiva import CargaMasivaScreen
from app.interfaz.visualizacion_datos import VisualizacionDatosScreen
from app.interfaz.generacion_reportes import GeneracionReportesScreen
from app.database import get_db_session
from app.controller.controllers import Controller
from app.interfaz.utils import setup_dynamic_button


class BasicApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión Tripulantes Shacketon's Way")
        self.setGeometry(100, 100, 1200, 800)

        db_session = get_db_session()
        self.controller = Controller(db_session)

        # Configurar estilos globales antes de crear los widgets
        self.set_global_styles()
        # UI setup
        self.setup_ui()

    def set_global_styles(self):
        """Configura estilos globales para la aplicación."""
        dark_blue = "#00272d"  # Color inicial del botón
        button_hover_color = "#134647"  # Color del botón al pasar el ratón
        border_color = "#bfac8b"  # Color del borde del botón
        text_color_hover = "white"  # Color del texto al pasar el ratón

        app_stylesheet = f"""
            QPushButton {{
                    background-color: white;
                    color: #00272d;
                    font-size: 18px;
                    font-weight: bold;
                    border: 2px solid {border_color};
                    border-radius: 5px;
                    padding: 15px;
                    text-align: center;
                    outline: none; /* Elimina el contorno por defecto */
            }}
            QPushButton:hover {{
                background-color: {button_hover_color}; /* Color al pasar el ratón */
                color: {text_color_hover}; /* Cambiar texto al pasar el ratón */
            }}
            QPushButton:pressed {{
                background-color: #0c7e7e; /* Color al presionar */
            }}
            QLabel {{
                font-family: Arial, sans-serif;
                color: #00272d; /* Color de texto de las etiquetas */
            }}
            QWidget {{
                background-color: white; /* Fondo blanco para todas las pantallas */
            }}
            QTabWidget::pane {{
            border: 2px solid #00272d; /* Borde alrededor del contenido */
            border-radius: 5px; /* Bordes redondeados */
            background-color: #ffffff; /* Fondo del área del contenido */
            }}
            QTabBar::tab {{
                background: white; /* Fondo de las pestañas */
                color: #00272d; /* Color del texto */
                border: 1px solid #00272d; /* Borde */
                border-top-left-radius: 5px; /* Bordes redondeados superior izquierdo */
                border-top-right-radius: 5px; /* Bordes redondeados superior derecho */
                padding: 10px; /* Espaciado dentro de las pestañas */
                font-size: 14px;
                font-weight: bold;
                min-width: 100px; /* Ancho mínimo de las pestañas */
            }}
            QTabBar::tab:selected {{
                background: #0c7e7e; /* Fondo de la pestaña seleccionada */
                color: white; /* Color del texto de la pestaña seleccionada */
                font-size: 15px;
                font-weight: bold;
            }}
            QTabBar::tab:hover {{
                background: #0b5e5e; /* Fondo al pasar el ratón */
                color: white; /* Color del texto al pasar el ratón */
            }}
            QComboBox {{
                background-color: white; /* Fondo del combo box */
                color: #00272d; /* Color del texto */
                font-size: 15px; /* Tamaño de fuente */
                font-weight: bold; /* Negrita */
                border: 2px solid {border_color}; /* Borde */
                border-radius: 5px; /* Bordes redondeados */
                padding: 5px; /* Espaciado interno */
            }}
            QComboBox::drop-down {{
                border-left: 0.5px solid {border_color}; /* Línea entre el texto y el botón de desplegable */
                width: 30px; /* Ancho del botón de desplegable */
                background-color: {border_color}; /* Fondo del botón desplegable */
            }}
            QComboBox::down-arrow {{
                width: 10px;
                height: 10px;
            }}
            QComboBox:hover {{
                background-color: #f0f0f0; /* Color al pasar el ratón */
                color: #00272d; /* Color del texto */
            }}
            QCheckBox {{
                font-size: 16px;
                color: #00272d;
                font-weight: bold;
                spacing: 5px; /* Espaciado entre el texto y la casilla */
                padding: 5px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 1px solid #00272d;
                border-radius: 3px;
                background: white;
            }}
            QCheckBox::indicator:checked {{
                background: #0c7e7e;
                border: 1px solid #00272d;
            }}
            QCheckBox::indicator:hover {{
                background: #0c7e7e;
            }}
            QDateEdit {{
                background-color: white;
                color: #00272d;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid {border_color};
                border-radius: 5px;
                padding: 5px;
            }}
            QDateEdit::drop-down {{
                border-left: 0.5px solid {border_color}; /* Línea entre el texto y el botón de desplegable */
                width: 30px;
                background-color: {border_color}; /* Fondo del botón desplegable */
            }}
            QTableWidget {{
                background-color: white;
                gridline-color: #00272d;
                font-size: 16px;
                border: 2px solid #00272d;
                border-radius: 5px;
            }}
            QHeaderView::section {{
                background-color: #0c7e7e;
                color: white;
                padding: 5px;
                font-size: 15px;
                font-weight: bold;
                border: 0.5px solid #134647;
            }}
            QTableWidget::item {{
                padding: 5px;
                font-size: 16px;
                border: 0.5px solid #134647;
            }}
        """
        
        self.setStyleSheet(app_stylesheet)
        self.repaint()  # Forzar renderizado de todos los elementos de la ventana

    def setup_ui(self):
        """Configura la interfaz principal de la aplicación."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        self.main_menu_widget = self.create_main_menu()
        self.main_menu_index = self.stacked_widget.addWidget(self.main_menu_widget)

        # Instanciar y agregar otras pantallas
        self.carga_masiva_screen = CargaMasivaScreen(self.controller, self)
        self.carga_masiva_index = self.stacked_widget.addWidget(self.carga_masiva_screen)
        
        self.visualizacion_datos_screen = VisualizacionDatosScreen(self.controller, self)
        self.visualizacion_datos_index = self.stacked_widget.addWidget(self.visualizacion_datos_screen)

        self.generacion_reportes_screen = GeneracionReportesScreen(self)
        self.menu_reportes_index = self.stacked_widget.addWidget(self.generacion_reportes_screen)

    def create_main_menu(self):
        """Crea el menú principal de la aplicación."""
        main_menu_widget = QWidget()
        layout = QVBoxLayout(main_menu_widget)

        # Añadir logo al inicio
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = "logo_shack.jpeg"  # Ruta al logo
        logo_label.setPixmap(QPixmap(logo_path).scaled(220, 220, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(logo_label)

        # Añadir título al inicio
        title_label = QLabel("GESTRIP")
        title_label.setStyleSheet("""
            font-size: 52px;
            font-weight: bold;
            color: #00272d;
            margin-bottom: 30px;
            text-align: center;
        """
        )

        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Añadir un espacio arriba para centrar los botones verticalmente
        layout.addStretch()

        # Botón Carga Masiva
        button_carga_masiva = QPushButton("Carga masiva")
        setup_dynamic_button(button_carga_masiva, self.width())
        button_carga_masiva.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.carga_masiva_screen))
        layout.addWidget(button_carga_masiva, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Botón Visualización de los datos
        button_visualizacion_datos = QPushButton("Visualización de datos")
        setup_dynamic_button(button_visualizacion_datos, self.width())
        button_visualizacion_datos.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.visualizacion_datos_screen))
        layout.addWidget(button_visualizacion_datos, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Botón Generación de Reportes
        button_generacion_reportes = QPushButton("Generación de reportes")
        setup_dynamic_button(button_generacion_reportes, self.width())
        button_generacion_reportes.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.generacion_reportes_screen))
        layout.addWidget(button_generacion_reportes, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Añadir un espacio abajo para centrar los botones verticalmente
        layout.addStretch()

        return main_menu_widget