from sqlalchemy import Column, Integer, Float, String
from backend.db.settings import Base, ENGINE


class RaceCard(Base):
    __tablename__ = 'race_card'

    horse_id = Column(String(255), primary_key=True)
    race_id = Column(String(255), primary_key=True)
    jockey_id = Column(String(255), nullable=False)
    jockey_name = Column(String(255), nullable=False)
    bracket_number = Column(Integer, nullable=False)
    horse_number = Column(Integer)
    weight_carry = Column(Float(asdecimal=True))
    popular = Column(Integer)
    age = Column(Integer)
    weight_horse = Column(Integer)
    diff_weight_horse = Column(Integer)


def create_table():
    Base.metadata.create_all(bind=ENGINE)


def delete_table():
    Base.metadata.drop_all(bind=ENGINE)


if __name__ == "__main__":
    # データの初期化
    delete_table()
    create_table()
