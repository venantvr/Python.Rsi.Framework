import unittest

from framework.quotes.bitoin import BTC
from framework.quotes.dollar import USDT
from framework.quotes.quotes_utils import base_from_pair, quote_from_pair, create_currency_quote, quote_currency


class TestQuotesUtils(unittest.TestCase):

    def test_base_from_pair(self):
        """Test de la fonction base_from_pair pour extraire la devise de base."""
        self.assertEqual(base_from_pair('BTC_USDT'), 'BTC')
        self.assertEqual(base_from_pair('ETH_BTC'), 'ETH')

    def test_quote_from_pair(self):
        """Test de la fonction quote_from_pair pour extraire la devise de cotation (quote)."""
        self.assertEqual(quote_from_pair('BTC_USDT'), 'USDT')
        self.assertEqual(quote_from_pair('ETH_BTC'), 'BTC')
        self.assertEqual(quote_from_pair('BTC'), 'USDT')  # Test avec une seule devise, utilise la valeur par défaut

    def test_create_currency_quote(self):
        """Test de la fonction create_currency_quote pour la création d'objets de devises."""
        self.assertIsInstance(create_currency_quote(1000, 'USDT'), USDT)
        self.assertIsInstance(create_currency_quote(0.5, 'BTC'), BTC)
        with self.assertRaises(ValueError):
            create_currency_quote(100, 'EUR')  # Test avec une devise non supportée

    def test_quote_currency(self):
        """Test de la fonction quote_currency pour extraire la devise de cotation à partir d'une paire."""
        self.assertEqual(quote_currency('BTC/USDT'), 'USDT')
        self.assertEqual(quote_currency('ETH-BTC'), 'BTC')
        self.assertEqual(quote_currency('ADA_USDT'), 'USDT')


if __name__ == '__main__':
    unittest.main()
