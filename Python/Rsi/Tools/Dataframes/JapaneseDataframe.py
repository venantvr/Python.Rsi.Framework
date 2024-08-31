from pandas import DataFrame


class JapaneseDataframe(DataFrame):

    def __init__(self, data, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

    @classmethod
    def from_dataframe(cls, df):
        return cls(df.values, index=df.index, columns=df.columns)
