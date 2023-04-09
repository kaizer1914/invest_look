import pandas
from pandas import DataFrame
from share_data import ShareData

class MTS:
    def __init__(self) -> None:
        self.__ticker: str = "mtss"
        self.__num_shares: DataFrame = pandas.read_csv("data/" + self.__ticker + "/num_shares.csv")
        self.__cf: DataFrame = pandas.read_csv("data/" + self.__ticker + "/fin.csv")
        self.__debt: DataFrame = pandas.read_csv("data/" + self.__ticker + "/debt.csv")
        self.__sales_type: DataFrame = pandas.read_csv("data/" + self.__ticker + "/sales_type.csv")

    def get_num_shares(self, year: int) -> int:
        num_shares: DataFrame = self.__num_shares[self.__num_shares['year'] == year]
        count_shares: int = num_shares['number'].values[0]
        return count_shares

    def get_fcf(self, year: int) -> int:
        cf: DataFrame = self.__cf[self.__cf['cf'] == "fcf"] # искомая строка по значению 1 столбца
        fcf: int = cf[str(year)].values[0] # в этой строке ограничивает столбцом с заданным годом
        return fcf

    def get_sales(self, year: int) -> int:
        cf: DataFrame = self.__cf[self.__cf['cf'] == "sales"] # искомая строка по значению 1 столбца
        sales: int = cf[str(year)].values[0] # в этой строке ограничивает столбцом с заданным годом
        return sales

    def get_oibda(self, year: int) -> int:
        cf: DataFrame = self.__cf[self.__cf['cf'] == "oibda"] # искомая строка по значению 1 столбца
        oibda: int = cf[str(year)].values[0] # в этой строке ограничивает столбцом с заданным годом
        return oibda

    def get_net_debt(self, year: int) -> int:
        debt: DataFrame = self.__debt[self.__debt['debt'] == "net debt"] # искомая строка по значению 1 столбца
        net_debt: int = debt[str(year)].values[0] # в этой строке ограничивает столбцом с заданным годом
        return net_debt

    def get_net_debt_oibda(self, year: int) -> float:
        return round(self.get_net_debt(year) / self.get_oibda(year), 2)

    def get_price(self, year: int, quant: float=0.5) -> int:
        share: ShareData = ShareData(self.__ticker)
        share.load_history(str(year) + '-01-01', str(year) + '-12-31')
        return round(share.get_history()['mean_price'].quantile(quant), 2)

    def get_years(self) -> list[int]:
        fin: list[int] = self.__cf.columns.to_list() # искомая строка по значению 1 столбца
        fin.pop(0)
        for i in range(len(fin)):
            fin[i] = int(fin[i])
        return fin

    def get_sales_per_share(self, year: int) -> int:
        return round(self.get_sales(year) * 1e+3 / self.get_num_shares(year), 2)

    def get_oibda_per_share(self, year: int) -> int:
        return round(self.get_oibda(year) * 1e+3 / self.get_num_shares(year), 2)

    def get_fcf_per_share(self, year: int) -> int:
        return round(self.get_fcf(year) * 1e+3 / self.get_num_shares(year), 2)

    def get_net_debt_per_share(self, year: int) -> int:
        return round(self.get_net_debt(year) * 1e+3 / self.get_num_shares(year), 2)

    def get_sales_type(self) -> DataFrame:
        return self.__sales_type
