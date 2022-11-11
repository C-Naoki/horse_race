import re
import time
import numpy as np
import pandas as pd
import copy
from datetime import datetime, date
from bs4 import BeautifulSoup
from tqdm import tqdm
from backend.environment.mapping import Mapping
from backend.environment.netkeiba import Netkeiba
from backend.module.mapping import RaceDateMapping
from backend.module.preparing import DataMerger
from backend.module.crud.update import (
    update_result,
    update_race_date_mapping
)
from backend.module.crud.read import read_result


class Result(DataMerger):

    race_date_mapping = RaceDateMapping()
    raw_df = read_result()

    def __init__(self) -> None:
        # 取得したデータの処理
        self.preprocessing()
        # date情報をmappingから付与する
        added_date_df = self.preprocessed_df.merge(self.race_date_mapping.df)
        super().__init__(added_date_df)

    @staticmethod
    def scrape(race_id_dict: dict):
        """
        馬の過去成績データをスクレイピングする関数
        Parameters:
        ----------
        race_id_dict : {place: race_id_place}
            レースIDの辞書
        race_id_place : {kai: race_id_kai}
            ある開催地限定のレースID
        race_id_kai: list
            ある回に開催されたレース限定のレースID

        Returns:
        ----------
        results_df : pandas.DataFrame
            全レースの過去成績データ
        """

        # race_idをkeyにしてDataFrame型を格納
        results = {}
        bf_upd_df = read_result()
        idx_set = set(bf_upd_df['race_id'])
        for place, race_id_place in race_id_dict.items():
            pre_kai = False
            for kai, race_id_kai in race_id_place.items():
                if pre_kai:
                    continue
                e_att = False
                e_key = False
                pbar = tqdm(total=len(race_id_kai))
                for race_id in race_id_kai:
                    pbar.update(1)
                    pbar.set_description('Scrape Race data in "{} {}回"'.format(
                        [k for k, v in Mapping.PLACE_ID_MAPPING.items() if v == str(place).zfill(2)][0],
                        kai
                    ))
                    if race_id in idx_set:
                        continue
                    try:
                        time.sleep(1)
                        url = "https://db.netkeiba.com/race/" + race_id
                        html = Netkeiba.session.get(url)
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
                        # メインとなるテーブルデータを取得
                        _df = pd.read_html(url)[0]
                        # _df.drop(['馬名', '調教師', '枠', '馬番', '性齢', '斤量', '騎手', 'タイム', '人気'], axis=1, inplace=True)
                        _df = _df[['着順', '着差', '単勝']]
                        _df.columns = [
                            'order',
                            'diff_time',
                            'odds'
                        ]
                        # 単勝オッズ列の'---'をNaNに変換
                        _df.replace({'odds': {'---': np.nan}}, inplace=True)
                        # 日付の抽出
                        for info in soup.find_all('li'):
                            if 'race/list' in info.find('a').get('href'):
                                d = datetime.strptime(re.sub('race/list|/', '', info.find('a').get('href')), '%Y%m%d')
                                _df['date'] = [date(d.year, d.month, d.day)] * len(_df)
                                break
                        # 賞金の抽出
                        hoge = 0
                        prize_ls = []
                        for info in soup.find_all('td'):
                            if info.get('class') == ['txt_r'] and info.get('nowrap') == 'nowrap':
                                if hoge % 5 == 4:
                                    if info.text:
                                        prize_ls.append(float(info.text.replace(',', '')))
                                    else:
                                        prize_ls.append(0)
                                hoge += 1
                        _df['prize'] = prize_ls
                        # ﾀｲﾑ指数の抽出
                        time_idx_ls = []
                        for info in soup.find_all('td'):
                            if info.get('class') and 'speed_index' in info.get('class'):
                                try:
                                    time_idx_ls.append(int(info.text.replace('\n', '')))
                                except ValueError:
                                    time_idx_ls.append(0)
                        _df['time_idx'] = time_idx_ls
                        # 馬場指数
                        _df["ground_state_idx"] = [0] * len(_df)
                        for i in soup.find_all('tr'):
                            if i.find('th') and i.find('th').text == '馬場指数':
                                _df["ground_state_idx"] = [int(i.find('td').text.replace('\xa0(?)', ''))] * len(_df)
                        # 上りの抽出
                        last3F_ls = []
                        for i in soup.find_all('td'):
                            if i.get('class') == ['txt_c'] and i.get('nowrap') == 'nowrap':
                                if i.find('span'):
                                    if i.text:
                                        last3F_ls.append(i.text)
                                    else:
                                        last3F_ls.append(np.nan)
                        _df['last3F'] = last3F_ls
                        # 備考の抽出
                        hoge = 0
                        remark_ls = []
                        passing_ls = []
                        for info in soup.find_all('td'):
                            if not info.get('class') and info.get('nowrap') == 'nowrap':
                                if hoge % 3 == 0:
                                    if info.text:
                                        passing_ls.append(info.text)
                                    else:
                                        passing_ls.append(np.nan)
                                if hoge % 3 == 2:
                                    text = info.text.replace('\n', '')
                                    if text:
                                        remark_ls.append(text)
                                    else:
                                        remark_ls.append(np.nan)
                                hoge += 1
                        _df['remark'] = remark_ls
                        _df['passing'] = passing_ls
                        # 型を変更する
                        _df = _df.astype({'order': 'str'})
                        _df["horse_id"] = horse_id_ls
                        # インデックスをrace_idとhorse_idのMultiIndexにする
                        _df['race_id'] = [race_id] * len(_df)
                        results[race_id] = _df
                    # 存在しないrace_idを飛ばし次のスクレイピングに移す
                    except AttributeError:
                        # 第1回のレースにてIndexErrorが生じた場合
                        if race_id[8:10] == '01':
                            pre_kai = True
                        e_att = True
                        # 第1Rが存在しない場合は、その後も存在しないとみなす。
                        # 2018年2月3日 1回東京3日目 第4Rが存在しないが、第5Rは存在するような稀なケース有り
                        if race_id[10:12] == '01':
                            break
                    # wifiの接続が切れた時などでも途中までのデータを返せるようにする
                    except KeyboardInterrupt:
                        e_key = True
                        break
                pbar.close()
                if e_att:
                    print("{}回{}日のレースは開催されていません。\n".format(str(race_id)[6:8], str(race_id)[8:10]))
                    if pre_kai:
                        print("別開催地のスクレイピングに移ります。\n")
                elif e_key:
                    print("スクレイピングを中断します。\n")
                    break
                else:
                    print("対象のレースを全て取得し終わりました。\n")
            else:
                continue
            break
        try:
            # pd.DataFrame型にして一つのデータにまとめる
            results_df = pd.concat([results[key] for key in results])
            # スクレイピングしたデータをデータベースに反映させる。
            update_result(results_df)
            update_race_date_mapping(results_df[['race_id', 'date']])
        except ValueError:
            pass

    def preprocessing(self) -> None:
        _df = copy.deepcopy(self.raw_df)

        # passing
        def corner(x, n):
            if type(x) != str:
                return x
            elif n == 4:
                return int(re.findall(r'\d+', x)[-1])
            elif n == 1:
                return int(re.findall(r'\d+', x)[0])

        # remark
        def remarks(x):
            if x in ['出遅れ', '出脚鈍い', '躓く', '好発']:
                return x
            else:
                return '0'

        # diff_time
        def diff_time2num(x):
            if x == '同着':
                return 0
            elif x == 'ハナ':
                return 0.08
            elif x == 'アタマ':
                return 0.15
            elif x == 'クビ':
                return 0.30
            elif x == '大':
                return 10
            elif '.' in x:
                x = x.split('.')
            else:
                x = [x]
            ans = 0
            for num in x:
                if '/' in num:
                    numerator, denominator = num.split('/')
                    ans += float(numerator) / float(denominator)
                else:
                    ans += float(num)
            return ans

        def difference_horses(x):
            ans = 0
            x = str(x)
            if '+' in x:
                x = x.split('+')
            else:
                x = [x]
            for num in x:
                ans += diff_time2num(num)
            return ans

        # 数字以外の値('除', '中'など)を取り除く
        _df['order'] = pd.to_numeric(_df['order'], errors='coerce')
        _df.dropna(subset=['order', 'odds'], inplace=True)
        _df['order'] = _df['order'].astype(int)
        # 第1コーナー通過時の着順
        _df['first_corner'] = _df['passing'].map(lambda x: corner(x, 1))
        # 最終コーナー通過時の着順
        _df['final_corner'] = _df['passing'].map(lambda x: corner(x, 4))
        # 最終コーナーからゴールまで何頭抜かしたか
        _df['final_to_rank'] = _df['final_corner'] - _df['order']
        # 第1コーナーからゴールまで何頭抜かしたか
        _df['first_to_rank'] = _df['first_corner'] - _df['order']
        # 第1コーナーから最終コーナーまで何頭抜かしたか
        _df['first_to_final'] = _df['first_corner'] - _df['final_corner']
        # df['remark']の整形
        _df['remark'] = _df['remark'].map(lambda x: remarks(x))
        # df['diff_time']の整形
        _df['diff_time'] = _df['diff_time'].map(lambda x: difference_horses(x)).fillna(0)
        # 目的関数の設定
        _df['rank'] = _df['order'].map(lambda x: 4-x if x < 4 else 0) * (_df["odds"])**0.2

        self.preprocessed_df = _df

    # TODO 修正
    def get_latest(self, _date: date) -> pd.DataFrame:
        _df = self.af_df[self.af_df['date'] == _date]
        horse_id_ls = _df['horse_id']
        race_id_df = _df[['horse_id', 'race_id']].set_index('horse_id')
        target_df = self.af_df.query('horse_id in @horse_id_ls', local_dict={'horse_id_ls': horse_id_ls})
        filtered_df = target_df[target_df['date'] < _date]
        latest_df = filtered_df.groupby('horse_id')['date'].max().rename('latest')
        return pd.concat([race_id_df, latest_df], axis=1).fillna(0)

    # TODO 修正
    def get_all_latest(self) -> pd.DataFrame:
        date_ls = self.af_df['date'].unique()
        temp_ls = list()
        for _date in date_ls:
            temp_ls.append(self.get_latest(_date))
        merged_df = pd.concat(temp_ls)
        return merged_df.set_index('race_id', append=True).swaplevel('horse_id', 'race_id')
