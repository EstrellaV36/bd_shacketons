from datetime import datetime, date
from typing import Optional
from sqlalchemy import ForeignKey, String, DateTime, Date, Integer, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

#-----------  TABLA AÑADIDA PARA MANEJAR MULTIPLES ETAS POR CIUDAD PARA BUQUES-----------
class EtaCiudad(Base):
    __tablename__ = "etas_ciudades"

    eta_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    buque_id: Mapped[int] = mapped_column(ForeignKey("buques.buque_id"))
    ciudad: Mapped[str] = mapped_column(String, nullable=False)  # PUQ, SCL, WPU, etc.
    eta: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    etd: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    buque: Mapped["Buque"] = relationship(back_populates="etas")

class Buque(Base):
    __tablename__ = "buques"

    buque_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    empresa: Mapped[str] = mapped_column(String, nullable=False)
    cobrar_a: Mapped[str] = mapped_column(String, nullable=True) #ver donde correspondería poner a quien cobrar
    ciudad: Mapped[str] = mapped_column(String, nullable=False)
    
    etas: Mapped[list["EtaCiudad"]] = relationship(back_populates="buque")
    tripulantes: Mapped[list["Tripulante"]] = relationship(back_populates="buque")
    viajes: Mapped[list["Viaje"]] = relationship(back_populates="buque")

    def __repr__(self):
        return f"Buque(id={self.buque_id}, nombre={self.nombre}, compañia={self.compañia})"

class Tripulante(Base):
    __tablename__ = "tripulantes"

    tripulante_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    apellido: Mapped[str] = mapped_column(String, nullable=False)
    nacionalidad: Mapped[str] = mapped_column(String, nullable=False)
    pasaporte: Mapped[str] = mapped_column(String, nullable=False)
    sexo: Mapped[str] = mapped_column(String(1), nullable=False)
    fecha_nacimiento: Mapped[date] = mapped_column(Date, nullable=False)
    posicion: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    puerto_desembarque: Mapped[str] = mapped_column(String, nullable=True)  # No estoy segura de este
    necesita_asistencia_puq: Mapped[bool] = mapped_column(Boolean, default=False)
    necesita_asistencia_scl: Mapped[bool] = mapped_column(Boolean, default=False)
    necesita_asistencia_wpu: Mapped[bool] = mapped_column(Boolean, default=False)

    buque_id: Mapped[Optional[int]] = mapped_column(ForeignKey("buques.buque_id"))
    tipo: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    estado: Mapped[str] = mapped_column(String, nullable=False)  # Añadido para diferenciar ON/OFF

    vuelos_asociados: Mapped[list["TripulanteVuelo"]] = relationship("TripulanteVuelo", back_populates="tripulante")

    buque: Mapped["Buque"] = relationship(back_populates="tripulantes")
    hoteles: Mapped[list["Hotel"]] = relationship(back_populates="tripulante")
    restaurantes: Mapped[list["Restaurante"]] = relationship(back_populates="tripulante")
    transportes: Mapped[list["Transporte"]] = relationship(back_populates="tripulante")
    viajes: Mapped[list["Viaje"]] = relationship(back_populates="tripulante")

    def __repr__(self):
        return f"Tripulante(id={self.tripulante_id}, nombre={self.nombre}, apellido={self.apellido})"
    
#-----------  TABLA AÑADIDA PARA MANEJAR MULTIPLES TRIPULANTES POR VUELO ----------
class TripulanteVuelo(Base):
    __tablename__ = "tripulante_vuelo"

    tripulante_id: Mapped[int] = mapped_column(ForeignKey("tripulantes.tripulante_id"), primary_key=True)
    vuelo_id: Mapped[int] = mapped_column(ForeignKey("vuelos.vuelo_id"), primary_key=True)

    # Relaciones
    tripulante: Mapped["Tripulante"] = relationship("Tripulante", back_populates="vuelos_asociados")
    vuelo: Mapped["Vuelo"] = relationship("Vuelo", back_populates="tripulantes_asociados")

    def __repr__(self):
        return f"TripulanteVuelo(tripulante_id={self.tripulante_id}, vuelo_id={self.vuelo_id})"

