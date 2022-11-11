import datetime
import lightgbm as lgb
import pandas as pd
import re
import requests
from backend.environment.lightgbm import LightGBM
from backend.environment.columns import Columns as Cols
from backend.module.repository import OriginalRaceCard
from backend.module.preparing import TableMerger
from backend.module.utils.fukusho_odds import FukushoOdds
from bs4 import BeautifulSoup
from sklearn.metrics import roc_auc_score

# TODO: weight_horse, diff_weight_horseについて
# TODO: LightGBM.PARAMSを書き換えたい (l.134)


class RankPredictor:
    """
    レースの予測を行う

    Attributes
    ----------
    table_merger: TableMerger
        過去データのaverageをmergeする
    prediction_extarctor: PredictionExtractor
        結果から必要な情報を取得
    method: str default regression
        lightgbmの種類
    lgb_clf: lightgbm
        lightgbmを用いて予測を行うためのモデル
    """

    table_merger = TableMerger()

    def __init__(self, prediction_extarctor, method='regression'):
        """
        Parameters
        ----------
        prediction_extarctor: PredictionExtractor
            結果から必要な情報を取得
        method: str default regression
            lightgbmの種類
        """
        self.prediction_extarctor = prediction_extarctor
        self.method = method
        self.lgb_clf = self.__create_model()

    def fit(self, X, y):
        """
        modelに説明変数及び、目的変数をfitさせる
        FukushoOddsCriteriaを作成する

        Parameters
        ----------
        X: pd.DataFrame
            説明変数
        y: pd.Series
            目的変数
        """

        self.fukusho_odds = FukushoOdds.create_criteria(self.__create_model(), X, y)

        if 'date' in X.columns:
            X = X.drop('date', axis=1).copy()
        if self.method == 'rank':
            query = self.__get_query(self.X)
            self.lgb_clf.fit(X.values, y.values, group=query)
        else:
            self.lgb_clf.fit(X.values, y.values)

    def predict(self, date_ls, venue_id_ls=[]):
        """
        ある日付に開催されたレースの予測を行う

        Parameters
        ----------
        X: pd.DataFrame
            説明変数
        y: pd.Series
            目的変数
        date_ls: list[date]
            レース開催日が格納されたリスト
        venue_id_ls: list[str] default []
            venue_idが格納されたリスト
            特定の開催地に対してのみpredictを実行したい時のみ利用
        """
        if type(date_ls) is datetime.date:
            date_ls = [date_ls]
        if not venue_id_ls:
            venue_id_ls = self.__make_venue_id_ls(date_ls)
        assert venue_id_ls
        for venue_id in venue_id_ls:
            original_data = self.__scrape_original_data(venue_id)
            predictions = self.__get_predictions(original_data)
            self.fukusho_odds = self.prediction_extarctor(predictions, self.fukusho_odds)

    def feature_importances(self, X, n_display=20):
        """
        特徴量の重要度を出力する

        Parameters
        ----------
        n_display: int default 20
            表示する特徴量の数

        Returns
        -------
        importances: pd.DataFrame
            特徴量の重要度
            columns = ['features', 'importance']
        """
        importances = pd.DataFrame({"features": X.columns, "importance": self.lgb_clf.feature_importances_})
        return importances.sort_values("importance", ascending=False)[:n_display]

    def score(self, X, y_true):
        """
        予測の正答率を算出する

        Parameters
        ----------
        X: pd.DataFrame
            説明変数
        y_true: pd.Series
            正解データ

        Returns
        -------
        roc_auc_score: float
            予測の正答率 min 0, max 1.0
        """
        return roc_auc_score(y_true, self.__get_predictions(X)['score'])

    def __create_model(self):
        """
        lightgbmをインスタンス化させる

        Returns
        -------
        lgb_clf: lightgbm
            lightgbmを用いて予測を行うためのモデル
        """
        if self.method == 'regression':
            lgb_clf = lgb.LGBMRegressor(**LightGBM.PARAMS)
        elif self.method == 'binary':
            lgb_clf = lgb.LGBMClassifier(**LightGBM.PARAMS)
        elif self.method == 'rank':
            lgb_clf = lgb.LGBMRanker(**LightGBM.PARAMS)
        else:
            raise TypeError
        return lgb_clf

    def __scrape_original_data(self, venue_id):
        """
        venue_idに対応した出馬表をスクレイピングする

        Parameters
        ----------
        venue_id: str
            開催地に対応したマスタid

        Returns
        -------
        original_data: pd.DataFrame
            出馬票データ
        """
        _race_id_ls = [venue_id+str(i+1).zfill(2) for i in range(12)]
        _original_race_card = OriginalRaceCard.scrape(_race_id_ls)
        _original_data = self.table_merger(_original_race_card.preprocessed_df, 'original').drop(Cols.DROP_COLUMNS+['date'], axis=1)
        return _original_data

    def __get_query(self, X: pd.DataFrame) -> list:
        """
        ランキング学習を行う際に必要なクエリデータを取得する

        Parameters
        ----------
        X: pd.DataFrame
            説明変数

        Returns
        -------
        query: list
            クエリデータ
        """
        query = list()
        for i in X.groupby(level=0):
            query.append(len(i[1]))
        return query

    def __make_venue_id_ls(self, date_ls, num='all') -> list:
        """
        ある日付に開催されたレースの開催地に対応したvenue_idを取得

        Parameters
        ----------
        data_ls: list[date]
            日付データ

        Returns
        -------
        venue_ids: list[str]
            開催地に対応したマスタid
        """
        venue_ids = set()
        for _date in date_ls:
            url = 'https://race.netkeiba.com/top/race_list_sub.html?kaisai_date=' + _date.strftime('%Y%m%d')
            responses = requests.get(url)
            soup = BeautifulSoup(responses.content, "html.parser")
            for race_list in soup.find_all('li'):
                venue_ids.add(re.findall(r'\d+', race_list.find_all('a')[0].get('href'))[0][:10])
        if num == 'all':
            return list(venue_ids)
        else:
            assert len(list(venue_ids)) <= num
            return list(venue_ids)[:num]

    def __get_predictions(self, original_data, is_std=True, is_nor=False):
        """
        予測データの取得

        Parameters
        ----------
        X: pd.DataFrame
            説明変数

        id_std: bool
            標準化するかどうか

        is_nor: bool
            正規化するかどうか
        """
        score = pd.Series(self.lgb_clf.predict(original_data), index=original_data.index)
        if is_std:
            score = score.groupby(level=0).transform(lambda x: (x - x.mean()) / x.std(ddof=0))
        if is_nor:
            score = (score - score.min()) / (score.max() - score.min())
        predictions = original_data[['horse_number']].astype('int').copy()
        predictions['score'] = score.astype('float64')
        predictions['race_class'] = self.__make_race_classes(original_data)
        return predictions

    def __make_race_classes(self, original_data):
        race_classes = list()
        df = original_data[[
            'race_class_未勝利',
            'race_class_１勝クラス',
            'race_class_２勝クラス',
            'race_class_３勝クラス',
            'race_class_オープン'
        ]].copy()

        for row in df.iterrows():
            flag = 1
            for col in df.columns:
                if row[1][col]:
                    flag = 0
                    race_classes.append(col.strip('race_class_'))
            if flag:
                race_classes.append('新馬')
        return race_classes
