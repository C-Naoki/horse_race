from fastapi import APIRouter
from api.services.horse_race.adapters.controllers.horse_profile import (
    HorseProfile, HorseProfileController, SuccessMessageResponse
)
from api.services.horse_race.adapters.controllers.healthz import HealthzController


def get_route(
    healthz_controller: HealthzController,
    horse_profile_controller: HorseProfileController,
) -> APIRouter:
    router = APIRouter(
        prefix="/api/horse_profile/v1",
        tags=["horse_profile"],
        responses={404: {"description": "Not found"}}
    )

    @router.get("/healthz")
    async def get_healthz():
        return healthz_controller.get()

    @router.post("horse_profile", status_code=201)
    async def post_horse_profile(horse_profile: HorseProfile):
        return horse_profile_controller.create(horse_profile)

    @router.put("horse_profile", status_code=201)
    async def put_horse_profile(horse_profile: HorseProfile):
        return horse_profile_controller.update(horse_profile)

    @router.delete("/horse_profile/{horse_id}", response_model=SuccessMessageResponse, status_code=200)
    async def delete_horse_profile(horse_id: str):
        return horse_profile_controller.delete(horse_id)

    @router.get("/horse_profile/{horse_id}", status_code=200)
    async def retrieve_horse_profile(horse_id: str):
        return horse_profile_controller.retrieve_by(horse_id)

    @router.get("/horse_profile/{breeder_id}", status_code=200)
    async def retrieve_horse_profile_by_breeder(breeder_id: str):
        return horse_profile_controller.retrieve_by(breeder_id)

    @router.get("/horse_profile/{owner_id}", status_code=200)
    async def retrieve_horse_profile_by_owner(owner_id: str):
        return horse_profile_controller.retrieve_by(owner_id)

    @router.get("/horse_profile/{trainer_id}", status_code=200)
    async def retrieve_horse_profile_by_trainer(trainer_id: str):
        return horse_profile_controller.retrieve_by(trainer_id)

    return router
