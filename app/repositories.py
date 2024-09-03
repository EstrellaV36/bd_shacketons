from advanced_alchemy.repository import SQLAlchemySyncRepository
from sqlalchemy.orm import Session

from app.models import Tripulante, Buque, Vuelo, Hotel, Restaurante, Transporte, Viaje

# Repositorio para Tripulante
class TripulanteRepository(SQLAlchemySyncRepository[Tripulante]):  # type: ignore
    model_type = Tripulante

async def provide_tripulante_repo(db_session: Session) -> TripulanteRepository:
    return TripulanteRepository(session=db_session, auto_commit=True)

# Repositorio para Buque
class BuqueRepository(SQLAlchemySyncRepository[Buque]):  # type: ignore
    model_type = Buque

async def provide_buque_repo(db_session: Session) -> BuqueRepository:
    return BuqueRepository(session=db_session, auto_commit=True)

# Repositorio para Vuelo
class VueloRepository(SQLAlchemySyncRepository[Vuelo]):  # type: ignore
    model_type = Vuelo

async def provide_vuelo_repo(db_session: Session) -> VueloRepository:
    return VueloRepository(session=db_session, auto_commit=True)

# Repositorio para Hotel
class HotelRepository(SQLAlchemySyncRepository[Hotel]):  # type: ignore
    model_type = Hotel

async def provide_hotel_repo(db_session: Session) -> HotelRepository:
    return HotelRepository(session=db_session, auto_commit=True)

# Repositorio para Restaurante
class RestauranteRepository(SQLAlchemySyncRepository[Restaurante]):  # type: ignore
    model_type = Restaurante

async def provide_restaurante_repo(db_session: Session) -> RestauranteRepository:
    return RestauranteRepository(session=db_session, auto_commit=True)

# Repositorio para Transporte
class TransporteRepository(SQLAlchemySyncRepository[Transporte]):  # type: ignore
    model_type = Transporte

async def provide_transporte_repo(db_session: Session) -> TransporteRepository:
    return TransporteRepository(session=db_session, auto_commit=True)

# Repositorio para Viaje
class ViajeRepository(SQLAlchemySyncRepository[Viaje]):  # type: ignore
    model_type = Viaje

async def provide_viaje_repo(db_session: Session) -> ViajeRepository:
    return ViajeRepository(session=db_session, auto_commit=True)
