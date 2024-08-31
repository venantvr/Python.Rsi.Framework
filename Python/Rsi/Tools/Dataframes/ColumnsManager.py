import warnings

from pandas import DataFrame


class ColumnsManager:

    def __init__(self, dataframe: DataFrame, keep: list = None, drop: list = None):
        self.df = dataframe
        self.keep_temp_columns = keep or []
        self.drop_temp_columns = drop or []

    def __enter__(self):
        # Assure simplement que les colonnes sont présentes, sans ajouter de données
        for column_name in self.keep_temp_columns + self.drop_temp_columns:
            if column_name not in self.df.columns:
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    self.df.loc[:, column_name] = None
        return self.df

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Supprime les colonnes temporaires du DataFrame
        if self.drop_temp_columns is not []:
            # if (not self.drop_temp_columns == ['macd'] and
            #         not self.drop_temp_columns == ['rsi'] and
            #         not self.drop_temp_columns == [] and
            #         not self.drop_temp_columns == ['no_lag_macd', 'signal', 'histogram'] and
            #         not self.drop_temp_columns == ['amount', 'closed']):
            #     logger.info(f'Suppression des colonnes {self.drop_temp_columns}')
            self.df.drop(columns=self.drop_temp_columns, inplace=True)
        else:
            columns = self.df.columns
            self.df.drop(columns=columns.difference(self.keep_temp_columns), inplace=True)
        # noinspection PyUnusedLocal
        stop = True
