import pandas as pd
import sys
from database import SessionLocal, engine
from models import Buque, Restaurante, Transporte, Hotel, Base

# Crear las tablas si no existen
Base.metadata.create_all(engine)

def process_excel_file(file_path):
    try:
        # Leer todas las hojas del archivo Excel
        excel_data = pd.read_excel(file_path, sheet_name=None)
        print("Hojas de Excel encontradas:", excel_data.keys())

        # Procesar las hojas 'Hotel', 'Cliente', 'Restaurant', 'Transporte'
        if 'Hotel' in excel_data:
            print("Procesando hoja 'Hotel'")
            save_hotel_data(excel_data['Hotel'])

        if 'Cliente' in excel_data:
            print("Procesando hoja 'Cliente'")
            save_buque_data(excel_data['Cliente'])

        if 'Restaurant' in excel_data:
            print("Procesando hoja 'Restaurant'")
            save_restaurant_data(excel_data['Restaurant'])

        if 'Transporte' in excel_data:
            print("Procesando hoja 'Transporte'")
            save_transporte_data(excel_data['Transporte'])

    except Exception as e:
        print(f"Error al procesar el archivo Excel: {e}")

def save_hotel_data(hotel_df):
    session = SessionLocal()
    try:
        for _, row in hotel_df.iterrows():
            nombre = row.get('nombre')
            ciudad = row.get('ciudad')

            if pd.isna(nombre) or pd.isna(ciudad):
                continue

            # Verificar si el hotel ya existe
            if session.query(Hotel).filter_by(nombre=nombre, ciudad=ciudad).first() is not None:
                print(f"Hotel '{nombre}' en '{ciudad}' ya existe. Omitiendo...")
                continue

            # Crear el nuevo objeto Hotel
            hotel = Hotel(nombre=nombre, ciudad=ciudad)  # solo se establecen nombre y ciudad
            session.add(hotel)

        session.commit()
        print("Datos de hoteles guardados correctamente.")
        
    except Exception as e:
        session.rollback()
        print(f"Error al guardar los datos de hoteles: {e}")
        
    finally:
        session.close()

def save_restaurant_data(restaurant_df):
    session = SessionLocal()
    try:
        for _, row in restaurant_df.iterrows():
            nombre = row.get('nombre')
            ciudad = row.get('ciudad')

            if pd.isna(nombre) or pd.isna(ciudad):
                continue

            # Verificar si el restaurante ya existe
            if session.query(Restaurante).filter_by(nombre=nombre, ciudad=ciudad).first() is not None:
                print(f"Restaurante '{nombre}' en '{ciudad}' ya existe. Omitiendo...")
                continue

            restaurant = Restaurante(nombre=nombre, ciudad=ciudad)
            session.add(restaurant)

        session.commit()
        print("Datos de restaurantes guardados correctamente.")
        
    except Exception as e:
        session.rollback()
        print(f"Error al guardar los datos de restaurantes: {e}")
        
    finally:
        session.close()

def save_transporte_data(transporte_df):
    session = SessionLocal()
    try:
        for _, row in transporte_df.iterrows():
            nombre = row.get('nombre')
            ciudad = row.get('ciudad')

            if pd.isna(nombre) or pd.isna(ciudad):
                continue

            # Verificar si el transporte ya existe
            if session.query(Transporte).filter_by(nombre=nombre, ciudad=ciudad).first() is not None:
                print(f"Transporte '{nombre}' en '{ciudad}' ya existe. Omitiendo...")
                continue

            transporte = Transporte(nombre=nombre, ciudad=ciudad)
            session.add(transporte)

        session.commit()
        print("Datos de transporte guardados correctamente.")
        
    except Exception as e:
        session.rollback()
        print(f"Error al guardar los datos de transporte: {e}")
        
    finally:
        session.close()

def save_buque_data(cliente_df):
    session = SessionLocal()
    try:
        for _, row in cliente_df.iterrows():
            barco = row.get('BARCO')
            cliente = row.get('CLIENTE')  # Aquí está el cliente
            ciudad = row.get('CIUDAD')

            if pd.isna(barco) or pd.isna(cliente) or pd.isna(ciudad):
                continue

            # Verificar si el buque ya existe
            if session.query(Buque).filter_by(nombre=barco, cobrar_a=cliente, ciudad=ciudad).first() is not None:
                print(f"Buque '{barco}' que cobra a '{cliente}' en '{ciudad}' ya existe. Omitiendo...")
                continue

            buque = Buque(nombre=barco, compañia=cliente, ciudad=ciudad)
            session.add(buque)

        session.commit()
        print("Datos de buques guardados correctamente.")
        
    except Exception as e:
        session.rollback()
        print(f"Error al guardar los datos de buques: {e}")
        
    finally:
        session.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python carga_datos.py ../proveedores.xlsx")
        sys.exit(1)

    file_path = sys.argv[1]
    process_excel_file(file_path)
