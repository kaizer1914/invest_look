import pandas
from pandas import DataFrame
from share_data import ShareData

class Seligdar:
    def __init__(self):
        self.__ticker: str = "selg"
        self.__num_shares: DataFrame = pandas.read_csv("data/" + self.__ticker + "/num_shares.csv")
        self.__fin: DataFrame = pandas.read_csv("data/" + self.__ticker + "/fin.csv")
        self.__oper: DataFrame = pandas.read_csv("data/" + self.__ticker + "/oper.csv")

    def get_num_shares(self, year: int) -> int:
        num_shares: DataFrame = self.__num_shares[self.__num_shares['year'] == year]
        count_shares: int = num_shares['number'].values[0]
        return count_shares

    def get_fcf(self, year: int) -> int:
        cf: DataFrame = self.__fin[self.__fin['млн руб'] == "FCF"] # искомая строка по значению 1 столбца
        fcf: int = cf[str(year)].values[0] # в этой строке ограничивает столбцом с заданным годом
        return fcf

    def get_revenue(self, year: int) -> int:
        cf: DataFrame = self.__fin[self.__fin['млн руб'] == "Выручка"] # искомая строка по значению 1 столбца
        revenue: int = cf[str(year)].values[0] # в этой строке ограничивает столбцом с заданным годом
        return revenue

    def get_ebitda(self, year: int) -> int:
        cf: DataFrame = self.__fin[self.__fin['млн руб'] == "EBITDA"] # искомая строка по значению 1 столбца
        ebitda: int = cf[str(year)].values[0] # в этой строке ограничивает столбцом с заданным годом
        return ebitda

    def get_price(self, year: int, quant: float=0.5) -> int:
        share: ShareData = ShareData(self.__ticker)
        return round(share.get_history(str(year) + '-01-01', str(year) + '-12-31')['mean_price'].quantile(quant), 2)

    def get_net_debt(self, year: int) -> int:
        debt: DataFrame = self.__fin[self.__fin['млн руб'] == "Чистый долг"] # искомая строка по значению 1 столбца
        net_debt: int = debt[str(year)].values[0] # в этой строке ограничивает столбцом с заданным годом
        return net_debt

    def get_net_debt_ebitda(self, year: int) -> float:
        return round(self.get_net_debt(year) / self.get_ebitda(year), 2)

    def get_fin_years(self) -> list[int]:
        fin: list[int] = self.__fin.columns.to_list() # искомая строка по значению 1 столбца
        fin.pop(0)
        for i in range(len(fin)):
            fin[i] = int(fin[i])
        return fin

    def get_oper_years(self) -> list[int]:
        oper: list[int] = self.__oper.columns.to_list() # искомая строка по значению 1 столбца
        oper.pop(0)
        for i in range(len(oper)):
            oper[i] = int(oper[i])
        return oper

    def get_revenue_per_share(self, year: int) -> float:
        return round(self.get_revenue(year) / self.get_num_shares(year) * 1e3, 2)

    def get_ebitda_per_share(self, year: int) -> float:
        return round(self.get_ebitda(year) / self.get_num_shares(year) * 1e3, 2)

    def get_fcf_per_share(self, year: int) -> float:
        return round(self.get_fcf(year) / self.get_num_shares(year) * 1e3, 2)

    def get_net_debt_per_share(self, year: int) -> float:
        return round(self.get_net_debt(year) / self.get_num_shares(year) * 1e3, 2)

    def get_ev_ebitda(self, year: int) -> float:
        return round((self.get_net_debt(year) + self.get_num_shares(year) * self.get_price(year)) / self.get_ebitda(year) / 1e3, 2)
