from datetime import datetime
from typing import Sequence

from advanced_alchemy.exceptions import NotFoundError
from advanced_alchemy.filters import CollectionFilter
from litestar import Controller, delete, get, patch, post
from litestar.dto import DTOData
from litestar.exceptions import HTTPException, NotFoundException
from sqlalchemy import select

from app.dtos import (
    TripulanteCreateDTO,
    TripulanteReadDTO,
    TripulanteReadFullDTO,
    TripulanteUpdateDTO,
    BuqueCreateDTO,
    BuqueReadDTO,
    BuqueReadFullDTO,
    BuqueUpdateDTO,
    VueloCreateDTO,
    VueloReadDTO,
    VueloReadFullDTO,
    VueloUpdateDTO,
    HotelCreateDTO,
    HotelReadDTO,
    HotelReadFullDTO,
    HotelUpdateDTO,
    RestauranteCreateDTO,
    RestauranteReadDTO,
    RestauranteReadFullDTO,
    RestauranteUpdateDTO,
    TransporteCreateDTO,
    TransporteReadDTO,
    TransporteReadFullDTO,
    TransporteUpdateDTO,
    ViajeCreateDTO,
    ViajeReadDTO,
    ViajeReadFullDTO,
    ViajeUpdateDTO,
)
from app.models import Tripulante, Buque, Vuelo, Hotel, Restaurante, Transporte, Viaje
from app.repositories import (
    TripulanteRepository,
    BuqueRepository,
    VueloRepository,
    HotelRepository,
    RestauranteRepository,
    TransporteRepository,
    ViajeRepository,
    provide_tripulante_repo,
    provide_buque_repo,
    provide_vuelo_repo,
    provide_hotel_repo,
    provide_restaurante_repo,
    provide_transporte_repo,
    provide_viaje_repo,
)


class TripulanteController(Controller):
    path = "/tripulantes"
    tags = ["tripulantes"]
    dependencies = {"tripulante_repo": provide_tripulante_repo}
    return_dto = TripulanteReadFullDTO

    @get()
    async def list_tripulantes(self, tripulante_repo: TripulanteRepository) -> Sequence[Tripulante]:
        return tripulante_repo.list()

    @get("/{tripulante_id:int}")
    async def get_tripulante(self, tripulante_repo: TripulanteRepository, tripulante_id: int) -> Tripulante:
        try:
            return tripulante_repo.get(tripulante_id)
        except NotFoundError as e:
            raise NotFoundException(detail=f"Tripulante {tripulante_id} no encontrado") from e

    @post("/", dto=TripulanteCreateDTO)
    async def add_tripulante(self, tripulante_repo: TripulanteRepository, data: Tripulante) -> Tripulante:
        return tripulante_repo.add(data)

    @patch("/{tripulante_id:int}", dto=TripulanteUpdateDTO)
    async def update_tripulante(
        self,
        tripulante_repo: TripulanteRepository,
        tripulante_id: int,
        data: DTOData[Tripulante],
    ) -> Tripulante:
        try:
            tripulante, _ = tripulante_repo.get_and_update(
                id=tripulante_id, **data.as_builtins(), match_fields=["id"]
            )
            return tripulante
        except NotFoundError as e:
            raise NotFoundException(detail=f"Tripulante {tripulante_id} no encontrado") from e

    @delete("/{tripulante_id:int}")
    async def delete_tripulante(self, tripulante_repo: TripulanteRepository, tripulante_id: int) -> None:
        try:
            tripulante_repo.delete(tripulante_id)
        except NotFoundError as e:
            raise NotFoundException(detail=f"Tripulante {tripulante_id} no encontrado") from e


class BuqueController(Controller):
    path = "/buques"
    tags = ["buques"]
    dependencies = {"buque_repo": provide_buque_repo}
    return_dto = BuqueReadFullDTO

    @get()
    async def list_buques(self, buque_repo: BuqueRepository) -> Sequence[Buque]:
        return buque_repo.list()

    @get("/{buque_id:int}")
    async def get_buque(self, buque_repo: BuqueRepository, buque_id: int) -> Buque:
        try:
            return buque_repo.get(buque_id)
        except NotFoundError as e:
            raise NotFoundException(detail=f"Buque {buque_id} no encontrado") from e

    @post("/", dto=BuqueCreateDTO)
    async def add_buque(self, buque_repo: BuqueRepository, data: Buque) -> Buque:
        return buque_repo.add(data)

    @patch("/{buque_id:int}", dto=BuqueUpdateDTO)
    async def update_buque(
        self,
        buque_repo: BuqueRepository,
        buque_id: int,
        data: DTOData[Buque],
    ) -> Buque:
        try:
            buque, _ = buque_repo.get_and_update(
                id=buque_id, **data.as_builtins(), match_fields=["id"]
            )
            return buque
        except NotFoundError as e:
            raise NotFoundException(detail=f"Buque {buque_id} no encontrado") from e

    @delete("/{buque_id:int}")
    async def delete_buque(self, buque_repo: BuqueRepository, buque_id: int) -> None:
        try:
            buque_repo.delete(buque_id)
        except NotFoundError as e:
            raise NotFoundException(detail=f"Buque {buque_id} no encontrado") from e


