import pandas as pd
from pandas import DataFrame

from venantvr.dataframes import TemporaryColumnsManager


def adjust_column_values_within_limits(dataframe: DataFrame, column: str, lower_limit: float, upper_limit: float, max_iterations=100):
    """
    Ajuste les valeurs d'une colonne spécifique d'un DataFrame de manière itérative afin de minimiser le nombre de points
    qui se situent au-dessus ou en dessous des seuils spécifiés (upper_limit et lower_limit).

    ### Correspondance des noms (Ancien → Nouveau → Signification)
    | Ancien Nom          | Nouveau Nom                          | Signification                                                              |
    |---------------------|--------------------------------------|----------------------------------------------------------------------------|
    | `adjust_iteratively`| `adjust_column_values_within_limits` | Ajuste les valeurs d'une colonne d'un DataFrame dans des limites données.  |
    | `dataframe`         | `dataframe`                          | Le DataFrame contenant les données à ajuster.                              |
    | `column`            | `column`                             | La colonne du DataFrame à ajuster.                                         |
    | `bottom`            | `lower_limit`                        | La limite inférieure pour les valeurs de la colonne.                       |
    | `top`               | `upper_limit`                        | La limite supérieure pour les valeurs de la colonne.                       |
    | `iterations`        | `max_iterations`                     | Le nombre maximal d'itérations pour ajuster les valeurs (par défaut 100).  |
    """
    total_adjustment = 0.0
    done = False
    i = 0
    while not done and i <= max_iterations:
        above_max = dataframe[column] > upper_limit
        below_min = dataframe[column] < lower_limit
        surface_above = above_max.sum()
        surface_below = below_min.sum()
        adjustment = 50.0 * (surface_above - surface_below) / len(dataframe)
        dataframe[column] = dataframe[column] - adjustment
        total_adjustment = total_adjustment + adjustment
        done = (surface_above == surface_below)
        i = i + 1
    return dataframe[column]


def flag_rows_with_consecutive_true_values(df: DataFrame, columns: list, consecutive_window: int):
    """
    Marque les lignes faisant partie d'un groupe de 'consecutive_window' lignes consécutives où toutes les valeurs dans 'columns'
    sont True.

    ### Correspondance des noms (Ancien → Nouveau → Signification)
    | Ancien Nom             | Nouveau Nom                              | Signification                                                              |
    |------------------------|------------------------------------------|----------------------------------------------------------------------------|
    | `check_all_conditions` | `flag_rows_with_consecutive_true_values` | Marque les lignes avec des conditions consécutives remplies.               |
    | `df`                   | `df`                                     | Le DataFrame à analyser.                                                   |
    | `columns`              | `columns`                                | Liste des colonnes à vérifier.                                             |
    | `window`               | `consecutive_window`                     | Nombre de lignes consécutives satisfaisant les conditions.                 |
    """
    consecutive = 'consecutive'
    with TemporaryColumnsManager(dataframe=df, drop=[]) as df:
        df[consecutive] = False
        cols_positions = [df.columns.get_loc(col) for col in columns]
        for i in range(len(df) - consecutive_window + 1):
            all_true_in_consecutive_rows = all(df.iloc[i + j, cols_positions].all() for j in range(consecutive_window))
            if all_true_in_consecutive_rows:
                df.iloc[i:i + consecutive_window, df.columns.get_loc(consecutive)] = True
    return df


def set_timestamp_as_index(dataframe: DataFrame):
    """
    Convertit la colonne 'timestamp' en format datetime UTC, la définit comme index du DataFrame et supprime les doublons d'index.

    ### Correspondance des noms (Ancien → Nouveau → Signification)
    | Ancien Nom        | Nouveau Nom                | Signification                                                              |
    |-------------------|----------------------------|----------------------------------------------------------------------------|
    | `set_index`       | `set_timestamp_as_index`   | Définit 'timestamp' comme index du DataFrame et supprime les doublons.     |
    | `dataframe`       | `dataframe`                | Le DataFrame à traiter.                                                    |
    """

    def remove_duplicate_indices(df):
        df = df[~df.index.duplicated(keep='first')]
        return df

    dataframe.loc[:, 'timestamp'] = pd.to_datetime(dataframe['timestamp'], utc=True)
    dataframe = dataframe.set_index('timestamp')
    return remove_duplicate_indices(dataframe)
