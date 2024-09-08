from typing import Optional

from gate_api import Order

from venantvr.quotes import Price


class Track:
    """
    Classe Track pour suivre les ordres d'achat et de vente.

    Cette classe gère le suivi des ordres d'achat et de vente associés à un bot de trading,
    en conservant l'état de chaque ordre et les prix correspondants.

    ### Correspondance des noms (Ancien → Nouveau → Signification)
    | Ancien Nom                 | Nouveau Nom                         | Signification                                      |
    |----------------------------|-------------------------------------|----------------------------------------------------|
    | `self.order`               | `tracked_order`                     | L'ordre actuellement suivi                         |
    | `self.price`               | `tracked_price`                     | Le prix associé à l'ordre suivi                    |
    | `self.buy`                 | `buy_order_tracking`                | Suivi de l'ordre d'achat                           |
    | `self.sell`                | `sell_order_tracking`               | Suivi de l'ordre de vente                          |
    """

    class OrderTrack:
        """
        Classe interne pour suivre un ordre spécifique.

        Cette classe encapsule les informations d'un ordre unique, y compris l'ordre lui-même
        et le prix auquel l'ordre est placé.
        """

        def __init__(self):
            """
            Initialise une instance de OrderTrack avec un ordre vide et un prix de zéro.
            """
            self.tracked_order: Optional[Order] = None  # Stocke l'objet Order, initialisé à None
            self.tracked_price: Price = Price.ZERO  # Stocke le prix de l'ordre, initialisé à zéro

    def __init__(self):
        """
        Initialise une instance de Track pour suivre les ordres d'achat et de vente.

        Crée deux instances de OrderTrack pour suivre séparément les ordres d'achat et de vente.
        """
        self.buy_order_tracking = self.OrderTrack()  # Instance de OrderTrack pour suivre l'ordre d'achat
        self.sell_order_tracking = self.OrderTrack()  # Instance de OrderTrack pour suivre l'ordre de vente

    def reset(self):
        """
        Réinitialise les ordres d'achat et de vente.

        Met à jour les objets OrderTrack pour que les ordres soient définis sur None,
        indiquant qu'il n'y a actuellement aucun ordre actif suivi.
        """
        self.buy_order_tracking.tracked_order = None  # Réinitialise l'ordre d'achat
        self.sell_order_tracking.tracked_order = None  # Réinitialise l'ordre de vente
