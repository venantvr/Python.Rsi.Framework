from pandas import DataFrame


class NewColumnsTracker:
    def __init__(self, dataframe: DataFrame, target_set: set[str]):
        self.dataframe = dataframe
        self.target_set = target_set
        self.initial_columns = set(dataframe.columns)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.target_set.update(set(self.dataframe.columns) - self.initial_columns)
