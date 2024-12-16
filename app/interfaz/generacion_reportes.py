from app.interfaz.programar.asistencias import AsistenciasScreen
from app.interfaz.programar.transportes import TransportesScreen
from app.interfaz.programar.roomlist import RoomListScreen
from app.interfaz.programar.hoteles import HotelScreen
from app.interfaz.programar.alimentos import AlimentosScreen
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from app.interfaz.utils import setup_dynamic_button


class GeneracionReportesScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.main_window.generacion_reportes_index = self.main_window.stacked_widget.addWidget(self)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Añadir un botón "Volver" al menú principal
        self.button_volver = QPushButton("Volver")
        self.button_volver.setStyleSheet("""
            font-size: 16px;  /* Tamaño de la letra */
            padding: 0px;    /* Elimina el espacio interno */
            line-height: 18px; /* Asegura que el texto no se corte verticalmente */
            text-align: center; /* Centra el texto */
        """)
        self.button_volver.setFixedWidth(80)
        self.button_volver.setFixedHeight(40)
        self.button_volver.clicked.connect(self.volver_al_menu_principal)
        layout.addWidget(self.button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        # Añadir título al inicio
        title_label = QLabel("Generación de reportes")
        title_label.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
            color: #00272d;
            margin-bottom: 1px; /* Espacio debajo del título */
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Layout para botones principales
        layout_botones = QHBoxLayout()
        layout_botones.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Botones de opciones
        botones = [
            {"texto": "Informar", "callback": self.dummy_action},
            {"texto": "Programar", "callback": self.mostrar_opciones_programar},
            {"texto": "Liquidar", "callback": self.dummy_action},
            {"texto": "Cuadrar Proveedor", "callback": self.dummy_action},
        ]

        for boton_info in botones:
            boton = QPushButton(boton_info["texto"])
            setup_dynamic_button(boton, self.width())
            boton.clicked.connect(boton_info["callback"])
            layout_botones.addWidget(boton)

        layout.addLayout(layout_botones)

    def dummy_action(self):
        print("Botón presionado!!!!")

    def mostrar_opciones_programar(self):
        opciones_programar_screen = OpcionesProgramarScreen(self.main_window)
        self.main_window.opciones_programar_index = self.main_window.stacked_widget.addWidget(opciones_programar_screen)
        self.main_window.stacked_widget.setCurrentWidget(opciones_programar_screen)

    def volver_al_menu_principal(self):
        self.main_window.stacked_widget.setCurrentIndex(0)  # Regresar al menú principal

class OpcionesProgramarScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
        self.menu_reportes_index = main_window.stacked_widget.addWidget(self)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Botón "Volver" para regresar a la pantalla anterior (Generación de Reportes)
        button_volver = QPushButton("Volver")
        button_volver.setStyleSheet("""
            font-size: 16px;  /* Tamaño de la letra */
            padding: 0px;    /* Elimina el espacio interno */
            line-height: 18px; /* Asegura que el texto no se corte verticalmente */
            text-align: center; /* Centra el texto */
        """)
        button_volver.setFixedWidth(80)
        button_volver.setFixedHeight(40)
        button_volver.clicked.connect(self.volver_a_reportes)
        layout.addWidget(button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        layout_botones = QHBoxLayout()
        layout_botones.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Añadir título al inicio
        title_label = QLabel("Opciones programar")
        title_label.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
            color: #00272d;
            margin-bottom: 1px; /* Espacio debajo del título */
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        # Lista de botones con texto y callbacks
        botones = [
            {"texto": "Asistencias", "callback": self.mostrar_asistencias},
            {"texto": "Req. transportes", "callback": self.mostrar_transportes},
            {"texto": "Room List", "callback": self.mostrar_room_list},
            {"texto": "Req. Hoteles", "callback": self.mostrar_req_hoteles},
            {"texto": "Solicitud SS Alimentación", "callback": self.mostrar_solicitud_alimentacion},
        ]

        for boton_info in botones:
            button = QPushButton(boton_info["texto"])
            setup_dynamic_button(button, self.width())
            button.clicked.connect(boton_info["callback"])
            layout_botones.addWidget(button)

        # Añadir el layout de botones al layout principal
        layout.addLayout(layout_botones)

    def mostrar_asistencias(self):
        print("Asistencias!!")
        asistencias_screen = AsistenciasScreen(self.main_window)
        asistencias_screen.opciones_programar_index = self.main_window.opciones_programar_index
        self.main_window.stacked_widget.addWidget(asistencias_screen)
        self.main_window.stacked_widget.setCurrentWidget(asistencias_screen)

    def mostrar_transportes(self):
        transportes_screen = TransportesScreen(self.main_window)
        self.main_window.stacked_widget.addWidget(transportes_screen)
        self.main_window.stacked_widget.setCurrentWidget(transportes_screen)

    def mostrar_room_list(self):
        room_list_screen = RoomListScreen(self.main_window)
        self.main_window.stacked_widget.addWidget(room_list_screen)
        self.main_window.stacked_widget.setCurrentWidget(room_list_screen)

    def mostrar_req_hoteles(self):
        hotel_screen = HotelScreen(self.main_window)
        self.main_window.stacked_widget.addWidget(hotel_screen)
        self.main_window.stacked_widget.setCurrentWidget(hotel_screen)

    def mostrar_solicitud_alimentacion(self):
        alimentos_screen = AlimentosScreen(self.main_window)
        self.main_window.stacked_widget.addWidget(alimentos_screen)
        self.main_window.stacked_widget.setCurrentWidget(alimentos_screen)

    def volver_a_reportes(self):
        #print(f"Regresando a GeneracionReportesScreen con índice {self.main_window.generacion_reportes_index}")
        self.main_window.stacked_widget.setCurrentIndex(self.main_window.generacion_reportes_index)