from datetime import date

from share_data import ShareData

ticker: str = str(input("Биржевой тикер: "))
years: int = int(input("Количество лет: "))

begin_date = date(date.today().year - years, date.today().month, date.today().day).strftime("%Y-%m-%d")

share = ShareData(ticker)
history = share.load_history(begin_date)
info = share.load_info()

print(f"Последняя цена: {share.get_last_price()}, {share.get_last_deviation()}%")

if input("Любая клавиша для выхода"):
    exit(0)
