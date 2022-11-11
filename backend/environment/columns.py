import dataclasses


@dataclasses.dataclass(frozen=True)
class Columns:
    """
    予想結果を整理する際に格納するDataFrameのcolumns
    """

    DROP_COLUMNS = ['jockey_id', 'breeder_id', 'owner_id', 'trainer_id', 'birthday', 'venue']

    PREDICTION_COLUMNS = ["本命馬ランク", 'レースクラス', "1着予想◎", "2着予想○", "3着予想▲", "4着予想△", "5着予想☆", "6着予想×", "頭数"]

    RESULT_COLUMNS = ["結果", "単勝オッズ", "1着複勝オッズ", "2着複勝オッズ", "3着複勝オッズ", "単勝回収額", "複勝回収額"]

    FAV_SUMMARY_COLUMNS = ["着順", "単勝的中率", "複勝的中率", "単勝回収率", "複勝回収率"]

    REFUND_COLUMNS_2 = ["ワイド", "三連複", "三連単"]

    TOTAL_COLUMNS = [
        '単勝A', '複勝A', '三連単流しA', '三連複流しA',
        '単勝B', '複勝B', '三連単流しB', '三連複流しB',
        '単勝C', '複勝C', '三連単流しC', '三連複流しC',
        '単勝ABC', '複勝ABC', '三連単流しABC', '三連複流しABC',
        '単勝', '複勝', '三連単流し', '三連複流し'
    ]
