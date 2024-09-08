import math
from pandas import DataFrame
from Python.Rsi.Tools.Quotes import Price
from Python.Rsi.Tools.Tooling import convert_gateio_timeframe_to_pandas
from Python.Rsi.Tools.Types import GateioTimeFrame, PandasTimeFrame


def round_up(value, decimals=4):
    """
    Arrondit une valeur à la hausse à un certain nombre de décimales.

    Args:
        value (float): La valeur à arrondir.
        decimals (int, optional): Le nombre de décimales (par défaut 4).

    Returns:
        float: La valeur arrondie à la hausse.
    """
    factor = 10 ** decimals
    return math.ceil(value * factor) / factor


def round_down(value, decimals=4):
    """
    Arrondit une valeur à la baisse à un certain nombre de décimales.

    Args:
        value (float): La valeur à arrondir.
        decimals (int, optional): Le nombre de décimales (par défaut 4).

    Returns:
        float: La valeur arrondie à la baisse.
    """
    factor = 10 ** decimals
    return math.floor(value * factor) / factor


def convert_percentage_to_decimal(percentage: str):
    """
    Convertit une chaîne de pourcentage en une valeur décimale.

    Args:
        percentage (str): La chaîne représentant un pourcentage (ex. "25%").

    Returns:
        float: La valeur du pourcentage sous forme décimale.
    """
    return float(percentage.strip('%'))


def calculate_stoploss_index(percentage: str):
    """
    Calcule l'indice de stop-loss à partir d'un pourcentage donné.

    Args:
        percentage (str): La chaîne représentant un pourcentage (ex. "5%").

    Returns:
        float: L'indice de stop-loss calculé.
    """
    return (100.0 - convert_percentage_to_decimal(percentage)) / 100.0


def calculate_profit_index(percentage: str):
    """
    Calcule l'indice de profit à partir d'un pourcentage donné.

    Args:
        percentage (str): La chaîne représentant un pourcentage (ex. "5%").

    Returns:
        float: L'indice de profit calculé.
    """
    return (100.0 + convert_percentage_to_decimal(percentage)) / 100.0


def calculate_max_quote_index(percentage: str):
    """
    Calcule l'indice de quote maximum à partir d'un pourcentage donné.

    Args:
        percentage (str): La chaîne représentant un pourcentage (ex. "25%").

    Returns:
        float: L'indice de quote maximum calculé.
    """
    return convert_percentage_to_decimal(percentage) / 100.0


def calculate_percentage(a: float | Price, b: float | Price) -> float:
    """
    Calcule le pourcentage de `a` par rapport à `b`.

    Args:
        a (float | Price): La première valeur ou un objet Price.
        b (float | Price): La deuxième valeur ou un objet Price.

    Returns:
        float: Le pourcentage de `a` par rapport à `b`.
    """
    if isinstance(a, Price):
        a = a.price
    if isinstance(b, Price):
        b = b.price
    return round(100.0 * a / b, 2)


def resample_dataframe(dataframe: DataFrame, resample_period: GateioTimeFrame, expected_length: int):
    """
    Resample un DataFrame sur une période donnée et retourne le nombre de lignes attendu.

    Args:
        dataframe (DataFrame): Le DataFrame à resampler.
        resample_period (GateioTimeFrame): La période de resampling.
        expected_length (int): Le nombre de lignes attendu après le resampling.

    Returns:
        tuple: Un tuple contenant le DataFrame resamplé et le DataFrame original.
    """
    pandas_period: PandasTimeFrame = convert_gateio_timeframe_to_pandas(resample_period)
    original_dataframe = dataframe.copy()  # Copie le DataFrame original pour une utilisation ultérieure
    dataframe = (dataframe.resample(pandas_period, closed='right')
                 .agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'}))
    resampled_dataframe: DataFrame = dataframe.tail(expected_length)  # Récupère les dernières lignes après le resampling
    return resampled_dataframe, original_dataframe  # Retourne le DataFrame resamplé et le DataFrame original


"""
### Correspondance des noms (Ancien → Nouveau → Signification)
| Ancien Nom                       | Nouveau Nom                      | Signification                                                   |
|----------------------------------|----------------------------------|-----------------------------------------------------------------|
| `pourcentage_value`              | `convert_percentage_to_decimal`  | Convertit une chaîne de pourcentage en valeur décimale          |
| `pourcentage_to_stoploss_indice` | `calculate_stoploss_index`       | Calcule l'indice de stop-loss à partir d'un pourcentage         |
| `pourcentage_to_profit_indice`   | `calculate_profit_index`         | Calcule l'indice de profit à partir d'un pourcentage            |
| `pourcentage_to_max_quote_indice`| `calculate_max_quote_index`      | Calcule l'indice de quote maximum à partir d'un pourcentage     |
| `pct`                            | `calculate_percentage`           | Calcule le pourcentage de `a` par rapport à `b`                 |
| `resample`                       | `resample_dataframe`             | Resample un DataFrame sur une période donnée                    |
"""
