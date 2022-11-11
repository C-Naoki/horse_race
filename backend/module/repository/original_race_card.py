import requests
import re
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from datetime import date, datetime
from tqdm import tqdm
from backend.environment.mapping import Mapping


class OriginalRaceCard():
    def __init__(self, df: pd.DataFrame):
        self.raw_df = df
        self.preprocessing()

    @classmethod
    def scrape(cls, race_id_ls: list):
        venue_id = race_id_ls[0][:10]
        place = venue_id[4:6]
        pbar = tqdm(total=len(race_id_ls))
        raw_df = pd.DataFrame()
        for race_id in race_id_ls:
            pbar.update(1)
            pbar.set_description(f"original race card in {[k for k, v in Mapping.PLACE_ID_MAPPING.items() if v == place][0]} {venue_id[6:8]}回")
            url = 'https://race.netkeiba.com/race/shutuba.html?race_id=' + race_id
            _df = pd.read_html(url)[0]
            _df = _df.T.reset_index(level=0, drop=True).T
            html = requests.get(url)
            html.encoding = "EUC-JP"
            soup = BeautifulSoup(html.text, "html.parser")
            texts = soup.find('div', attrs={'class': 'RaceData01'}).text
            texts = re.findall(r'\w+', texts)
            for text in texts:
                if 'm' in text:
                    _df['course_len'] = [int(re.findall(r"(\d+)m", text)[0])] * len(_df)
                if text in ["曇", "晴", "雨", "小雨", "小雪", "雪"]:
                    _df["weather"] = [text] * len(_df)
                if text in ["良", "稍重", "重"]:
                    _df["ground_state"] = [text] * len(_df)
                if '不' in text:
                    _df["ground_state"] = ['不良'] * len(_df)
                # 2020/12/13追加
                if '稍' in text:
                    _df["ground_state"] = ['稍重'] * len(_df)
                if '芝' in text:
                    _df['course_type'] = ['芝'] * len(_df)
                if '障' in text:
                    _df['course_type'] = ['障害'] * len(_df)
                if 'ダ' in text:
                    _df['course_type'] = ['ダート'] * len(_df)
                if "右" in text:
                    _df["turn"] = ['右'] * len(_df)
                elif "左" in text:
                    _df["turn"] = ['左'] * len(_df)
                elif '直線' in text:
                    _df["turn"] = ['直線'] * len(_df)
            texts = soup.find('div', attrs={'class': 'RaceData02'}).text
            texts = re.findall(r'\w+', texts)
            for text in texts:
                if text in ["新馬", "未勝利", "１勝クラス", "２勝クラス", "３勝クラス", "オープン"]:
                    _df['race_class'] = [text] * len(_df)
            _df["nth_race"] = [int(race_id[-2:])] * len(_df)
            _df["nth_day"] = [int(race_id[8:10])] * len(_df)
            _df["nth_time"] = [int(race_id[6:8])] * len(_df)
            for info in soup.find_all('dd'):
                if info.get('class') == ['Active']:
                    d = datetime.strptime(info.find('a').get('href').split('&')[0][-8:], '%Y%m%d')
                    _df['date'] = [date(d.year, d.month, d.day)] * len(_df)
            # horse_id
            horse_id_list = []
            horse_td_list = soup.find_all("td", attrs={'class': 'HorseInfo'})
            for td in horse_td_list:
                horse_id = re.findall(r'\d+', td.find('a')['href'])[0]
                horse_id_list.append(horse_id)
            # jockey_id
            jockey_id_list = []
            jockey_td_list = soup.find_all("td", attrs={'class': 'Jockey'})
            for td in jockey_td_list:
                jockey_id = re.findall(r'\d+', td.find('a')['href'])[0]
                jockey_id_list.append(jockey_id)
            _df['horse_id'] = horse_id_list
            _df['jockey_id'] = jockey_id_list
            _df['race_id'] = [race_id] * len(_df)
            raw_df = pd.concat([raw_df, _df])
        raw_df.rename(columns={
            '枠': 'bracket_number',
            '馬番': 'horse_number',
            '性齢': 'sex&age',
            '斤量': 'weight_carry',
            '馬体重(増減)': 'weight_horse'
        }, inplace=True)
        # 型を変更する
        raw_df = raw_df.astype({'bracket_number': int, 'horse_number': int, 'weight_carry': int})
        raw_df.index = list(range(len(raw_df)))
        return cls(raw_df)

    # 前処理
    def preprocessing(self):
        _df = self.raw_df.copy()
        _df["age"] = _df["sex&age"].map(lambda x: str(x)[1:]).astype(int)
        # 馬体重を馬体重と馬体重差に分割
        _df = pd.concat([_df, _df['weight_horse'].str.split('(', expand=True)], axis=1).drop('weight_horse', axis=1)
        _df.rename(columns={0: 'weight_horse', 1: 'diff_weight_horse'}, inplace=True)
        _df['weight_horse'] = _df['weight_horse'].replace('計不', 0).replace('--', 0)
        _df['diff_weight_horse'] = _df['diff_weight_horse'].map(lambda x: x.replace(')', '') if x else 0)
        _df["month_sin"] = _df["date"].map(lambda x: np.sin(2*np.pi*(date(x.year, x.month, x.day)-date(x.year, 1, 1)).days/366))
        _df["month_cos"] = _df["date"].map(lambda x: np.cos(2*np.pi*(date(x.year, x.month, x.day)-date(x.year, 1, 1)).days/366))
        _df['venue'] = _df.index.map(lambda x: str(x)[4:6])
        _df['n_horses'] = _df.groupby('race_id').max(numeric_only=True)['horse_number']
        _df["course_len"] = _df["course_len"].astype(float) // 100
        # 型を変更する
        _df = _df.astype({'weight_horse': int, 'diff_weight_horse': int})
        # 削除する列を選択
        _df.drop([
            '印',
            '馬名',
            'sex&age',
            '騎手',
            '厩舎',
            'Unnamed: 9_level_1',
            '人気',
            '登録',
            'メモ',
        ], axis=1, inplace=True)
        try:
            _df[['weather', 'ground_state']]
        except Exception:
            # レース当日にならないと未来の天気及び馬場状況は判定できないため、それぞれ晴、良と仮定する。
            _df.loc[:, 'weather'] = '晴'
            _df.loc[:, 'ground_state'] = '良'
        self.preprocessed_df = _df
