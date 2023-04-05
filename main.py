from share_data import ShareData

ticker: str = input("Биржевой тикер: ")

begin_date = input("Начальная дата yyyy-mm-dd: ")
end_date = input("Конечная дата yyyy-mm-dd: ")

share = ShareData(ticker)
share.load_info()
share.load_history(begin_date, end_date)

print(f"Текущая цена: {share.get_current_price()}, {share.get_current_deviation()}%")
print(f"Текущая капитализация: {share.get_current_market_cap()}")



if input("Любая клавиша для выхода"):
    exit(0)
