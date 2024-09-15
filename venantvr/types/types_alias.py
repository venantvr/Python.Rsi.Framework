from typing import NewType, Callable, Optional, Union

from gate_api import CurrencyPair
from pandas import DataFrame

# from venantvr.business.bot_currency_pair import BotCurrencyPair

# Définition d'un nouveau type `GateioTimeFrame` qui est une sous-classe de `str`.
# Utilisé pour représenter les timeframes spécifiques de Gate.io, une plateforme de trading.
GateioTimeFrame = NewType('GateioTimeFrame', str)

# Définition d'un nouveau type `PandasTimeFrame` qui est également une sous-classe de `str`.
# Utilisé pour représenter les timeframes dans un format compatible avec Pandas pour le resampling.
PandasTimeFrame = NewType('PandasTimeFrame', str)

CandlesCountLambda = Callable[[Optional[CurrencyPair], GateioTimeFrame], int]
DataframeLambda = Callable[[CurrencyPair, DataFrame, GateioTimeFrame], DataFrame]

NumberOrPrice = Union[float, 'Price']
