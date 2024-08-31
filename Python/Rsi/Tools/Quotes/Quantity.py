import decimal
from typing import Optional

from Python.Rsi.Tools.Business import BotCurrencyPair
from Python.Rsi.Tools.Quotes import Price
from Python.Rsi.Tools.Quotes.Currencies import create_currency_quote


class Quantity:
    ZERO = None

    def __init__(self, currency_pair: Optional[BotCurrencyPair], quantity: float):
        if not isinstance(quantity, (float, int)):
            raise TypeError('La quantité doit être un nombre')
        self.quantity = quantity
        self.currency_pair = currency_pair

    def __mul__(self, other):
        if not isinstance(other, Price):
            raise TypeError('Quantity ne peut être multiplié qu\'avec un objet de type Price')
        amount = self.quantity * other.price
        return create_currency_quote(amount=amount, quote=other.quote)

    def manage_amount_precision(self, pair_precision: int):
        amount = decimal.Decimal(self.quantity)
        rounded_amount = amount.quantize(decimal.Decimal('1.' + '0' * pair_precision),
                                         rounding=decimal.ROUND_DOWN)
        return Quantity(currency_pair=self.currency_pair, quantity=float(rounded_amount))

    def __str__(self):
        if self.currency_pair is None:
            return f'{self.quantity}'
        else:
            return f'{self.quantity} {self.currency_pair.base}'

    def __eq__(self, other):
        if not isinstance(other, Quantity):
            return NotImplemented
        return self.quantity == other.quantity

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if not isinstance(other, Quantity):
            return NotImplemented
        return self.quantity < other.quantity

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other):
        if not isinstance(other, Quantity):
            return NotImplemented
        return self.quantity > other.quantity

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)


Quantity.ZERO = Quantity(currency_pair=None, quantity=0.0)
