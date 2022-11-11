import numpy as np
from backend.module.repository import Refund
from itertools import combinations
from itertools import permutations


class ModelEvaluator:
    """
    テストデータを用いて、モデルの評価を行う

    Attributes
    ----------
    rank_predictor: RankPredictor
        ある日付に開催されたレースの予測を行う
    """
    refund = Refund()

    def __init__(self, rank_predictor):
        self.rank_predictor = rank_predictor
        self.fukusho = self.refund.fukusho
        self.tansho = self.refund.tansho
        self.umaren = self.refund.umaren
        self.umatan = self.refund.umatan
        self.wide = self.refund.wide
        self.sanrentan = self.refund.sanrentan
        self.sanrenpuku = self.refund.sanrenpuku

    def fukusho_return(self, X, threshold=0.5):
        pred_table = self.__pred_table(X, threshold)
        n_bets = len(pred_table)
        return_list = []
        for race_id, preds in pred_table.groupby(level=0):
            return_list.append(np.sum([
                self.__bet(race_id, 'fukusho', umaban, 1) for umaban in preds['horse_num']
            ]))
        return_rate = np.sum(return_list) / n_bets
        std = np.std(return_list) * np.sqrt(len(return_list)) / n_bets
        n_hits = np.sum([x > 0 for x in return_list])
        return n_bets, return_rate, n_hits, std

    def tansho_return(self, X, threshold=0.5):
        pred_table = self.__pred_table(X, threshold)
        n_bets = len(pred_table)
        return_list = []
        for race_id, preds in pred_table.groupby(level=0):
            return_list.append(np.sum([self.__bet(race_id, 'tansho', umaban, 1) for umaban in preds['horse_num']]))
        std = np.std(return_list) * np.sqrt(len(return_list)) / n_bets
        n_hits = np.sum([x > 0 for x in return_list])
        return_rate = np.sum(return_list) / n_bets
        return n_bets, return_rate, n_hits, std

    def tansho_return_proper(self, X, threshold=0.5):
        pred_table = self.__pred_table(X, threshold)
        n_bets = len(pred_table)
        return_list = []
        for race_id, preds in pred_table.groupby(level=0):
            return_list.append(np.sum(preds.apply(lambda x: self.__bet(race_id, 'tansho', x['horse_num'], 1/x['odds']), axis=1)))
        bet_money = (1 / pred_table['odds']).sum()
        std = np.std(return_list) * np.sqrt(len(return_list)) / bet_money
        n_hits = np.sum([x > 0 for x in return_list])
        return_rate = np.sum(return_list) / bet_money
        return n_bets, return_rate, n_hits, std

    def umaren_box(self, X, threshold=0.5, n_aite=5):
        pred_table = self.__pred_table(X, threshold)
        n_bets = 0
        return_list = []
        for race_id, preds in pred_table.groupby(level=0):
            return_ = 0
            preds_jiku = preds.query('pred == 1')
            if len(preds_jiku) == 1:
                continue
            elif len(preds_jiku) >= 2:
                for umaban in combinations(preds_jiku['horse_num'], 2):
                    return_ += self.__bet(race_id, 'umaren', umaban, 1)
                    n_bets += 1
                return_list.append(return_)
        std = np.std(return_list) * np.sqrt(len(return_list)) / n_bets
        n_hits = np.sum([x > 0 for x in return_list])
        return_rate = np.sum(return_list) / n_bets
        return n_bets, return_rate, n_hits, std

    def umatan_box(self, X, threshold=0.5, n_aite=5):
        pred_table = self.__pred_table(X, threshold, is_bet_only=False)
        n_bets = 0
        return_list = []
        for race_id, preds in pred_table.groupby(level=0):
            return_ = 0
            preds_jiku = preds.query('pred == 1')
            if len(preds_jiku) == 1:
                continue
            elif len(preds_jiku) >= 2:
                for umaban in permutations(preds_jiku['horse_num'], 2):
                    return_ += self.__bet(race_id, 'umatan', umaban, 1)
                    n_bets += 1
            return_list.append(return_)

        std = np.std(return_list) * np.sqrt(len(return_list)) / n_bets
        n_hits = np.sum([x > 0 for x in return_list])
        return_rate = np.sum(return_list) / n_bets
        return n_bets, return_rate, n_hits, std

    def wide_box(self, X, threshold=0.5, n_aite=5):
        pred_table = self.__pred_table(X, threshold, is_bet_only=False)
        n_bets = 0
        return_list = []
        for race_id, preds in pred_table.groupby(level=0):
            return_ = 0
            preds_jiku = preds.query('pred == 1')
            if len(preds_jiku) == 1:
                continue
            elif len(preds_jiku) >= 2:
                for umaban in combinations(preds_jiku['horse_num'], 2):
                    return_ += self.__bet(race_id, 'wide', umaban, 1)
                    n_bets += 1
                return_list.append(return_)
        std = np.std(return_list) * np.sqrt(len(return_list)) / n_bets
        n_hits = np.sum([x > 0 for x in return_list])
        return_rate = np.sum(return_list) / n_bets
        return n_bets, return_rate, n_hits, std

    def sanrentan_box(self, X, threshold=0.5):
        pred_table = self.__pred_table(X, threshold)
        n_bets = 0
        return_list = []
        for race_id, preds in pred_table.groupby(level=0):
            return_ = 0
            if len(preds) < 3:
                continue
            else:
                for umaban in permutations(preds['horse_num'], 3):
                    return_ += self.__bet(race_id, 'sanrentan', umaban, 1)
                    n_bets += 1
                return_list.append(return_)
        std = np.std(return_list) * np.sqrt(len(return_list)) / n_bets
        n_hits = np.sum([x > 0 for x in return_list])
        return_rate = np.sum(return_list) / n_bets
        return n_bets, return_rate, n_hits, std

    def sanrenpuku_box(self, X, threshold=0.5):
        pred_table = self.__pred_table(X, threshold)
        n_bets = 0
        return_list = []
        for race_id, preds in pred_table.groupby(level=0):
            return_ = 0
            if len(preds) < 3:
                continue
            else:
                for umaban in combinations(preds['horse_num'], 3):
                    return_ += self.__bet(race_id, 'sanrenpuku', umaban, 1)
                    n_bets += 1
                return_list.append(return_)
        std = np.std(return_list) * np.sqrt(len(return_list)) / n_bets
        n_hits = np.sum([x > 0 for x in return_list])
        return_rate = np.sum(return_list) / n_bets
        return n_bets, return_rate, n_hits, std

    def umaren_nagashi(self, X, threshold=0.5, n_aite=5):
        pred_table = self.__pred_table(X, threshold, is_bet_only=False)
        n_bets = 0
        return_list = []
        for race_id, preds in pred_table.groupby(level=0):
            return_ = 0
            preds_jiku = preds.query('pred == 1')
            if len(preds_jiku) == 1:
                preds_aite = preds.sort_values('score', ascending=False).iloc[1:(n_aite+1)]['horse_num']
                return_ = preds_aite.map(lambda x: self.__bet(race_id, 'umaren', [preds_jiku['horse_num'].values[0], x], 1)).sum()
                n_bets += n_aite
                return_list.append(return_)
            elif len(preds_jiku) >= 2:
                for umaban in combinations(preds_jiku['horse_num'], 2):
                    return_ += self.__bet(race_id, 'umaren', umaban, 1)
                    n_bets += 1
                return_list.append(return_)
        std = np.std(return_list) * np.sqrt(len(return_list)) / n_bets
        n_hits = np.sum([x > 0 for x in return_list])
        return_rate = np.sum(return_list) / n_bets
        return n_bets, return_rate, n_hits, std

    def umatan_nagashi(self, X, threshold=0.5, n_aite=5):
        pred_table = self.__pred_table(X, threshold, is_bet_only=False)
        n_bets = 0
        return_list = []
        for race_id, preds in pred_table.groupby(level=0):
            return_ = 0
            preds_jiku = preds.query('pred == 1')
            if len(preds_jiku) == 1:
                preds_aite = preds.sort_values('score', ascending=False).iloc[1:(n_aite+1)]['horse_num']
                return_ = preds_aite.map(lambda x: self.__bet(race_id, 'umatan', [preds_jiku['horse_num'].values[0], x], 1)).sum()
                n_bets += n_aite
            elif len(preds_jiku) >= 2:
                for umaban in permutations(preds_jiku['horse_num'], 2):
                    return_ += self.__bet(race_id, 'umatan', umaban, 1)
                    n_bets += 1
            return_list.append(return_)
        std = np.std(return_list) * np.sqrt(len(return_list)) / n_bets
        n_hits = np.sum([x > 0 for x in return_list])
        return_rate = np.sum(return_list) / n_bets
        return n_bets, return_rate, n_hits, std

    def wide_nagashi(self, X, threshold=0.5, n_aite=5):
        pred_table = self.__pred_table(X, threshold, is_bet_only=False)
        n_bets = 0
        return_list = []
        for race_id, preds in pred_table.groupby(level=0):
            return_ = 0
            preds_jiku = preds.query('pred == 1')
            if len(preds_jiku) == 1:
                preds_aite = preds.sort_values('score', ascending=False).iloc[1:(n_aite+1)]['horse_num']
                return_ = preds_aite.map(lambda x: self.__bet(race_id, 'wide', [preds_jiku['horse_num'].values[0], x], 1)).sum()
                n_bets += len(preds_aite)
                return_list.append(return_)
            elif len(preds_jiku) >= 2:
                for umaban in combinations(preds_jiku['horse_num'], 2):
                    return_ += self.__bet(race_id, 'wide', umaban, 1)
                    n_bets += 1
                return_list.append(return_)
        std = np.std(return_list) * np.sqrt(len(return_list)) / n_bets
        n_hits = np.sum([x > 0 for x in return_list])
        return_rate = np.sum(return_list) / n_bets
        return n_bets, return_rate, n_hits, std

    # 1着, 2着固定の三連単フォーメーション
    def sanrentan_nagashi(self, X, threshold=1.5, n_aite=7):
        pred_table = self.__pred_table(X, threshold, is_bet_only=False).sort_values('score')
        n_bets = 0
        return_list = []
        for race_id, preds in pred_table.groupby(level=0):
            # pred == 1: thresholdの結果、購入すべきと判断されたhorse_num
            preds_jiku = preds.query('pred == 1')
            if len(preds_jiku) == 1:
                continue
            elif len(preds_jiku) == 2:
                preds_aite = preds.sort_values('score', ascending=False).iloc[2:(n_aite+2)]['horse_num']
                return_ = preds_aite.map(lambda x: self.__bet(race_id, 'sanrentan', np.append(preds_jiku['horse_num'].values, x), 1)).sum()
                n_bets += len(preds_aite)
                return_list.append(return_)
            elif len(preds_jiku) >= 3:
                return_ = 0
                for umaban in permutations(preds_jiku['horse_num'], 3):
                    return_ += self.__bet(race_id, 'sanrentan', umaban, 1)
                    n_bets += 1
                return_list.append(return_)
        std = np.std(return_list) * np.sqrt(len(return_list)) / n_bets
        n_hits = np.sum([x > 0 for x in return_list])
        return_rate = np.sum(return_list) / n_bets
        return n_bets, return_rate, n_hits, std

    def __binarization(self, X, threshold=0.5):
        y_pred = self.rank_predictor.__get_predictions(X)['score']
        self.proba = y_pred
        return [0 if p < threshold else 1 for p in y_pred]

    def __pred_table(self, X, threshold=0.5, is_bet_only=True):
        pred_table = X.copy()[['horse_number', 'odds']]
        pred_table['pred'] = self.__binarization(X, threshold)
        pred_table['score'] = self.proba
        if is_bet_only:
            return pred_table[pred_table['pred'] == 1]
        else:
            return pred_table[['horse_number', 'odds', 'score', 'pred']]

    def __bet(self, race_id, kind, umaban, amount):
        if kind == 'fukusho':
            rt_1R = self.fukusho.loc[race_id]
            return_ = (rt_1R[['horse_number_0', 'horse_number_1', 'horse_number_2']] == umaban)\
                .values * rt_1R[['return_0', 'return_1', 'return_2']].values * amount/100
            return_ = np.sum(return_)
        if kind == 'tansho':
            rt_1R = self.tansho.loc[race_id]
            return_ = (rt_1R['horse_number'] == umaban) * rt_1R['return'] * amount/100
        if kind == 'umaren':
            rt_1R = self.umaren.loc[race_id]
            return_ = (set(rt_1R[['horse_number_0', 'horse_number_1']]) == set(umaban)) * rt_1R['return']/100 * amount
        if kind == 'umatan':
            rt_1R = self.umatan.loc[race_id]
            return_ = (list(rt_1R[['horse_number_0', 'horse_number_1']]) == list(umaban)) * rt_1R['return']/100 * amount
        if kind == 'wide':
            rt_1R = self.wide.loc[race_id]
            return_ = (rt_1R[['horse_number_0', 'horse_number_1']].apply(lambda x: set(x) == set(umaban), axis=1)) * rt_1R['return']/100 * amount
            return_ = return_.sum()
        if kind == 'sanrentan':
            rt_1R = self.sanrentan.loc[race_id]
            return_ = (list(rt_1R[['horse_number_0', 'horse_number_1', 'horse_number_2']]) == list(umaban)) * rt_1R['return']/100 * amount
        if kind == 'sanrenpuku':
            rt_1R = self.sanrenpuku.loc[race_id]
            return_ = (set(rt_1R[['horse_number_0', 'horse_number_1', 'horse_number_2']]) == set(umaban)) * rt_1R['return']/100 * amount
        if not (return_ >= 0):
            return_ = amount
        return return_
