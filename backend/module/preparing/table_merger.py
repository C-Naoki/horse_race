import pandas as pd
import copy
from backend.module.mapping import RaceDateMapping
from backend.module.repository import (
    Race,
    Result,
    HorseProfile,
    RaceCard,
)


class TableMerger:

    race = Race()
    race_card = RaceCard()
    result = Result()
    horse_profile = HorseProfile()
    race_date_mapping = RaceDateMapping()

    def __init__(self, type: str = 'train') -> None:
        self.type = type

    def __call__(self, df: pd.DataFrame, type: str = 'train') -> pd.DataFrame:
        _df = copy.deepcopy(df)
        self.type = type
        if 'date' not in _df.columns:
            _df = _df.merge(self.race_date_mapping.df)
        _df = self.__process_categorical(
                self.__merge_race_card(
                    self.__merge_result(
                        self.__merge_horse_profile(
                            self.__merge_race(
                                _df
                            )
                        )
                    )
                ).fillna(0).sort_values(['date', 'race_id', 'horse_number'])
            ).set_index(['race_id', 'horse_id'])
        return _df

    # jockeyの性能データをmerge
    def __merge_race_card(self, df: pd.DataFrame) -> pd.DataFrame:
        _df = copy.deepcopy(df)
        _df = self.race_card.merge_all_average(_df, 'jockey_id')
        return _df

    # breeder, owner, trainerの性能データをmerge
    def __merge_result(self, df: pd.DataFrame) -> pd.DataFrame:
        _df = copy.deepcopy(df)
        _df = self.result.merge_all_average(_df, 'horse_id')
        if self.type == 'train':
            return _df.merge(self.result.preprocessed_df[['race_id', 'horse_id', 'rank', 'odds']], how='left')
        elif self.type == 'original':
            return _df

    # horseの性能データ, profile dataをmerge
    def __merge_horse_profile(self, df: pd.DataFrame) -> pd.DataFrame:
        _df = copy.deepcopy(df)
        _df = _df.merge(self.horse_profile.preprocessed_df[['horse_id', 'breeder_id', 'owner_id', 'trainer_id']], how='left')
        for col in ['breeder_id', 'owner_id', 'trainer_id']:
            _df = self.horse_profile.merge_all_average(_df, col)
        return _df.merge(self.horse_profile.preprocessed_df[['horse_id', 'sex', 'birthday']], how='left')

    # race dataをmerge
    def __merge_race(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.type == 'train':
            df = df.merge(self.race.preprocessed_df, how='left')
        df['n_horses'] = df['race_id'].map(df['race_id'].value_counts())
        return df

    # 数値でないデータをダミー変数化する。
    def __process_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        _df = copy.deepcopy(df)
        weathers = ["曇", "晴", "雨", "小雨", "小雪", "雪"]
        course_types = ["芝", "ダート"]
        ground_states = ["良", "稍重", "重", "不良"]
        sexes = ['牡', '牝', 'セ']
        turns = ['右', '左', '直線']
        race_classes = ["新馬", "未勝利", "１勝クラス", "２勝クラス", "３勝クラス", "オープン"]
        venues = ['札幌', '函館', '福島', '新潟', '東京', '中山', '中京', '京都', '阪神', '小倉']
        _df['weather'] = pd.Categorical(_df['weather'], weathers)
        _df['course_type'] = pd.Categorical(_df['course_type'], course_types)
        _df['ground_state'] = pd.Categorical(_df['ground_state'], ground_states)
        _df['sex'] = pd.Categorical(_df['sex'], sexes)
        _df['turn'] = pd.Categorical(_df['turn'], turns)
        _df['race_class'] = pd.Categorical(_df['race_class'], race_classes)
        _df['venue'] = pd.Categorical(_df['venue'], venues)
        _df = pd.get_dummies(_df, columns=['weather', 'course_type', 'ground_state', 'sex', 'turn', 'race_class'], drop_first=True)

        return _df
