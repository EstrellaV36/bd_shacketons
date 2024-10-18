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

    def __repr__(self):
        return f"id={self.eta_id}, buque={self.buque}, ciudad={self.ciudad}, eta={self.eta}, etd={self.etd})"

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
        return f"Buque(id={self.nombre}, nombre={self.empresa}, compañia={self.ciudad})"

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
    condicion: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    puerto_desembarque: Mapped[str] = mapped_column(String, nullable=True)
    necesita_asistencia_puq: Mapped[bool] = mapped_column(Boolean, default=False)
    necesita_asistencia_scl: Mapped[bool] = mapped_column(Boolean, default=False)
    necesita_asistencia_wpu: Mapped[bool] = mapped_column(Boolean, default=False)
    pref_alimenticia: Mapped[Optional[str]] = mapped_column(String, default='NORMAL')
    estado: Mapped[str] = mapped_column(String, nullable=False)  # Añadido para diferenciar ON/OFF


    buque_id: Mapped[Optional[int]] = mapped_column(ForeignKey("buques.buque_id"))
    tipo: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    vuelos_asociados: Mapped[list["TripulanteVuelo"]] = relationship("TripulanteVuelo", back_populates="tripulante")

    buque: Mapped["Buque"] = relationship(back_populates="tripulantes")
    
    # Relación a través de la tabla intermedia TripulanteHotel
    tripulante_hotels: Mapped[list["TripulanteHotel"]] = relationship("TripulanteHotel", back_populates="tripulante")
    tripulante_transports: Mapped[list["TripulanteTransporte"]] = relationship("TripulanteTransporte", back_populates="tripulante")
    tripulante_restaurantes: Mapped[list["TripulanteRestaurante"]] = relationship("TripulanteRestaurante", back_populates="tripulante")
    transportes: Mapped[list["Transporte"]] = relationship(back_populates="tripulante")
    viajes: Mapped[list["Viaje"]] = relationship(back_populates="tripulante")

    def __repr__(self):
        return f"Tripulante(id={self.tripulante_id}, nombre={self.nombre}, apellido={self.apellido}, buque={self.buque_id})"

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
    tipo: Mapped[str] = mapped_column(String, nullable=False)
    hora_salida: Mapped[datetime] = mapped_column(nullable=False)
    hora_llegada: Mapped[datetime] = mapped_column(nullable=False)
    aeropuerto_salida: Mapped[str] = mapped_column(String, nullable=False)
    aeropuerto_llegada: Mapped[str] = mapped_column(String, nullable=False)
    requiere_colacion: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    tipo_colacion: Mapped[Optional[str]] = mapped_column(String)

    tripulantes_asociados: Mapped[list["TripulanteVuelo"]] = relationship("TripulanteVuelo", back_populates="vuelo")

    def __repr__(self):
        return f"Vuelo(id={self.vuelo_id}, codigo={self.codigo})"

#----------- TABLA AÑADIDA PARA MANEJAR MULTIPLES HOTELES POR TRIPULANTE ----------
class TripulanteHotel(Base):
    __tablename__ = "tripulante_hotel"

    tripulante_hotel_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tripulante_id: Mapped[int] = mapped_column(ForeignKey("tripulantes.tripulante_id"), nullable=False)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hoteles.hotel_id"), nullable=False)
    categoria: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    fecha_entrada: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    fecha_salida: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    tipo_habitacion: Mapped[str] = mapped_column(String, nullable=True, default=None)
    numero_noches: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    day_room: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)

    tripulante: Mapped["Tripulante"] = relationship("Tripulante", back_populates="tripulante_hotels")
    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="tripulante_hotels")

    def __repr__(self):
        return f"TripulanteHotel(tripulante_id={self.tripulante_id}, hotel_id={self.hotel_id})"

