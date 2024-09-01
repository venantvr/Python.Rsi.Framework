from gate_api import Currency


class Position:
    """
    Classe Position représentant une position dans une devise spécifique avec un montant donné.

    Utilisée pour stocker et manipuler des informations sur la quantité d'un actif (ou d'une devise) détenue.
    """

    def __init__(self, token: Currency, amount: float):
        """
        Initialise une instance de Position avec une devise (token) et un montant spécifique.

        Paramètres :
        token (Currency) : La devise ou l'actif de la position (par exemple, BTC, USDT).
        amount (float) : Le montant de la devise ou de l'actif détenu.
        """
        self.currency: Currency = token  # Devise ou actif de la position
        self.amount = amount  # Montant de la devise ou de l'actif détenu
