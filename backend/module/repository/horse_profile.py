import copy
import pandas as pd
import re
import time
from datetime import datetime, date
from bs4 import BeautifulSoup
from tqdm import tqdm
from backend.environment.netkeiba import Netkeiba
from backend.module.preparing import DataMerger
from backend.module.mapping import RaceDateMapping
from backend.module.repository import Result
from backend.module.crud.update import update_horse_profile
from backend.module.crud.read import read_horse_profile


class HorseProfile(DataMerger):

    race_date_mapping = RaceDateMapping()
    raw_df = read_horse_profile()

    def __init__(self) -> None:
        # 取得したデータの処理
        self.preprocessing()
        # resultをmerge
        merged_with_result_df = self.merge_result()
        # date情報をmappingから付与する
        added_date_df = merged_with_result_df.merge(self.race_date_mapping.df)
        super().__init__(added_date_df)

    @staticmethod
    def scrape(horse_id_ls: list) -> None:
        """
        馬の過去成績データをスクレイピングする関数
        Parameters:
        ----------
        horse_id_ls : list
            馬IDのリスト
        Returns:
        ----------
        horse_profiles_df : pandas.DataFrame
            全馬の過去成績データ
        """

        # horse_idをkeyにしてDataFrame型を格納
        horse_profiles = {}
        bf_upd_df = read_horse_profile()
        for horse_id in tqdm(horse_id_ls):
            horse_id = horse_id.horse_id
            if bf_upd_df['horse_id'].isin([horse_id]).any():
                continue
            try:
                time.sleep(1)
                url = 'https://db.netkeiba.com/horse/' + horse_id
                html = Netkeiba.SESSION.get(url)
                html.encoding = "EUC-JP"
                df = pd.read_html(html.content)[1]
                # dfのカラム名を英語に変更
                df = df.set_index(0).T
                df = df.loc[:, ['生年月日', '調教師', '馬主', '生産者', '近親馬']]  # 使用するデータのみ抽出
                df.columns = ['birthday', 'trainer_name', 'owner_name', 'breeder_name', 'near_relation_horses']
                df = pd.concat([df, df['near_relation_horses'].str.split('、', expand=True)], axis=1).drop('near_relation_horses', axis=1)
                df.rename(columns={0: 'near_relation_horse_name_0', 1: 'near_relation_horse_name_1'}, inplace=True)
                soup = BeautifulSoup(html.content, "html.parser")
                info_list = soup.find_all('table')[1].find_all('td')
                # 調教師id, 馬主id, 生産者id、誕生日の取得
                for info in info_list:
                    text = info.text
                    if re.sub('[年月日]', '', text).isdigit():
                        d = datetime.strptime(text, "%Y年%m月%d日")
                        df['birthday'] = [date(d.year, d.month, d.day)]
                    try:
                        if "/trainer/" in info.find('a').get('href'):
                            df['trainer_id'] = [re.sub('trainer|/', '', info.find('a').get('href'))]
                        if "/owner/" in info.find('a').get('href'):
                            df['owner_id'] = [re.sub('owner|/', '', info.find('a').get('href'))]
                        if "/breeder/" in info.find('a').get('href'):
                            df['breeder_id'] = [re.sub('breeder|/', '', info.find('a').get('href'))]
                        if "/horse/" in info.find('a').get('href') and "/horse/result/" not in info.find('a').get('href'):
                            for i, _info in enumerate(info.find_all('a')):
                                df['near_relation_horse_id_{}'.format(i)] = [re.sub('horse|/', '', _info.get('href'))]
                    except AttributeError:
                        continue
                # 母id, 父idの取得
                info_list = soup.find_all('dd')
                parent_chk = [0, 0]
                for info in info_list[3].find_all('td'):
                    if info.get('rowspan') == '2' and info.get('class') == ['b_ml']:
                        df['father_id'] = [re.sub('/horse/ped/|/', '', info.find('a').get('href'))]
                        df['father_name'] = [info.find('a').text]
                        parent_chk[0] = 1
                    if info.get('rowspan') == '2' and info.get('class') == ['b_fml']:
                        df['mother_id'] = [re.sub('/horse/ped/|/', '', info.find('a').get('href'))]
                        df['mother_name'] = [info.find('a').text]
                        parent_chk[1] = 1
                # 母id及び父idが存在しない場合
                if not parent_chk[0]:
                    df['father_id'] = [None]
                if not parent_chk[1]:
                    df['mother_id'] = [None]
                # 名前の取得
                info_list = soup.find_all('h1')
                for info in info_list:
                    if not info.find_all('a'):
                        df['horse_name'] = [info.text]
                # 性別の取得
                info_list = soup.find_all('p')
                for info in info_list:
                    if info.get('class') == ['txt_01']:
                        for sex in ['牝', '牡', 'セ']:
                            if sex in info.text:
                                df['sex'] = [sex]
                df['horse_id'] = [horse_id]
                horse_profiles[horse_id] = df
            except KeyboardInterrupt:
                break
        try:
            # pd.DataFrame型にして一つのデータにまとめる
            horse_profiles_df = pd.concat([horse_profiles[key] for key in horse_profiles])
            # スクレイピングしたデータをデータベースに反映させる。
            update_horse_profile(horse_profiles_df)
        except ValueError:
            pass

    def preprocessing(self) -> None:
        _df = copy.deepcopy(self.raw_df)

        _df.drop([
            'horse_name',
            'breeder_name',
            'owner_name',
            'trainer_name',
            'near_relation_horse_name_0',
            'near_relation_horse_name_1',
            'father_name',
            'mother_name'
        ], axis=1, inplace=True)
        _df['birthday'] = _df['birthday'].map(lambda x: int(x.strftime('%Y%m%d')))

        self.preprocessed_df = _df

    def merge_result(self) -> pd.DataFrame:
        result = Result()
        return pd.merge(self.preprocessed_df, result.preprocessed_df)
