from datetime import date
from alrs import Alrosa
from share_data import ShareData

ticker: str = str(input("Биржевой тикер: "))
years: int = int(input("Количество лет: "))

begin_date = date(date.today().year - years, date.today().month, date.today().day).strftime("%Y-%m-%d")
share = ShareData(ticker)
history = share.load_history(begin_date)

print(f"Текущая цена: {share.get_current_price()}, {share.get_current_deviation()}%")
print(f"Текущая капитализация: {share.get_current_market_cap()}")
print(Alrosa().get_num_shares(2021))
print(share.get_current_num_shares())
# print(share.get_history()['mean_price'])

if input("Любая клавиша для выхода"):
    exit(0)
