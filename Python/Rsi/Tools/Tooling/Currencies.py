import os
from typing import Optional

from Python.Rsi.Tools.Business import BotCurrencyPair
from Python.Rsi.Tools.Parameters import Parameters


def gateio_currency_pair(pair_symbol: str, keep_pair_quote: bool, trading_quote) -> Optional[BotCurrencyPair]:
    """
    Transforme une paire de devises en un objet BotCurrencyPair.

    Cette fonction prend une paire de devises sous forme de chaîne, normalise le format,
    et crée un objet BotCurrencyPair. Si la base et la quote de la paire sont identiques,
    la fonction retourne None.

    Args:
        pair_symbol (str): La paire de devises sous forme de chaîne (ex: 'BTC/USD').
        keep_pair_quote (bool): Indique si la quote de la paire doit être conservée.
        trading_quote (str): La quote à utiliser si keep_pair_quote est False.

    Returns:
        Optional[BotCurrencyPair]: Un objet BotCurrencyPair ou None si la base et la quote sont identiques.
    """

    # Normalise la paire de devises en remplaçant les '/' et '-' par des '_' et en mettant en majuscule
    symbol = pair_symbol.replace('/', '_').replace('-', '_').upper()
    parts = symbol.split('_')  # Sépare la paire de devises en base et quote
    base = parts[0]  # Devise de base de la paire
    quote = trading_quote  # Initialisation de la devise de cotation avec la valeur par défaut

    # Détermine la quote à utiliser en fonction des arguments
    if not keep_pair_quote:
        # Si la quote de la paire ne doit pas être conservée, utilise `trading_quote`
        symbol = f'{base}_{quote}'
    elif len(parts) == 2:
        # Si `keep_pair_quote` est True et la paire contient une quote, utilise cette quote
        quote = parts[1]

    # Crée et retourne l'objet BotCurrencyPair si base et quote sont différents
    if base != quote:
        parameters = Parameters.get()  # Obtient les paramètres de configuration
        # Construit le chemin du répertoire pour le stockage des logs du bot
        directory = os.path.join(parameters.parsed_args.logs, 'Python.Rsi.Bot')

        # Retourne un nouvel objet BotCurrencyPair avec les informations fournies
        return BotCurrencyPair(
            id=symbol,
            base=base,
            quote=quote,
            directory=directory
        )
    else:
        # Retourne None si la base et la quote sont identiques (paire non valide)
        return None
