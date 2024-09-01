from typing import NewType

# Définition d'un nouveau type `GateioTimeFrame` qui est une sous-classe de `str`.
# Utilisé pour représenter les timeframes spécifiques de Gate.io, une plateforme de trading.
GateioTimeFrame = NewType('GateioTimeFrame', str)

# Définition d'un nouveau type `PandasTimeFrame` qui est également une sous-classe de `str`.
# Utilisé pour représenter les timeframes dans un format compatible avec Pandas pour le resampling.
PandasTimeFrame = NewType('PandasTimeFrame', str)
