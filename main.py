from share_data import ShareData
from datetime import date

def input_begin_date() -> str:
    begin_date = date.today()
    begin_input: str = input("Начальная дата (год, месяц, день): ")
    begin_input: list[int] = [int(i) for i in begin_input.split()]

    for i in range(len(begin_input)):
        if i == 0:
            begin_date = begin_date.replace(year=begin_input[i])
        elif i == 1:
            begin_date = begin_date.replace(month=begin_input[i])
        elif i == 2:
            begin_date = begin_date.replace(day=begin_input[i])

    return begin_date.strftime("%Y-%m-%d")

def input_end_date() -> str:
    end_date = date.today()
    end_input: str = input("Конечная дата (год, месяц, день): ")
    end_input: list[int] = [int(i) for i in end_input.split()]
    
    for i in range(len(end_input)):
        if i == 0:
            end_date = end_date.replace(year=end_input[i])
        elif i == 1:
            end_date = end_date.replace(month=end_input[i])
        elif i == 2:
            end_date = end_date.replace(day=end_input[i])
    
    return end_date.strftime("%Y-%m-%d")

def main():
    ticker: str = input("Биржевой тикер: ")

    share = ShareData(ticker)
    try:
        share.load_info()
        share.load_history(input_begin_date(), input_end_date())
        
        print(f"Текущая цена: {share.get_current_price()}, {share.get_current_deviation()}%")
        print(f"Текущая капитализация: {share.get_current_market_cap()}")
    except Exception:
        print("Ошибка")

    if input("Любая клавиша для выхода"):
        exit(0)

main()