class Hotel(Base):
    __tablename__ = "hoteles"

    hotel_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    ciudad: Mapped[str] = mapped_column(String, nullable=False)

    # Relación inversa a través de la tabla intermedia TripulanteHotel
    tripulante_hotels: Mapped[list["TripulanteHotel"]] = relationship("TripulanteHotel", back_populates="hotel")

    def __repr__(self):
        return f"Hotel(id={self.hotel_id}, nombre={self.nombre}, ciudad={self.ciudad})"

class TripulanteRestaurante(Base):
    __tablename__ = "tripulante_restaurante"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # ID único para la relación
    fecha_reserva: Mapped[datetime] = mapped_column(nullable=True, default=None)  # Campo nulo permitido
    tipo_comida: Mapped[str] = mapped_column(nullable=True, default=None)
    tripulante_id: Mapped[int] = mapped_column(ForeignKey("tripulantes.tripulante_id"), nullable=False)
    restaurante_id: Mapped[int] = mapped_column(ForeignKey("restaurantes.restaurante_id"), nullable=False)

    # Relaciones
    tripulante: Mapped["Tripulante"] = relationship("Tripulante", back_populates="tripulante_restaurantes")
    restaurante: Mapped["Restaurante"] = relationship("Restaurante", back_populates="tripulante_restaurantes")

    def __repr__(self):
        return f"TripulanteRestaurante(id={self.id}, tripulante_id={self.tripulante_id}, restaurante_id={self.restaurante_id}, fecha_reserva={self.fecha_reserva})"

class Restaurante(Base):
    __tablename__ = "restaurantes"

    restaurante_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)  # Campo no nulo
    ciudad: Mapped[str] = mapped_column(String, nullable=False)  # Campo no nulo

    tripulante_restaurantes: Mapped[list["TripulanteRestaurante"]] = relationship("TripulanteRestaurante", back_populates="restaurante")

    def __repr__(self):
        return f"Restaurante(id={self.restaurante_id}, nombre={self.nombre}, ciudad={self.ciudad})"

class TripulanteTransporte(Base):
    __tablename__ = "tripulante_transporte"

    tripulante_transporte_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tripulante_id: Mapped[int] = mapped_column(ForeignKey("tripulantes.tripulante_id"), nullable=False)
    transporte_id: Mapped[int] = mapped_column(ForeignKey("transportes.transporte_id"), nullable=False)
    
    ciudad: Mapped[str] = mapped_column(String, nullable=True, default=None)  # Cambiado a String
    lugar_inicio: Mapped[str] = mapped_column(String, nullable=True, default=None)
    lugar_final: Mapped[str] = mapped_column(String, nullable=True, default=None)
    fecha: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    
    # Relaciones con Tripulante y Transporte
    tripulante: Mapped["Tripulante"] = relationship("Tripulante", back_populates="tripulante_transports")
    transporte: Mapped["Transporte"] = relationship("Transporte", back_populates="tripulante_transports")

    def __repr__(self):
        return f"TripulanteTransporte(tripulante_id={self.tripulante_id}, transporte_id={self.transporte_id})"

class Transporte(Base):
    __tablename__ = "transportes"

    transporte_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String, nullable=True)
    ciudad: Mapped[str] = mapped_column(String, nullable=False)

    tripulante_id: Mapped[int] = mapped_column(ForeignKey("tripulantes.tripulante_id"), nullable=True)
    
    # Relación con Tripulante, si se quiere un tripulante asignado directamente
    tripulante: Mapped["Tripulante"] = relationship(back_populates="transportes")

    # Relación con TripulanteTransporte para la relación uno a muchos
    tripulante_transports: Mapped[list["TripulanteTransporte"]] = relationship("TripulanteTransporte", back_populates="transporte")

    def __repr__(self):
        return f"Transporte(id={self.transporte_id}, nombre={self.nombre}, ciudad={self.ciudad})"

class Viaje(Base):
    __tablename__ = "viajes"

    viaje_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipaje_perdido: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=False)
    asistencia_medica: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=False)
    estado: Mapped[str] = mapped_column(String, nullable=False)  # Añadido para diferenciar ON/OFF

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