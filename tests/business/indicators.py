import unittest
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from framework.business.bot_currency_pair import BotCurrencyPair
from framework.business.indicators import replace_nan_values, calculate_relative_strength_index, calculate_exponential_moving_average, calculate_hourly_volume
from framework.types.types_alias import GateioTimeFrame


class TestFunctions(unittest.TestCase):

    # Tests pour replace_nan_values
    def test_replace_nan_values(self):
        # Test de base
        data = pd.Series([1, np.nan, 3, np.nan, 5])
        result = replace_nan_values(data)
        self.assertFalse(result.isna().any())
        self.assertEqual(result[0], 1)

        # Test avec une série sans NaN
        data_no_nan = pd.Series([1, 2, 3, 4, 5])
        result_no_nan = replace_nan_values(data_no_nan)
        pd.testing.assert_series_equal(result_no_nan, data_no_nan)

        # Test avec une série avec tous les NaN
        all_nan_data = pd.Series([np.nan, np.nan, np.nan])
        result_all_nan = replace_nan_values(all_nan_data)
        pd.testing.assert_series_equal(result_all_nan, all_nan_data)

    # Tests pour calculate_relative_strength_index
    def test_calculate_rsi(self):
        # DataFrame avec des données de test
        data = pd.DataFrame({
            'close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110]
        })
        price_columns = ['close']
        rsi = calculate_relative_strength_index(data, price_columns)

        # Vérification que les résultats sont calculés
        self.assertIsInstance(rsi, pd.Series)
        self.assertEqual(len(rsi), len(data))
        # self.assertFalse(rsi.isna().all())

    # Tests pour calculate_exponential_moving_average
    def test_calculate_ema(self):
        # DataFrame avec des données de test
        data = pd.DataFrame({
            'close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110]
        })
        price_columns = ['close']
        ema = calculate_exponential_moving_average(data, price_columns)

        # Vérification que les résultats sont calculés
        self.assertIsInstance(ema, pd.DataFrame)
        self.assertEqual(len(ema), len(data))
        self.assertFalse(ema.isna().all().all())

    # Tests pour calculate_hourly_volume
    def test_calculate_hourly_volume(self):
        # Simuler une heure actuelle légèrement après la dernière bougie
        current_time = datetime.now()

        # Créez un DataFrame avec 5 bougies horaires
        data = pd.DataFrame({
            'volume': [1000, 2000, 3000, 4000, 5000],  # Volume de trading pour chaque période
            'rsi': [30, 40, 50, 60, 70],  # Valeurs RSI pour chaque bougie
        })

        # Génération d'un index de temps pour les bougies horaires, avec la dernière bougie étant incomplète (commençant il y a 50 minutes)
        timestamps = [current_time - timedelta(hours=i) for i in range(4, 0, -1)]  # 4 bougies horaires complètes
        timestamps.append(current_time - timedelta(minutes=50))  # Bougie incomplète commençant il y a 50 minutes
        data['timestamp'] = timestamps
        data = data.set_index('timestamp')  # Définir l'index du DataFrame

        # Définir currency_pair et timeframe
        currency_pair = BotCurrencyPair('BTC/USDT')  # Paires de devises pour le test
        timeframe = GateioTimeFrame('1h')  # Timeframe pour les bougies (1 heure)

        # Tolerance pour filtrer les segments basés sur le RSI
        tolerance_bandwidth = 5.0

        # Appel de la fonction avec les données
        normalized_volume, mean_volume = calculate_hourly_volume(
            currency_pair, data, 'rsi', current_time, timeframe, tolerance_bandwidth
        )

        # Vérifications pour s'assurer qu'il n'y a pas de division par zéro et que les résultats sont valides
        self.assertGreater(normalized_volume, 0)  # Vérifie que le volume normalisé est supérieur à 0
        self.assertGreater(mean_volume, 0)  # Vérifie que le volume moyen filtré est supérieur à 0


if __name__ == '__main__':
    unittest.main()
