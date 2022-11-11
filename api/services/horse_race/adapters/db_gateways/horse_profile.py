from typing import Optional

from api.services.horse_race.domains.horse_profile.schema import HorseProfile
from api.services.horse_race.domains.horse_profile.builder import HorseProfileBuilder
from api.services.horse_race.domains.horse_profile.interfaces.db_gateway import HorseProfileDBGatewayInterface
from api.services.horse_race.infrastructures.db_driver.base import Base
from sqlalchemy.engine.base import Connectable
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, String


class NotFoundError(Exception):
    pass


class DuplicationError(Exception):
    pass


class HorseProfileModel(Base):

    horse_profile_builder: HorseProfileBuilder = HorseProfileBuilder()

    __tablename__ = 'horse_profile'

    horse_id = Column(String(255), primary_key=True)
    breeder_id = Column(String(255), nullable=False)
    owner_id = Column(String(255), nullable=False)
    trainer_id = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    sex = Column(String(255))
    birthday = Column(DateTime)
    father_id = Column(String(255))
    mother_id = Column(String(255))

    @classmethod
    def from_entity(cls, horse_profile: HorseProfile) -> "HorseProfileModel":
        assert isinstance(horse_profile, HorseProfile)
        return HorseProfileModel(
            horse_id=horse_profile.horse_id,
            breeder_id=horse_profile.breeder_id,
            owner_id=horse_profile.owner_id,
            trainer_id=horse_profile.trainer_id,
            name=horse_profile.name,
            sex=horse_profile.sex,
            birthday=horse_profile.birthday,
            age=horse_profile.age,
            father_id=horse_profile.father_id,
            mother_id=horse_profile.mother_id
        )

    def to_entity(self) -> HorseProfile:
        return self.horse_profile_builder().new(
            horse_id=self.horse_id,
            breeder_id=self.breeder_id,
            owner_id=self.owner_id,
            trainer_id=self.trainer_id,
            name=self.name,
            sex=self.sex,
            birthday=self.birthday,
            age=self.age,
            father_id=self.father_id,
            mother_id=self.mother_id
        ).build()

    def update_by(self, horse_profile: HorseProfile) -> None:
        self.horse_id = horse_profile.horse_id
        self.breeder_id = horse_profile.breeder_id
        self.owner_id = horse_profile.owner_id
        self.trainer_id = horse_profile.trainer_id
        self.name = horse_profile.name
        self.sex = horse_profile.sex
        self.birthday = horse_profile.birthday
        self.age = horse_profile.age
        self.father_id = horse_profile.father_id
        self.mother_id = horse_profile.mother_id


class HorseProfileDBGateway(HorseProfileDBGatewayInterface):
    def __init__(self, engine: Connectable) -> None:
        HorseProfileModel.metadata.bind = engine
        self.__horse_profile = sessionmaker(engine)()

    def retrieve(self, horse_id: str) -> HorseProfile:
        model: Optional[HorseProfile] = self.__horse_profile.query(HorseProfileModel).get(horse_id)
        if model is None:
            raise NotFoundError
        return model.to_entity()

    def select_by_breeder(self, breeder_id: str) -> list[HorseProfile]:
        models: Optional[HorseProfile] = self.__horse_profile.query(HorseProfileModel).filter_by(breeder_id).all()
        if models is None:
            raise NotFoundError
        return [model.to_entity() for model in models]

    def select_by_owner(self, owner_id: str) -> list[HorseProfile]:
        models: Optional[HorseProfile] = self.__horse_profile.query(HorseProfileModel).filter_by(owner_id).all()
        if models is None:
            raise NotFoundError
        return [model.to_entity() for model in models]

    def select_by_trainer(self, trainer_id: str) -> list[HorseProfile]:
        models: Optional[HorseProfile] = self.__horse_profile.query(HorseProfileModel).filter_by(trainer_id).all()
        if models is None:
            raise NotFoundError
        return [model.to_entity() for model in models]

    def list(self) -> list[HorseProfile]:
        models: list[HorseProfile] = self.__horse_profile.query(HorseProfileModel).all()
        return [model.to_entity() for model in models]

    def create(self, horse_profile: HorseProfile) -> str:
        if self.has(horse_id=self.horse_id):
            raise DuplicationError
        model = HorseProfileModel.from_entity(horse_profile)
        self.__horse_profile.add(model)
        self.__horse_profile.commit()
        return model.horse_id

    def update(self, horse_profile: HorseProfile) -> HorseProfile:
        model: Optional[HorseProfile] = self.__horse_profile.query(HorseProfileModel).get(horse_profile.horse_id)
        if model is None:
            raise NotFoundError
        model.update(horse_profile)
        self.__horse_profile.commit()
        return horse_profile

    def delete(self, horse_id: str) -> None:
        model: Optional[HorseProfile] = self.__horse_profile.query(HorseProfileModel).get(horse_id)
        if model is None:
            raise NotFoundError
        self.__horse_profile.delete(model)
        self.__horse_profile.commit()

    def has(self, horse_id: str) -> bool:
        model: Optional[HorseProfile] = self.__horse_profile.query(HorseProfileModel).get(horse_id)
        if model is None:
            return False
        else:
            return True

    def has_breeder(self, breeder_id: str) -> bool:
        model: Optional[HorseProfile] = self.__horse_profile.query(HorseProfileModel).get(breeder_id)
        if model is None:
            return False
        else:
            return True

    def has_owner(self, owner_id: str) -> bool:
        model: Optional[HorseProfile] = self.__horse_profile.query(HorseProfileModel).get(owner_id)
        if model is None:
            return False
        else:
            return True

    def has_trainer(self, trainer_id: str) -> bool:
        model: Optional[HorseProfile] = self.__horse_profile.query(HorseProfileModel).get(trainer_id)
        if model is None:
            return False
        else:
            return True
