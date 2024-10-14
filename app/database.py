# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#from models import Base
from app.models import Base 

# Configura la conexión a la base de datos
engine = create_engine("sqlite:///shacketons_db.sqlite3")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crea las tablas
Base.metadata.create_all(engine)

# Crea una función para obtener la sesión
def get_db_session():
    return SessionLocal()