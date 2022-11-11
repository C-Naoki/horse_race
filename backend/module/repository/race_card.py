import copy
import pandas as pd
import re
import time
from bs4 import BeautifulSoup
from tqdm import tqdm
from backend.environment.netkeiba import Netkeiba
from backend.module.mapping import RaceDateMapping
from backend.module.preparing import DataMerger
from backend.module.repository import Result
from backend.module.crud.update import update_race_card
from backend.module.crud.read import read_race_card


class RaceCard(DataMerger):

    race_date_mapping = RaceDateMapping()
    raw_df = read_race_card()

    def __init__(self) -> None:
        # 取得したデータの処理
        self.preprocessing()
        # resultをmerge
        merged_with_result_df = self.merge_result()
        # date情報をmappingから付与する
        added_date_df = merged_with_result_df.merge(self.race_date_mapping.df)
        super().__init__(added_date_df)

    @staticmethod
    def scrape(race_id_ls: list) -> None:
        """
        馬の過去成績データをスクレイピングする関数
        Parameters:
        ----------
        race_id_ls : {place: race_id_place}
            レースIDの辞書
        race_id_place : {kai: race_id_kai}
            ある開催地限定のレースID
        race_id_kai: list
            ある回に開催されたレース限定のレースID

        Returns:
        ----------
        race_cards_df : pandas.DataFrame
            全レースの過去成績データ
        """

        # race_idをkeyにしてDataFrame型を格納
        race_cards = {}
        bf_upd_df = read_race_card()
        for race_id in tqdm(race_id_ls):
            race_id = race_id.race_id
            if bf_upd_df['race_id'].isin([race_id]).any():
                continue
            try:
                time.sleep(1)
                url = "https://db.netkeiba.com/race/" + race_id
                html = Netkeiba.SESSION.get(url)
                html.encoding = "EUC-JP"
                soup = BeautifulSoup(html.text, "html.parser")
                # 馬IDをスクレイピング
                horse_id_ls = []
                horse_a_ls = soup.find("table", attrs={"summary": "レース結果"}).find_all(
                    "a", attrs={"href": re.compile("^/horse")}
                )
                for a in horse_a_ls:
                    horse_id = re.findall(r"\d+", a["href"])
                    horse_id_ls.append(horse_id[0])
                # 騎手IDをスクレイピング
                jockey_id_ls = []
                jockey_a_ls = soup.find("table", attrs={"summary": "レース結果"}).find_all(
                    "a", attrs={"href": re.compile("^/jockey")}
                )
                for a in jockey_a_ls:
                    jockey_id = re.findall(r"\d+", a["href"])
                    jockey_id_ls.append(jockey_id[0])
                # メインとなるテーブルデータを取得
                _df = pd.read_html(url)[0]
                _df.drop(['着順', '馬名', '調教師', '着差', 'タイム', '単勝'], axis=1, inplace=True)
                _df.columns = [
                    'bracket_number',
                    'horse_number',
                    'sex&age',
                    'weight_carry',
                    'jockey_name',
                    'popular',
                    'weight_horse'
                ]
                # int型においてNaNが利用できないため、0で埋める。
                _df.fillna({'popular': 0}, inplace=True)
                # 馬体重を馬体重と馬体重差に分割
                _df = pd.concat([_df, _df['weight_horse'].str.split('(', expand=True)], axis=1).drop('weight_horse', axis=1)
                _df.rename(columns={0: 'weight_horse', 1: 'diff_weight_horse'}, inplace=True)
                _df['weight_horse'] = _df['weight_horse'].replace('計不', 0)
                _df['diff_weight_horse'] = _df['diff_weight_horse'].map(lambda x: x.replace(')', '') if x else 0)
                # 性齢から年齢のみを取り出す。
                _df['age'] = _df['sex&age'].map(lambda x: re.sub('牝|牡|セ', '', x))
                _df.drop('sex&age', axis=1, inplace=True)
                # 型を変更する
                _df = _df.astype({'weight_horse': 'int', 'diff_weight_horse': 'int', 'age': 'int', 'popular': 'int'})
                _df["horse_id"] = horse_id_ls
                _df["jockey_id"] = jockey_id_ls
                # インデックスをrace_idとhorse_idのMultiIndexにする
                _df['race_id'] = [race_id] * len(_df)
                # 馬番順に変更する
                _df.sort_values('horse_number', inplace=True)
                race_cards[race_id] = _df
            except KeyboardInterrupt:
                break
        try:
            # pd.DataFrame型にして一つのデータにまとめる
            race_cards_df = pd.concat([race_cards[key] for key in race_cards])
            # スクレイピングしたデータをデータベースに反映させる。
            update_race_card(race_cards_df)
        except ValueError:
            pass

    def preprocessing(self):
        _df = copy.deepcopy(self.raw_df)
        _df.drop(['jockey_name'], axis=1, inplace=True)
        self.preprocessed_df = _df

    def merge_result(self) -> pd.DataFrame:
        result = Result()
        return pd.merge(self.preprocessed_df, result.preprocessed_df)
