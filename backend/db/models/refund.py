from sqlalchemy import Column, String
from backend.db.settings import Base, ENGINE


class Refund(Base):
    __tablename__ = 'refund'

    race_id = Column(String(255), primary_key=True)
    betting = Column(String(255), primary_key=True)
    horse_number = Column(String(255))
    money = Column(String(255))
    popular = Column(String(255))


def create_table():
    Base.metadata.create_all(bind=ENGINE)


def delete_table():
    Base.metadata.drop_all(bind=ENGINE)


if __name__ == "__main__":
    # データの初期化
    delete_table()
    create_table()
