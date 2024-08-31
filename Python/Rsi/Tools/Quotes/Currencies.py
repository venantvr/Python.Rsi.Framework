import os
import time

from Python.Rsi.Tools.Quotes import USDT, BTC


def base_from_pair(pair: str):
    parts = pair.split('_')
    base = parts[0]
    return base


def quote_from_pair(pair: str, default='USDT'):
    parts = pair.split('_')
    if len(parts) == 2:
        quote = parts[1]
    else:
        quote = default
    return quote


def create_currency_quote(amount, quote):
    if quote == 'USDT':
        return USDT(amount)
    elif quote == 'BTC':
        return BTC(amount)
    else:
        raise ValueError('Unsupported quote currency')


def quote_currency(currency_pair):
    quote = currency_pair.replace('/', '_').replace('-', '_').split('_')[-1]
    return quote.upper()


def file_exists(filepath: str, factor: int = 10) -> bool:
    """
    Vérifie si un fichier existe et a été modifié dans les dernières 24 heures.
    Si le fichier est plus ancien, il sera supprimé.

    Args:
    filepath (str): Le chemin vers le fichier à vérifier.

    Returns:
    str: 'oui' si le fichier existe et a été modifié il y a moins de 24 heures,
         'non' sinon.
    """
    output = False

    if os.path.exists(filepath):
        last_modified = os.path.getmtime(filepath)
        current_time = time.time()
        time_difference = current_time - last_modified

        # Convertir la différence de temps en heures
        hours_difference = time_difference / 3600

        if hours_difference < 24 * factor:
            output = True
        else:
            # Supprimer le fichier s'il est plus vieux que 24 heures
            os.remove(filepath)

    return output
