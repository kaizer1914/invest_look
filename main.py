from datetime import date
from alrs import Alrosa
from share_data import ShareData

ticker: str = input("Биржевой тикер: ")

begin_date = input("Начальная дата yyyy-mm-dd: ")
end_date = input("Конечная дата yyyy-mm-dd: ")

share = ShareData(ticker)
share.load_info()
share.load_history(begin_date, end_date)

print(f"Текущая цена: {share.get_current_price()}, {share.get_current_deviation()}%")
print(f"Текущая капитализация: {share.get_current_market_cap()}")

alrosa = Alrosa()
print(alrosa.get_fin_years())
print(alrosa.get_oper_years())

# for year in alrosa.get_fin_years():
#     print(f"year={year}, revenue={alrosa.get_revenue_per_share(year)}, "
#           f"ebitda={alrosa.get_ebitda_per_share(year)}, "
#           f"fcf={alrosa.get_fcf_per_share(year)}, "
#           f"net debt/ebitda={alrosa.get_net_debt_ebitda(year)}, "
#           f"price={alrosa.get_price(year, 0.25)}, {alrosa.get_price(year)}, {alrosa.get_price(year, 0.75)}")

if input("Любая клавиша для выхода"):
    exit(0)
