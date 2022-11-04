import pandas
from pandas import DataFrame

'''
https://iss.moex.com/iss/engines/stock/markets/shares/securities.xml?iss.meta=off - список всех российских акций
https://iss.moex.com/iss/engines/stock/markets/foreignshares/securities.xml?iss.meta=off - список всех иностранных акций

https://iss.moex.com/iss/engines/stock/markets/shares.xml?iss.meta=off  - справка по рынкам российских акций
https://iss.moex.com/iss/engines/stock/markets/foreignshares.xml?iss.meta=off  - справка по рынкам иностранных акций

https://iss.moex.com/iss/engines/stock/markets/bonds/securities.xml?iss.meta=off - список всех облигаций
https://iss.moex.com/iss/engines/stock/markets/bonds.xml?iss.meta=off  - справка по рынкам облигаций
'''


class ShareStockData:
    def __init__(self, ticker: str):
        self.__ticker: str = ticker.upper()
        self.__info_df: DataFrame = DataFrame()
        self.__history_df: DataFrame = DataFrame()

    def load_sec_history(self, begin_date: str = None, end_date: str = None) -> DataFrame:
        start, end = '', ''
        if begin_date is not None:
            start = f'&from={begin_date}'
        if end_date is not None:
            end = f'&till={end_date}'

        index, page_size, total = 0, 0, 1
        self.__history_df = None

        while index + page_size <= total:
            url = f'https://iss.moex.com/iss/history/engines/stock/markets/shares/securities/{self.__ticker}.json?' \
                  f'iss.meta=off&start={index + page_size}{start}{end}'
            response_df = pandas.read_json(url)
            history_cursor = response_df['history.cursor']
            history_cursor_df = DataFrame(data=history_cursor.data, columns=history_cursor.columns)

            index = history_cursor_df['INDEX'].values[0]
            page_size = history_cursor_df['PAGESIZE'].values[0]
            total = history_cursor_df['TOTAL'].values[0]

            history = response_df['history']
            response_df = DataFrame(data=history.data, columns=history.columns)
            response_df = response_df[response_df['BOARDID'].isin(['TQBR'])]
            if self.__history_df is None:
                self.__history_df = response_df
            else:
                self.__history_df = pandas.concat([self.__history_df, response_df])

        self.__history_df = self.__history_df[[
            'SECID', 'SHORTNAME', 'TRADEDATE', 'NUMTRADES', 'VALUE', 'OPEN', 'LOW', 'HIGH',
            'WAPRICE', 'CLOSE', 'VOLUME']]
        self.__history_df = self.__history_df.rename(columns={'SECID': 'ticker',
                                                              'SHORTNAME': 'short_name',
                                                              'TRADEDATE': 'date',
                                                              'NUMTRADES': 'num_trades',
                                                              'VALUE': 'sum_per_day',
                                                              'VOLUME': 'sec_count_per_day',
                                                              'OPEN': 'open_price',
                                                              'LOW': 'low_price',
                                                              'HIGH': 'high_price',
                                                              'WAPRICE': 'median_price',
                                                              'CLOSE': 'close_price'
                                                              })
        self.__history_df = self.__history_df.fillna(0)
        null_price_index = self.__history_df[self.__history_df['sum_per_day'] == 0].index.values
        self.__history_df = self.__history_df.drop(index=null_price_index)
        self.__history_df = self.__history_df.reset_index(drop=True)
        return self.__history_df

    def load_info(self) -> DataFrame:
        url = f'https://iss.moex.com/iss/engines/stock/markets/shares/securities/{self.__ticker}' \
              f'/securities.json?iss.meta=off'
        response_df = pandas.read_json(url)
        response_df = response_df['securities']
        self.__info_df = DataFrame(data=response_df.data, columns=response_df.columns)
        self.__info_df = self.__info_df[self.__info_df['BOARDID'].isin(['TQBR'])]
        return self.__info_df

    def get_sec_history(self):
        return self.__history_df

    def get_info(self):
        return self.__info_df

    def get_current_market_cap(self):
        market_cap = self.__info_df['PREVWAPRICE'] * self.__info_df['ISSUESIZE']

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
        cur_df = ShareStockData.get_currencies_df()  # Получаем датафрейм с валютами с Мосбиржи
        cur_df = cur_df[cur_df['secid'].isin([currencies_par])]  # Находим строку в датафрейме с валютной парой
        course = cur_df['rate'].values[0]  # Извлекаем значение курса из строки
        return course
