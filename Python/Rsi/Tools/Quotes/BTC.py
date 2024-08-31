from Python.Rsi.Tools.Quotes import Quote


class BTC(Quote):

    def __str__(self):
        return f'{self.amount} BTC'
