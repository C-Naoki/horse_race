import dataclasses


@dataclasses.dataclass(frozen=True)
class Mapping:
    PLACE_ID_MAPPING = {
        '札幌': '01', '函館': '02', '福島': '03', '新潟': '04', '東京': '05',
        '中山': '06', '中京': '07', '京都': '08', '阪神': '09', '小倉': '10'
    }

    ID_PLACE_MAPPING = {value: key for key, value in PLACE_ID_MAPPING.items()}

    RACE_TYPE_MAPPING = {
        '芝': '芝', 'ダ': 'ダート', '障': '障害'
    }

    ID_CLASS_MAPPING = {
        0: '新馬', 1: '未勝利', 2: '1勝クラス', 3: '2勝クラス', 4: '3勝クラス', 5: 'オープン'
    }
