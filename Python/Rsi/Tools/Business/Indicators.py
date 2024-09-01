from datetime import datetime

import numpy as np
import pandas as pd
from Python.Rsi.Tools.Business import BotCurrencyPair
from Python.Rsi.Tools.Types import GateioTimeFrame
from pandas import DataFrame, Series


def remove_nan(dataframe_column: Series):
    """
    Remplace les valeurs NaN dans une colonne de DataFrame par des valeurs générées aléatoirement autour
    de la première valeur non-NaN trouvée dans la colonne.

    Args:
        dataframe_column (Series): La colonne du DataFrame contenant des valeurs NaN.

    Returns:
        Series: Une série avec les NaN remplacés par des valeurs générées aléatoirement.
    """
    if not dataframe_column.dropna().empty:
        # Trouver la première valeur non-NaN
        first_non_nan = dataframe_column.dropna().iloc[0]
        # Calculer le bruit pour chaque élément NaN individuellement et remplir
        column_filled = dataframe_column.apply(lambda x: first_non_nan + np.random.normal(0, 1) if pd.isna(x) else x)
        return column_filled
    else:
        return dataframe_column


def calculate_rsi(dataframe: DataFrame, columns: list, length=14):
    """
    Calcule l'indicateur de force relative (RSI) pour un ensemble de colonnes dans un DataFrame.

    Args:
        dataframe (DataFrame): Le DataFrame contenant les colonnes de prix.
        columns (list): Liste des colonnes pour lesquelles calculer le RSI.
        length (int, optional): La période de calcul du RSI (par défaut 14).

    Returns:
        Series: Une série contenant les valeurs de RSI.
    """
    if len(columns) == 1:
        # Calcul de la variation des prix pour une seule colonne
        price_change = dataframe[columns[0]].diff().fillna(0.0)
    else:
        # Calcul de la variation moyenne des prix pour plusieurs colonnes
        price_change = dataframe[columns].mean(axis=1).diff().fillna(0.0)

    # Calcul des gains et des pertes
    gain = (price_change.where(price_change > 0, 0)).ewm(alpha=1 / length, adjust=False).mean()
    loss = (-price_change.where(price_change < 0, 0)).ewm(alpha=1 / length, adjust=False).mean()

    # Calcul du ratio de gain/perte
    rs = gain / loss
    rs.replace(-np.inf, np.nan, inplace=True)
    rs.replace(+np.inf, np.nan, inplace=True)

    # Remplissage des valeurs manquantes par du bruit aléatoire
    rs = remove_nan(rs)

    # Calcul final du RSI
    output = 100.0 - (100.0 / (1 + rs))
    return output


def calculate_ema(dataframe: DataFrame, columns: list, length: int = 10):
    """
    Calcule la moyenne mobile exponentielle (EMA) pour un ensemble de colonnes dans un DataFrame.

    Args:
        dataframe (DataFrame): Le DataFrame contenant les colonnes de prix.
        columns (list): Liste des colonnes pour lesquelles calculer l'EMA.
        length (int, optional): La période de calcul de l'EMA (par défaut 10).

    Returns:
        Series: Une série contenant les valeurs de l'EMA.
    """
    new_dataframe = DataFrame()
    column_name_that_prevents_warning = 'close'

    if len(columns) == 1:
        # Utiliser la colonne spécifiée ou remplir par des zéros si NaN
        new_dataframe[column_name_that_prevents_warning] = dataframe[columns[0]].fillna(0.0)
    else:
        # Utiliser la moyenne des colonnes spécifiées
        new_dataframe[column_name_that_prevents_warning] = dataframe[columns].mean(axis=1).fillna(0.0)

    # Calcul de l'EMA et remplissage des NaN avec des zéros
    return new_dataframe.ta.ema(length=length).fillna(0.0)


# noinspection PyUnusedLocal
def hourly_volume(currency_pair: BotCurrencyPair, dataframe: DataFrame, column: str, now: datetime, timeframe: GateioTimeFrame, bandwidth: float):
    """
    Calcule le volume normalisé par seconde et le volume moyen pour les segments de données correspondant à un RSI donné.

    Args:
        currency_pair (BotCurrencyPair): La paire de devises pour laquelle calculer le volume.
        dataframe (DataFrame): Le DataFrame contenant les données de prix et de volume.
        column (str): Le nom de la colonne contenant les valeurs de RSI.
        now (datetime): L'heure actuelle pour calculer le temps écoulé.
        timeframe (GateioTimeFrame): L'intervalle de temps pour les chandeliers.
        bandwidth (float): La bande de tolérance autour du RSI courant pour filtrer les segments.

    Returns:
        tuple: Un tuple contenant le volume normalisé et le volume moyen.
    """
    # Obtenir le timeframe de référence à partir des chandeliers
    original_timeframe = (dataframe.index[-1] - dataframe.index[0]) / (len(dataframe) - 1)
    original_seconds = original_timeframe.total_seconds()

    # Obtenir le temps écoulé dans le chandelier courant
    elapsed_time = (now - dataframe.index[-1]) % original_timeframe
    elapsed_time_seconds = elapsed_time.total_seconds()

    # Obtenir les valeurs courantes du chandelier
    current_rsi = dataframe[column].iloc[-1]
    current_volume = dataframe.volume.iloc[-1]

    # Calculer le volume normalisé par seconde
    normalized_volume = original_seconds * (current_volume / elapsed_time_seconds)

    # Filtrer le DataFrame pour les segments où le RSI est dans la bande de tolérance
    filtered_segment = dataframe[(dataframe[column] >= current_rsi - bandwidth) & (dataframe[column] <= current_rsi + bandwidth)]

    # Calculer le volume moyen des segments filtrés
    mean_volume = filtered_segment.volume.mean()

    # Retourner le volume normalisé et le volume moyen
    return normalized_volume, mean_volume
