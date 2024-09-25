from sqlalchemy.orm import sessionmaker
from database import engine, SessionLocal
from models import Hotel, Tripulante, Buque

# Crear una sesión para interactuar con la base de datos
Session = sessionmaker(bind=engine)
session = Session()

def consultar_hoteles():
    """Consulta y muestra todos los hoteles en la base de datos."""
    try:
        hoteles = session.query(Hotel).all()
        if hoteles:
            print("Lista de Hoteles en la base de datos:")
            for hotel in hoteles:
                print(f"ID: {hotel.hotel_id}, Nombre: {hotel.nombre}, Ciudad: {hotel.ciudad}")
        else:
            print("No hay hoteles en la base de datos.")
    except Exception as e:
        print(f"Error al consultar hoteles: {e}")

def consultar_tripulantes():
    """Consulta y muestra todos los tripulantes en la base de datos."""
    try:
        tripulantes = session.query(Tripulante).all()
        if tripulantes:
            print("Lista de Tripulantes en la base de datos:")
            for tripulante in tripulantes:
                print(f"ID: {tripulante.tripulante_id}, Nombre: {tripulante.nombre}, Apellido: {tripulante.apellido}, Estado: {tripulante.estado}")
        else:
            print("No hay tripulantes en la base de datos.")
    except Exception as e:
        print(f"Error al consultar tripulantes: {e}")

def main():
    """Función principal para ejecutar las consultas de prueba."""
    print("Consultando la base de datos...")
    
    # Consultar y mostrar hoteles
    consultar_hoteles()
    
    # Consultar y mostrar tripulantes
    consultar_tripulantes()

if __name__ == "__main__":
    # Ejecutar las consultas de prueba
    main()

    # Cerrar la sesión al finalizar
    session.close()
