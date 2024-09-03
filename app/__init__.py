from litestar import Litestar

from app.controllers import (
    TripulanteController,
    BuqueController,
    RestauranteController,
    TransporteController,
    ViajeController,
)
from app.database import db_plugin

app = Litestar(
    [
        TripulanteController,
        BuqueController,
        RestauranteController,
        TransporteController,
        ViajeController
    ],
    debug=True,
    plugins=[db_plugin],
)
