import time

from Python.Rsi.Tools.Business import BotCurrencyPair
from Python.Rsi.Tools.Quotes import Price


class State:
    """
    Classe State pour représenter l'état d'une paire de devises dans le contexte d'un trading bot.

    Cette classe capture l'état actuel d'une paire de devises spécifique à un moment donné, incluant
    le prix et un timestamp indiquant le moment où l'état a été enregistré.
    """

    def __init__(self, currency_pair: BotCurrencyPair, price: Price):
        """
        Initialise une nouvelle instance de State.

        Args:
            currency_pair (BotCurrencyPair): La paire de devises associée à cet état.
            price (Price): Le prix de la paire de devises au moment où l'état est capturé.
        """
        self.currency_pair: BotCurrencyPair = currency_pair  # Stocke la paire de devises associée à cet état
        self.price: Price = price  # Stocke le prix associé à cet état
        self.timestamp = time.time()  # Enregistre le timestamp actuel en secondes depuis l'époque Unix
