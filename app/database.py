# app/database.py

#HOLA PROBANDO
from litestar.contrib.sqlalchemy.plugins import SQLAlchemySyncConfig, SQLAlchemyPlugin
from models import Base 
#from app.models import Base 

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Configuración de SQLAlchemy para Litestar
db_config = SQLAlchemySyncConfig(
    connection_string="sqlite:///shacketons_db.sqlite3",
    metadata=Base.metadata,
    create_all=True,
)
db_plugin = SQLAlchemyPlugin(db_config)

# Configura la sesión de SQLAlchemy
engine = create_engine(db_config.connection_string)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
