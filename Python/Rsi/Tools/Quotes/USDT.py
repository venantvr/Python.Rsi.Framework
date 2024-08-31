from Python.Rsi.Tools.Quotes import Quote


class USDT(Quote):

    def __str__(self):
        return f'{self.amount} USDT'
