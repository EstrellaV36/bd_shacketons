from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QStackedWidget
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve

class GeneracionReportesScreen(QWidget):
    def __init__(self, main_window, stacked_widget):
        super().__init__()
        self.main_window = main_window
        self.stacked_widget = stacked_widget
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Botón "Volver" al menú principal
        button_volver = QPushButton("Volver")
        button_volver.setFixedWidth(100)
        button_volver.clicked.connect(lambda: self.main_window.stacked_widget.setCurrentIndex(0))
        layout.addWidget(button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        # Crear el botón para abrir el menú flotante
        self.button_toggle_menu = QPushButton("Menú")
        self.button_toggle_menu.setFixedWidth(100)
        self.button_toggle_menu.clicked.connect(self.toggle_menu)
        layout.addWidget(self.button_toggle_menu, alignment=Qt.AlignmentFlag.AlignRight)

        # Crear el menú flotante
        self.create_floating_menu()

        label = QLabel("Generación de reportes (contenido aquí)")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # Crear pantallas específicas para "Informar" y "Programar"
        self.informar_widget = self.create_generic_screen("Informar")
        self.programar_widget = self.create_generic_screen("Programar")

        # Añadir las pantallas al stacked_widget
        self.stacked_widget.addWidget(self.informar_widget)
        self.stacked_widget.addWidget(self.programar_widget)

        self.setLayout(layout)

    # Método para crear pantallas genéricas con el botón "Volver" y un título
    def create_generic_screen(self, title):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Añadir un botón "Volver" que lleva de vuelta a la pantalla de Generación de Reportes
        button_volver = QPushButton("Volver")
        button_volver.setFixedWidth(100)
        button_volver.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self))
        layout.addWidget(button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        # Añadir un botón "Menú" que abre el menú flotante
        button_toggle_menu = QPushButton("Menú")
        button_toggle_menu.setFixedWidth(100)
        button_toggle_menu.clicked.connect(self.toggle_menu)
        layout.addWidget(button_toggle_menu, alignment=Qt.AlignmentFlag.AlignRight)

        # Añadir el título centrado para la pantalla
        label = QLabel(title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        widget.setLayout(layout)
        return widget

    def create_floating_menu(self):
        # Crear el widget flotante
        self.menu_widget = QWidget(self.main_window)
        self.menu_widget.setGeometry(-250, 0, 250, self.main_window.height())
        self.menu_widget.setStyleSheet("background-color: rgba(0, 0, 0, 0.8); color: white;")

        # Crear un layout vertical para el menú
        menu_layout = QVBoxLayout()
        self.menu_widget.setLayout(menu_layout)

        # Agregar opciones al menú
        self.menu_list = QListWidget()
        self.menu_list.addItems(["Informar", "Programar"])
        self.menu_list.currentRowChanged.connect(self.change_tab)

        # Botón para cerrar el menú
        close_button = QPushButton("Cerrar Menú")
        close_button.clicked.connect(self.toggle_menu)

        # Agregar elementos al layout del menú
        menu_layout.addWidget(QLabel("Menú"))
        menu_layout.addWidget(self.menu_list)
        menu_layout.addWidget(close_button)

        # Inicialmente ocultar el menú
        self.menu_widget.hide()

    def toggle_menu(self):
        if self.menu_widget.isVisible():
            self.animation = QPropertyAnimation(self.menu_widget, b"geometry")
            self.animation.setDuration(500)
            self.animation.setStartValue(QRect(0, 0, 250, self.main_window.height()))
            self.animation.setEndValue(QRect(-250, 0, 250, self.main_window.height()))
            self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.animation.start()
            self.animation.finished.connect(lambda: self.menu_widget.hide())
        else:
            self.menu_widget.raise_()  # Asegurarse de que el menú esté al frente
            self.menu_widget.show()
            self.animation = QPropertyAnimation(self.menu_widget, b"geometry")
            self.animation.setDuration(500)
            self.animation.setStartValue(QRect(-250, 0, 250, self.main_window.height()))
            self.animation.setEndValue(QRect(0, 0, 250, self.main_window.height()))
            self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.animation.start()

    def close_menu(self):
        # Cierra el menú de forma inmediata, asegurando que quede completamente oculto
        self.menu_widget.setGeometry(-250, 0, 250, self.main_window.height())  # Ajustar la posición fuera de la pantalla
        self.menu_widget.hide()  # Asegurarse de ocultarlo sin animación

    def change_tab(self, index):
        # Cerrar el menú antes de realizar cualquier acción
        self.close_menu()

        if index == 0:  # Informar
            self.stacked_widget.setCurrentWidget(self.informar_widget)
        elif index == 1:  # Programar
            self.stacked_widget.setCurrentWidget(self.programar_widget)
