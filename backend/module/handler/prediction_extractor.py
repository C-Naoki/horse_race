import numpy as np
import pandas as pd
from backend.environment.columns import Columns
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class PredictionExtractor:
    def __init__(self, prediction_handler):
        self.prediction_handler = prediction_handler

    def __call__(self, predictions, fukusho_odds):
        """
        予測結果から必要な情報を取得する
        Parameters
        ----------
        predictions: pd.DataFrame
            rank_predictorにより算出されたレースの予測結果
            columns = ['horse_number', 'score']
        fukusho_odds: FukushoOdds
            複勝馬券に関する情報

        Returns
        -------
        recommended_fukushoes: pd.DataFrame
            購入すべき複勝馬券
            columns = ['race_id', 'horse_number', 'odds', 'score']
        shaped_predictions: pd.DataFrame
            修正後の予測結果
            columns = ["本命馬ランク", "1着予想◎", "2着予想○", "3着予想▲", "4着予想△", "5着予想☆", "6着予想×", "頭数"]
        """
        shaped_predictions = pd.DataFrame(index=[], columns=Columns.PREDICTION_COLUMNS)
        for one_race in predictions.groupby(level=0):

            race_id = one_race[0]
            one_race = one_race[1].sort_values('score', ascending=False)

            oddses = self.__scrape_oddses(race_id, one_race)
            fukusho_odds.update_recommendation(oddses)
            one_race = self.__shape_one_race(race_id, fukusho_odds.recommendation, one_race)
            fav_rank = self.__get_fav_rank(one_race)

            shaped_predictions.loc[race_id[-2:].lstrip('0')+'R'] = [
                fav_rank,
                one_race['race_class'][0],
                one_race.iat[0, 0],
                one_race.iat[1, 0],
                one_race.iat[2, 0],
                one_race.iat[3, 0],
                one_race.iat[4, 0],
                one_race.iat[5, 0],
                len(one_race)
            ]

        self.prediction_handler(shaped_predictions, sorted(list(set(predictions.index.get_level_values('race_id')))))

        return fukusho_odds

    def __scrape_oddses(self, race_id, one_race):
        """
        race_idが示すレースの単勝及び複勝オッズを取得する。

        Parameters
        ----------
        race_id: str
            対象のレースのマスタID
        one_race: pd.DataFrame
            1レース分の予測結果
            columns = ['horse_number', 'score']

        Returns
        -------
        oddses: pd.DataFrame
            race_idに対応したレースの単勝及び複勝オッズ
            columms = ['race_id', 'horse_number', 'tansho', 'fukusho', 'score]

        Raises
        ------
        KeyError
            スクレイプ対象のwebサイトが確立していない場合
        """
        oddses = pd.DataFrame()
        driver = self.__set_selenium()
        driver.get('https://race.netkeiba.com/odds/index.html?type=b1&race_id='+race_id+'&rf=shutuba_submenu')
        html = driver.page_source.encode('utf-8')
        _dfs = pd.read_html(str(BeautifulSoup(html, "html.parser").html))
        oddses['race_id'] = [race_id] * len(_dfs[0])
        oddses['horse_number'] = _dfs[0]['馬番']
        oddses['tansho'] = _dfs[0]['オッズ']
        oddses['fukusho'] = _dfs[1]['オッズ']
        oddses.set_index('horse_number', inplace=True)
        oddses['fukusho'] = oddses.loc[:, 'fukusho']
        oddses['score'] = list(one_race.sort_values('horse_number')['score'])
        oddses = self.__determine_fukusho_odds(oddses[oddses['tansho'] != '---.-'], one_race)
        oddses.sort_values('tansho', inplace=True)
        oddses['popular'] = [i+1 for i in range(len(oddses))]
        return oddses.sort_index()

    def __set_selenium(self):
        """
        Seleniumライブラリを用いたスクレイピングの準備を行う

        Returns
        -------
        driver : webdriver.chrome.webdriver.WebDriver
            chromeの操作のためのドライバ
        """
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.implicitly_wait(15)
        return driver

    def __determine_fukusho_odds(self, oddses, one_race):
        """
        レース終了まで確定しない複勝オッズの推定値の算出

        Parameters
        ----------
        oddses: pd.DataFrame
            race_idに対応したレースの単勝及び複勝オッズ
            columms = ['race_id', 'horse_number', 'tansho', 'fukusho']
        one_race: pd.DataFrame
            1レース分の予測結果
            columns = ['horse_number', 'score']

        Returns
        -------
        oddses: pd.DataFrame
            複勝オッズ推定値格納後のoddses

        Notes
        -----
        推定の際に用いる式は以下の通り
            (オッズの最小値) + (予測結果上位3頭のうち、人気が4位以下の頭数 *1) * ((オッズの最大値) - (オッズの最小値)) / 9
            (*1 予測結果上位3頭の人気が順に[1, 4, 2]の場合、1となる。)
        """
        _oddses = oddses.copy()
        popular_ls = _oddses.sort_values('tansho').index
        hoge = set(list(popular_ls[:3]) + list(one_race['horse_number'][:3]))
        _fukusho_oddses = _oddses.loc[:, 'fukusho'].copy()
        _oddses['fukusho'] = _fukusho_oddses.map(
            lambda x: round(float(x.split(' - ')[0]) + (len(hoge)-3)*(float(x.split(' - ')[1]) - float(x.split(' - ')[0]))/9, 2))
        return _oddses

    def __update_recommended_fukushoes(self, recommended_fukushoes, oddses, fukushoes_criteria):
        """
        購入すべき複勝馬券を算出し、recommended_fukushoesに追加する

        Parameters
        ----------
        recommended_fukushoes: pd.DataFrame
            購入すべき複勝馬券
            columns = ['race_id', 'horse_number', 'odds', 'score']
        oddses: pd.DataFrame
            対象のレースの単勝及び複勝オッズ
            columms = ['race_id', 'horse_number', 'tansho', 'fukusho']
        fukushoes_criteria: pd.DataFrame
            複勝オッズとスコアの対応表
            columns = ['num', 'ratio', 'odds']

        Returns
        -------
        recommended_fukushoes: pd.DataFrame
            更新後のrecommended_fukushoes
        """
        for horse_number, row in oddses.iterrows():
            if self.__is_recommended_fukushoes(fukushoes_criteria, row['score'], row['fukusho']):
                new_recommended_fukushoes = pd.DataFrame([[
                                    row['race_id'],
                                    horse_number,
                                    row['fukusho'],
                                    row['score']
                                ]], columns=recommended_fukushoes.columns)
                recommended_fukushoes = pd.concat([recommended_fukushoes, new_recommended_fukushoes], ignore_index=True)
        return recommended_fukushoes

    def __is_recommended_fukushoes(self, fukushoes_criteria, score, odds):
        """
        fukushoes_criteriaを基準とし、買うに値する複勝馬券かどうかの算出

        Parameters
        ----------
        fukushoes_criteria: pd.DataFrame
            複勝オッズとスコアの対応表
            columns = ['num', 'ratio', 'odds']
        score: float
            対象の馬の評価値
        odds: float
            レースで提示されているオッズ

        Returns
        -------
        is_recommended: bool
            購入する価値があるかどうか
        """
        index_list = fukushoes_criteria.index
        for index in index_list:
            hoge = index.split(' ~ ')
            try:
                if score < float(hoge[1]):
                    std_odd = fukushoes_criteria.loc[index, 'odds']
                    break
            except Exception:
                std_odd = fukushoes_criteria.iloc[-1]['odds']
        return std_odd <= odds

    def __shape_one_race(self, race_id, recommended_fukushoes, one_race):
        """
        one_raceを整形する

        Parameters
        ----------
        race_id: str
            対象のレースのマスタID
        recommended_fukushoes: pd.DataFrame
            購入すべき複勝馬券
            columns = ['race_id', 'horse_number', 'odds', 'score']
        one_race: pd.DataFrame
            1レース分の予測結果
            columns = ['horse_number', 'score']

        Returns
        -------
        one_race: pd.DataFrame
            購入すべき馬に星マークが付与されたone_race
        """
        return self.__fill_in_missing_values(
            self.__attach_star2proba(
                race_id, recommended_fukushoes, one_race
            )
        )

    def __attach_star2proba(self, race_id, recommended_fukushoes, one_race):
        """
        recommended_fukushoesに記録されている購入すべき馬に対して、星マークを付与する

        Parameters
        ----------
        race_id: str
            対象のレースのマスタID
        recommended_fukushoes: pd.DataFrame
            購入すべき複勝馬券
            columns = ['race_id', 'horse_number', 'odds', 'score']
        one_race: pd.DataFrame
            1レース分の予測結果
            columns = ['horse_number', 'score']

        Returns
        -------
        one_race: pd.DataFrame
            購入すべき馬に星マークが付与されたone_race
        """
        for horse_number in recommended_fukushoes[recommended_fukushoes['race_id'] == race_id]['horse_number']:
            for i, proba in enumerate(one_race.iterrows()):
                if '☆' not in str(proba[1]['horse_number']) and int(proba[1]['horse_number']) == horse_number:
                    one_race.iat[i, 0] = '☆ '+str(one_race.iat[i, 0])
        return one_race

    def __get_fav_rank(self, one_race):
        """
        各レースの本命馬のランクを取得する

        Parameters
        ----------
        one_race: pd.DataFrame
            1レース分の予測結果
            columns = ['horse_number', 'score']

        Returns
        -------
        fav_rank: str
            本命馬のランク
        """
        if one_race.iat[0, 1] - one_race.iat[1, 1] >= 1 and one_race.iat[0, 1] >= 2:
            fav_rank = 'A'
        elif one_race.iat[0, 1] - one_race.iat[1, 1] >= 1 or one_race.iat[0, 1] >= 2:
            fav_rank = 'B'
        elif one_race.iat[0, 1] - one_race.iat[1, 1] >= 0.4:
            fav_rank = 'C'
        elif np.isnan(one_race.iat[0, 1]) or (one_race.iat[0, 1] == one_race.iat[2, 1]):
            fav_rank = 'x'
        else:
            fav_rank = '-'
        return fav_rank

    def __fill_in_missing_values(self, one_race):
        """
        one_raceの欠損値を補完する

        Parameters
        ----------
        one_race: pd.DataFrame
            1レース分の予測結果
            columns = ['horse_number', 'score']

        Returns
        -------
        one_race: pd.DataFrame
            欠損値を補完後のone_race
        """
        # TODO: 書き方が微妙
        s = pd.Series(['-', '-', '-'], index=one_race.columns, name=one_race.index[0])
        for _ in range(6-len(one_race)):
            one_race = pd.concat([one_race, s])
        return one_race
