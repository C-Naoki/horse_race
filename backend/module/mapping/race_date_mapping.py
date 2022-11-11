from backend.module.crud.read import read_race_date_mapping


class RaceDateMapping:

    df = read_race_date_mapping()

    def get_date(self, race_id: str):
        return self.df[self.df['race_id'] == race_id].iat[0, 1]

    def get_year_month_day(self, race_id: str):
        date = self.get_date(race_id)
        return date.year, date.month, date.day

    def get_race_id_ls(self, date):
        return list(self.df[self.df['date'] == date]['race_id'])
