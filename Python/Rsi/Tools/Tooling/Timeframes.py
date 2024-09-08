from datetime import datetime
from Python.Rsi.Tools.Types.Alias import GateioTimeFrame, PandasTimeFrame  # Import des types personnalisés pour les timeframes


def diviser_timeframe(timeframe: GateioTimeFrame, division: int) -> GateioTimeFrame:
    """
    Divise un timeframe par un facteur spécifié et renvoie le nouveau timeframe.

    Args:
        timeframe (GateioTimeFrame): Timeframe à diviser (ex. '1h', '30m').
        division (int): Facteur de division.

    Returns:
        GateioTimeFrame: Nouveau timeframe divisé.
    """
    unit = timeframe[-1]  # Extrait l'unité de temps ('m', 'h', 'd')
    amount = int(timeframe[:-1])  # Extrait la quantité de temps (ex. 1, 30)

    # Convertit le timeframe en minutes totales en fonction de l'unité
    if unit == 'm':
        total_minutes = amount
    elif unit == 'h':
        total_minutes = amount * 60
    elif unit == 'd':
        total_minutes = amount * 1440
    else:
        raise ValueError('Unité de timeframe non prise en charge')

    new_minutes = total_minutes // division  # Divise le total de minutes par le facteur de division

    # Détermine la nouvelle unité et valeur de temps
    if new_minutes % 1440 == 0:
        value = new_minutes // 1440
        unit = 'd'
    elif new_minutes % 60 == 0:
        value = new_minutes // 60
        unit = 'h'
    else:
        value = new_minutes
        unit = 'm'

    return GateioTimeFrame(f'{value}{unit}')  # Retourne le nouveau timeframe


def seconds_to_timeframe(seconds: int) -> GateioTimeFrame:
    """
    Convertit un nombre de secondes en un format de timeframe.

    Args:
        seconds (int): Nombre de secondes à convertir.

    Returns:
        GateioTimeFrame: Le timeframe correspondant au nombre de secondes.
    """
    if seconds >= 2592000:  # Mois
        output = str(seconds // 2592000) + 'M'
    elif seconds >= 604800:  # Semaine
        output = str(seconds // 604800) + 'w'
    elif seconds >= 86400:  # Jour
        output = str(seconds // 86400) + 'd'
    elif seconds >= 3600:  # Heure
        output = str(seconds // 3600) + 'h'
    elif seconds >= 60:  # Minute
        output = str(seconds // 60) + 'm'
    else:  # Seconde
        output = str(seconds) + 's'

    return GateioTimeFrame(output)


def timeframe_to_seconds(timeframe: GateioTimeFrame) -> int:
    """
    Convertit un timeframe en secondes.

    Args:
        timeframe (GateioTimeFrame): Le timeframe à convertir (ex. '1h', '30m').

    Returns:
        int: Le nombre de secondes correspondant au timeframe.
    """
    unit = timeframe[-1]  # Extrait l'unité de temps
    amount = int(timeframe[:-1])  # Extrait la quantité de temps

    # Convertit le timeframe en secondes selon l'unité
    if unit == 'm':
        seconds = amount * 60
    elif unit == 'h':
        seconds = amount * 3600
    elif unit == 'd':
        seconds = amount * 86400
    elif unit == 'w':
        seconds = amount * 604800
    elif unit == 'M':
        seconds = amount * 2592000
    else:
        seconds = None  # Unité non reconnue

    return seconds


def convert_gateio_timeframe_to_pandas(timeframe: GateioTimeFrame) -> PandasTimeFrame:
    """
    Convertit un timeframe donné en chaîne de période pour resampling avec pandas.

    Args:
        timeframe (GateioTimeFrame): Le timeframe à convertir (ex. '1h', '30m', '1d').

    Returns:
        PandasTimeFrame: La chaîne de période correspondante pour utilisation avec pandas.resample().
    """
    # Dictionnaire de correspondance entre les unités de temps et les alias pandas
    unit_mapping = {'h': 'h', 'm': 'T', 'd': 'D'}

    # Extraction de la quantité et de l'unité du timeframe
    quantity = ''.join([char for char in timeframe if char.isdigit()])  # Quantité (ex. 1, 30)
    unit = ''.join([char for char in timeframe if char.isalpha()]).lower()  # Unité ('h', 'm', 'd')

    # Conversion de l'unité en alias pandas
    pandas_alias = unit_mapping.get(unit, None)

    if pandas_alias is None:
        raise ValueError(f'Unité de temps non reconnue {unit}')

    return PandasTimeFrame(quantity + pandas_alias)  # Retourne le timeframe pour pandas


def get_seconds_till_close(timeframe_in_seconds: int) -> int:
    """
    Calcule le nombre de secondes restantes jusqu'à la fin du timeframe en cours.

    Args:
        timeframe_in_seconds (int): Le nombre de secondes du timeframe.

    Returns:
        int: Nombre de secondes restantes jusqu'à la fermeture du timeframe en cours.
    """
    now = datetime.now()
    return timeframe_in_seconds - (now.minute * 60 + now.second) % timeframe_in_seconds


"""
### Correspondance des noms (Ancien → Nouveau → Signification)
| Ancien Nom                           | Nouveau Nom                             | Signification                                                      |
|--------------------------------------|-----------------------------------------|--------------------------------------------------------------------|
| `diviser_timeframe`                  | `diviser_timeframe`                     | Divise un timeframe par un facteur spécifié                        |
| `seconds_to_timeframe`               | `seconds_to_timeframe`                  | Convertit un nombre de secondes en un timeframe                    |
| `timeframe_to_seconds`               | `timeframe_to_seconds`                  | Convertit un timeframe en secondes                                 |
| `convert_gateio_timeframe_to_pandas` | `convert_gateio_timeframe_to_pandas`    | Convertit un timeframe Gate.io en un format Pandas                 |
| `get_seconds_till_close`             | `get_seconds_till_close`                | Calcule le nombre de secondes restantes avant la fin du timeframe  |
"""