class Vuelo(Base):
    __tablename__ = "vuelos"

    vuelo_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String, nullable=False)
    fecha: Mapped[datetime] = mapped_column(nullable=False)
    hora_salida: Mapped[datetime] = mapped_column(nullable=False)
    hora_llegada: Mapped[datetime] = mapped_column(nullable=False)
    aeropuerto_salida: Mapped[str] = mapped_column(String, nullable=False)
    aeropuerto_llegada: Mapped[str] = mapped_column(String, nullable=False)
    requiere_colacion: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    tipo_colacion: Mapped[Optional[str]] = mapped_column(String)

    tripulantes_asociados: Mapped[list["TripulanteVuelo"]] = relationship("TripulanteVuelo", back_populates="vuelo")

    def __repr__(self):
        return f"Vuelo(id={self.vuelo_id}, codigo={self.codigo})"

class Hotel(Base):
    __tablename__ = "hoteles"

    hotel_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    ciudad: Mapped[str] = mapped_column(String, nullable=False)
    categoria: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    fecha_entrada: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    fecha_salida: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    tipo_habitacion: Mapped[str] = mapped_column(String, nullable=True, default=None)
    numero_noches: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    day_room: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)

    tripulante_id: Mapped[int] = mapped_column(ForeignKey("tripulantes.tripulante_id"), nullable=True)

    tripulante: Mapped["Tripulante"] = relationship(back_populates="hoteles")

    def __repr__(self):
        return f"Hotel(id={self.hotel_id}, nombre={self.nombre}, ciudad={self.ciudad})"

class Restaurante(Base):
    __tablename__ = "restaurantes"

    restaurante_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)  # Campo no nulo
    direccion: Mapped[str] = mapped_column(String, nullable=True, default=None)  # Campo nulo permitido
    ciudad: Mapped[str] = mapped_column(String, nullable=False)  # Campo no nulo
    fecha_reserva: Mapped[datetime] = mapped_column(nullable=True, default=None)  # Campo nulo permitido

    tripulante_id: Mapped[int] = mapped_column(ForeignKey("tripulantes.tripulante_id"), nullable=True)

    tripulante: Mapped["Tripulante"] = relationship(back_populates="restaurantes")

    def __repr__(self):
        return f"Restaurante(id={self.restaurante_id}, nombre={self.nombre}, ciudad={self.ciudad})"

class Transporte(Base):
    __tablename__ = "transportes"

    transporte_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    ciudad: Mapped[str] = mapped_column(String, nullable=False)

    tipo: Mapped[str] = mapped_column(String, nullable=True, default=None)
    empresa: Mapped[str] = mapped_column(String, nullable=True, default=None)
    capacidad: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    fecha_transporte: Mapped[datetime] = mapped_column(nullable=True, default=None)
    hora_recogida: Mapped[datetime] = mapped_column(nullable=True, default=None)
    hora_salida: Mapped[datetime] = mapped_column(nullable=True, default=None)
    hora_llegada: Mapped[datetime] = mapped_column(nullable=True, default=None)

    tripulante_id: Mapped[int] = mapped_column(ForeignKey("tripulantes.tripulante_id"), nullable=True)

    tripulante: Mapped["Tripulante"] = relationship(back_populates="transportes")

    def __repr__(self):
        return f"Transporte(id={self.transporte_id}, tipo={self.tipo}, empresa={self.empresa})"

class Viaje(Base):
    __tablename__ = "viajes"

    viaje_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipaje_perdido: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    asistencia_medica: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    tripulante_id: Mapped[int] = mapped_column(ForeignKey("tripulantes.tripulante_id"))
    buque_id: Mapped[int] = mapped_column(ForeignKey("buques.buque_id"))
    vuelo_id: Mapped[int] = mapped_column(ForeignKey("vuelos.vuelo_id"))
    """
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hoteles.hotel_id"))
    restaurante_id: Mapped[int] = mapped_column(ForeignKey("restaurantes.restaurante_id"))
    transporte_id: Mapped[int] = mapped_column(ForeignKey("transportes.transporte_id"))
    """
    #relaciones
    tripulante: Mapped["Tripulante"] = relationship(back_populates="viajes")
    buque: Mapped["Buque"] = relationship(back_populates="viajes")
    vuelo: Mapped["Vuelo"] = relationship()
    """
    hotel: Mapped["Hotel"] = relationship()
    restaurante: Mapped["Restaurante"] = relationship()
    transporte: Mapped["Transporte"] = relationship()
    """
    def __repr__(self):
        return f"Viaje(id={self.viaje_id}, empresa_pagadora={self.empresa_pagadora}, fecha_inicio={self.fecha_inicio})"