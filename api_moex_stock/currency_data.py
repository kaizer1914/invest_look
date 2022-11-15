import pandas
from pandas import DataFrame


class CurrencyData:

    @staticmethod
    def get_currencies_df() -> DataFrame:
        url = 'https://iss.moex.com/iss/statistics/engines/futures/markets/indicativerates/securities.json?iss.meta=off'
        response_df = pandas.read_json(url)
        response_df = response_df['securities']
        response_list = response_df.tolist()
        response_df = DataFrame(data=response_list[1], columns=response_list[0])
        return response_df

    @staticmethod
    def get_currency_course(first_currency: str, second_currency: str = 'RUB') -> float:
        first_currency = first_currency.upper()
        second_currency = second_currency.upper()
        currencies_par = first_currency + '/' + second_currency  # Валютная пара, которая интересует
        cur_df = CurrencyData.get_currencies_df()  # Получаем датафрейм с валютами с Мосбиржи
        cur_df = cur_df[cur_df['secid'].isin([currencies_par])]  # Находим строку в датафрейме с валютной парой
        course = cur_df['rate'].values[0]  # Извлекаем значение курса из строки
        return course
