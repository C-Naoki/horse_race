from sqlalchemy import Column, Integer, Float, String
from backend.db.settings import Base, ENGINE


class Result(Base):
    __tablename__ = 'result'

    horse_id = Column(String(255), primary_key=True)
    race_id = Column(String(255), primary_key=True)
    order = Column(String(255))
    odds = Column(Float)
    last3F = Column(Float)
    time_idx = Column(Integer)
    ground_state_idx = Column(Integer)
    passing = Column(String(255))
    remark = Column(String(255))
    diff_time = Column(String(255))
    prize = Column(Float)


def create_table():
    Base.metadata.create_all(bind=ENGINE)


def delete_table():
    Base.metadata.drop_all(bind=ENGINE)


if __name__ == "__main__":
    # データの初期化
    delete_table()
    create_table()
