import pandas
from pandas import DataFrame


# Справка по режиму торгов облигациями (boards)
# TQOB - Гособлигации

# TQCB - Облигации
# TQOY - Облигации (CNY)
# TQOD - Облигации (USD)
# TQOE - Облигации (EUR)

# TQIR - Облигации ПИР
# TQIY - Облигации ПИР (CNY)
# TQIU - Облигации ПИР (USD)
# TQIE - Облигации ПИР (EUR)

# TQRD - Облигации Д (дефолтные)
# TQUD - Облигации Д (USD)
# TQED - Облигации Д (EUR)

# Замена значений типа бумаги на более понятные
# '3', 'ОФЗ'
# '4', 'Муниципальные'
# '5', 'ЦБ'
# '6', 'Корпоративные'
# '7', 'МФО'
# '8', 'Корпоративные'
# 'C', 'Муниципальные'

class BondsData:
    def __init__(self, board: str = 'TQCB'):
        self.__url = f'https://iss.moex.com/iss/engines/stock/markets/bonds/boards/{board}' \
                     f'/securities.json?iss.meta=off'
        self.__bonds_df = DataFrame()

    def load_bonds_df(self) -> DataFrame:
        response_data = pandas.read_json(self.__url)
        securities = response_data['securities']
        market_data = response_data['marketdata']
        market_yields = response_data['marketdata_yields']

        # Задаем содержимое и заголовки колонок
        securities_df = DataFrame(data=securities.data, columns=securities.columns)
        market_data_df = DataFrame(data=market_data.data, columns=market_data.columns)
        market_yields_df = DataFrame(data=market_yields.data, columns=market_yields.columns)

        # Объединяем таблицы
        securities_df = pandas.merge(securities_df, market_yields_df, how='left').dropna(axis=1, how='all')

        securities_df = securities_df[securities_df['PRICE'].notna()]  # Удаляем такие строки с нулевой ценой
        securities_df = securities_df.query("YIELDDATETYPE == 'MATDATE'")
        securities_df = securities_df.query("BUYBACKDATE == '0000-00-00'")
        securities_df = securities_df.query("YIELDATPREVWAPRICE != 0")
        securities_df = securities_df.query("FACEVALUE == 1000")
        securities_df = securities_df.query("EFFECTIVEYIELD > 0")
        securities_df = securities_df.query("(FACEUNIT == 'SUR' & COUPONPERCENT > 5) | (FACEUNIT != 'SUR')")

        # Удаляем лишние столбцы
        securities_df = securities_df.drop(['DECIMALS', 'SEQNUM', 'SYSTIME', 'BOARDID', 'BOARDNAME', 'STATUS',
                                            'MARKETCODE', 'OFFERDATE', 'YIELDDATETYPE', 'YIELDTOOFFER', 'INSTRID',
                                            'BUYBACKDATE', 'BUYBACKPRICE', 'REMARKS'],
                                           axis=1)

        # Приводим к типу данных строки
        # securities_df['YIELDDATE'] = securities_df['YIELDDATE'].astype(datetime64)
        # securities_df['MATDATE'] = securities_df['MATDATE'].astype(datetime64)
        # securities_df['OFFERDATE'] = securities_df['OFFERDATE'].astype(datetime64)

        securities_df.reset_index(inplace=True)
        securities_df = securities_df.drop(['index'], axis=1)
        self.__bonds_df = securities_df
        return self.__bonds_df
