from api.services.horse_race.domains.horse_profile.schema import HorseProfile
from datetime import date


class HorseProfileBuilder:
    def __init__(self) -> None:
        self.__session = False

    def __call__(self) -> "HorseProfileBuilder":
        assert not self.__session
        self.__session = True
        return self

    def new(
        self,
        horse_id: str,
        breeder_id: str,
        owner_id: str,
        trainer_id: str,
        name: str,
        sex: str,
        birthday: date,
        age: int,
        father_id: str,
        mother_id: str
    ) -> "HorseProfileBuilder":
        self.__horse_profile = HorseProfile(
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
        )
        return self

    def reconstruct_from(
        self,
        horse_id: str,
        breeder_id: str,
        owner_id: str,
        trainer_id: str,
        name: str,
        sex: str,
        birthday: date,
        age: int,
        father_id: str,
        mother_id: str
    ) -> "HorseProfileBuilder":
        assert self.__session
        self.__horse_profile = HorseProfile(
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
        )
        return self

    def build(self) -> HorseProfile:
        assert self.__session
        self.__session = False
        return self.__horse_profile
