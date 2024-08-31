class Price:
    ZERO = None

    def __init__(self, price: float, quote):
        if not isinstance(price, (float, int)):
            raise TypeError('Le montant doit être un nombre')
        self.price = price
        self.quote = quote

    def take_percentage(self, percentage, quote):
        price = percentage * self.price
        return Price(price=price, quote=quote)

    def __str__(self):
        return f'{self.price} {self.quote}'

    def __sub__(self, other):
        """Soustraction de deux prix, en supposant qu'ils ont la même devise (quote)."""
        if not isinstance(other, Price):
            raise TypeError("L'opérande doit être une instance de Price")

        if self.quote != other.quote:
            raise ValueError("Impossible de soustraire des prix avec des devises différentes")

        return Price(self.price - other.price, self.quote)

    def __mul__(self, other):
        if not isinstance(other, float):
            raise TypeError('Price ne peut être multiplié qu\'avec un objet de type float')
        price = self.price * other
        return Price(price=price, quote=self.quote)

    def __eq__(self, other):
        if not isinstance(other, Price):
            return NotImplemented
        return self.price == other.price

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if not isinstance(other, Price):
            return NotImplemented
        return self.price < other.price

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other):
        if not isinstance(other, Price):
            return NotImplemented
        return self.price > other.price

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)


Price.ZERO = Price(price=0.0,
                   quote=None)
