from share_data import ShareData

ticker: str = str(input("Биржевой тикер: "))
begin_date = str(input("Начальная дата yyyy-mm-dd: "))
end_date = str(input("Конечная дата yyyy-mm-dd: "))

ticker.upper()
share = ShareData(ticker)
history = share.load_history(begin_date, end_date)
info = share.load_info()

print(f"Последняя цена: {info['LAST'].values[0]}")
print(history['WAPRICE'].describe(percentiles=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]))

if input():
    exit(0)
