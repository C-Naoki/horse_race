from backend.module.repository import (
    Result,
    Race,
    HorseProfile,
    RaceCard,
    Refund
)
from backend.module.crud.read import (
    read_race_id_ls,
    read_horse_id_ls
)
scrape_year = '2022'

race_id_dict = {}
for place in range(1, 11):
    race_id_place = {}
    for kai in range(1, 13):
        race_id_kai = []
        for day in range(1, 13):
            for r in range(1, 13):
                race_id = scrape_year + str(place).zfill(2) + str(kai).zfill(2) + str(day).zfill(2) + str(r).zfill(2)
                race_id_kai.append(race_id)
        race_id_place[kai] = race_id_kai
    race_id_dict[place] = race_id_place

# Resultのスクレイピング
Result.scrape(race_id_dict)

# id_lsの取得
race_id_ls = read_race_id_ls()
horse_id_ls = read_horse_id_ls()

# HorseProfileのスクレイピング
HorseProfile.scrape(horse_id_ls)

# Raceのスクレイピング
Race.scrape(race_id_ls)

# RaceCardのスクレイピング
RaceCard.scrape(race_id_ls)

# Returnのスクレイピング
Refund.scrape(race_id_ls)
