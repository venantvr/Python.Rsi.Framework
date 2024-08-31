import pandas as pd
from pandas import DataFrame

from Python.Rsi.Tools.Dataframes import ColumnsManager


def adjust_iteratively(dataframe: DataFrame, column: str, bottom: float, top: float, iterations=100):
    total_adjustment = 0.0
    done = False
    i = 0
    while not done and i <= iterations:
        above_max = dataframe[column] > top
        below_min = dataframe[column] < bottom
        # Calcul des "surfaces" (ici, simplement le nombre de points au-dessus ou en dessous des seuils)
        surface_above = above_max.sum()
        surface_below = below_min.sum()
        # Calcul de l'ajustement nécessaire basé sur la différence de surfaces
        # Cette partie est très simplifiée et nécessiterait une approche plus sophistiquée pour un équilibrage précis
        adjustment = 50.0 * (surface_above - surface_below) / len(dataframe)
        # Application de l'ajustement
        dataframe[column] = dataframe[column] - adjustment
        total_adjustment = total_adjustment + adjustment
        done = (surface_above == surface_below)
        i = i + 1
    return dataframe[column]


def check_all_conditions(df: DataFrame, columns: list, window: int):
    """
    Marque les lignes qui font partie d'un groupe de 'num_consecutive' lignes consécutives
    où toutes les valeurs dans 'cols_to_check' sont True, indépendamment de l'index du DataFrame.
    """
    consecutive = 'consecutive'
    with ColumnsManager(dataframe=df,
                        drop=[]) as df:
        # Initialiser la colonne de marquage à False
        df[consecutive] = False
        # Convertir les noms des colonnes en positions pour une utilisation avec .iloc
        cols_positions = [df.columns.get_loc(col) for col in columns]
        # Vérifier les lignes jusqu'à ce qu'il reste moins que 'num_consecutive' lignes
        for i in range(len(df) - window + 1):
            # Vérifier si toutes les lignes consécutives satisfont les conditions
            all_true_in_consecutive_rows = all(df.iloc[i + j, cols_positions].all() for j in range(window))
            # Si oui, marquer toutes ces lignes comme True
            if all_true_in_consecutive_rows:
                df.iloc[i:i + window, df.columns.get_loc(consecutive)] = True
    return df


def set_index(dataframe: DataFrame):
    def fix_index(df):
        df = df[~df.index.duplicated(keep='first')]
        return df

    dataframe.loc[:, 'timestamp'] = pd.to_datetime(dataframe['timestamp'], utc=True)
    dataframe = dataframe.set_index('timestamp')
    return fix_index(dataframe)
