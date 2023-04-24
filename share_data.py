import pandas
from pandas import DataFrame
import sqlite3
from time import sleep
from datetime import datetime, timedelta
from urllib.error import URLError

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

    def get_ticker(self) -> str:
        return self.__ticker

    def __load_history(self, begin_date: str = None, end_date: str = None):
        start, end = '', ''
        history_df = DataFrame()
        page: int = 0
        
        # Находим отличную от waprice среднюю цену (только сессии торгов на бирже, а не общую)
        def divide(a: int, b: int) -> float:
            return a / b

        if begin_date is not None:
            start = f'&from={begin_date}'
        if end_date is not None:
            end = f'&till={end_date}'

        while True:
            url = f'https://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/' \
                f'{self.__ticker}.json?iss.meta=off&start={page}{start}{end}&numtrades=1'
            try:
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
            except URLError:
                print(f"Сервер устал {self.__ticker}")
                sleep(60)

        if not history_df.empty:
            # Преобразуем полученный датафрейм
            # Оставляем только нужные колонки
            history_df = history_df[['TRADEDATE', 'SHORTNAME', 'SECID', 'NUMTRADES', 'VALUE', 'OPEN', 'LOW', 'HIGH', 'WAPRICE', 'CLOSE', 'VOLUME']]
            history_df = history_df.astype({'TRADEDATE': 'datetime64'}) # Дату из строки в божеский вид        
            # history_df = history_df[history_df['NUMTRADES'] > 0] # Удаляем дни с нулевым числом заявок за день
            # Находим отличную от waprice среднюю цену (только сессии торгов на бирже, а не общую)
            history_df['mean_price'] = history_df.apply(lambda x: divide(x['VALUE'], x['VOLUME']), axis=1)
            with sqlite3.connect("stock.db") as con:
                history_df.to_sql("history_share", con, if_exists='append', index=False)

    def __restore_history(self, begin_date: str = None, end_date: str = None) -> DataFrame:
        request: str = f"SELECT * FROM history_share WHERE SECID = '{self.__ticker}' AND TRADEDATE >= '{begin_date}' AND TRADEDATE <= '{end_date}';"
        if begin_date is None:
            request = f"SELECT * FROM history_share WHERE SECID = '{self.__ticker}' AND TRADEDATE <= '{end_date}';"
        elif end_date is None:
            request = f"SELECT * FROM history_share WHERE SECID = '{self.__ticker}' AND TRADEDATE >= '{begin_date}';"
        history: DataFrame = DataFrame()
        with sqlite3.connect("stock.db") as con:
            history = pandas.read_sql(request, con)
        return history

    def __get_next_date(self) -> str:
        next_date: datetime = None
        request: str = f"SELECT MAX(TRADEDATE) FROM history_share WHERE SECID = '{self.__ticker}';"
        response: str = None
        with sqlite3.connect("stock.db") as con:
            try:
                response = pandas.read_sql(request, con).values[0][0]
            except:
                response = None

            if response is not None:
                next_date: datetime = datetime.strptime(response, "%Y-%m-%d %H:%M:%S")
                next_date += timedelta(days=1)

        if response is None:
            return next_date
        else:
            return next_date.strftime("%Y-%m-%d")

    # грузит данные из базы и дозагружает с сайти московской биржи (по последней дате)
    def get_history(self, begin_date: str = None, end_date: str = None) -> DataFrame:
        next_date: str = self.__get_next_date()
        if next_date is None:
            self.__load_history()
            print(f"Скачиваем всю историю котировок {self.__ticker}")
        else:
            self.__load_history(begin_date=next_date)
            print(f"Обновлены данные {self.__ticker} с {next_date}")
        return self.__restore_history(begin_date, end_date)

    def load_info(self) -> DataFrame:
        url = f'https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{self.__ticker}' \
              f'/securities.json?iss.meta=off'
        response_df = pandas.read_json(url)

        securities_df = response_df['securities']
        marketdata_df = response_df['marketdata']

        securities_df = DataFrame(data=securities_df.data, columns=securities_df.columns)
        marketdata_df = DataFrame(data=marketdata_df.data, columns=marketdata_df.columns)

        info_df = securities_df.merge(marketdata_df)

        # Преобразуем полученный датафрейм
        info_df = info_df[['SECID', 'SHORTNAME', 'LOTSIZE', 'FACEVALUE', 'DECIMALS', 'SECNAME', 'MINSTEP',
                                         'FACEUNIT', 'ISSUESIZE', 'ISIN', 'CURRENCYID', 'LISTLEVEL', 'OPEN', 'LOW',
                                         'HIGH', 'LAST', 'WAPRICE', 'NUMTRADES', 'VOLTODAY', 'VALTODAY', 'VALTODAY_RUR',
                                         'VALTODAY_USD', 'NUMBIDS', 'NUMOFFERS', 'HIGHBID', 'LOWOFFER',
                                         'ISSUECAPITALIZATION']]
        return info_df

    def get_info(self) -> DataFrame:
        request = f"SELECT * FROM info_share WHERE SECID = '{self.__ticker}';"
        info: DataFrame = DataFrame()
        with sqlite3.connect("stock.db") as con:
            info = pandas.read_sql(request, con)
        return info

    def get_current_num_shares(self, fresh_info: DataFrame=None) -> int:
        if fresh_info is None:
            return self.get_info()['ISSUESIZE'].values[0]
        else:
            return self.load_info()['ISSUESIZE'].values[0]

    def get_current_deviation(self, begin_date: str = None, end_date: str = None, fresh_info: DataFrame=None) -> float:
        med = self.get_history(begin_date, end_date)['mean_price'].median()
        res: float = round(self.get_current_price(fresh_info) / med * 100 - 50, 2)
        return res

    def get_current_price(self, fresh_info: DataFrame=None) -> float:
        if fresh_info is None:
            return self.get_info()['LAST'].values[0]
        else:
            return self.load_info()['LAST'].values[0]

    def get_current_market_cap(self, fresh_info: DataFrame=None) -> float:
        if fresh_info is None:
            return round(self.get_info()['ISSUECAPITALIZATION'].values[0])
        else:
            return round(self.load_info()['ISSUECAPITALIZATION'].values[0])

    @staticmethod
    def update_all_info():
        # Total - 250
        # MOEXBMI - TOP-100
        # IMOEX - TOP-40
        index: str = 'MOEXBMI'
        url = f'https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json?iss.meta=off&index={index}&sort_column=VALTODAY&sort_order=des'
        response_df = pandas.read_json(url)

        securities_df = response_df['securities']
        marketdata_df = response_df['marketdata']

        securities_df = DataFrame(data=securities_df.data, columns=securities_df.columns)
        marketdata_df = DataFrame(data=marketdata_df.data, columns=marketdata_df.columns)

        all_info_df = securities_df.merge(marketdata_df)
        all_info_df = all_info_df[['SECID', 'SHORTNAME', 'LOTSIZE', 'FACEVALUE', 'DECIMALS', 'SECNAME', 'MINSTEP',
                                   'FACEUNIT', 'ISSUESIZE', 'ISIN', 'CURRENCYID', 'LISTLEVEL', 'OPEN', 'LOW',
                                   'HIGH', 'LAST', 'WAPRICE', 'NUMTRADES', 'VOLTODAY', 'VALTODAY', 'VALTODAY_RUR',
                                   'VALTODAY_USD', 'NUMBIDS', 'NUMOFFERS', 'HIGHBID', 'LOWOFFER',
                                   'ISSUECAPITALIZATION']]
        with sqlite3.connect("stock.db") as con:
            all_info_df.to_sql("info_share", con, if_exists='replace', index=False)

    @staticmethod
    def get_all_tickers() -> list[str]:
        request = f"SELECT SECID FROM info_share WHERE FACEUNIT = 'SUR';"
        tickers: list[str] = list()
        with sqlite3.connect("stock.db") as con:
            result = pandas.read_sql(request, con)
            for val in result.values:
                tickers.append(val[0])
        return tickers
