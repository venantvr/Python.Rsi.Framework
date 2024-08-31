import decimal
from abc import abstractmethod


class Quote:
    ZERO = None

    currencies = ['USDT', 'BTC']

    def __init__(self, amount: float):
        if not isinstance(amount, (float, int)):
            raise TypeError('La valeur doit être un nombre')
        self.amount = amount

    def take_percentage(self, percentage: float):
        return Quote(percentage * self.amount)

    def compute_slot_amount(self, free_slots: int):
        return Quote(self.amount / free_slots)

    def manage_amount_precision(self, pair_precision: int):
        amount = decimal.Decimal(self.amount)
        rounded_amount = amount.quantize(decimal.Decimal('1.' + '0' * pair_precision),
                                         rounding=decimal.ROUND_DOWN)
        return Quote(float(rounded_amount))

    @abstractmethod
    def __str__(self):
        return f'{self.amount}'

    def __eq__(self, other):
        if not isinstance(other, Quote):
            return NotImplemented
        return self.amount == other.amount

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if not isinstance(other, Quote):
            return NotImplemented
        return self.amount < other.amount

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other):
        if not isinstance(other, Quote):
            return NotImplemented
        return self.amount > other.amount

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)


Quote.ZERO = Quote(0.0)
