import pandas
from pandas import DataFrame
from share_data import ShareData

class Alrosa:
    def __init__(self) -> None:
        self.__ticker: str = "alrs"
        self.__num_shares: DataFrame = pandas.read_csv("data/" + self.__ticker + "/num_shares.csv")
        self.__cf: DataFrame = pandas.read_csv("data/" + self.__ticker + "/fin/cf.csv")

    def get_num_shares(self, year: int) -> int:
        num_shares: DataFrame = self.__num_shares[self.__num_shares['year'] == year]
        count_shares: int = num_shares['number'].values[0]
        return count_shares

    def get_fcf(self, year: int) -> int:
        cf: DataFrame = self.__cf[self.__cf['CF'] == "Free cash flow"] # искомая строка по значению 1 столбца
        fcf: int = cf[str(year)].values[0] # в этой строке ограничивает столбцом с заданным годом
        return fcf

    def get_revenue(self, year: int) -> int:
        cf: DataFrame = self.__cf[self.__cf['CF'] == "Total revenue"] # искомая строка по значению 1 столбца
        revenue: int = cf[str(year)].values[0] # в этой строке ограничивает столбцом с заданным годом
        return revenue

    def get_ebitda(self, year: int) -> int:
        cf: DataFrame = self.__cf[self.__cf['CF'] == "EBITDA"] # искомая строка по значению 1 столбца
        ebitda: int = cf[str(year)].values[0] # в этой строке ограничивает столбцом с заданным годом
        return ebitda

    def get_revenue_per_share(self, year: int) -> int:
        return round(self.get_revenue(year) / (self.get_num_shares(year) / 1e6), 2)

    def get_ebitda_per_share(self, year: int) -> int:
        return round(self.get_ebitda(year) / (self.get_num_shares(year) / 1e6), 2)

    def get_fcf_per_share(self, year: int) -> int:
        return round(self.get_fcf(year) / (self.get_num_shares(year) / 1e6), 2)

    def get_median_price(self, year: int) -> int:
        share: ShareData = ShareData(self.__ticker)
        share.load_history(str(year) + '-01-01', str(year) + '-12-31')
        return round(share.get_history()['mean_price'].median(), 2)
