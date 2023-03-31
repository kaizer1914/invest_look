from datetime import date

from share_data import ShareData

ticker: str = str(input("Биржевой тикер: "))
years: int = int(input("Количество лет: "))

begin_date = date(date.today().year - years, date.today().month, date.today().day).strftime("%Y-%m-%d")
share = ShareData(ticker)
history = share.load_history(begin_date)

print(f"Последняя цена: {share.get_last_price()}, {share.get_last_deviation()}%")
print(share.get_info()['ISSUECAPITALIZATION'].values[0])

if input("Любая клавиша для выхода"):
    exit(0)
