from sqlalchemy import text
from database import engine

# Ejecutar una consulta SQL cruda
with engine.connect() as connection:
    result = connection.execute(text("SELECT * FROM tripulantes"))
    for row in result:
        print(row)
