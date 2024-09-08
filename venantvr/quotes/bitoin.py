from venantvr.quotes import Quote


class BTC(Quote):
    """
    Classe BTC représentant une quote spécifique pour la devise Bitcoin (BTC).

    Hérite de la classe `Quote` pour utiliser les fonctionnalités de manipulation et de comparaison
    tout en fournissant une représentation spécifique pour Bitcoin.
    """

    def __str__(self):
        """
        Retourne une représentation en chaîne de caractères de la quote en Bitcoin.

        Retourne :
        str : Le montant de la quote suivi de 'BTC'.
        """
        return f'{self.amount} BTC'
