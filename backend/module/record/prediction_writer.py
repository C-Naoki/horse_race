import pandas as pd
from backend.environment.path import Path
from backend.module.mapping import RaceDateMapping
from backend.module.record import ExcelDecorator, BasicExcelWriter
from backend.environment.mapping import Mapping


class PredictionWriter(BasicExcelWriter):

    path = Path()
    race_date_mapping = RaceDateMapping()

    def __init__(self, refund_calculator):
        self.refund_calculator = refund_calculator

    def __call__(self, shaped_predictions, race_id_ls, refund):
        race_id = race_id_ls[0]
        year, month, day = self.race_date_mapping.get_year_month_day(race_id)
        xlsx_dir_path, xlsx_file_path = self.path.get_xlsx(month, year)
        venue = Mapping.ID_PLACE_MAPPING[race_id[4:6]]
        sheet_name = f'{venue}{day}日'

        refund_results, fav_summaries = self.refund_calculator(shaped_predictions, race_id_ls, refund)
        records = pd.concat([shaped_predictions, refund_results], axis=1)

        self._mkdir(xlsx_dir_path)
        self._mkxlsx(xlsx_file_path)

        self._overwrite_df2xlsx(records, xlsx_file_path, sheet_name)
        records_decorator = ExcelDecorator(xlsx_file_path, sheet_name, records.shape)
        records_decorator()

        self._append_df2xlsx(fav_summaries, xlsx_file_path, sheet_name)
        fav_summaries_decorator = ExcelDecorator(
            xlsx_file_path,
            sheet_name,
            fav_summaries.shape,
            upper_left=[records_decorator.row_headline+records_decorator.row_length+2, 1]
        )
        fav_summaries_decorator(
            headline_color_mapping={
                'ffbf7f': 'A',
                'a8d3ff': 'B',
                'd3d3d3': 'C',
                },
            pct_list=['単勝回収率', '複勝回収率']
            )
