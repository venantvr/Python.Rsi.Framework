import io
import sys
from datetime import datetime, timezone

import mplfinance as mpf
import pandas as pd
from pandas import DataFrame
from framework.business.bot_currency_pair import BotCurrencyPair
from framework.logs.logs_utils import logger, log_exception_error
from framework.quotes.price import Price
from framework.tooling.telegram_notification_service import code_configuration
from framework.types.types_alias import GateioTimeFrame


# matplotlib.use('Agg')


class SnapshotCreator:
    _instance = None

    # noinspection PyUnusedLocal
    # @staticmethod
    def create_image(self, currency_pair: BotCurrencyPair, timeframe: GateioTimeFrame, dataframe: DataFrame, prefix: str, price: Price, items=15):
        logger.log_currency_warning(currency_pair, f'Méthode {type(self).__name__} \'create_image\' : {prefix}')
        # Création d'un buffer de mémoire pour stocker l'image
        buffer = io.BytesIO()
        code = code_configuration()
        base = currency_pair.base
        if base is None:
            base = currency_pair.id.split('_')[0]
        # noinspection PyBroadException
        try:
            # Assurez-vous que l'index du DataFrame est de type datetime
            dataframe.index = pd.to_datetime(dataframe.index, utc=True)
            # Zoomer sur les 10 dernières chandelles
            last_items = dataframe.iloc[-items:]
            # Création et sauvegarde du graphique en chandelles dans le buffer
            now = datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M:%S')
            mpf.plot(last_items, type='candle',
                     style='charles',
                     title=f'({code}) {prefix} {base} | {now} | {price}',
                     savefig=buffer)
            # Réinitialisation de la position du curseur au début du buffer
            buffer.seek(0)
        except Exception as ex:
            # Capture de l'exception courante
            exc_type, exc_value, tb = exc_info = sys.exc_info()
            # Log de l'exception avec la stack d'appels
            log_exception_error(exc_type, exc_value, tb)
        return buffer
