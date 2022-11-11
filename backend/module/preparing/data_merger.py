import pandas as pd
from tqdm import tqdm
from typing import Any
from datetime import date


class DataMerger:

    target_ls = [
        'order',
        'time_idx',
        'prize'
    ]
    horse_target_ls = [
        'first_corner',
        'final_corner',
        'first_to_rank',
        'first_to_final',
        'final_to_rank',
        'last3F',
        'diff_time',
    ] + target_ls

    def __init__(self, added_date_df: pd.DataFrame) -> None:
        self.added_date_df = added_date_df

    def merge_all_average(self, df: pd.DataFrame, col: str, n_last: Any = 'all') -> pd.DataFrame:
        date_ls = df['date'].unique()
        temp_ls = list()
        pbar = tqdm(total=len(date_ls))
        for _date in date_ls:
            pbar.update(1)
            pbar.set_description("merge last {} datas by {}".format(str(n_last)+(" "*(3-len(str(n_last)))), col))
            temp_ls.append(self.__merge_average(df, col, _date, n_last))
        merged_df = pd.concat(temp_ls)
        return merged_df

    # n_lastレース分馬ごとに平均する
    def __get_average(self, id_ls: list, _date: date, col: str, n_last: Any = 'all') -> pd.DataFrame:
        # 取得したhorse_idに関するデータを全て取得
        target_df = self.added_date_df.query('{} in @id_ls'.format(col), local_dict={'id_ls': id_ls})
        # 過去n_last分のデータに限定する
        filtered_df = self.__filter_by_date(target_df, _date, col, n_last)
        # 平均値を出力する
        avg_df = self.__calc_mean(filtered_df, col, n_last)
        return avg_df

    def __merge_average(self, df: pd.DataFrame, col: str, _date: date, n_last: Any = 'all') -> pd.DataFrame:
        _df = df[df['date'] == _date]
        id_ls = _df[col]
        avg_df = self.__get_average(id_ls, _date, col, n_last)
        return pd.merge(_df, avg_df, left_on=col, right_index=True, how='left')

    def __filter_by_date(self, target_df: pd.DataFrame, _date: date, col: str, n_last: Any = 'all'):
        if n_last == 'all':
            filtered_df = target_df[target_df['date'] < _date]
        elif n_last > 0:
            filtered_df = target_df[target_df['date'] < _date].sort_values('date', ascending=False).groupby(col).head(n_last)
        else:
            raise TypeError
        return filtered_df

    def __calc_mean(self, filtered_df: pd.DataFrame, col: str, n_last: Any = 'all'):
        # 平均値を出力する
        if col == 'horse_id':
            avg_df = filtered_df.groupby(col)[self.horse_target_ls].mean().add_prefix('avg_').add_suffix('_for_{}R_by_{}'.format(n_last, col))
        else:
            avg_df = filtered_df.groupby(col)[self.target_ls].mean().add_prefix('avg_').add_suffix('_for_{}R_by_{}'.format(n_last, col))
        return avg_df
