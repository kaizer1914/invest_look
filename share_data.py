import pandas
from pandas import DataFrame
import sqlite3

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


class ShareData:
    def __init__(self, ticker: str):
        self.__ticker: str = ticker.upper()
        self.__info_df: DataFrame = DataFrame()

    def __load_history(self, begin_date: str = None, end_date: str = None):
        start, end = '', ''
        history_df = DataFrame()
        page: int = 0
        
        # Находим отличную от waprice среднюю цену (только сессии торгов на бирже, а не общую)
        def divide(a: int, b: int):
            return round(a / b, 2)

        if begin_date is not None:
            start = f'&from={begin_date}'
        if end_date is not None:
            end = f'&till={end_date}'

        while True:
            url = f'https://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/' \
                  f'{self.__ticker}.json?iss.meta=off&start={page}{start}{end}'
            response_df = pandas.read_json(url)
            history = response_df['history']
            response_df = DataFrame(data=history.data, columns=history.columns)
            if response_df.empty:
                break
            else:
                page += 100

            if history_df.empty:
                history_df = response_df
            else:
                history_df = pandas.concat([history_df, response_df])

        # Преобразуем полученный датафрейм
        # Оставляем только нужные колонки
        history_df = history_df[['TRADEDATE', 'SHORTNAME', 'SECID', 'NUMTRADES', 'VALUE', 'OPEN', 'LOW', 'HIGH', 'WAPRICE', 'CLOSE', 'VOLUME']]
        history_df = history_df.astype({'TRADEDATE': 'datetime64'}) # Дату из строки в божеский вид        
        history_df = history_df[history_df['NUMTRADES'] > 0] # Удаляем дни с нулевым числом заявок за день
        # Находим отличную от waprice среднюю цену (только сессии торгов на бирже, а не общую)
        history_df['mean_price'] = history_df.apply(lambda x: divide(x['VALUE'], x['VOLUME']), axis=1)
        self.__save_history(history_df) # Сохраняем в БД

    def __save_history(self, history: DataFrame):
        with sqlite3.connect("history.db") as con:
            history.to_sql("price", con, if_exists='append', index=False)

    def __restore_history(self, begin_date: str = None, end_date: str = None) -> DataFrame:
        request: str = f"SELECT * FROM price WHERE SECID = '{self.__ticker}' AND TRADEDATE >= '{begin_date}' AND TRADEDATE <= '{end_date}';"
        if begin_date is None:
            request = f"SELECT * FROM price WHERE SECID = '{self.__ticker}' AND TRADEDATE <= '{end_date}';"
        elif end_date is None:
            request = f"SELECT * FROM price WHERE SECID = '{self.__ticker}' AND TRADEDATE >= '{begin_date}';"
        history: DataFrame = DataFrame()
        with sqlite3.connect("history.db") as con:
            history = pandas.read_sql(request, con)
        return history

    def __get_max_date(self) -> str:
        max_date: str = None
        request: str = f"SELECT MAX(TRADEDATE) FROM price WHERE SECID = '{self.__ticker}';"
        with sqlite3.connect("history.db") as con:
            try:
                max_date = pandas.read_sql(request, con).values[0][0]
                max_date = max_date[:10]
            except:
                max_date = None
        return max_date

    # грузит данные из базы и дозагружает с сайти московской биржи
    def get_history(self, begin_date: str = None, end_date: str = None) -> DataFrame:
        try:
            self.__load_history(self.__get_max_date())
        except:
            print("Новые данные не загружены")
        return self.__restore_history(begin_date, end_date)

    def load_info(self) -> DataFrame:
        url = f'https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{self.__ticker}' \
              f'/securities.json?iss.meta=off'
        response_df = pandas.read_json(url)

        securities_df = response_df['securities']
        marketdata_df = response_df['marketdata']

        securities_df = DataFrame(data=securities_df.data, columns=securities_df.columns)
        marketdata_df = DataFrame(data=marketdata_df.data, columns=marketdata_df.columns)

        self.__info_df = securities_df.merge(marketdata_df)

        # Преобразуем полученный датафрейм
        self.__info_df = self.__info_df[['SECID', 'SHORTNAME', 'LOTSIZE', 'FACEVALUE', 'DECIMALS', 'SECNAME', 'MINSTEP',
                                         'FACEUNIT', 'ISSUESIZE', 'ISIN', 'CURRENCYID', 'LISTLEVEL', 'OPEN', 'LOW',
                                         'HIGH', 'LAST', 'WAPRICE', 'NUMTRADES', 'VOLTODAY', 'VALTODAY', 'VALTODAY_RUR',
                                         'VALTODAY_USD', 'NUMBIDS', 'NUMOFFERS', 'HIGHBID', 'LOWOFFER',
                                         'ISSUECAPITALIZATION']]
        return self.__info_df

    def get_info(self) -> DataFrame:
        return self.__info_df

    def get_current_num_shares(self) -> int:
        return self.get_info()['ISSUESIZE'].values[0]

    def get_current_deviation(self) -> int:
        med = self.get_history()['mean_price'].median()
        res: int = round(self.get_current_price() / med * 100 - 50)
        return res

    def get_current_price(self) -> float:
        return self.get_info()['LAST'].values[0]

    def get_current_market_cap(self) -> float:
        return round(self.get_info()['ISSUECAPITALIZATION'].values[0])

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
