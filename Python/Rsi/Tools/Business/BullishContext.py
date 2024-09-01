from typing import Callable, List

from Python.Rsi.Tools.Business import BotCurrencyPair

# Définition d'un type pour une fonction qui prend une liste de BotCurrencyPair et retourne une liste de BotCurrencyPair
BullishFunctionType = Callable[[List[BotCurrencyPair]], List[BotCurrencyPair]]


class BullishContext:
    """
    Classe de gestion de contexte pour appliquer une fonction "bullish" sur une liste d'actifs.

    Cette classe utilise le protocole de gestion de contexte (avec les méthodes __enter__ et __exit__)
    pour encapsuler l'application d'une fonction sur une liste d'actifs de type BotCurrencyPair.
    """

    def __init__(self, bullish_function: BullishFunctionType, assets: list[BotCurrencyPair]):
        """
        Initialise une instance de BullishContext.

        Args:
            bullish_function (BullishFunctionType): Une fonction qui prend en entrée une liste de BotCurrencyPair
                                                    et retourne une liste de BotCurrencyPair après transformation.
            assets (list[BotCurrencyPair]): La liste des actifs (paires de devises) à transformer.
        """
        self.__bullish_function = bullish_function  # Stocke la fonction bullish à appliquer
        self.__assets: list[BotCurrencyPair] = assets  # Stocke la liste des actifs

    def __enter__(self) -> List[BotCurrencyPair]:
        """
        Méthode appelée à l'entrée du bloc "with".

        Returns:
            List[BotCurrencyPair]: La liste des BotCurrencyPair transformée par la fonction bullish.
        """
        return self.__bullish_function(self.__assets)  # Applique la fonction bullish et retourne le résultat

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Méthode appelée à la sortie du bloc "with".

        Args:
            exc_type: Type de l'exception levée (si existant).
            exc_val: Valeur de l'exception levée (si existant).
            exc_tb: Traceback de l'exception levée (si existant).
        """
        pass  # Ne fait rien à la sortie du bloc "with"
