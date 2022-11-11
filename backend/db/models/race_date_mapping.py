from sqlalchemy import Column, String, Date
from backend.db.settings import Base, ENGINE


class RaceDateMapping(Base):
    __tablename__ = 'race_date_mapping'

    race_id = Column(String(255), primary_key=True)
    date = Column(Date)


def create_table():
    Base.metadata.create_all(bind=ENGINE)


def delete_table():
    Base.metadata.drop_all(bind=ENGINE)


if __name__ == "__main__":
    # データの初期化
    delete_table()
    create_table()
