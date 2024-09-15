from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from pandas import DataFrame, Series

from venantvr.business.bot_currency_pair import BotCurrencyPair
from venantvr.tooling.tooling_utils import timeframe_to_seconds
from venantvr.types.types_alias import GateioTimeFrame


def replace_nan_values(dataframe_column: Series):
    """
    Remplace les valeurs NaN dans une colonne de DataFrame par des valeurs générées aléatoirement autour
    de la première valeur non-NaN trouvée dans la colonne.

    ### Correspondance des noms (Ancien → Nouveau → Signification)
    | Ancien Nom          | Nouveau Nom           | Signification                                                                |
    |---------------------|-----------------------|------------------------------------------------------------------------------|
    | `remove_nan`        | `replace_nan_values`  | Fonction de remplacement des NaN dans une colonne par des valeurs générées   |
    | `first_non_nan`     | `first_valid_value`   | Première valeur non-NaN trouvée dans la colonne                              |
    | `column_filled`     | `filled_column`       | Colonne avec les NaN remplacés par des valeurs aléatoires                    |

    Args:
        dataframe_column (Series): La colonne du DataFrame contenant des valeurs NaN.

    Returns:
        Series: Une série avec les NaN remplacés par des valeurs générées aléatoirement.
    """
    if not dataframe_column.dropna().empty:
        first_valid_value = dataframe_column.dropna().iloc[0]
        filled_column = dataframe_column.apply(lambda x: first_valid_value + np.random.normal(0, 1) if pd.isna(x) else x)
        return filled_column
    else:
        return dataframe_column


def calculate_relative_strength_index(dataframe: DataFrame, price_columns: list, period_length=14):
    """
    Calcule l'indicateur de force relative (RSI) pour un ensemble de colonnes dans un DataFrame.

    ### Correspondance des noms (Ancien → Nouveau → Signification)
    | Ancien Nom        | Nouveau Nom                        | Signification                                                           |
    |-------------------|------------------------------------|-------------------------------------------------------------------------|
    | `calculate_rsi`   | `calculate_relative_strength_index`| Fonction pour calculer le RSI                                           |
    | `columns`         | `price_columns`                    | Liste des colonnes de prix pour calculer le RSI                         |
    | `length`          | `period_length`                    | La période pour le calcul du RSI                                        |
    | `price_change`    | `price_variation`                  | Variation des prix pour les colonnes sélectionnées                      |
    | `gain`            | `average_gain`                     | Moyenne des gains calculée à partir des variations positives            |
    | `loss`            | `average_loss`                     | Moyenne des pertes calculée à partir des variations négatives           |
    | `rs`              | `relative_strength_ratio`          | Ratio entre les gains moyens et les pertes moyennes                     |

    Args:
        dataframe (DataFrame): Le DataFrame contenant les colonnes de prix.
        price_columns (list): Liste des colonnes de prix pour lesquelles calculer le RSI.
        period_length (int, optional): La période de calcul du RSI (par défaut 14).

    Returns:
        Series: Une série contenant les valeurs de RSI.
    """
    if len(price_columns) == 1:
        price_variation = dataframe[price_columns[0]].diff().fillna(0.0)
    else:
        price_variation = dataframe[price_columns].mean(axis=1).diff().fillna(0.0)

    average_gain = (price_variation.where(price_variation > 0, 0)).ewm(alpha=1 / period_length, adjust=False).mean()
    average_loss = (-price_variation.where(price_variation < 0, 0)).ewm(alpha=1 / period_length, adjust=False).mean()
    relative_strength_ratio = average_gain / average_loss
    relative_strength_ratio.replace(-np.inf, np.nan, inplace=True)
    relative_strength_ratio.replace(+np.inf, np.nan, inplace=True)

    relative_strength_ratio = replace_nan_values(relative_strength_ratio)
    relative_strength_index = 100.0 - (100.0 / (1 + relative_strength_ratio))
    return relative_strength_index


def calculate_exponential_moving_average(dataframe: DataFrame, price_columns: list, period_length: int = 10):
    """
    Calcule la moyenne mobile exponentielle (EMA) pour un ensemble de colonnes dans un DataFrame.

    ### Correspondance des noms (Ancien → Nouveau → Signification)
    | Ancien Nom                              | Nouveau Nom                                | Signification                                                     |
    |-----------------------------------------|--------------------------------------------|-------------------------------------------------------------------|
    | `calculate_ema`                         | `calculate_exponential_moving_average`     | Fonction pour calculer la moyenne mobile exponentielle (EMA)      |
    | `columns`                               | `price_columns`                            | Liste des colonnes de prix pour calculer l'EMA                    |
    | `length`                                | `period_length`                            | Période pour le calcul de l'EMA                                   |
    | `new_dataframe`                         | `adjusted_dataframe`                       | DataFrame ajusté contenant les colonnes de prix pour le calcul    |
    | `column_name_that_prevents_warning`     | `main_price_column`                        | Nom utilisé pour la colonne de prix dans le DataFrame             |

    Args:
        dataframe (DataFrame): Le DataFrame contenant les colonnes de prix.
        price_columns (list): Liste des colonnes pour lesquelles calculer l'EMA.
        period_length (int, optional): La période de calcul de l'EMA (par défaut 10).

    Returns:
        Series: Une série contenant les valeurs de l'EMA.
    """
    adjusted_dataframe = DataFrame()
    main_price_column = 'close'

    if len(price_columns) == 1:
        adjusted_dataframe[main_price_column] = dataframe[price_columns[0]].fillna(0.0)
    else:
        adjusted_dataframe[main_price_column] = dataframe[price_columns].mean(axis=1).fillna(0.0)

    return adjusted_dataframe.ewm(span=period_length, adjust=False).mean().fillna(0.0)
    # return ta.ema(adjusted_dataframe, length=period_length).fillna(0.0)


