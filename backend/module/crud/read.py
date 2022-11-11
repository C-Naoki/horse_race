import pandas as pd
from backend.db.settings import SESSION
from backend.db.models import (
    Result,
    HorseProfile,
    Race,
    Refund,
    RaceCard,
    RaceDateMapping
)


def read_race_id_ls() -> list[str]:
    session = SESSION()
    race_id_ls = session.query(Result.race_id).all()
    session.close()
    return list(set(race_id_ls))


def read_horse_id_ls() -> list[str]:
    session = SESSION()
    horse_id_ls = session.query(Result.horse_id).all()
    session.close()
    return list(set(horse_id_ls))


def read_horse_profile() -> pd.DataFrame:
    session = SESSION()
    sql_statement = session.query(HorseProfile).filter().statement
    df = pd.read_sql(
        sql_statement,
        session.bind
    )
    session.close()
    return df


def read_result() -> pd.DataFrame:
    session = SESSION()
    sql_statement = session.query(Result).filter().statement
    df = pd.read_sql(
        sql_statement,
        session.bind
    )
    session.close()
    return df


def read_race() -> pd.DataFrame:
    session = SESSION()
    sql_statement = session.query(Race).filter().statement
    df = pd.read_sql(
        sql_statement,
        session.bind
    )
    session.close()
    return df


def read_refund() -> pd.DataFrame:
    session = SESSION()
    sql_statement = session.query(Refund).filter().statement
    df = pd.read_sql(
        sql_statement,
        session.bind
    )
    session.close()
    return df


def read_race_card() -> pd.DataFrame:
    session = SESSION()
    sql_statement = session.query(RaceCard).filter().statement
    df = pd.read_sql(
        sql_statement,
        session.bind
    )
    session.close()
    return df


def read_race_date_mapping() -> pd.DataFrame:
    session = SESSION()
    sql_statement = session.query(RaceDateMapping).filter().statement
    df = pd.read_sql(
        sql_statement,
        session.bind
    )
    session.close()
    return df
