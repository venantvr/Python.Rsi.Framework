from venantvr.quotes import Quote


class USDT(Quote):
    """
    Classe USDT représentant une quote spécifique pour la devise Tether (USDT).

    Hérite de la classe `Quote` pour utiliser les fonctionnalités de manipulation et de comparaison,
    tout en fournissant une représentation spécifique pour la devise USDT.
    """

    def __str__(self):
        """
        Retourne une représentation en chaîne de caractères de la quote en USDT.

        Retourne :
        str : Le montant de la quote suivi de 'USDT'.
        """
        return f'{self.amount} USDT'
