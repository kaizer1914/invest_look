from datetime import datetime

import pandas

from stock.moscow_exchange import MoscowExchange


class MarketCap:
    @staticmethod
    def get_median_price_history(ticker: str):
        price_df = MoscowExchange.load_security_history(ticker)
        # price_df['date'] = price_df['date'].map(lambda x: x[:4])  # В ДД-ММ-ГГГГ оставляем только год
        price_df = price_df.groupby(['date'], as_index=False).median()
        # price_df['date'] = price_df['date'].astype(int)
        price_df.rename(columns={'date': 'year'}, inplace=True)
        price_df['ticker'] = ticker
        return price_df

    @staticmethod
    def get_market_cap_history(ticker: str):
        current_year = datetime.now().year
        median_price = MarketCap.get_median_price_history(ticker)
        current_median_price = median_price[median_price['year'] == current_year]

        shares_count = pandas.read_csv('stock/shares_count.csv')
        market_cap_df = median_price.merge(shares_count, on=['ticker', 'year'])

        current_market_cup = MoscowExchange.get_current_year_market_cap(ticker)
        current_market_cup = current_market_cup.merge(current_median_price, on=['ticker', 'year'])
        market_cap_df = market_cap_df.merge(current_market_cup, how='outer')

        market_cap_df['market_cap'] = market_cap_df['shares_count'] * market_cap_df['medium_price']
        return market_cap_df
