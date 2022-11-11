from typing import Optional
from api.services.horse_race.domains.horse_profile.schema import HorseProfile
from api.services.horse_race.domains.horse_profile.interfaces.db_gateway import HorseProfileDBGatewayInterface
from api.services.horse_race.domains.horse_profile.repository import HorseProfileRepository
from api.services.horse_race.domains.horse_profile.builder import HorseProfileBuilder
from datetime import date


class HorseProfileUsecase:
    horse_profile_builder: HorseProfileBuilder = HorseProfileBuilder()

    def __init__(self, horse_profile_db_gateway: HorseProfileDBGatewayInterface) -> None:
        HorseProfileRepository.horse_profile_db_gateway = horse_profile_db_gateway

    def add_horse_profile(
        self,
        horse_id: str,
        breeder_id: str,
        owner_id: str,
        trainer_id: str,
        name: str,
        sex: str,
        birthday: date,
        age: int,
        father_id: Optional[str],
        mother_id: Optional[str]
    ) -> str:
        horse_profile = self.horse_profile_builder().new(
            horse_id=horse_id,
            breeder_id=breeder_id,
            owner_id=owner_id,
            trainer_id=trainer_id,
            name=name,
            sex=sex,
            birthday=birthday,
            age=age,
            father_id=father_id,
            mother_id=mother_id
        ).build()
        return HorseProfileRepository.save(horse_profile)

    def update_horse_profile(
        self,
        horse_id: str,
        breeder_id: str,
        owner_id: str,
        trainer_id: str,
        name: str,
        sex: str,
        birthday: date,
        age: int,
        father_id: Optional[str],
        mother_id: Optional[str]
    ) -> HorseProfile:
        horse_profile = self.horse_profile_builder().reconstruct_from(
            horse_id=horse_id,
            breeder_id=breeder_id,
            owner_id=owner_id,
            trainer_id=trainer_id,
            name=name,
            sex=sex,
            birthday=birthday,
            age=age,
            father_id=father_id,
            mother_id=mother_id
        ).build()
        return HorseProfileRepository.update(horse_profile)

    def delete_horse_profile(self, horse_id: str):
        HorseProfileRepository.delete(horse_id)

    def get_horse_profile_by(self, horse_id: str) -> HorseProfile:
        return HorseProfileRepository.select_by(horse_id)

    def get_horse_profile_by_breeder(self, breeder_id: str) -> HorseProfile:
        return HorseProfileRepository.select_by_breeder(breeder_id)

    def get_horse_profile_by_owner(self, owner_id: str) -> HorseProfile:
        return HorseProfileRepository.select_by_owner(owner_id)

    def get_horse_profile_by_trainer(self, trainer_id: str) -> HorseProfile:
        return HorseProfileRepository.select_by_trainer(trainer_id)

    def list(self) -> list[HorseProfile]:
        return HorseProfileRepository.list()
