from sqlalchemy import Column, String, Date
from backend.db.settings import Base, ENGINE


class HorseProfile(Base):
    __tablename__ = 'horse_profile'

    horse_id = Column(String(255), primary_key=True)
    horse_name = Column(String(255), nullable=False)
    breeder_id = Column(String(255), nullable=False)
    breeder_name = Column(String(255), nullable=False)
    owner_id = Column(String(255), nullable=False)
    owner_name = Column(String(255), nullable=False)
    trainer_id = Column(String(255), nullable=False)
    trainer_name = Column(String(255), nullable=False)
    near_relation_horse_id_0 = Column(String(255))
    near_relation_horse_id_1 = Column(String(255))
    near_relation_horse_name_0 = Column(String(255))
    near_relation_horse_name_1 = Column(String(255))
    sex = Column(String(255))
    birthday = Column(Date)
    father_id = Column(String(255))
    father_name = Column(String(255))
    mother_id = Column(String(255))
    mother_name = Column(String(255))


def create_table():
    Base.metadata.create_all(bind=ENGINE)


def delete_table():
    Base.metadata.drop_all(bind=ENGINE)


if __name__ == "__main__":
    # データの初期化
    delete_table()
    create_table()
