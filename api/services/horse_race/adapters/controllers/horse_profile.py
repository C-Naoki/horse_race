from fastapi import HTTPException
from pydantic import BaseModel
from api.services.horse_race.domains.horse_profile.schema import HorseProfile
from api.services.horse_race.adapters.db_gateways.horse_profile import (
    DuplicationError,
    NotFoundError
)
from api.services.horse_race.applications.horse_profile_usecase import HorseProfileUsecase


class SuccessMessageResponse(BaseModel):
    message: str = "success"


class HorseProfileController:
    def __init__(self, usecase: HorseProfileUsecase) -> None:
        self.__usecase = usecase

    def create(self, horse_profile: HorseProfile) -> str:
        try:
            horse_id = self.__usecase.add_horse_profile(**horse_profile.dict())
            return horse_id
        except DuplicationError:
            raise HTTPException(status_code=400, detail="Already exists")

    def update(self, horse_profile: HorseProfile) -> dict:
        try:
            __horse_profile = self.__usecase.update_horse_profile(**horse_profile.dict())
            return __horse_profile.to_dict()
        except NotFoundError:
            raise HTTPException(status_code=404, detail="Not found")

    def delete(self, horse_id: str) -> SuccessMessageResponse:
        try:
            self.__usecase.delete_horse_profile(horse_id=horse_id)
            return SuccessMessageResponse()
        except NotFoundError:
            raise HTTPException(status_code=404, detail="Not found")

    def retrieve_by(self, horse_id: str) -> dict:
        try:
            horse_profile = self.__usecase.get_horse_profile_by(horse_id)
            return horse_profile.to_dict()
        except NotFoundError:
            raise HTTPException(status_code=404, detail="Not found")

    def retrieve_by_breeder(self, breeder_id: str) -> dict:
        try:
            horse_profile = self.__usecase.get_horse_profile_by_breeder(breeder_id)
            return horse_profile.to_dict()
        except NotFoundError:
            raise HTTPException(status_code=404, detail="Not found")

    def retrieve_by_owner(self, owner_id: str) -> dict:
        try:
            horse_profile = self.__usecase.get_horse_profile_by_owner(owner_id)
            return horse_profile.to_dict()
        except NotFoundError:
            raise HTTPException(status_code=404, detail="Not found")

    def retrieve_by_trainer(self, trainer_id: str) -> dict:
        try:
            horse_profile = self.__usecase.get_horse_profile_by_trainer(trainer_id)
            return horse_profile.to_dict()
        except NotFoundError:
            raise HTTPException(status_code=404, detail="Not found")
