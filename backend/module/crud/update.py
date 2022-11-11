import pandas as pd
from typing import Callable
from backend.db.settings import SESSION
from backend.db.models import (
    HorseProfile,
    Result,
    Race,
    Refund,
    RaceCard,
    RaceDateMapping
)
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm.session import Session


def update(func: Callable[[pd.DataFrame, Session], None]) -> Callable[[pd.DataFrame], None]:
    def wrapper(df: pd.DataFrame) -> None:
        try:
            session = SESSION()
            func(df, session)
            session.close()
        except OperationalError:
            print('サーバが起動していません。')
    return wrapper


@update
def update_horse_profile(df: pd.DataFrame, session: Session) -> None:
    datas: list = list()
    for _, row in df.iterrows():
        if not session.query(HorseProfile).filter(HorseProfile.horse_id == row['horse_id']).all():
            data = dict()
            data['horse_id'] = row['horse_id']
            data['breeder_id'] = row['breeder_id']
            data['owner_id'] = row['owner_id']
            data['trainer_id'] = row['trainer_id']
            data['near_relation_horse_id_0'] = row['near_relation_horse_id_0']
            data['near_relation_horse_id_1'] = row['near_relation_horse_id_1']
            data['horse_name'] = row['horse_name']
            data['breeder_name'] = row['breeder_name']
            data['owner_name'] = row['owner_name']
            data['trainer_name'] = row['trainer_name']
            data['near_relation_horse_name_0'] = row['near_relation_horse_name_0']
            data['near_relation_horse_name_1'] = row['near_relation_horse_name_1']
            data['sex'] = row['sex']
            data['birthday'] = row['birthday']
            data['father_id'] = row['father_id']
            data['father_name'] = row['father_name']
            data['mother_id'] = row['mother_id']
            data['mother_name'] = row['mother_name']
            datas.append(data)
    session.execute(HorseProfile.__table__.insert(), datas)
    session.commit()


@update
def update_result(df: pd.DataFrame, session: Session) -> None:
    datas: list = list()
    for _, row in df.iterrows():
        if not session.query(Result).filter(Result.race_id == row['race_id'] and Result.horse_id == row['horse_id']).all():
            data = dict()
            data['race_id'] = row['race_id']
            data['horse_id'] = row['horse_id']
            data['order'] = row['order']
            data['odds'] = row['odds']
            data['last3F'] = row['last3F']
            data['time_idx'] = row['time_idx']
            data['ground_state_idx'] = row['ground_state_idx']
            data['passing'] = row['passing']
            data['remark'] = row['remark']
            data['diff_time'] = row['diff_time']
            data['prize'] = row['prize']
            datas.append(data)
    session.execute(Result.__table__.insert(), datas)
    session.commit()


@update
def update_race_card(df: pd.DataFrame, session: Session) -> None:
    datas: list = list()
    for _, row in df.iterrows():
        if not session.query(RaceCard).filter(RaceCard.race_id == row['race_id'] and RaceCard.horse_id == row['horse_id']).all():
            data = dict()
            data['race_id'] = row['race_id']
            data['horse_id'] = row['horse_id']
            data['jockey_id'] = row['jockey_id']
            data['jockey_name'] = row['jockey_name']
            data['bracket_number'] = row['bracket_number']
            data['horse_number'] = row['horse_number']
            data['weight_carry'] = row['weight_carry']
            data['popular'] = row['popular']
            data['age'] = row['age']
            data['weight_horse'] = row['weight_horse']
            data['diff_weight_horse'] = row['diff_weight_horse']
            datas.append(data)
    session.execute(RaceCard.__table__.insert(), datas)
    session.commit()


@update
def update_race(df: pd.DataFrame, session: Session) -> None:
    datas: list = list()
    for _, row in df.iterrows():
        if not session.query(Race).filter(Race.race_id == row['race_id']).all():
            data = dict()
            data['race_id'] = row['race_id']
            data['race_name'] = row['race_name']
            data['turn'] = row['turn']
            data['weather'] = row['weather']
            data['course_len'] = row['course_len']
            data['course_type'] = row['course_type']
            data['ground_state'] = row['ground_state']
            data['race_class'] = row['race_class']
            data['nth_race'] = row['nth_race']
            data['nth_day'] = row['nth_day']
            data['nth_time'] = row['nth_time']
            data['venue'] = row['venue']
            datas.append(data)
    session.execute(Race.__table__.insert(), datas)
    session.commit()


@update
def update_race_date_mapping(df: pd.DataFrame, session: Session) -> None:
    datas: list = list()
    for _, row in df.iterrows():
        if not session.query(RaceDateMapping).filter(RaceDateMapping.race_id == row['race_id']).all():
            data = dict()
            data['race_id'] = row['race_id']
            data['date'] = row['date']
            datas.append(data)
    session.execute(RaceDateMapping.__table__.insert(), datas)
    session.commit()


@update
def update_refund(df: pd.DataFrame, session: Session) -> None:
    datas: list = list()
    for _, row in df.iterrows():
        if not session.query(Refund).filter(Refund.race_id == row['race_id'] and Refund.betting == row['betting']).all():
            data = dict()
            data['race_id'] = row['race_id']
            data['betting'] = row['betting']
            data['horse_number'] = row['horse_number']
            data['money'] = row['money']
            data['popular'] = row['popular']
            datas.append(data)
    session.execute(Refund.__table__.insert(), datas)
    session.commit()
