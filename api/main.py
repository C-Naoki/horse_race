import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.migrations.engine import get_engine
from api.services.horse_race import main as main_horse_profile
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# 通信するアプリ(例: react)のurlを記載。
origins = [
    "http://localhost:3000",
]

engine = get_engine(
    os.environ.get("DATABASE"),
    os.environ.get("USER"),
    os.environ.get("PASSWORD"),
    os.environ.get("HOST"),
    os.environ.get("PORT"),
    os.environ.get("DB_NAME"),
)

app.include_router(main_horse_profile())

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
