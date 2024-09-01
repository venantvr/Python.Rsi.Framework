import pandas as pd
from pandas import DataFrame

from Python.Rsi.Tools.Dataframes import ColumnsManager


def adjust_iteratively(dataframe: DataFrame, column: str, bottom: float, top: float, iterations=100):
    """
    Ajuste les valeurs d'une colonne spécifique d'un DataFrame de manière itérative afin de minimiser le nombre de points
    qui se situent au-dessus ou en dessous des seuils spécifiés (top et bottom).

    Paramètres :
    dataframe (DataFrame) : Le DataFrame contenant les données à ajuster.
    column (str) : Le nom de la colonne à ajuster.
    bottom (float) : La limite inférieure pour les valeurs de la colonne.
    top (float) : La limite supérieure pour les valeurs de la colonne.
    iterations (int, optionnel) : Le nombre maximal d'itérations pour ajuster les valeurs (par défaut 100).

    Retourne :
    Series : La colonne ajustée du DataFrame.
    """

    total_adjustment = 0.0  # Variable pour suivre l'ajustement total appliqué
    done = False  # Indicateur pour savoir si l'ajustement est terminé
    i = 0  # Compteur d'itérations

    # Boucle d'ajustement itérative
    while not done and i <= iterations:
        # Identifie les lignes où les valeurs sont au-dessus de la limite supérieure
        above_max = dataframe[column] > top

        # Identifie les lignes où les valeurs sont en-dessous de la limite inférieure
        below_min = dataframe[column] < bottom

        # Calcule le nombre de points au-dessus de la limite supérieure
        surface_above = above_max.sum()

        # Calcule le nombre de points en-dessous de la limite inférieure
        surface_below = below_min.sum()

        # Calcule l'ajustement nécessaire en fonction de la différence entre les surfaces au-dessus et en-dessous
        # Ici, l'ajustement est simplifié en tant que proportion de la différence des surfaces par rapport à la taille totale du DataFrame
        adjustment = 50.0 * (surface_above - surface_below) / len(dataframe)

        # Applique l'ajustement aux valeurs de la colonne
        dataframe[column] = dataframe[column] - adjustment

        # Met à jour l'ajustement total effectué
        total_adjustment = total_adjustment + adjustment

        # Détermine si l'équilibre est atteint (si le nombre de points au-dessus et en-dessous est égal)
        done = (surface_above == surface_below)

        # Incrémente le compteur d'itérations
        i = i + 1

    # Retourne la colonne ajustée du DataFrame
    return dataframe[column]


def check_all_conditions(df: DataFrame, columns: list, window: int):
    """
    Marque les lignes qui font partie d'un groupe de 'window' lignes consécutives
    où toutes les valeurs dans 'columns' sont True, indépendamment de l'index du DataFrame.

    Paramètres :
    df (DataFrame) : Le DataFrame à analyser.
    columns (list) : Liste des noms des colonnes à vérifier.
    window (int) : Nombre de lignes consécutives devant satisfaire la condition.

    Retourne :
    DataFrame : Le DataFrame original avec une colonne supplémentaire 'consecutive'
    indiquant les lignes qui font partie de séquences consécutives répondant à la condition.
    """

    consecutive = 'consecutive'

    # Utilisation d'un gestionnaire de contexte personnalisé (ColumnsManager)
    # pour manipuler le DataFrame de manière sécurisée et propre.
    with ColumnsManager(dataframe=df, drop=[]) as df:
        # Initialiser la colonne de marquage 'consecutive' à False pour toutes les lignes
        df[consecutive] = False

        # Convertir les noms des colonnes en positions d'index pour une utilisation avec .iloc
        cols_positions = [df.columns.get_loc(col) for col in columns]

        # Boucler à travers les lignes du DataFrame jusqu'à ce qu'il reste moins de 'window' lignes
        for i in range(len(df) - window + 1):
            # Vérifier si toutes les lignes dans la fenêtre 'window' ont toutes les valeurs True
            # dans les colonnes spécifiées
            all_true_in_consecutive_rows = all(df.iloc[i + j, cols_positions].all() for j in range(window))

            # Si la condition est remplie pour toutes les lignes dans la fenêtre,
            # marquer ces lignes comme True dans la colonne 'consecutive'
            if all_true_in_consecutive_rows:
                df.iloc[i:i + window, df.columns.get_loc(consecutive)] = True

    # Retourner le DataFrame modifié avec la colonne 'consecutive' mise à jour
    return df


def set_index(dataframe: DataFrame):
    """
    Convertit la colonne 'timestamp' en format datetime UTC, la définit comme index du DataFrame
    et supprime les doublons d'index.

    Paramètres :
    dataframe (DataFrame) : Le DataFrame à traiter.

    Retourne :
    DataFrame : Le DataFrame avec la colonne 'timestamp' en tant qu'index, sans doublons d'index.
    """

    def fix_index(df):
        """
        Supprime les doublons dans l'index du DataFrame, ne gardant que la première occurrence.

        Paramètres :
        df (DataFrame) : Le DataFrame dont on veut supprimer les doublons d'index.

        Retourne :
        DataFrame : Le DataFrame sans doublons d'index.
        """
        df = df[~df.index.duplicated(keep='first')]
        return df

    # Convertit la colonne 'timestamp' en format datetime avec le fuseau horaire UTC
    dataframe.loc[:, 'timestamp'] = pd.to_datetime(dataframe['timestamp'], utc=True)

    # Définit la colonne 'timestamp' comme l'index du DataFrame
    dataframe = dataframe.set_index('timestamp')

    # Applique la fonction 'fix_index' pour supprimer les doublons d'index et retourne le DataFrame
    return fix_index(dataframe)