class VueloController(Controller):
    path = "/vuelos"
    tags = ["vuelos"]
    dependencies = {"vuelo_repo": provide_vuelo_repo}
    return_dto = VueloReadFullDTO

    @get()
    async def list_vuelos(self, vuelo_repo: VueloRepository) -> Sequence[Vuelo]:
        return vuelo_repo.list()

    @get("/{vuelo_id:int}")
    async def get_vuelo(self, vuelo_repo: VueloRepository, vuelo_id: int) -> Vuelo:
        try:
            return vuelo_repo.get(vuelo_id)
        except NotFoundError as e:
            raise NotFoundException(detail=f"Vuelo {vuelo_id} no encontrado") from e

    @post("/", dto=VueloCreateDTO)
    async def add_vuelo(self, vuelo_repo: VueloRepository, data: Vuelo) -> Vuelo:
        return vuelo_repo.add(data)

    @patch("/{vuelo_id:int}", dto=VueloUpdateDTO)
    async def update_vuelo(
        self,
        vuelo_repo: VueloRepository,
        vuelo_id: int,
        data: DTOData[Vuelo],
    ) -> Vuelo:
        try:
            vuelo, _ = vuelo_repo.get_and_update(
                id=vuelo_id, **data.as_builtins(), match_fields=["id"]
            )
            return vuelo
        except NotFoundError as e:
            raise NotFoundException(detail=f"Vuelo {vuelo_id} no encontrado") from e

    @delete("/{vuelo_id:int}")
    async def delete_vuelo(self, vuelo_repo: VueloRepository, vuelo_id: int) -> None:
        try:
            vuelo_repo.delete(vuelo_id)
        except NotFoundError as e:
            raise NotFoundException(detail=f"Vuelo {vuelo_id} no encontrado") from e


class HotelController(Controller):
    path = "/hoteles"
    tags = ["hoteles"]
    dependencies = {"hotel_repo": provide_hotel_repo}
    return_dto = HotelReadFullDTO

    @get()
    async def list_hoteles(self, hotel_repo: HotelRepository) -> Sequence[Hotel]:
        return hotel_repo.list()

    @get("/{hotel_id:int}")
    async def get_hotel(self, hotel_repo: HotelRepository, hotel_id: int) -> Hotel:
        try:
            return hotel_repo.get(hotel_id)
        except NotFoundError as e:
            raise NotFoundException(detail=f"Hotel {hotel_id} no encontrado") from e

    @post("/", dto=HotelCreateDTO)
    async def add_hotel(self, hotel_repo: HotelRepository, data: Hotel) -> Hotel:
        return hotel_repo.add(data)

    @patch("/{hotel_id:int}", dto=HotelUpdateDTO)
    async def update_hotel(
        self,
        hotel_repo: HotelRepository,
        hotel_id: int,
        data: DTOData[Hotel],
    ) -> Hotel:
        try:
            hotel, _ = hotel_repo.get_and_update(
                id=hotel_id, **data.as_builtins(), match_fields=["id"]
            )
            return hotel
        except NotFoundError as e:
            raise NotFoundException(detail=f"Hotel {hotel_id} no encontrado") from e

    @delete("/{hotel_id:int}")
    async def delete_hotel(self, hotel_repo: HotelRepository, hotel_id: int) -> None:
        try:
            hotel_repo.delete(hotel_id)
        except NotFoundError as e:
            raise NotFoundException(detail=f"Hotel {hotel_id} no encontrado") from e


