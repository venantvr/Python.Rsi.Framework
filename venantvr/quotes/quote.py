import decimal
from abc import abstractmethod


class Quote:
    """
    Classe Quote représentant une valeur monétaire associée à une devise.
    Fournit des méthodes pour manipuler cette valeur, telles que le calcul de pourcentages,
    la gestion de la précision, et la comparaison avec d'autres instances de Quote.
    """

    # Constante ZERO représentant une quote de montant 0
    ZERO = None

    # Liste de devises prises en charge par défaut
    currencies = ['USDT', 'BTC']

    def __init__(self, amount: float):
        """
        Initialise une instance de Quote avec un montant spécifié.

        Paramètres :
        amount (float) : Le montant de la quote.

        Lève :
        TypeError : Si le montant n'est pas un float ou un int.
        """
        # Vérifie que le montant est bien un nombre (float ou int)
        if not isinstance(amount, (float, int)):
            raise TypeError('La valeur doit être un nombre')
        self.amount = amount

    def take_percentage(self, percentage: float):
        """
        Calcule un certain pourcentage de la quote.

        Paramètres :
        percentage (float) : Le pourcentage à prendre du montant actuel.

        Retourne :
        Quote : Une nouvelle instance de Quote avec le montant ajusté.
        """
        return Quote(percentage * self.amount)

    def compute_slot_amount(self, free_slots: int):
        """
        Calcule le montant par slot, en fonction du nombre de slots libres.

        Paramètres :
        free_slots (int) : Le nombre de slots libres pour répartir le montant.

        Retourne :
        Quote : Une nouvelle instance de Quote avec le montant divisé par le nombre de slots libres.
        """
        return Quote(self.amount / free_slots)

    def manage_amount_precision(self, pair_precision: int):
        """
        Gère la précision du montant en fonction d'une précision spécifiée.

        Paramètres :
        pair_precision (int) : Le nombre de décimales à conserver.

        Retourne :
        Quote : Une nouvelle instance de Quote avec le montant ajusté à la précision spécifiée.
        """
        # Convertit le montant en Decimal pour un contrôle précis de la précision
        amount = decimal.Decimal(self.amount)
        # Arrondit le montant à la précision spécifiée
        rounded_amount = amount.quantize(decimal.Decimal('1.' + '0' * pair_precision),
                                         rounding=decimal.ROUND_DOWN)
        return Quote(float(rounded_amount))

    @abstractmethod
    def __str__(self):
        """
        Retourne une représentation en chaîne de caractères de la quote.

        Retourne :
        str : Le montant sous forme de chaîne.
        """
        return f'{self.amount}'

    def __eq__(self, other):
        """
        Vérifie si deux instances de Quote sont égales.

        Paramètres :
        other (Quote) : Une autre instance de Quote à comparer.

        Retourne :
        bool : True si les montants sont égaux, False sinon.
        """
        if not isinstance(other, Quote):
            return NotImplemented
        return self.amount == other.amount

    def __ne__(self, other):
        """
        Vérifie si deux instances de Quote ne sont pas égales.

        Paramètres :
        other (Quote) : Une autre instance de Quote à comparer.

        Retourne :
        bool : True si les montants sont différents, False sinon.
        """
        return not self.__eq__(other)

    def __lt__(self, other):
        """
        Vérifie si une instance de Quote est inférieure à une autre.

        Paramètres :
        other (Quote) : Une autre instance de Quote à comparer.

        Retourne :
        bool : True si le montant est inférieur, False sinon.
        """
        if not isinstance(other, Quote):
            return NotImplemented
        return self.amount < other.amount

    def __le__(self, other):
        """
        Vérifie si une instance de Quote est inférieure ou égale à une autre.

        Paramètres :
        other (Quote) : Une autre instance de Quote à comparer.

        Retourne :
        bool : True si le montant est inférieur ou égal, False sinon.
        """
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other):
        """
        Vérifie si une instance de Quote est supérieure à une autre.

        Paramètres :
        other (Quote) : Une autre instance de Quote à comparer.

        Retourne :
        bool : True si le montant est supérieur, False sinon.
        """
        if not isinstance(other, Quote):
            return NotImplemented
        return self.amount > other.amount

    def __ge__(self, other):
        """
        Vérifie si une instance de Quote est supérieure ou égale à une autre.

        Paramètres :
        other (Quote) : Une autre instance de Quote à comparer.

        Retourne :
        bool : True si le montant est supérieur ou égal, False sinon.
        """
        return self.__gt__(other) or self.__eq__(other)


# Initialise la constante ZERO avec une instance de Quote de montant 0.0
Quote.ZERO = Quote(0.0)
