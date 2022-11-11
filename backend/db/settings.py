import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

# .envから環境変数の読み込み
load_dotenv()

# DBの設定
DATABASE = os.environ['DATABASE']
USER = os.environ['USER']
PASSWORD = os.environ['PASSWORD']
HOST = os.environ['HOST']
PORT = os.environ['PORT']
DB_NAME = os.environ['DB_NAME']

SQLALCHEMY_DATABASE_URL = '{}://{}:{}@{}:{}/{}'.format(DATABASE, USER, PASSWORD, HOST, PORT, DB_NAME)

# DB接続するためのEngineインスタンス
ENGINE = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True  # Trueだと実行のたびにSQLが出力される
)

# DB_NAMEが名前であるdatabaseが存在しない場合は自動で作成
if not database_exists(ENGINE.url):
    try:
        create_database(ENGINE.url)
    except OperationalError:
        pass

# DBに対してORM操作するときに利用
SESSION = sessionmaker(
    autocommit=False, autoflush=False, bind=ENGINE
)

# 各modelで利用
# classとDBをMapping
Base = declarative_base()
