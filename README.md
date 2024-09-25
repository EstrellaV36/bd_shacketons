# BD_Shacketons

## Descripción

La aplicación de gestión de crew permite manejar los datos de los tripulantes y sus vuelos. Facilita la gestión de todos los servicios ofrecidos, incluyendo el transporte desde el aeropuerto a la ciudad, de la ciudad a la nave, así como opciones de restaurante y alojamiento.

## Carga de Datos inicial

Para cargar los datos inicialmente desde la terminal, se debe utilizar el siguiente comando:

```bash
$ pdm run python app/carga_datos.py proveedores.xlsx
```

## Ejecución de la aplicación

Para ejecutar la aplicación desde la terminal, utiliza el siguiente comando:

```bash
$ pdm run python main.py
```

## Estructura del proyecto

```plaintext
bd_shacketons/
│
├── app/
│   ├── carga_datos.py          # Script para cargar datos iniciales de proveedores
│   ├── controllers.py           # Controladores de la aplicación (Maneja procesamiento de datos y asignaciones)
│   ├── database.py              # Módulo de base de datos
│   ├── gui.py                   # Interfaz gráfica de usuario
│   ├── models.py                # Modelos de datos
│   ├── __init__.py              # Inicialización del paquete
│   ├── Plantilla_Pasajeros_Vuelos.xlsx # Plantilla de datos de tripulantes y vuelos
│   └── __pycache__/             # Caché de Python
│
├── main.py                      # Archivo principal de la aplicación
├── pdm.lock                     # Bloqueo de dependencias
├── pyproject.toml               # Configuración del proyecto
├── README.md                    # Documentación del proyecto
├── shacketons_db.sqlite3        # Base de datos SQLite
└── proveedores.xlsx             # Excel con datos iniciales de clientes y proveedores       
```
