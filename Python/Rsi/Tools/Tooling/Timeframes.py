from datetime import datetime

from Python.Rsi.Tools.Types.Alias import GateioTimeFrame, PandasTimeFrame


def diviser_timeframe(timeframe: GateioTimeFrame, division) -> GateioTimeFrame:
    """
    Divise un timeframe par un facteur spécifié et renvoie le nouveau timeframe.

    Args:
    timeframe (str): Timeframe à diviser (ex. '1h', '30m').
    division (int): Facteur de division.

    Returns:
    str: Nouveau timeframe divisé.
    """
    unit = timeframe[-1]
    amount = int(timeframe[:-1])
    if unit == 'm':
        total_minutes = amount
    elif unit == 'h':
        total_minutes = amount * 60
    elif unit == 'd':
        total_minutes = amount * 1440
    else:
        raise ValueError('Unité de timeframe non prise en charge')
    new_minutes = total_minutes // division
    if new_minutes % 1440 == 0:
        value = new_minutes // 1440
        unit = 'd'
    elif new_minutes % 60 == 0:
        value = new_minutes // 60
        unit = 'h'
    else:
        value = new_minutes
        unit = 'm'
    return GateioTimeFrame(f'{value}{unit}')


def seconds_to_timeframe(seconds) -> GateioTimeFrame:
    if seconds >= 2592000:
        output = str(seconds // 2592000) + 'M'
    elif seconds >= 604800:
        output = str(seconds // 604800) + 'w'
    elif seconds >= 86400:
        output = str(seconds // 86400) + 'd'
    elif seconds >= 3600:
        output = str(seconds // 3600) + 'h'
    elif seconds >= 60:
        output = str(seconds // 60) + 'm'
    else:
        output = str(seconds) + 's'
    return GateioTimeFrame(output)


def timeframe_to_seconds(timeframe: GateioTimeFrame):
    unit = timeframe[-1]
    amount = int(timeframe[:-1])
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
        seconds = None
    return seconds


def convert_gateio_timeframe_to_pandas(timeframe: GateioTimeFrame) -> PandasTimeFrame:
    """
    Convertit un timeframe donné en chaîne de période pour resampling avec pandas.

    Args:
    timeframe (str): Le timeframe à convertir (ex. "1h", "30m", "1d").

    Returns:
    str: La chaîne de période correspondante pour utilisation avec pandas.resample().
    """
    # Dictionnaire de correspondance entre les unités de temps et les alias pandas
    unit_mapping = {'h': 'h', 'm': 'T', 'd': 'D'}  # FutureWarning: 'H' is deprecated and will be removed in a future version, please use 'h' instead.

    # Extraction de la quantité et de l'unité du timeframe
    quantity = ''.join([char for char in timeframe if char.isdigit()])
    unit = ''.join([char for char in timeframe if char.isalpha()]).lower()

    # Conversion de l'unité en alias pandas
    pandas_alias = unit_mapping.get(unit, None)

    if pandas_alias is None:
        raise ValueError(f'Unité de temps non reconnue {unit}')

    return PandasTimeFrame(quantity + pandas_alias)


def get_seconds_till_close(timeframe_in_seconds):
    now = datetime.now()
    return timeframe_in_seconds - (now.minute * 60 + now.second) % timeframe_in_seconds
