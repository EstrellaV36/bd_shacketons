from PyQt6.QtWidgets import QSizePolicy

def setup_dynamic_button(button, width):
    """Configura el tamaño dinámico de los botones."""
    if not hasattr(button, "_dynamic_setup_done"):
        button.setMinimumWidth(200)  # Cambia el tamaño según sea necesario
        button.setMaximumWidth(300)
        button.setFixedHeight(60)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button._dynamic_setup_done = True

def setup_dynamic_button(button, width):
    """Configura el tamaño dinámico de los botones con un ancho proporcionado."""
    if not hasattr(button, "_dynamic_setup_done"):
        button.setMinimumWidth(int(width * 0.2))  # Usa el ancho proporcionado
        button.setMaximumWidth(300)
        button.setFixedHeight(60)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button._dynamic_setup_done = True
