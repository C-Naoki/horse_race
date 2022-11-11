import pandas as pd
import numpy as np
import re
import time
from datetime import datetime, date, timedelta
from bs4 import BeautifulSoup
from tqdm import tqdm
from backend.environment.netkeiba import Netkeiba
from backend.environment.mapping import Mapping
from backend.module.mapping import RaceDateMapping
from backend.module.crud.update import update_race
from backend.module.crud.read import read_race


class Race:

    race_date_mapping = RaceDateMapping()
    raw_df = read_race()

    def __init__(self) -> None:
        self.preprocessing()

    @staticmethod
    def scrape(race_id_ls: list) -> None:
        """
        馬の過去成績データをスクレイピングする関数
        Parameters:
        ----------
        race_id_ls : list
            レースIDのリスト(resultから取得)

        Returns:
        ----------
        races_df : pandas.DataFrame
            全レースの過去成績データ
        """

        # race_idをkeyにしてDataFrame型を格納
        races = {}
        bf_upd_df = read_race()
        for race_id in tqdm(race_id_ls):
            race_id = race_id.race_id
            if bf_upd_df['race_id'].isin([race_id]).any():
                continue
            try:
                time.sleep(1)
                url = "https://db.netkeiba.com/race/" + race_id
                # メインとなるテーブルデータを取得
                df = pd.DataFrame([])
                html = Netkeiba.SESSION.get(url)
                html.encoding = "EUC-JP"
                soup = BeautifulSoup(html.text, "html.parser")
                # 天候、レースの種類、コースの長さ、馬場の状態、日付をスクレイピング
                texts = (
                    soup.find("div", attrs={"class": "data_intro"}).find_all("p")[0].text
                    + soup.find("div", attrs={"class": "data_intro"}).find_all("p")[1].text
                )
                info = re.findall(r'\w+', texts)
                for text in info:
                    if text in ["芝", "ダート"]:
                        df["course_type"] = [text]
                    if "障" in text:
                        df["course_type"] = ["障害"]
                        df["turn"] = ["障害"]
                    if "m" in text:
                        df["course_len"] = [int(re.findall(r"(\d+)m", text)[0])]
                    if text in ["良", "稍重", "重", "不良"]:
                        df["ground_state"] = [text]
                    if text in ["曇", "晴", "雨", "小雨", "小雪", "雪"]:
                        df["weather"] = [text]
                    if all([w in text for w in ['年', '月', '日']]):
                        d = datetime.strptime(text, "%Y年%m月%d日")
                        df["date"] = [date(d.year, d.month, d.day)]
                    if "右" in text:
                        df["turn"] = ["右"]
                    elif "左" in text:
                        df["turn"] = ["左"]
                    elif "直線" in text:
                        df["turn"] = ["直線"]
                    if "新馬" in text:
                        df["race_class"] = ["新馬"]
                    elif "未勝利" in text:
                        df["race_class"] = ["未勝利"]
                    elif "1勝クラス" in text or "500万下" in text:
                        df["race_class"] = ["1勝クラス"]
                    elif "2勝クラス" in text or "1000万下" in text:
                        df["race_class"] = ["2勝クラス"]
                    elif "3勝クラス" in text or "1600万下" in text:
                        df["race_class"] = ["3勝クラス"]
                    elif "オープン" in text:
                        df["race_class"] = ["オープン"]
                df['race_name'] = [soup.find_all('h1')[1].text]
                df["nth_race"] = [int(race_id[-2:])]
                df["nth_day"] = [int(race_id[8:10])]
                df["nth_time"] = [int(race_id[6:8])]
                df["venue"] = [v for v, k in Mapping.PLACE_ID_MAPPING.items() if k == race_id[4:6]]
                df['race_id'] = [race_id]
                races[race_id] = df
            except ValueError:
                print(race_id)
            except KeyboardInterrupt:
                break
        try:
            # pd.DataFrame型にして一つのデータにまとめる
            races_df = pd.concat([races[key] for key in races])
            update_race(races_df)
        except ValueError:
            pass

    def preprocessing(self) -> None:
        # date情報をmappingから付与する
        _df = self.raw_df.merge(self.race_date_mapping.df)

        # 1/1から何日経過したか計算する
        def calc_days(_date: date) -> timedelta:
            return _date - date(_date.year, 1, 1)

        # 季節情報を三角関数に変換
        _df["month_sin"] = _df["date"].map(lambda x: np.sin(2*np.pi*(calc_days(x)).days/366))
        _df["month_cos"] = _df["date"].map(lambda x: np.cos(2*np.pi*(calc_days(x)).days/366))
        _df.drop(['race_name'], axis=1, inplace=True)

        self.preprocessed_df = _df
