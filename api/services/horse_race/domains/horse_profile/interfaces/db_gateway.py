import abc
from typing import Optional
from api.services.horse_race.domains.horse_profile.schema import HorseProfile


class HorseProfileDBGatewayInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def retrieve(self, horse_id: str) -> HorseProfile:
        pass

    @abc.abstractmethod
    def select_by_breeder(self, breeder_id: str) -> list[HorseProfile]:
        pass

    @abc.abstractmethod
    def select_by_owner(self, owner_id: str) -> list[HorseProfile]:
        pass

    @abc.abstractmethod
    def select_by_trainer(self, trainer_id: str) -> list[HorseProfile]:
        pass

    @abc.abstractmethod
    def list(self) -> list[HorseProfile]:
        pass

    @abc.abstractmethod
    def create(self, horse_profile: HorseProfile) -> str:
        pass

    @abc.abstractmethod
    def delete(self, horse_profile: HorseProfile) -> None:
        pass

    @abc.abstractmethod
    def has(self, horse_id: Optional[str]) -> bool:
        pass

    @abc.abstractmethod
    def has_breeder(self, breeder_id: Optional[str]) -> bool:
        pass

    @abc.abstractmethod
    def has_owner(self, owner_id: Optional[str]) -> bool:
        pass

    @abc.abstractmethod
    def has_trainer(self, trainer_id: Optional[str]) -> bool:
        pass
