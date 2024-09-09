import decimal
from typing import Optional

from venantvr.business.bot_currency_pair import BotCurrencyPair
from venantvr.quotes.price import Price
from venantvr.quotes.quotes_utils import create_currency_quote


class Quantity:
    """
    Classe Quantity représentant une quantité d'une devise ou d'un actif, associée à une paire de devises.

    Fournit des méthodes pour manipuler la quantité, ajuster la précision, et effectuer des opérations
    arithmétiques telles que la multiplication avec des objets de type Price.
    """

    # Constante ZERO représentant une quantité nulle
    ZERO = None

    def __init__(self, currency_pair: Optional[BotCurrencyPair], quantity: float):
        """
        Initialise une instance de Quantity avec une paire de devises et une quantité spécifiée.

        Paramètres :
        currency_pair (Optional[BotCurrencyPair]) : La paire de devises associée à la quantité (ou None).
        quantity (float) : La quantité de la devise.

        Lève :
        TypeError : Si la quantité n'est pas un float ou un int.
        """
        if not isinstance(quantity, (float, int)):
            raise TypeError('La quantité doit être un nombre')
        self.quantity = quantity  # Quantité de la devise
        self.currency_pair = currency_pair  # Paire de devises associée

    def __mul__(self, other):
        """
        Permet la multiplication de Quantity par un objet Price pour calculer la valeur totale.

        Paramètres :
        other (Price) : Un objet Price représentant le prix de la devise.

        Retourne :
        Quote : Un objet Quote représentant le montant total après multiplication.

        Lève :
        TypeError : Si l'objet other n'est pas de type Price.
        """
        if not isinstance(other, Price):
            raise TypeError('Quantity ne peut être multiplié qu\'avec un objet de type Price')

        # Calcule le montant total après multiplication par le prix
        amount = self.quantity * other.price

        # Crée et retourne une instance de Quote avec le montant calculé
        return create_currency_quote(amount=amount, quote=other.quote)

    def manage_amount_precision(self, pair_precision: int):
        """
        Ajuste la précision de la quantité en fonction d'une précision spécifiée.

        Paramètres :
        pair_precision (int) : Le nombre de décimales à conserver.

        Retourne :
        Quantity : Une nouvelle instance de Quantity avec la quantité ajustée à la précision spécifiée.
        """
        # Convertit la quantité en Decimal pour un contrôle précis de la précision
        amount = decimal.Decimal(self.quantity)

        # Arrondit la quantité à la précision spécifiée
        rounded_amount = amount.quantize(decimal.Decimal('1.' + '0' * pair_precision),
                                         rounding=decimal.ROUND_DOWN)

        # Retourne une nouvelle instance de Quantity avec la quantité ajustée
        return Quantity(currency_pair=self.currency_pair, quantity=float(rounded_amount))

    def __str__(self):
        """
        Retourne une représentation en chaîne de caractères de la quantité.

        Retourne :
        str : La quantité suivie de la devise de base (si disponible), sinon juste la quantité.
        """
        if self.currency_pair is None:
            return f'{self.quantity}'
        else:
            return f'{self.quantity} {self.currency_pair.base}'

    def __eq__(self, other):
        """
        Vérifie si deux instances de Quantity sont égales.

        Paramètres :
        other (Quantity) : Une autre instance de Quantity à comparer.

        Retourne :
        bool : True si les quantités sont égales, False sinon.
        """
        if not isinstance(other, Quantity):
            return NotImplemented
        return self.quantity == other.quantity

    def __ne__(self, other):
        """
        Vérifie si deux instances de Quantity ne sont pas égales.

        Paramètres :
        other (Quantity) : Une autre instance de Quantity à comparer.

        Retourne :
        bool : True si les quantités sont différentes, False sinon.
        """
        return not self.__eq__(other)

    def __lt__(self, other):
        """
        Vérifie si une instance de Quantity est inférieure à une autre.

        Paramètres :
        other (Quantity) : Une autre instance de Quantity à comparer.

        Retourne :
        bool : True si la quantité est inférieure, False sinon.
        """
        if not isinstance(other, Quantity):
            return NotImplemented
        return self.quantity < other.quantity

    def __le__(self, other):
        """
        Vérifie si une instance de Quantity est inférieure ou égale à une autre.

        Paramètres :
        other (Quantity) : Une autre instance de Quantity à comparer.

        Retourne :
        bool : True si la quantité est inférieure ou égale, False sinon.
        """
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other):
        """
        Vérifie si une instance de Quantity est supérieure à une autre.

        Paramètres :
        other (Quantity) : Une autre instance de Quantity à comparer.

        Retourne :
        bool : True si la quantité est supérieure, False sinon.
        """
        if not isinstance(other, Quantity):
            return NotImplemented
        return self.quantity > other.quantity

    def __ge__(self, other):
        """
        Vérifie si une instance de Quantity est supérieure ou égale à une autre.

        Paramètres :
        other (Quantity) : Une autre instance de Quantity à comparer.

        Retourne :
        bool : True si la quantité est supérieure ou égale, False sinon.
        """
        return self.__gt__(other) or self.__eq__(other)


# Initialise la constante ZERO avec une instance de Quantity de montant 0.0
Quantity.ZERO = Quantity(currency_pair=None, quantity=0.0)
