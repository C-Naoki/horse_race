import datetime
import numpy as np
import pandas as pd


class FukushoOdds:
    def __init__(self, criteria):
        self.criteria = criteria
        self.recommendation = pd.DataFrame([], columns=['race_id', 'horse_number', 'popular', 'odds', 'score'])

    @classmethod
    def create_criteria(cls, model, X, y, threshold_date=datetime.date(2020, 1, 1), range=[0, 2.2], width=0.05):
        """
        あるオッズの複勝馬券に対して、回収率の期待値100%以上を達成するために必要なスコアの算出

        Parameters
        ----------
        X: pd.DataFrame
            説明変数
        y: pd.Series
            目的変数
        range: list, default [0.1, 2.5]
            計算対象のスコアの範囲
        width: float default 0.05
            全体を等間隔に分割した際の、一つあたりの幅

        Returns
        -------
        fukusho_odds_criteria: pd.DataFrame
            オッズとスコアの対応表
            columns = ['num', 'ratio', 'odds']
        """
        X_train = X[X['date'] < threshold_date].copy()
        y_train = y[:len(X_train)]
        X_test = X[X['date'] >= threshold_date].copy()
        y_test = y[len(X_train):]
        X_train.drop('date', axis=1, inplace=True)
        X_test.drop('date', axis=1, inplace=True)

        model.fit(X_train.values, y_train.values)

        fukusho_odds_criteria = pd.DataFrame([], columns=['num', 'ratio', 'odds'])
        for threshold in np.arange(range[0]-width, range[1]+width, width):
            temp = pd.DataFrame({'score': model.predict(X_test), 'correct': y_test})
            threshold = round(threshold, len(str(int(1/width))))
            if threshold != range[0]-width:
                temp = temp[threshold < temp['score']]
            if threshold != range[1]:
                temp = temp[temp['score'] <= threshold+width]
            if threshold == range[0]-width:
                row_name = ' ~ {}'.format(range[0])
            elif threshold == range[1]:
                row_name = '{} ~ '.format(range[1])
            else:
                row_name = '{} ~ {}'.format(threshold, round(threshold+width, len(str(int(1/width)))))
            if len(temp[temp['correct'] != 0]):
                odds = len(temp)/len(temp[temp['correct'] != 0])
            else:
                odds = 9999
            fukusho_odds_criteria.loc[row_name] = [
                len(temp),
                len(temp[temp['correct'] != 0])/len(temp),
                odds
            ]

        return cls(fukusho_odds_criteria)

    def update_recommendation(self, oddses):
        for horse_number, row in oddses.iterrows():
            if self.__is_recommendation(row['score'], row['fukusho']):
                new_recommendation = pd.DataFrame([[
                                    row['race_id'],
                                    horse_number,
                                    row['popular'],
                                    row['fukusho'],
                                    row['score'],
                                ]], columns=self.recommendation.columns)
                self.recommendation = pd.concat([self.recommendation, new_recommendation], ignore_index=True)

    def __is_recommendation(self, score, odds):
        index_list = self.criteria.index
        for index in index_list:
            interval = index.split(' ~ ')
            try:
                if score < float(interval[1]):
                    std_odd = self.criteria.loc[index, 'odds']
                    break
            except Exception:
                std_odd = self.criteria.iloc[-1]['odds']
        return std_odd <= odds
