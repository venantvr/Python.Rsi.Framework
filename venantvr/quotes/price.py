class Price:
    """
    Classe Price représentant un prix associé à une devise (quote).

    Fournit des méthodes pour manipuler le prix, effectuer des opérations arithmétiques
    telles que la soustraction et la multiplication, et comparer différents prix.
    """

    # Constante ZERO représentant un prix de 0.0 avec une devise nulle
    ZERO = None

    def __init__(self, price: float, quote):
        """
        Initialise une instance de Price avec un montant de prix et une devise spécifiée.

        Paramètres :
        price (float) : Le montant du prix.
        quote : La devise associée au prix.

        Lève :
        TypeError : Si le montant du prix n'est pas un float ou un int.
        """
        if not isinstance(price, (float, int)):
            raise TypeError('Le montant doit être un nombre')
        self.price = price  # Montant du prix
        self.quote = quote  # Devise associée au prix

    def take_percentage(self, percentage, quote):
        """
        Calcule un certain pourcentage du prix et retourne un nouvel objet Price.

        Paramètres :
        percentage (float) : Le pourcentage à prendre du montant actuel.
        quote : La devise associée au nouveau prix.

        Retourne :
        Price : Une nouvelle instance de Price avec le montant ajusté.
        """
        price = percentage * self.price
        return Price(price=price, quote=quote)

    def __str__(self):
        """
        Retourne une représentation en chaîne de caractères du prix.

        Retourne :
        str : Le montant du prix suivi de la devise.
        """
        return f'{self.price} {self.quote}'

    def __sub__(self, other):
        """
        Soustraction de deux prix, en supposant qu'ils ont la même devise (quote).

        Paramètres :
        other (Price) : Une autre instance de Price à soustraire.

        Retourne :
        Price : Une nouvelle instance de Price représentant la différence.

        Lève :
        TypeError : Si l'objet other n'est pas de type Price.
        ValueError : Si les devises des deux prix sont différentes.
        """
        if not isinstance(other, Price):
            raise TypeError("L'opérande doit être une instance de Price")

        if self.quote != other.quote:
            raise ValueError("Impossible de soustraire des prix avec des devises différentes")

        return Price(self.price - other.price, self.quote)

    def __mul__(self, other):
        """
        Permet la multiplication de Price par un nombre flottant (float).

        Paramètres :
        other (float) : Un nombre flottant pour multiplier le prix.

        Retourne :
        Price : Une nouvelle instance de Price avec le montant ajusté.

        Lève :
        TypeError : Si l'objet other n'est pas de type float.
        """
        if not isinstance(other, float):
            raise TypeError('Price ne peut être multiplié qu\'avec un objet de type float')

        price = self.price * other
        return Price(price=price, quote=self.quote)

    def __eq__(self, other):
        """
        Vérifie si deux instances de Price sont égales.

        Paramètres :
        other (Price) : Une autre instance de Price à comparer.

        Retourne :
        bool : True si les montants de prix sont égaux, False sinon.
        """
        if not isinstance(other, Price):
            return NotImplemented
        return self.price == other.price

    def __ne__(self, other):
        """
        Vérifie si deux instances de Price ne sont pas égales.

        Paramètres :
        other (Price) : Une autre instance de Price à comparer.

        Retourne :
        bool : True si les montants de prix sont différents, False sinon.
        """
        return not self.__eq__(other)

    def __lt__(self, other):
        """
        Vérifie si une instance de Price est inférieure à une autre.

        Paramètres :
        other (Price) : Une autre instance de Price à comparer.

        Retourne :
        bool : True si le montant du prix est inférieur, False sinon.
        """
        if not isinstance(other, Price):
            return NotImplemented
        return self.price < other.price

    def __le__(self, other):
        """
        Vérifie si une instance de Price est inférieure ou égale à une autre.

        Paramètres :
        other (Price) : Une autre instance de Price à comparer.

        Retourne :
        bool : True si le montant du prix est inférieur ou égal, False sinon.
        """
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other):
        """
        Vérifie si une instance de Price est supérieure à une autre.

        Paramètres :
        other (Price) : Une autre instance de Price à comparer.

        Retourne :
        bool : True si le montant du prix est supérieur, False sinon.
        """
        if not isinstance(other, Price):
            return NotImplemented
        return self.price > other.price

    def __ge__(self, other):
        """
        Vérifie si une instance de Price est supérieure ou égale à une autre.

        Paramètres :
        other (Price) : Une autre instance de Price à comparer.

        Retourne :
        bool : True si le montant du prix est supérieur ou égal, False sinon.
        """
        return self.__gt__(other) or self.__eq__(other)


# Initialise la constante ZERO avec une instance de Price de montant 0.0 et sans devise
Price.ZERO = Price(price=0.0, quote=None)
