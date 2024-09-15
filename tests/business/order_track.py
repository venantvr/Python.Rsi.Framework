import unittest
from unittest.mock import MagicMock

from gate_api import Order

from venantvr.business.order_track import Track
from venantvr.quotes.price import Price


class TestTrack(unittest.TestCase):

    def setUp(self):
        """
        Cette méthode est appelée avant chaque test pour initialiser une instance de Track.
        """
        self.track = Track()  # Instance de la classe Track pour les tests

    def test_initialization(self):
        """
        Teste si les objets OrderTrack pour le suivi des ordres d'achat et de vente sont correctement initialisés.
        """
        # Vérifie que l'initialisation des ordres d'achat et de vente est correcte
        self.assertIsNone(self.track.buy_order_tracking.tracked_order)
        self.assertIsNone(self.track.sell_order_tracking.tracked_order)
        self.assertEqual(self.track.buy_order_tracking.tracked_price, Price.ZERO)
        self.assertEqual(self.track.sell_order_tracking.tracked_price, Price.ZERO)

    def test_reset_orders(self):
        """
        Teste si la méthode reset() réinitialise correctement les ordres d'achat et de vente.
        """
        # Simule l'ajout d'ordres dans le suivi
        self.track.buy_order_tracking.tracked_order = MagicMock(spec=Order)
        self.track.sell_order_tracking.tracked_order = MagicMock(spec=Order)

        # Réinitialisation
        self.track.reset()

        # Vérifie que les ordres ont été réinitialisés
        self.assertIsNone(self.track.buy_order_tracking.tracked_order)
        self.assertIsNone(self.track.sell_order_tracking.tracked_order)

    def test_order_tracking(self):
        """
        Teste la mise à jour et le suivi des ordres d'achat et de vente.
        """
        # Crée des ordres fictifs
        buy_order = MagicMock(spec=Order)
        sell_order = MagicMock(spec=Order)

        # Simule la mise à jour des ordres suivis
        self.track.buy_order_tracking.tracked_order = buy_order
        self.track.buy_order_tracking.tracked_price = Price(50000, quote='USDT')  # Simule un prix d'achat
        self.track.sell_order_tracking.tracked_order = sell_order
        self.track.sell_order_tracking.tracked_price = Price(60000, quote='USDT')  # Simule un prix de vente

        # Vérifie que les ordres et les prix sont correctement mis à jour
        self.assertEqual(self.track.buy_order_tracking.tracked_order, buy_order)
        self.assertEqual(self.track.buy_order_tracking.tracked_price, Price(50000, quote='USDT'))
        self.assertEqual(self.track.sell_order_tracking.tracked_order, sell_order)
        self.assertEqual(self.track.sell_order_tracking.tracked_price, Price(60000, quote='USDT'))


if __name__ == '__main__':
    unittest.main()
