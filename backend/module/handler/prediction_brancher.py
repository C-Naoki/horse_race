from backend.module.repository import Refund
from tabulate import tabulate


class PredictionBrancher:

    def __init__(self, prediction_writer):
        self.prediction_writer = prediction_writer

    def __call__(self, shaped_predictions, race_id_ls):
        """
        予測結果の処理を行う
        a) 対象のレースが開催されていない場合
            予測結果の出力(prediction_displayer)
        b) 対象のレースが開催後の場合
            予測結果をExcelに書き込む(prediction_recoder)

        Parameters
        ----------
        shaped_predictions: pd.DataFrame
            rank_predictorにより算出されたレースの予測結果
            columns = ["本命馬ランク", "1着予想◎", "2着予想○", "3着予想▲", "4着予想△", "5着予想☆", "6着予想×", "頭数"]
        """
        """
        if (レースが開催されていない)
            (予測結果を出力する関数)
        else
            (予測結果をExcelに書き込む関数)
        """
        try:
            refund = Refund.scrape(race_id_ls, mode='return')
            assert not refund == 'not found'
            self.prediction_writer(shaped_predictions, race_id_ls, refund)
        except KeyError:
            refund = None
            print(tabulate(shaped_predictions.iloc[:, :8], ['レース番号']+list(shaped_predictions.columns), tablefmt='presto', showindex=True))
