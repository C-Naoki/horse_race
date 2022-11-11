from typing import Optional

from sqlalchemy.engine import create_engine
from sqlalchemy.engine.base import Connectable


def get_engine(dialect: str, username: str, password: str, host: str, port: str, db_name: str) -> Connectable:
    return create_engine('{}://{}:{}@{}:{}/{}'.format(dialect, username, password, host, port, db_name))


def get_db_connection_str(
    dialect: Optional[str],
    username: Optional[str],
    password: Optional[str],
    host: Optional[str],
    port: Optional[str],
    db_name: Optional[str],
) -> str:
    return f"{dialect}://{username}:{password}@{host}:{port}/{db_name}"
