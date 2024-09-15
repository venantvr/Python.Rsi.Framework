import unittest
from unittest.mock import MagicMock

from venantvr.business.bot_currency_pair import BotCurrencyPair
from venantvr.business.bullish_context import BullishContext


class TestBullishContext(unittest.TestCase):

    def setUp(self):
        # Créer des objets BotCurrencyPair pour les tests
        self.pair1 = BotCurrencyPair('BTC/USDT')
        self.pair2 = BotCurrencyPair('ETH/USDT')
        self.assets = [self.pair1, self.pair2]  # Liste d'actifs

        # Fonction bullish de test
        self.mock_bullish_function = MagicMock()  # Utiliser un mock pour simuler la fonction bullish
        self.mock_bullish_function.return_value = [self.pair1]  # Simuler une fonction qui ne garde que BTC/USDT

    def test_bullish_transformation_function_applied(self):
        """Teste si la fonction bullish est bien appliquée à la liste d'actifs."""
        with BullishContext(self.mock_bullish_function, self.assets) as transformed_assets:
            self.mock_bullish_function.assert_called_once_with(self.assets)  # Vérifie que la fonction a bien été appelée
            self.assertEqual(transformed_assets, [self.pair1])  # Vérifie que la fonction a retourné le résultat attendu

    def test_bullish_context_without_exception(self):
        """Teste le contexte de BullishContext sans exception."""
        with BullishContext(self.mock_bullish_function, self.assets) as transformed_assets:
            self.assertIsInstance(transformed_assets, list)  # Vérifie que le retour est bien une liste
            self.assertEqual(transformed_assets, [self.pair1])  # Vérifie que le retour est conforme

    def test_bullish_context_with_exception(self):
        """Teste la gestion du contexte lorsqu'une exception est levée."""
        with self.assertRaises(Exception):  # Vérifie que l'exception est bien levée
            with BullishContext(self.mock_bullish_function, self.assets) as transformed_assets:
                raise Exception("Test exception")

    def test_bullish_context_exit_handling(self):
        """Teste que __exit__ ne fait rien de spécial à la sortie."""
        with BullishContext(self.mock_bullish_function, self.assets) as transformed_assets:
            pass
        # __exit__ ne doit rien faire, donc on vérifie juste que le bloc with s'exécute sans erreur
        self.assertTrue(True)  # Si aucune exception n'est levée, le test passe


if __name__ == '__main__':
    unittest.main()
