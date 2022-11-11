import pandas as pd
import time
from typing import Union
from tqdm import tqdm
from urllib.request import urlopen
from backend.module.crud.update import update_refund
from backend.module.crud.read import read_refund


class Refund:
    def __init__(self, df=pd.DataFrame()) -> None:
        if len(df):
            self.df = df
        else:
            self.df = read_refund()
        self.df.set_index('race_id', inplace=True)

    @classmethod
    def scrape(cls, race_id_ls, mode='save') -> Union[None, pd.DataFrame]:
        refunds = {}
        for race_id in tqdm(race_id_ls):
            # TODO databaseから得られた値の型を調べる。
            if not isinstance(race_id, str):
                race_id = race_id.race_id
            try:
                time.sleep(1)
                url = "https://db.netkeiba.com/race/" + race_id
                # 普通にスクレイピングすると複勝やワイドなどが区切られないで繋がってしまう。
                # そのため、改行コードを文字列brに変換して後でsplitする
                f = urlopen(url)
                html = f.read()
                html = html.replace(b'<br />', b'br')
                df1 = pd.read_html(html, match='単勝')[1]
                df2 = pd.read_html(html, match='三連複')[0]
                # dfの1番目に単勝〜馬連、2番目にワイド〜三連単がある
                df = pd.concat([df1, df2])
                df.columns = ['betting', 'horse_number', 'money', 'popular']
                df.set_index('betting', inplace=True)
                # 複勝払い戻しの行を分割する
                fukusho_row = df.loc['複勝', :].str.split('br', expand=True).T
                fukusho_row.index = pd.Series([f'複勝_{i+1}' for i in range(len(fukusho_row))], name='betting')
                df = pd.concat([df, fukusho_row]).drop('複勝')
                # ワイド払い戻しの行を分割する
                wide_row = df.loc['ワイド', :].str.split('br', expand=True).T
                wide_row.index = pd.Series(['ワイド_12', 'ワイド_13', 'ワイド_23'], name='betting')
                df = pd.concat([df, wide_row]).drop('ワイド')
                df['race_id'] = [race_id] * len(df)
                df.reset_index(inplace=True)
                refunds[race_id] = df
            except ValueError:
                return 'not found'
            except KeyboardInterrupt:
                break
        # pd.DataFrame型にして一つのデータにまとめる
        refunds_df = pd.concat([refunds[key] for key in refunds])
        if mode == 'save':
            update_refund(refunds_df)
            return None
        elif mode == 'return':
            return cls(refunds_df)
        else:
            raise TypeError

    @property
    def fukusho(self):
        _ls = list()
        for i in range(3):
            _ls.append(self.df[self.df['betting'] == f'複勝_{i+1}'][['horse_number', 'money']].add_suffix(f'{i+1}'))
        _df = pd.concat(_ls, axis=1)
        return self.__to_int(_df)

    @property
    def tansho(self):
        _df = self.df[self.df['betting'] == '単勝'][['horse_number', 'money']]
        return self.__to_int(_df)

    @property
    def umaren(self):
        _df = self.df[self.df['betting'] == '馬連'][['horse_number', 'money']]
        _horse_number = _df['horse_number'].str.split('-', expand=True)[[0, 1]].add_prefix('horse_number')
        _money = _df['money']
        _df = pd.concat([_horse_number, _money], axis=1)
        return self.__to_int(_df)

    @property
    def umatan(self):
        _df = self.df[self.df['betting'] == '馬単'][['horse_number', 'money']]
        _horse_number = _df['horse_number'].str.split('→', expand=True)[[0, 1]].add_prefix('horse_number')
        _money = _df['money']
        _df = pd.concat([_horse_number, _money], axis=1)
        return self.__to_int(_df)

    @property
    def wide(self):
        _ls = [list(), list()]
        for i in ['12', '13', '23']:
            for j, col in enumerate(['horse_number', 'money']):
                _ls[j].append(self.df[self.df['betting'] == f'ワイド_{i}'][[col]].rename(columns={col: i}))
        _horse_number = pd.concat(_ls[0], axis=1).stack().str.split('-', expand=True).add_prefix('horse_number_')
        _money = pd.concat(_ls[1], axis=1).stack().rename('money')
        _df = pd.concat([_horse_number, _money], axis=1)
        return self.__to_int(_df)

    @property
    def sanrentan(self):
        _df = self.df[self.df['betting'] == '三連単'][['horse_number', 'money']]
        _horse_number = _df['horse_number'].str.split('→', expand=True)[[0, 1, 2]].add_prefix('horse_number')
        _money = _df['money']
        _df = pd.concat([_horse_number, _money], axis=1)
        return self.__to_int(_df)

    @property
    def sanrenpuku(self):
        _df = self.df[self.df['betting'] == '三連複'][['horse_number', 'money']]
        _horse_number = _df['horse_number'].str.split('-', expand=True)[[0, 1, 2]].add_prefix('horse_number')
        _money = _df['money']
        _df = pd.concat([_horse_number, _money], axis=1)
        return self.__to_int(_df)

    def __to_int(self, df: pd.DataFrame):
        return df.apply(lambda x: pd.to_numeric(x.str.replace(',', ''), errors='coerce'))
