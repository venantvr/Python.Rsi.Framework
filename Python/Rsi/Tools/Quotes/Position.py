from gate_api import Currency


class Position:

    def __init__(self, token: Currency, amount: float):
        self.currency: Currency = token
        self.amount = amount
