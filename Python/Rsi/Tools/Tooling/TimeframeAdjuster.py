import pandas as pd
from Python.Rsi.Tools.Types import GateioTimeFrame, CandlesCountLambda
from pandas import DataFrame, Timestamp
from sklearn.preprocessing import MinMaxScaler


class TimeframeAdjuster:
    """
    Classe TimeframeAdjuster pour ajuster les index des DataFrames en fonction des timeframes et normaliser les colonnes.

    Cette classe permet d'ajuster les index des données des paires de devises à partir des bougies (candlesticks)
    et de normaliser les colonnes de données dans un DataFrame.

    ### Correspondance des noms (Ancien → Nouveau → Signification)
    | Ancien Nom                   | Nouveau Nom                            | Signification                                                       |
    |------------------------------|----------------------------------------|---------------------------------------------------------------------|
    | `Adjuster`                   | `TimeframeAdjuster`                    | Nom de la classe ajusté pour refléter sa fonction d'ajustement.     |
    | `adjust_indexes`             | `adjust_dataframe_indexes`             | Ajuste les index des DataFrames en fonction des timeframes.         |
    | `candlesticks`               | `candlestick_dataframes`               | Dictionnaire contenant les DataFrames pour chaque paire de devises. |
    | `expected_number_of_candles` | `calculate_expected_candlestick_count` | Fonction pour calculer le nombre attendu de bougies.                |
    | `currency_pairs_index`       | `currency_pair_mapping`                | Mapping des paires de devises.                                      |
    | `scaler`                     | `data_normalizer`                      | Normaliseur de données pour les colonnes.                           |
    | `normalize_dataframe`        | `normalize_dataframe_columns`          | Normalise les colonnes spécifiées dans un DataFrame.                |
    """

    def __init__(self):
        """
        Initialise une instance de TimeframeAdjuster avec un scaler (normaliseur).
        """
        self.data_normalizer = MinMaxScaler()

    @staticmethod
    def adjust_dataframe_indexes(timeframe: GateioTimeFrame, candlestick_dataframes: dict,
                                 calculate_expected_candlestick_count: CandlesCountLambda,
                                 currency_pair_mapping: dict):
        """
        Ajuste les index des DataFrames pour chaque paire de devises et timeframe, et normalise leur longueur
        en fonction du nombre attendu de bougies.

        Args:
            timeframe (GateioTimeFrame): Timeframe à ajuster.
            candlestick_dataframes (dict): Dictionnaire contenant les DataFrames pour chaque paire de devises et timeframe.
            calculate_expected_candlestick_count (CandlesCountLambda): Fonction pour calculer le nombre attendu de bougies.
            currency_pair_mapping (dict): Dictionnaire de mappage des paires de devises.

        Returns:
            dict: Le dictionnaire ajusté de candlestick DataFrames.
        """
        # Initialisation du dictionnaire avec l'index maximum pour chaque paire.
        max_index = {pair: Timestamp('1970-01-01 00:00:00+0000', tz='UTC') for timeframe_key in candlestick_dataframes
                     for pair in candlestick_dataframes[timeframe_key]}

        # Mise à jour des index maximums pour chaque paire de devises.
        for timeframe_key, pairs in candlestick_dataframes.items():
            for pair, dataframe in pairs.items():
                last_index = dataframe.index[-1]
                max_index[pair] = max(max_index[pair], last_index)

        # Ajout de l'offset de temps pour chaque DataFrame en fonction de l'index maximum.
        for timeframe_key, pairs in candlestick_dataframes.items():
            for pair, dataframe in pairs.items():
                timedelta = max_index[pair] - dataframe.index[-1]
                offset = pd.DateOffset(seconds=timedelta.seconds)
                dataframe.index = dataframe.index + offset

        # Ajustement du nombre de bougies pour chaque paire de devises.
        for timeframe_key, pairs in candlestick_dataframes.items():
            for pair, dataframe in pairs.items():
                currency_pair = currency_pair_mapping[pair]
                number_of_candles = calculate_expected_candlestick_count(currency_pair, timeframe)
                candlestick_dataframes[timeframe_key][pair] = pairs[pair].tail(number_of_candles)

        return candlestick_dataframes

    def normalize_dataframe_columns(self, dataframe: DataFrame, columns: list):
        """
        Normalise les colonnes spécifiées dans le DataFrame en appliquant un normaliseur (MinMaxScaler).

        Args:
            dataframe (DataFrame): Le DataFrame contenant les colonnes à normaliser.
            columns (list): Liste des noms de colonnes à normaliser.

        Returns:
            DataFrame: Le DataFrame avec les colonnes normalisées.
        """
        for column in columns:
            non_nan_values = dataframe[column].dropna()
            scaled_values = self.data_normalizer.fit_transform(non_nan_values.values.reshape(-1, 1))
            dataframe.loc[dataframe[column].notnull(), column] = (100.0 * scaled_values.flatten()).round(decimals=2)
        return dataframe