def calculate_hourly_volume(currency_pair: BotCurrencyPair, dataframe: DataFrame, rsi_column: str, current_time: datetime, timeframe: GateioTimeFrame,
                            tolerance_bandwidth: float):
    """
    Calcule le volume normalisé par seconde et le volume moyen pour les segments de données correspondant à un RSI donné.

    ### Correspondance des noms (Ancien → Nouveau → Signification)
    | Ancien Nom             | Nouveau Nom                     | Signification                                                               |
    |------------------------|---------------------------------|-----------------------------------------------------------------------------|
    | `hourly_volume`        | `calculate_hourly_volume`       | Fonction pour calculer le volume horaire normalisé                          |
    | `column`               | `rsi_column`                    | Colonne contenant les valeurs de l'indicateur RSI                           |
    | `now`                  | `current_time`                  | Heure actuelle utilisée pour le calcul du temps écoulé                      |
    | `bandwidth`            | `tolerance_bandwidth`           | Largeur de bande de tolérance pour filtrer les segments basés sur le RSI    |
    | `current_rsi`          | `current_rsi_value`             | Valeur actuelle du RSI                                                      |
    | `current_volume`       | `current_trading_volume`        | Volume de trading actuel dans la période                                    |
    | `normalized_volume`    | `normalized_volume_per_second`  | Volume normalisé par seconde                                                |
    | `filtered_segment`     | `filtered_rsi_segment`          | Segment filtré en fonction du RSI courant et de la bande de tolérance       |
    | `mean_volume`          | `mean_filtered_volume`          | Volume moyen des segments filtrés                                           |

    Args:
        currency_pair (BotCurrencyPair): La paire de devises pour laquelle calculer le volume.
        dataframe (DataFrame): Le DataFrame contenant les données de prix et de volume.
        rsi_column (str): Le nom de la colonne contenant les valeurs de RSI.
        current_time (datetime): L'heure actuelle pour calculer le temps écoulé.
        timeframe (GateioTimeFrame): L'intervalle de temps pour les chandeliers.
        tolerance_bandwidth (float): La bande de tolérance autour du RSI courant pour filtrer les segments.

    Returns:
        tuple: Un tuple contenant le volume normalisé et le volume moyen.
    """

    # Utilisation de la durée du timeframe pour garantir un calcul robuste
    total_seconds_in_timeframe = timeframe_to_seconds(timeframe)

    # Calcul du temps écoulé dans la dernière bougie
    elapsed_time_in_candle = (current_time - dataframe.index[-1]) % timedelta(seconds=total_seconds_in_timeframe)
    elapsed_time_in_seconds = elapsed_time_in_candle.total_seconds()

    # Obtenir les valeurs actuelles du RSI et du volume de trading
    current_rsi_value = dataframe[rsi_column].iloc[-1]
    current_trading_volume = dataframe['volume'].iloc[-1]

    # Gestion du cas où elapsed_time_in_seconds est égal à 0 (bougie complète)
    if elapsed_time_in_seconds == 0:
        normalized_volume_per_second = current_trading_volume  # Utiliser le dernier volume fourni
    else:
        # Calcul du volume normalisé par seconde si la bougie n'est pas complète
        normalized_volume_per_second = total_seconds_in_timeframe * (current_trading_volume / elapsed_time_in_seconds)

    # Filtrer les segments basés sur le RSI avec la tolérance définie
    filtered_rsi_segment = dataframe[
        (dataframe[rsi_column] >= current_rsi_value - tolerance_bandwidth) &
        (dataframe[rsi_column] <= current_rsi_value + tolerance_bandwidth)
    ]

    # Calcul du volume moyen des segments filtrés, retourner 0 si aucune valeur n'est trouvée (éviter NaN)
    mean_filtered_volume = filtered_rsi_segment['volume'].mean() or 0

    # Retourner le volume normalisé et le volume moyen filtré
    return normalized_volume_per_second, mean_filtered_volume


"""
| Ancien Nom             | Nouveau Nom                           | Signification                                                              |
|------------------------|---------------------------------------|----------------------------------------------------------------------------|
| `remove_nan`           | `replace_nan_values`                  | Remplacer les valeurs NaN par des valeurs générées aléatoirement           |
| `calculate_rsi`        | `calculate_relative_strength_index`   | Calculer l'indicateur de force relative (RSI)                              |
| `calculate_ema`        | `calculate_exponential_moving_average`| Calculer la moyenne mobile exponentielle (EMA)                             |
| `hourly_volume`        | `calculate_hourly_volume`             | Calculer le volume horaire normalisé basé sur l'indicateur RSI             |
"""
