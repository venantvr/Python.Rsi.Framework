import unittest

import pandas as pd

from venantvr.tooling.timeframe_adjuster import TimeframeAdjuster
from venantvr.types.types_alias import GateioTimeFrame


class TestTimeframeAdjuster(unittest.TestCase):

    def setUp(self):
        """Initialise l'environnement de test avec des données factices."""
        self.adjuster = TimeframeAdjuster()

    def test_normalize_dataframe_columns(self):
        """Test de la méthode normalize_dataframe_columns pour la normalisation des colonnes."""
        # Créer un DataFrame factice
        data = {
            'col1': [10, 20, 30, None, 50],
            'col2': [100, 200, 300, 400, None]
        }
        df = pd.DataFrame(data)

        # Colonnes à normaliser
        columns_to_normalize = ['col1', 'col2']

        # Appliquer la normalisation
        normalized_df = self.adjuster.normalize_dataframe_columns(df, columns_to_normalize)

        # Vérifier que les colonnes ont été normalisées entre 0 et 100
        self.assertEqual(normalized_df['col1'].dropna().min(), 0.0)
        self.assertEqual(normalized_df['col1'].dropna().max(), 100.0)
        self.assertEqual(normalized_df['col2'].dropna().min(), 0.0)
        self.assertEqual(normalized_df['col2'].dropna().max(), 100.0)

    def test_adjust_dataframe_indexes(self):
        """Test de la méthode adjust_dataframe_indexes pour ajuster les index des DataFrames."""
        # Créer des DataFrames avec des index tz-naive et les rendre tz-aware
        df1 = pd.DataFrame({'price': [10, 20, 30]}, index=pd.date_range('2023-01-01', periods=3, freq='h').tz_localize('UTC'))
        df2 = pd.DataFrame({'price': [40, 50, 60]}, index=pd.date_range('2023-01-02', periods=3, freq='h').tz_localize('UTC'))

        # Dictionnaire de bougies par paire et timeframe
        candlestick_dataframes = {
            '1h': {
                'BTC_USDT': df1,
                'ETH_USDT': df2
            }
        }

        # Dictionnaire de mappage de paires
        currency_pair_mapping = {
            'BTC_USDT': 'BTC_USDT',
            'ETH_USDT': 'ETH_USDT'
        }

        # Fonction factice pour calculer le nombre attendu de bougies
        def mock_candles_count(pair, timeframe):
            return 2  # Simule un nombre de bougies attendu

        # Appliquer l'ajustement des index
        adjusted_df = self.adjuster.adjust_dataframe_indexes(GateioTimeFrame('1h'), candlestick_dataframes, mock_candles_count, currency_pair_mapping)

        # Vérifier que les index ont été ajustés
        btc_usdt_index = adjusted_df['1h']['BTC_USDT'].index
        eth_usdt_index = adjusted_df['1h']['ETH_USDT'].index

        self.assertEqual(len(btc_usdt_index), 2)
        self.assertEqual(len(eth_usdt_index), 2)

        # Comparer les timestamps en tz-aware
        self.assertEqual(btc_usdt_index[-1], pd.Timestamp('2023-01-01 02:00:00', tz='UTC'))
        self.assertEqual(eth_usdt_index[-1], pd.Timestamp('2023-01-02 02:00:00', tz='UTC'))


if __name__ == '__main__':
    unittest.main()
