import numpy as np
import pandas as pd
from backend.environment.columns import Columns


class RefundCalculator:

    rank_ls = ['A', 'B', 'C', '-']

    def __call__(self, predictions, race_id_ls, refund):
        # TODO 他馬券の追加(特にワイド)
        tanshoes = refund.tansho
        fukushoes = refund.fukusho
        sanrentans = refund.sanrentan
        race_results = pd.DataFrame(index=[], columns=Columns.RESULT_COLUMNS)
        fav_summaries = pd.DataFrame(index=[], columns=Columns.FAV_SUMMARY_COLUMNS)

        rank_counter = dict()
        money_counter = dict()
        for rank in self.rank_ls:
            rank_counter[rank] = np.zeros(4, dtype=int)
            money_counter[rank] = np.zeros(2)
        for race_id in race_id_ls:
            actual_top_3 = sanrentans.loc[race_id][['horse_number0', 'horse_number1', 'horse_number2']].astype(int)
            predictive_top_3 = self._remove_star(predictions.loc[race_id[-2:].lstrip('0')+'R'][2:5])

            tansho_odds = tanshoes.loc[race_id]
            fukusho_odds = fukushoes.loc[race_id]

            tansho_money = self.calculate_tansho_money(tansho_odds, predictive_top_3, actual_top_3)
            fukusho_money = self.calculate_fukusho_money(fukusho_odds, predictive_top_3, actual_top_3)

            race_results.loc[race_id[-2:].lstrip('0')+'R'] = [
                f"{actual_top_3[0]} → {actual_top_3[1]} → {actual_top_3[2]}",
                tansho_odds['money'] / 100,
                fukusho_odds['money1'] / 100,
                fukusho_odds['money2'] / 100,
                fukusho_odds['money3'] / 100,
                tansho_money,
                sum(fukusho_money),
            ]

            fav_rank = predictions.loc[race_id[-2:].lstrip('0')+'R', '本命馬ランク']
            try:
                rank_counter[fav_rank][list(actual_top_3).index(predictive_top_3[0])] += 1
            except ValueError:
                rank_counter[fav_rank][3] += 1
            money_counter[fav_rank] += np.array([tansho_money, fukusho_money[0]])

        rank_counter['Total'] = sum(rank_counter.values())
        money_counter['Total'] = sum(money_counter.values())

        for rank in rank_counter.keys():
            if '-' == rank:
                continue
            if sum(rank_counter[rank]):
                tansho_refund_ratio = round(money_counter[rank][0]/(100*sum(rank_counter[rank])), 4)
                fukusho_refund_ratio = round(money_counter[rank][1]/(100*sum(rank_counter[rank])), 4)
            else:
                tansho_refund_ratio = '-'
                fukusho_refund_ratio = '-'

            fav_summaries.loc[rank] = [
                f'{rank_counter[rank][0]}-{rank_counter[rank][1]}-{rank_counter[rank][2]}-{rank_counter[rank][3]}',
                f'{rank_counter[rank][0]}/{sum(rank_counter[rank])}',
                f'{sum(rank_counter[rank][0:3])}/{sum(rank_counter[rank])}',
                tansho_refund_ratio,
                fukusho_refund_ratio,
            ]

        return race_results, fav_summaries

    def _remove_star(self, predictions):
        return predictions.astype('str').str.strip('☆ ').astype('int')

    def calculate_tansho_money(self, tansho_odds, predictive_top_3, actual_top_3):
        if predictive_top_3[0] == actual_top_3[0]:
            return tansho_odds['money']
        else:
            return 0

    def calculate_fukusho_money(self, fukusho_odds, predictive_top_3, actual_top_3):
        fukusho_money = [0] * 3
        for i, horse_number in enumerate(actual_top_3):
            if horse_number in predictive_top_3.values:
                fukusho_money[np.where(predictive_top_3.values == horse_number)[0][0]] = fukusho_odds[f'money{i+1}']
        return fukusho_money
