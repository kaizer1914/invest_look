from datetime import date
from alrs import Alrosa
from share_data import ShareData

ticker: str = str(input("Биржевой тикер: "))
years: int = int(input("Количество лет: "))

begin_date = date(date.today().year - years, date.today().month, date.today().day).strftime("%Y-%m-%d")

share = ShareData(ticker)
share.load_info()
share.load_history(begin_date)

print(f"Текущая цена: {share.get_current_price()}, {share.get_current_deviation()}%")
print(f"Текущая капитализация: {share.get_current_market_cap()}")

alrosa = Alrosa()
for year in range(2017, 2022):
    print(f"year={year}, revenue={alrosa.get_revenue_per_share(year)}, "
          f"ebitda={alrosa.get_ebitda_per_share(year)}, "
          f"fcf={alrosa.get_fcf_per_share(year)}, "
          f"net debt/ebitda={alrosa.get_net_debt_ebitda(year)}, "
          f"price={alrosa.get_price(year, 0.25)}, {alrosa.get_price(year)}, {alrosa.get_price(year, 0.75)}")

if input("Любая клавиша для выхода"):
    exit(0)
