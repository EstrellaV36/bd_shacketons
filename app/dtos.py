from advanced_alchemy.extensions.litestar import SQLAlchemyDTO, SQLAlchemyDTOConfig

from models import Tripulante, Buque, Vuelo, Hotel, Restaurante, Transporte, Viaje

# DTOs para Tripulante
class TripulanteReadDTO(SQLAlchemyDTO[Tripulante]):
    config = SQLAlchemyDTOConfig(exclude={"buque", "vuelos", "hoteles", "restaurantes", "transportes", "viajes"})

class TripulanteReadFullDTO(SQLAlchemyDTO[Tripulante]):
    pass

class TripulanteCreateDTO(SQLAlchemyDTO[Tripulante]):
    config = SQLAlchemyDTOConfig(
        exclude={"tripulante_id", "posicion", "necesita_asistencia_puq",
                 "necesita_asistencia_scl", "necesita_asistencia_wpu", 
                 "buque", "vuelos", "hoteles", "puerto_desembarque",
                 "buque_id", "tipo", "eta",
                 "restaurantes", "transportes", "viajes"}
    )

class TripulanteUpdateDTO(SQLAlchemyDTO[Tripulante]):
    config = SQLAlchemyDTOConfig(
        exclude={"tripulante_id", "buque", "vuelos", "hoteles", "restaurantes", "transportes", "viajes"}, partial=True
    )

# DTOs para Buque
class BuqueReadDTO(SQLAlchemyDTO[Buque]):
    config = SQLAlchemyDTOConfig(exclude={"tripulantes", "viajes"})

class BuqueReadFullDTO(SQLAlchemyDTO[Buque]):
    pass

class BuqueCreateDTO(SQLAlchemyDTO[Buque]):
    config = SQLAlchemyDTOConfig(exclude={"buque_id", "tripulantes", "viajes", "cobrar_a"})

class BuqueUpdateDTO(SQLAlchemyDTO[Buque]):
    config = SQLAlchemyDTOConfig(exclude={"buque_id", "tripulantes", "viajes"}, partial=True)


# DTOs para Vuelo
class VueloReadDTO(SQLAlchemyDTO[Vuelo]):
    config = SQLAlchemyDTOConfig(exclude={"tripulante"})

class VueloReadFullDTO(SQLAlchemyDTO[Vuelo]):
    pass

class VueloCreateDTO(SQLAlchemyDTO[Vuelo]):
    config = SQLAlchemyDTOConfig(exclude={"vuelo_id", "tripulante"})

class VueloUpdateDTO(SQLAlchemyDTO[Vuelo]):
    config = SQLAlchemyDTOConfig(exclude={"vuelo_id", "tripulante"}, partial=True)

# DTOs para Hotel
class HotelReadDTO(SQLAlchemyDTO[Hotel]):
    config = SQLAlchemyDTOConfig(exclude={"tripulante"})

class HotelReadFullDTO(SQLAlchemyDTO[Hotel]):
    pass

class HotelCreateDTO(SQLAlchemyDTO[Hotel]):
    config = SQLAlchemyDTOConfig(exclude={"hotel_id", "tripulante"})

class HotelUpdateDTO(SQLAlchemyDTO[Hotel]):
    config = SQLAlchemyDTOConfig(exclude={"hotel_id", "tripulante"}, partial=True)

# DTOs para Restaurante
class RestauranteReadDTO(SQLAlchemyDTO[Restaurante]):
    config = SQLAlchemyDTOConfig(exclude={"tripulante"})

class RestauranteReadFullDTO(SQLAlchemyDTO[Restaurante]):
    pass

class RestauranteCreateDTO(SQLAlchemyDTO[Restaurante]):
    config = SQLAlchemyDTOConfig(exclude={"restaurante_id", "tripulante"})

class RestauranteUpdateDTO(SQLAlchemyDTO[Restaurante]):
    config = SQLAlchemyDTOConfig(exclude={"restaurante_id", "tripulante"}, partial=True)

# DTOs para Transporte
class TransporteReadDTO(SQLAlchemyDTO[Transporte]):
    config = SQLAlchemyDTOConfig(exclude={"tripulante"})

class TransporteReadFullDTO(SQLAlchemyDTO[Transporte]):
    pass

class TransporteCreateDTO(SQLAlchemyDTO[Transporte]):
    config = SQLAlchemyDTOConfig(exclude={"transporte_id", "tripulante"})

class TransporteUpdateDTO(SQLAlchemyDTO[Transporte]):
    config = SQLAlchemyDTOConfig(exclude={"transporte_id", "tripulante"}, partial=True)

# DTOs para Viaje
class ViajeReadDTO(SQLAlchemyDTO[Viaje]):
    config = SQLAlchemyDTOConfig(exclude={"tripulante", "buque", "vuelo", "hotel", "restaurante", "transporte"})

class ViajeReadFullDTO(SQLAlchemyDTO[Viaje]):
    pass

class ViajeCreateDTO(SQLAlchemyDTO[Viaje]):
    config = SQLAlchemyDTOConfig(exclude={"viaje_id", "tripulante", "buque", "vuelo", "hotel", "restaurante", "transporte"})

class ViajeUpdateDTO(SQLAlchemyDTO[Viaje]):
    config = SQLAlchemyDTOConfig(
        exclude={"viaje_id", "tripulante", "buque", "vuelo", "hotel", "restaurante", "transporte"}, partial=True
    )