import pandas
from pandas import DataFrame

'''
https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.xml?iss.meta=off - список российских акций
https://iss.moex.com/iss/engines/stock/markets/shares.xml?iss.meta=off  - справка по рынкам российских акций

https://iss.moex.com/iss/engines/stock/markets/bonds/securities.xml?iss.meta=off - список облигаций
https://iss.moex.com/iss/engines/stock/markets/bonds.xml?iss.meta=off  - справка по рынкам облигаций

** Возможные значения поля SecType:
1 - Акция обыкновенная 
2 - Акция привилегированная 
3 - Государственные облигации 
4 - Региональные облигации 
5 - Облигации центральных банков 
6 - Корпоративные облигации 
7 - Облигации МФО 
8 - Биржевые облигации 
9 - Паи открытых ПИФов 
A - Паи интервальных ПИФов 
B - Паи закрытых ПИФов 
C - Муниципальные облигации 
D - Депозитарные расписки 
E - Бумаги иностранных инвестиционных фондов (ETF) 
F - Ипотечный сертификат 
G - Корзина бумаг 
H - Доп. идентификатор списка 
I - ETC (товарные инструменты)
J - Пай биржевого ПИФа (Exchange Investment Unit share)
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

        self.__history_df = self.__history_df.fillna(0)
        null_price_index = self.__history_df[self.__history_df['VALUE'] == 0].index.values
        self.__history_df = self.__history_df.drop(index=null_price_index)
        self.__history_df = self.__history_df.reset_index(drop=True)
        return self.__history_df

    def load_info(self) -> DataFrame:
        url = f'https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{self.__ticker}' \
              f'/securities.json?iss.meta=off'
        response_df = pandas.read_json(url)

        securities_df = response_df['securities']
        marketdata_df = response_df['marketdata']

        securities_df = DataFrame(data=securities_df.data, columns=securities_df.columns)
        marketdata_df = DataFrame(data=marketdata_df.data, columns=marketdata_df.columns)

        self.__info_df = securities_df.merge(marketdata_df)
        return self.__info_df

    def get_sec_history(self):
        return self.__history_df

    def get_info(self):
        return self.__info_df

    @staticmethod
    def load_all_info() -> DataFrame:
        url = f'https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json?iss.meta=off'
        response_df = pandas.read_json(url)

        securities_df = response_df['securities']
        marketdata_df = response_df['marketdata']

        securities_df = DataFrame(data=securities_df.data, columns=securities_df.columns)
        marketdata_df = DataFrame(data=marketdata_df.data, columns=marketdata_df.columns)

        all_info_df = securities_df.merge(marketdata_df)
        return all_info_df
