import os

from migrations.engine import get_engine
from api.services.horse_race.adapters.controllers.horse_profile import HorseProfileController
from api.services.horse_race.adapters.controllers.healthz import HealthzController
from api.services.horse_race.adapters.db_gateways.horse_profile import HorseProfileDBGateway
from api.services.horse_race.applications.horse_profile_usecase import HorseProfileUsecase
from api.services.horse_race.infrastructures.servers.horse_profile_route import get_route


def main():
    engine = get_engine(
        os.environ.get("DATABASE"),
        os.environ.get("USER"),
        os.environ.get("PASSWORD"),
        os.environ.get("HOST"),
        os.environ.get("PORT"),
        os.environ.get("DB_NAME"),
    )
    route = get_route(
        healthz_controller=HealthzController(),
        horse_profile_controller=HorseProfileController(
            HorseProfileUsecase(
                HorseProfileDBGateway(
                    engine
                )
            )
        )
    )
    return route
