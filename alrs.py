import pandas

class Alrosa:
    def __init__(self) -> None:
        self.__ticker = "ALRS"

    def get_num_shares(self, year: int) -> int:
        df = pandas.read_csv("data/" + self.__ticker.lower() + "/num_shares.csv")
        df = df[df['year'] == year]
        num_shares: int = df['number'].values[0]
        return num_shares
