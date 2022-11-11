from pydantic.dataclasses import dataclass
from datetime import date


@dataclass
class HorseProfile:
    horse_id: str
    breeder_id: str
    owner_id: str
    trainer_id: str
    name: str
    sex: str
    birthday: date
    age: int
    father_id: str
    mother_id: str

    def to_dict(self) -> dict:
        return {
            "horse_id": self.horse_id,
            "breeder_id": self.breeder_id,
            "owner_id": self.owner_id,
            "trainer_id": self.trainer_id,
            "name": self.name,
            "sex": self.sex,
            "birthday": self.birthday,
            "age": self.age,
            "father_id": self.father_id,
            "mother_id": self.mother_id
        }
