import os
import time

from Python.Rsi.Tools.Quotes import USDT, BTC  # Import des classes USDT et BTC depuis le module Python.Rsi.Tools.Quotes


def base_from_pair(pair: str):
    """
    Extrait la devise de base à partir d'une paire de devises.

    Paramètres :
    pair (str) : La paire de devises au format 'BASE_QUOTE' (par exemple, 'BTC_USDT').

    Retourne :
    str : La devise de base (par exemple, 'BTC').
    """
    parts = pair.split('_')  # Sépare la paire de devises en utilisant '_' comme séparateur
    base = parts[0]  # La première partie est la devise de base
    return base


def quote_from_pair(pair: str, default='USDT'):
    """
    Extrait la devise de cotation (quote) à partir d'une paire de devises, ou retourne une devise par défaut.

    Paramètres :
    pair (str) : La paire de devises au format 'BASE_QUOTE' (par exemple, 'BTC_USDT').
    default (str) : La devise par défaut si aucune devise de cotation n'est trouvée.

    Retourne :
    str : La devise de cotation (quote) ou la devise par défaut.
    """
    parts = pair.split('_')  # Sépare la paire de devises en utilisant '_' comme séparateur
    if len(parts) == 2:  # Vérifie si la paire contient une devise de cotation
        quote = parts[1]  # La deuxième partie est la devise de cotation
    else:
        quote = default  # Utilise la devise par défaut si aucune devise de cotation n'est trouvée
    return quote


def create_currency_quote(amount, quote):
    """
    Crée un objet de devises (quote) basé sur le montant et la devise de cotation fournis.

    Paramètres :
    amount (float) : Le montant pour la devise de cotation.
    quote (str) : La devise de cotation ('USDT', 'BTC', etc.).

    Retourne :
    USDT ou BTC : Une instance de la classe USDT ou BTC.

    Lève :
    ValueError : Si la devise de cotation n'est pas prise en charge.
    """
    if quote == 'USDT':
        return USDT(amount)  # Retourne une instance de la classe USDT avec le montant spécifié
    elif quote == 'BTC':
        return BTC(amount)  # Retourne une instance de la classe BTC avec le montant spécifié
    else:
        raise ValueError('Unsupported quote currency')  # Lève une erreur si la devise de cotation n'est pas supportée


def quote_currency(currency_pair):
    """
    Extrait la devise de cotation (quote) à partir d'une paire de devises en remplaçant certains séparateurs.

    Paramètres :
    currency_pair (str) : La paire de devises au format 'BASE/QUOTE' ou 'BASE-QUOTE'.

    Retourne :
    str : La devise de cotation (quote) en majuscules.
    """
    quote = currency_pair.replace('/', '_').replace('-', '_').split('_')[-1]  # Remplace '/' et '-' par '_' et extrait la dernière partie
    return quote.upper()  # Retourne la devise de cotation en majuscules


def file_exists(filepath: str, factor: int = 10) -> bool:
    """
    Vérifie si un fichier existe et a été modifié dans les dernières '24 * facteur' heures.
    Si le fichier est plus ancien, il sera supprimé.

    Paramètres :
    filepath (str) : Le chemin vers le fichier à vérifier.
    factor (int) : Le facteur multiplicatif pour définir l'âge limite du fichier en heures (par défaut 10).

    Retourne :
    bool : True si le fichier existe et a été modifié il y a moins de '24 * facteur' heures, False sinon.
    """
    output = False

    if os.path.exists(filepath):  # Vérifie si le fichier existe
        last_modified = os.path.getmtime(filepath)  # Obtient le temps de dernière modification du fichier
        current_time = time.time()  # Obtient le temps actuel
        time_difference = current_time - last_modified  # Calcule la différence de temps

        # Convertit la différence de temps en heures
        hours_difference = time_difference / 3600

        if hours_difference < 24 * factor:  # Vérifie si le fichier a été modifié dans la période limite
            output = True
        else:
            # Supprime le fichier s'il est plus vieux que la période limite
            os.remove(filepath)

    return output
