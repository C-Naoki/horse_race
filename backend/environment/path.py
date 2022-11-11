import dataclasses
import os
from dotenv import load_dotenv

load_dotenv()


@dataclasses.dataclass(frozen=True)
class Path:
    # TODO: 環境変数から取得するようにする(ユーザー毎に必要なpathが異なる)
    BASE_EXCEL_PATH = os.environ['BASE_EXCEL_PATH']

    def get_xlsx(self, month, year):
        xlsx_dir = Path.EXCEL_PATH_BASE + f'{year}/xlsx/'
        return xlsx_dir, xlsx_dir + f'{month}月.xlsx'
