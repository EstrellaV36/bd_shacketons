import pandas as pd

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel, QTableView, QDateEdit, QPushButton, QSizePolicy, QListWidget
from PyQt6.QtCore import Qt, QDate, QPropertyAnimation, QRect, QEasingCurve, QEvent
from app.interfaz.pandas_model import PandasModel

class VisualizacionDatosScreen(QWidget):
    def __init__(self, controller, main_window, cargamasiva, hotel_widget, transporte_widget, restaurant_widget):
        super().__init__()
        self.controller = controller
        self.cargamasiva = cargamasiva
        self.main_window = main_window
        self.hotel_widget = hotel_widget
        self.transporte_widget = transporte_widget
        self.restaurant_widget = restaurant_widget
        self.setup_ui()

        # Instalar el filtro de eventos para detectar clics fuera del menú
        self.installEventFilter(self)
        self.city_combo_box.installEventFilter(self)
        self.start_date_edit.installEventFilter(self)
        self.end_date_edit.installEventFilter(self)
        self.visualizacion_table_view.installEventFilter(self)
        self.visualizacion_table_view.viewport().installEventFilter(self)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Añadir un botón "Volver" al menú principal
        self.button_volver = QPushButton("Volver")
        self.button_volver.setFixedWidth(100)
        self.button_volver.clicked.connect(self.volver_al_menu_principal)
        layout.addWidget(self.button_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        # Crear el botón para abrir el menú flotante
        self.button_toggle_menu = QPushButton("Menú")
        self.button_toggle_menu.setFixedWidth(100)
        self.button_toggle_menu.clicked.connect(self.toggle_menu)
        layout.addWidget(self.button_toggle_menu, alignment=Qt.AlignmentFlag.AlignRight)

        # Crear menú flotante
        self.create_floating_menu()

        # Crear los controles adicionales (ciudad, fechas, tabla)
        self.city_combo_box = QComboBox()
        self.city_combo_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.city_combo_box.addItems(self.controller.get_city_list())
        self.city_combo_box.currentIndexChanged.connect(self.reload_data_on_date_change)
        layout.addWidget(QLabel("Seleccionar ciudad"))
        layout.addWidget(self.city_combo_box)

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1))
        self.start_date_edit.dateChanged.connect(self.reload_data_on_date_change)
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.dateChanged.connect(self.reload_data_on_date_change)

        layout.addWidget(QLabel("Fecha inicio"))
        layout.addWidget(self.start_date_edit)
        layout.addWidget(QLabel("Fecha fin"))
        layout.addWidget(self.end_date_edit)

        self.visualizacion_table_view = QTableView()
        layout.addWidget(self.visualizacion_table_view)

        self.setLayout(layout)

    def create_floating_menu(self):
        # Crear el widget flotante
        self.menu_widget = QWidget(self)
        self.menu_widget.setGeometry(-250, 0, 250, self.height())
        self.menu_widget.setStyleSheet("background-color: rgba(0, 0, 0, 0.8); color: white;")

        # Crear un layout vertical para el menú
        menu_layout = QVBoxLayout()
        self.menu_widget.setLayout(menu_layout)

        # Agregar opciones al menú
        self.menu_list = QListWidget()
        self.menu_list.addItems(["Tripulante", "Hotel", "Transporte", "Restaurant"])
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
            self.animation.setStartValue(QRect(0, 0, 250, self.height()))
            self.animation.setEndValue(QRect(-250, 0, 250, self.height()))
            self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.animation.start()
            self.animation.finished.connect(lambda: self.menu_widget.hide())
        else:
            self.menu_widget.raise_()  # Asegurarse de que el menú esté al frente
            self.menu_widget.show()
            self.animation = QPropertyAnimation(self.menu_widget, b"geometry")
            self.animation.setDuration(500)
            self.animation.setStartValue(QRect(-250, 0, 250, self.height()))
            self.animation.setEndValue(QRect(0, 0, 250, self.height()))
            self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.animation.start()

    def close_menu(self):
        # Cierra el menú de forma inmediata, asegurando que quede completamente oculto
        self.menu_widget.setGeometry(-250, 0, 250, self.height())  # Ajustar la posición fuera de la pantalla
        self.menu_widget.hide()  # Asegurarse de ocultarlo sin animación

    def volver_al_menu_principal(self):
        # Asegurarse de que el menú esté cerrado antes de volver al menú principal
        self.close_menu()

        # Cambiar al menú principal
        self.main_window.stacked_widget.setCurrentIndex(0)

    def change_tab(self, index):
        # Cambiar la pantalla según la selección del menú
        self.close_menu()  # Asegurarse de cerrar el menú al cambiar de categoría

        if index == 0:  # Tripulante
            self.reload_data_on_date_change()  # Recargar datos de Tripulante
        elif index == 1:  # Hotel
            self.main_window.stacked_widget.setCurrentWidget(self.hotel_widget)
        elif index == 2:  # Transporte
            self.main_window.stacked_widget.setCurrentWidget(self.transporte_widget)
        elif index == 3:  # Restaurant
            self.main_window.stacked_widget.setCurrentWidget(self.restaurant_widget)

    def eventFilter(self, obj, event):
        # Detectar clic fuera del menú flotante para cerrarlo
        if event.type() == QEvent.Type.MouseButtonPress and self.menu_widget.isVisible():
            global_pos = event.globalPosition().toPoint()  # Obtén la posición global del clic
            # Verificar si el clic ocurrió fuera del área del menú
            if not self.menu_widget.rect().translated(self.menu_widget.mapToGlobal(self.menu_widget.rect().topLeft())).contains(global_pos):
                # Si se hace clic en cualquier lugar fuera del menú, incluyendo el QTableView
                self.toggle_menu()  # Cierra el menú si el clic fue fuera del área del menú

        return super().eventFilter(obj, event)

    def reload_data_on_date_change(self):
        self.load_existing_data()

    def load_existing_data(self):
        selected_city = self.city_combo_box.currentText()
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")

        eta_vuelo_df_on, eta_vuelo_df_off = self.controller.load_existing_data(selected_city, start_date, end_date)

        if eta_vuelo_df_on is not None and not eta_vuelo_df_on.empty:
            self.cargamasiva.show_sheet(eta_vuelo_df_on, self.visualizacion_table_view)

        if eta_vuelo_df_off is not None and not eta_vuelo_df_off.empty:
            df_combined = pd.concat([eta_vuelo_df_on, eta_vuelo_df_off])
            self.cargamasiva.show_sheet(df_combined, self.visualizacion_table_view)