class RestauranteController(Controller):
    path = "/restaurantes"
    tags = ["restaurantes"]
    dependencies = {"restaurante_repo": provide_restaurante_repo}
    return_dto = RestauranteReadFullDTO

    @get()
    async def list_restaurantes(self, restaurante_repo: RestauranteRepository) -> Sequence[Restaurante]:
        return restaurante_repo.list()

    @get("/{restaurante_id:int}")
    async def get_restaurante(self, restaurante_repo: RestauranteRepository, restaurante_id: int) -> Restaurante:
        try:
            return restaurante_repo.get(restaurante_id)
        except NotFoundError as e:
            raise NotFoundException(detail=f"Restaurante {restaurante_id} no encontrado") from e

    @post("/", dto=RestauranteCreateDTO)
    async def add_restaurante(self, restaurante_repo: RestauranteRepository, data: Restaurante) -> Restaurante:
        return restaurante_repo.add(data)

    @patch("/{restaurante_id:int}", dto=RestauranteUpdateDTO)
    async def update_restaurante(
        self,
        restaurante_repo: RestauranteRepository,
        restaurante_id: int,
        data: DTOData[Restaurante],
    ) -> Restaurante:
        try:
            restaurante, _ = restaurante_repo.get_and_update(
                id=restaurante_id, **data.as_builtins(), match_fields=["id"]
            )
            return restaurante
        except NotFoundError as e:
            raise NotFoundException(detail=f"Restaurante {restaurante_id} no encontrado") from e

    @delete("/{restaurante_id:int}")
    async def delete_restaurante(self, restaurante_repo: RestauranteRepository, restaurante_id: int) -> None:
        try:
            restaurante_repo.delete(restaurante_id)
        except NotFoundError as e:
            raise NotFoundException(detail=f"Restaurante {restaurante_id} no encontrado") from e


class TransporteController(Controller):
    path = "/transportes"
    tags = ["transportes"]
    dependencies = {"transporte_repo": provide_transporte_repo}
    return_dto = TransporteReadFullDTO

    @get()
    async def list_transportes(self, transporte_repo: TransporteRepository) -> Sequence[Transporte]:
        return transporte_repo.list()

    @get("/{transporte_id:int}")
    async def get_transporte(self, transporte_repo: TransporteRepository, transporte_id: int) -> Transporte:
        try:
            return transporte_repo.get(transporte_id)
        except NotFoundError as e:
            raise NotFoundException(detail=f"Transporte {transporte_id} no encontrado") from e

    @post("/", dto=TransporteCreateDTO)
    async def add_transporte(self, transporte_repo: TransporteRepository, data: Transporte) -> Transporte:
        return transporte_repo.add(data)

    @patch("/{transporte_id:int}", dto=TransporteUpdateDTO)
    async def update_transporte(
        self,
        transporte_repo: TransporteRepository,
        transporte_id: int,
        data: DTOData[Transporte],
    ) -> Transporte:
        try:
            transporte, _ = transporte_repo.get_and_update(
                id=transporte_id, **data.as_builtins(), match_fields=["id"]
            )
            return transporte
        except NotFoundError as e:
            raise NotFoundException(detail=f"Transporte {transporte_id} no encontrado") from e

    @delete("/{transporte_id:int}")
    async def delete_transporte(self, transporte_repo: TransporteRepository, transporte_id: int) -> None:
        try:
            transporte_repo.delete(transporte_id)
        except NotFoundError as e:
            raise NotFoundException(detail=f"Transporte {transporte_id} no encontrado") from e


class ViajeController(Controller):
    path = "/viajes"
    tags = ["viajes"]
    dependencies = {"viaje_repo": provide_viaje_repo}
    return_dto = ViajeReadFullDTO

    @get()
    async def list_viajes(self, viaje_repo: ViajeRepository) -> Sequence[Viaje]:
        return viaje_repo.list()

    @get("/{viaje_id:int}")
    async def get_viaje(self, viaje_repo: ViajeRepository, viaje_id: int) -> Viaje:
        try:
            return viaje_repo.get(viaje_id)
        except NotFoundError as e:
            raise NotFoundException(detail=f"Viaje {viaje_id} no encontrado") from e

    @post("/", dto=ViajeCreateDTO)
    async def add_viaje(self, viaje_repo: ViajeRepository, data: Viaje) -> Viaje:
        return viaje_repo.add(data)

    @patch("/{viaje_id:int}", dto=ViajeUpdateDTO)
    async def update_viaje(
        self,
        viaje_repo: ViajeRepository,
        viaje_id: int,
        data: DTOData[Viaje],
    ) -> Viaje:
        try:
            viaje, _ = viaje_repo.get_and_update(
                id=viaje_id, **data.as_builtins(), match_fields=["id"]
            )
            return viaje
        except NotFoundError as e:
            raise NotFoundException(detail=f"Viaje {viaje_id} no encontrado") from e

    @delete("/{viaje_id:int}")
    async def delete_viaje(self, viaje_repo: ViajeRepository, viaje_id: int) -> None:
        try:
            viaje_repo.delete(viaje_id)
        except NotFoundError as e:
            raise NotFoundException(detail=f"Viaje {viaje_id} no encontrado") from e
