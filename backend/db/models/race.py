from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String
from backend.db.settings import Base, ENGINE


class Race(Base):
    __tablename__ = 'race'

    race_id = Column(String(255), primary_key=True)
    race_name = Column(String(255), nullable=False)
    turn = Column(String(255))
    weather = Column(String(255))
    course_len = Column(Integer)
    course_type = Column(String(255))
    ground_state = Column(String(255))
    race_class = Column(String(255))
    nth_race = Column(Integer)
    nth_day = Column(Integer)
    nth_time = Column(Integer)
    venue = Column(String(255))


def create_table():
    Base.metadata.create_all(bind=ENGINE)


def delete_table():
    Base.metadata.drop_all(bind=ENGINE)


if __name__ == "__main__":
    # データの初期化
    delete_table()
    create_table()
