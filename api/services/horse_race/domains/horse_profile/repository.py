from api.services.horse_race.domains.horse_profile.schema import HorseProfile
from api.services.horse_race.domains.horse_profile.interfaces.db_gateway import HorseProfileDBGatewayInterface


class HorseProfileRepository:

    horse_profile_db_gateway: HorseProfileDBGatewayInterface

    @classmethod
    def list(cls) -> list[HorseProfile]:
        return cls.horse_profile_db_gateway.list()

    @classmethod
    def select_by(cls, horse_id: str) -> HorseProfile:
        return cls.horse_profile_db_gateway.retrieve(horse_id)

    @classmethod
    def select_by_breeder(cls, breeder_id: str) -> HorseProfile:
        return cls.horse_profile_db_gateway.select_by_breeder(breeder_id)

    @classmethod
    def select_by_owner(cls, owner_id: str) -> HorseProfile:
        return cls.horse_profile_db_gateway.select_by_owner(owner_id)

    @classmethod
    def select_by_trainer(cls, trainer_id: str) -> HorseProfile:
        return cls.horse_profile_db_gateway.select_by_trainer(trainer_id)

    @classmethod
    def save(cls, horse_profile: HorseProfile) -> str:
        cls.horse_profile_db_gateway.create(horse_profile)
        return horse_profile.horse_id

    @classmethod
    def update(cls, horse_profile: HorseProfile) -> HorseProfile:
        return cls.horse_profile_db_gateway.update(horse_profile)

    @classmethod
    def delete(cls, horse_id: str) -> None:
        cls.horse_profile_db_gateway.delete(horse_id)
