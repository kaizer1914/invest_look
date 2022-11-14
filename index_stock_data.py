import pandas
from pandas import DataFrame


class IndexStockData:
    def __init__(self, ticker: str):
        self.__ticker: str = ticker.upper()
        self.__info_df: DataFrame = DataFrame()
        self.__history_df: DataFrame = DataFrame()

    def load_history(self, begin_date: str = None, end_date: str = None) -> DataFrame:
        start, end = '', ''
        self.__history_df = DataFrame()
        page: int = 0

        if begin_date is not None:
            start = f'&from={begin_date}'
        if end_date is not None:
            end = f'&till={end_date}'

        while True:
            url = f'https://iss.moex.com/iss/history/engines/stock/markets/index/boards/SNDX/securities/' \
                  f'{self.__ticker}.json?iss.meta=off&start={page}{start}{end}'
            response_df = pandas.read_json(url)
            history = response_df['history']
            response_df = DataFrame(data=history.data, columns=history.columns)
            if response_df.empty:
                break
            else:
                page += 100
            print(page)

            if self.__history_df.empty:
                self.__history_df = response_df
            else:
                self.__history_df = pandas.concat([self.__history_df, response_df])

        self.__history_df.fillna(0, inplace=True)
        self.__history_df.reset_index(drop=True, inplace=True)
        return self.__history_df

    def load_info(self) -> DataFrame:
        url = f'https://iss.moex.com/iss/engines/stock/markets/index/boards/SNDX/securities/{self.__ticker}' \
              f'/securities.json?iss.meta=off'
        response_df = pandas.read_json(url)

        securities_df = response_df['securities']
        marketdata_df = response_df['marketdata']

        securities_df = DataFrame(data=securities_df.data, columns=securities_df.columns)
        marketdata_df = DataFrame(data=marketdata_df.data, columns=marketdata_df.columns)

        self.__info_df = securities_df.merge(marketdata_df)
        return self.__info_df

    def get_history(self):
        return self.__history_df

    def get_info(self):
        return self.__info_df

    @staticmethod
    def load_all_info() -> DataFrame:
        url = f'https://iss.moex.com/iss/engines/stock/markets/index/boards/SNDX/securities.json?iss.meta=off'
        response_df = pandas.read_json(url)

        securities_df = response_df['securities']
        marketdata_df = response_df['marketdata']

        securities_df = DataFrame(data=securities_df.data, columns=securities_df.columns)
        marketdata_df = DataFrame(data=marketdata_df.data, columns=marketdata_df.columns)

        all_info_df = securities_df.merge(marketdata_df)
        return all_info_df
