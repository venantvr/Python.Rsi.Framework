from __future__ import print_function

import os
import time
import warnings
from typing import List, Dict, Optional, Literal

import gate_api
import pandas as pd
from gate_api import Currency, CurrencyPair, Order, ApiException
from joblib import dump, load

from venantvr.business.bot_currency_pair import BotCurrencyPair
from venantvr.dataframes.japanese_dataframe import JapaneseDataframe
from venantvr.logs.logs_utils import logger
from venantvr.parameters.parameters import Parameters
from venantvr.quotes.position import Position
from venantvr.quotes.price import Price
from venantvr.quotes.quantity import Quantity
from venantvr.quotes.quote import Quote
from venantvr.quotes.quotes_utils import base_from_pair, create_currency_quote, quote_currency
from venantvr.tooling.database_manager import DatabaseManager
from venantvr.tooling.security_wait import SecurityWait
from venantvr.tooling.telegram_notification_service import TelegramNotificationService
from venantvr.tooling.tooling_utils import round_down, file_exists, timeframe_to_seconds
from venantvr.types.types_alias import GateioTimeFrame

warnings.filterwarnings('ignore', category=DeprecationWarning)


class GateioProxy:
    spot_api_instance = None
    singleton_instance = None

    yaml = Parameters.get_instance().yaml
    gateio_parameters = yaml['gateio']
    v4 = gateio_parameters['v4']
    configuration = gate_api.Configuration(
        host=v4['host'],
        key=v4['key'],
        secret=v4['secret'],
    )
    closed = gateio_parameters['candles']['closed']
    __nominal_number_of_candles = gateio_parameters['candles']['nominal']
    __max_number_of_candles = gateio_parameters['candles']['max']
    bot = yaml['bot']
    quote = bot['quote']
    max_time = bot['wait']['order']['max']
    sleep_time = bot['wait']['order']['sleep']
    debug = bot['mode'] == 'debug'
    script_path = os.path.dirname(os.path.abspath(__file__))
    # currencies_file: str | bytes = os.path.join(script_path, gateio_parameters['currencies']['file'])
    currencies_file: str | bytes = os.path.join(Parameters.script_path, gateio_parameters['currencies']['file'])

    def get_nominal_number_of_candles(self):
        return self.__nominal_number_of_candles

    def get_max_number_of_candles(self):
        return self.__max_number_of_candles

    def __new__(cls):
        if cls.singleton_instance is None:
            cls.singleton_instance = super(GateioProxy, cls).__new__(cls)
            api_client = gate_api.ApiClient(cls.configuration)
            cls.spot_api_instance = gate_api.SpotApi(api_client)
            if not file_exists(cls.currencies_file):
                currency_pairs: List[CurrencyPair] = cls.singleton_instance.list_currency_pairs()
                dump(currency_pairs, cls.currencies_file)
            else:
                currency_pairs: List[CurrencyPair] = load(cls.currencies_file)
            cls.trading_pairs_dictionnary = {trading_pair.id: trading_pair for trading_pair in currency_pairs}
            cls.security_wait = SecurityWait()
            cls.telegram_service = TelegramNotificationService()
            cls.database_manager = DatabaseManager()

        return cls.singleton_instance

    def cancel_order(self, currency_pair: BotCurrencyPair, order: Order):
        # Log de l'annulation de l'ordre
        order_id = self.get_order_id(order)
        logger.log_currency_warning(currency_pair=currency_pair,
                                    message=f'Ordre annulé avec succès. ID de l\'ordre: {order_id}')

        return self.spot_api_instance.cancel_order(order_id, currency_pair.id)

    def list_currency_pairs(self) -> List[CurrencyPair]:
        logger.warning('C\'est un peu long...')
        return [currency_pair for currency_pair in self.spot_api_instance.list_currency_pairs() if
                currency_pair.quote == self.quote and currency_pair.trade_status == 'tradable']

    def pair_from_currency(self, token: Currency) -> BotCurrencyPair:
        if f'_{self.quote}' not in token.currency.upper():
            return BotCurrencyPair(pair_id=f'{token.currency.upper()}_{self.quote}',
                                   base_currency=token.currency.upper(),
                                   quote_currency=self.quote.upper(),
                                   data_dir=os.path.join(Parameters.get_instance().parsed_args.logs, 'Python.Rsi.Bot'))
        else:
            return BotCurrencyPair(pair_id=token.currency.upper(),
                                   base_currency=base_from_pair(token.currency.upper()),
                                   quote_currency=self.quote.upper(),
                                   data_dir=os.path.join(Parameters.get_instance().parsed_args.logs, 'Python.Rsi.Bot'))

    def base_quantity_precision(self, currency_pair: BotCurrencyPair):  # VENTE
        # Amount Precision: Ce terme est habituellement associé à la quantité de l'actif échangé.
        # Il détermine le nombre de décimales jusqu'auxquelles vous pouvez spécifier la quantité de l'actif que
        # vous voulez acheter ou vendre. Par exemple, si la précision de la quantité est de 3, vous pouvez passer
        # une commande pour 0.001, 0.002 unités de cet actif, etc. => Lors de la vente !!!!
        if currency_pair.id in list(self.trading_pairs_dictionnary.keys()):
            amount_precision = int(self.trading_pairs_dictionnary[currency_pair.id].amount_precision)
        else:
            amount_precision = 256
        logger.log_currency_warning(currency_pair, f'Précision de la base {amount_precision}')
        return amount_precision

    # Fonction pour obtenir la précision d'une paire de trading
    def quotation_amount_precision(self, currency_pair: BotCurrencyPair) -> int:  # ACHAT
        # Precision: Ce terme fait souvent référence à la précision des prix d'une paire de devises.
        # Cela détermine le nombre de chiffres significatifs ou décimales auxquels le prix d'une devise peut être
        # exprimé. Par exemple, si la précision est de 2, alors le prix peut être spécifié jusqu'à deux décimales,
        # comme 0.01, 0.02, etc. => Cotation , lors de l'achat !!!!!!
        if currency_pair.id in list(self.trading_pairs_dictionnary.keys()):
            precision = int(self.trading_pairs_dictionnary[currency_pair.id].precision)
        else:
            precision = 256
        logger.log_currency_info(currency_pair, f'Précision de quotation {precision}')
        return precision

    def token_min_quote_amount(self, currency_pair: BotCurrencyPair) -> Quote:
        if currency_pair.id in list(self.trading_pairs_dictionnary.keys()):
            min_amount = float(self.trading_pairs_dictionnary[currency_pair.id].min_quote_amount)
        else:
            min_amount = 0.0
        output: Quote = create_currency_quote(amount=min_amount,
                                              quote=self.quote)
        logger.log_currency_warning(currency_pair, f'Quantité minimale de vente {output}')
        return output

    @classmethod
    def get(cls):
        if cls.singleton_instance is None:
            cls.singleton_instance = cls()
        return cls.singleton_instance

    @classmethod
    def dispose(cls):
        cls.singleton_instance = None
        return True

    def wait_for_order(self, currency_pair: BotCurrencyPair, order: Order | Dict):
        order_id = self.get_order_id(order)
        max_wait_time = self.max_time
        status = None
        current_order = None
        while max_wait_time > 0:
            current_order = self.spot_api_instance.get_order(order_id, currency_pair.id)
            status = current_order.status
            if current_order.status == 'closed':
                break
            time.sleep(self.sleep_time)
            max_wait_time = max_wait_time - self.sleep_time
            logger.info(f'{order_id} a le statut : {status}')
        return current_order, status

    def poll_order(self, currency_pair: BotCurrencyPair, order: Order | Dict):
        order_id = self.get_order_id(order)
        current_order = self.spot_api_instance.get_order(order_id, currency_pair.id)
        status = current_order.status
        logger.info(f'{order_id} a le statut : {status}')
        return current_order, status

    # noinspection PyMethodMayBeStatic
    def get_order_id(self, order: Order | dict):
        if isinstance(order, Order):
            order_id = order.id
        else:
            order_id = order['id']
        return order_id

    def __place_order(self, currency_pair: BotCurrencyPair, side: Literal['buy', 'sell'], amount: Quantity, price: Price):
        """
        1. Ordre Limit (limit)
        Un ordre limité est un type d'ordre qui te permet de spécifier le prix maximal que tu es prêt à payer pour un achat ou le prix minimal que tu es prêt
        à accepter pour une vente. L'ordre ne sera exécuté que si le marché atteint ton prix spécifié ou mieux.

        Avantages de l'ordre limit :
        Contrôle du prix : Tu contrôles le prix auquel l'ordre doit être exécuté, ce qui t'évite de payer plus cher que prévu lors de l'achat ou de vendre à
        un prix inférieur à celui souhaité.
        Budget maîtrisé : Tu ne dépenseras pas plus que ton budget alloué pour un achat.
        Stratégie d'entrée/sortie précise : Permet de planifier les entrées et les sorties à des niveaux de prix pré-définis qui correspondent à ta stratégie
        de trading.
        2. Good Till Canceled (gtc)
        Good Till Canceled est une instruction pour maintenir l'ordre actif jusqu'à ce qu'il soit soit complètement exécuté, soit annulé par toi. Cela signifie
        que l'ordre restera sur le livre d'ordres et tentera de se remplir au fil du temps jusqu'à ce que les conditions du marché permettent son exécution ou
        jusqu'à ce que tu décides de l'annuler.

        Avantages de gtc :
        Pas besoin de renouveler l'ordre : Si l'ordre n'est pas exécuté immédiatement, il reste en vigueur jusqu'à ce qu'il soit exécuté ou annulé.
        Utilité pour les stratégies à long terme : C'est particulièrement utile si tu ne veux pas surveiller constamment le marché ou si tu as une cible
        de prix à long terme pour acheter ou vendre un actif.
        Flexibilité : Permet de réagir aux fluctuations du marché sur une plus longue période sans avoir besoin de passer de nouveaux ordres fréquemment.
        """
        order = gate_api.Order(currency_pair=currency_pair.id,
                               side=side,
                               amount=str(amount.quantity),
                               price=str(price.price),
                               time_in_force='gtc',
                               type='limit')
        try:
            # Placer l'ordre
            result = self.spot_api_instance.create_order(order)
            message = f'Ordre {side} créé avec succès. ID de l\'ordre : {result.id}'
            logger.log_currency_warning(currency_pair=currency_pair,
                                        message=message)
            self.telegram_service.chat(currency_pair=currency_pair,
                                       message=message)
            return result
        except ApiException as e:
            logger.log_currency_warning(currency_pair=currency_pair,
                                        message=f'Une erreur est survenue lors de la création de l\'ordre {side} : {e}\n')

    def place_conditional_sell_order(self, currency_pair: BotCurrencyPair, quantity: Optional[Quantity], price: Price) -> Optional[Order]:
        logger.log_currency_warning(currency_pair, 'Création d\'un ordre de vente')
        order: Optional[Order] = None
        if (quantity > Quantity.ZERO or self.debug) and price > Price.ZERO:  # On fait "comme si" pour débugger...
            order = self.__place_order(currency_pair=currency_pair,
                                       side='sell',
                                       amount=quantity,
                                       price=price)
        return order  # Sortir le nombre d'unités achetées

    def place_conditional_buy_order(self, currency_pair: BotCurrencyPair, price: Price, free_slots: int = 0) -> Optional[Order]:
        logger.log_currency_warning(currency_pair, 'Création d\'un order d\'achat')
        order: Optional[Order] = None
        quote = self.quote_position()
        quote_balance: Quote = create_currency_quote(amount=quote.amount,
                                                     quote=self.quote)

        if (quote_balance > Quote.ZERO or self.debug) and price > Price.ZERO:  # On fait "comme si" pour débugger...
            quote_slot = quote_balance.compute_slot_amount(free_slots=free_slots)
            quantity = self.quote_to_token_quantity(currency_pair, quote_slot, price)

            order = self.__place_order(currency_pair=currency_pair,
                                       side='buy',
                                       amount=quantity,
                                       price=price)
        return order

    def create_market_sell_order(self, currency_pair: BotCurrencyPair, token_balance: Quantity = None, token_price_quote: Price = None) -> Optional[Order]:
        logger.log_currency_warning(currency_pair, 'Création d\'un ordre de vente')
        pair_precision = self.base_quantity_precision(currency_pair=currency_pair)
        if token_balance > Quantity.ZERO or self.debug:  # On fait "comme si" pour débugger...
            if token_price_quote is None:
                token_price_quote = self.token_price(currency_pair=currency_pair)
            if token_price_quote > Price.ZERO:
                accepted_amount_token = token_balance.manage_amount_precision(pair_precision)
                min_quote_account = self.token_min_quote_amount(currency_pair=currency_pair)
                order_amount_quote = accepted_amount_token * token_price_quote
                if (accepted_amount_token > Quantity.ZERO and order_amount_quote >= min_quote_account) or self.debug:  # On fait "comme si" pour débugger...
                    amount = str(accepted_amount_token.quantity)
                    order = Order(currency_pair=currency_pair.id,
                                  side='sell',
                                  time_in_force='ioc',
                                  amount=amount,
                                  price='',
                                  type='market')
                    if not self.debug:
                        response_from_server: Order = self.spot_api_instance.create_order(order)
                        logger.info(f'{response_from_server}')
                        output, status = self.wait_for_order(currency_pair=currency_pair, order=response_from_server)
                        logger.log_currency_warning(currency_pair, f'Ordre de vente {token_balance} : {status}')
                    else:
                        output = order
                        output.status = 'closed'
                        output.price, _ = self.get_sell_price(currency_pair=currency_pair)
                        logger.warning(f'Emission d\'ordres de vente désactivée : {accepted_amount_token}')
                else:
                    output = None
                    logger.log_currency_warning(currency_pair, f'Impossible de vendre {accepted_amount_token}')
            else:
                output = None
                logger.log_currency_warning(currency_pair, 'Erreur de prix')
        else:
            output = None
            logger.log_currency_warning(currency_pair, f'Impossible de vendre {token_balance}')
        return output

    def create_market_buy_order(self, currency_pair: BotCurrencyPair, quote_balance: Quote = None, free_slots: int = 0) -> Optional[Order]:
        logger.log_currency_warning(currency_pair, 'Création d\'un order d\'achat')
        """
        Précision des montants pour USDT dans la paire cible... quotation.
        """
        pair_precision = self.quotation_amount_precision(currency_pair=currency_pair)
        if quote_balance > Quote.ZERO or self.debug:  # On fait "comme si" pour débugger...
            quote_slot = quote_balance.compute_slot_amount(free_slots=free_slots)
            adjusted_amount = quote_slot.manage_amount_precision(pair_precision)
            amount = str(adjusted_amount.amount)
            order = Order(currency_pair=currency_pair.id,
                          side='buy',
                          time_in_force='ioc',
                          amount=amount,
                          price='',
                          type='market')
            if not self.debug:
                response_from_server: Order = self.spot_api_instance.create_order(order)
                logger.info(f'{response_from_server}')
                output, status = self.wait_for_order(currency_pair=currency_pair, order=response_from_server)
                logger.log_currency_warning(currency_pair, f'Ordre d\'achat {adjusted_amount} : {status}')
            else:
                output = order
                output.status = 'closed'
                output.price, _ = self.get_buy_price(currency_pair=currency_pair)
                logger.log_currency_warning(currency_pair, f'Emission d\'ordres d\'achat désactivée {adjusted_amount}')
        else:
            output = None
            logger.log_currency_warning(currency_pair, f'Impossible d\'acheter avec {quote_balance}')
        return output

    def list_spot_accounts(self, currency=None):
        if currency is not None:
            api_response = self.spot_api_instance.list_spot_accounts(currency=currency)
        else:
            api_response = self.spot_api_instance.list_spot_accounts()
        return api_response

    def __list_candlesticks(self, currency_pair: BotCurrencyPair, interval: GateioTimeFrame, number_of_candles=2000, limit_per_call=1000,
                            closed: bool = None) -> JapaneseDataframe:
        if closed is None:
            closed = self.closed

        pd.set_option('display.precision', 10)
        api_responses = []
        output = None

        try:
            from_time = None  # Initialisation pour le premier appel

            while len(api_responses) < number_of_candles:
                result = self.spot_api_instance.list_candlesticks(currency_pair.id, interval=interval, limit=limit_per_call, _from=from_time)
                if not result:
                    logger.log_currency_warning(currency_pair, 'Aucune donnée supplémentaire récupérée')
                    break

                api_responses.extend(result)

                # Mise à jour de 'from_time' pour remonter dans le passé
                # Utilisation de la première valeur du résultat actuel pour ajuster 'from_time'
                from_time = int(result[0][0]) - limit_per_call * timeframe_to_seconds(interval)

                if len(result) < limit_per_call:
                    logger.log_currency_info(currency_pair, 'Fin des données disponibles atteinte')
                    break
            # Trier les données récupérées par timestamp
            api_responses = sorted(api_responses, key=lambda x: x[0])

            # Création du DataFrame
            df = JapaneseDataframe(api_responses, columns=['timestamp', 'volume', 'close', 'high', 'low', 'open', 'amount', 'closed'])
            df = self.__prepare_dataframe(df, closed)

            output = df.loc[df['closed']].tail(number_of_candles) if closed else df.tail(number_of_candles)

            if number_of_candles == self.get_max_number_of_candles():
                currency_pair.save_raw_dataframe(output, interval)

        except ApiException as e:
            logger.log_currency_warning(currency_pair, f'Exception lors de l\'appel à list_candlesticks: {e}')

        return output

    # noinspection PyMethodMayBeStatic
    def __prepare_dataframe(self, df, closed):
        # Conversion et nettoyage des données
        df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', utc=True)
        df[['volume', 'close', 'high', 'low', 'open', 'amount']] = df[['volume', 'close', 'high', 'low', 'open', 'amount']].apply(pd.to_numeric,
                                                                                                                                  errors='coerce')
        df['closed'] = df['closed'].map({'true': True, 'false': False})
        return df.loc[df['closed']] if closed else df

    def main_position(self, forbidden=None) -> Position:
        value_max = Quote.ZERO
        available = Quantity.ZERO
        token_max = None
        balances = self.spot_api_instance.list_spot_accounts()
        for balance in [balance for balance in balances if balance.currency not in forbidden]:
            # Information de position, on peut sortir 0.0...
            currency = Currency(currency=balance.currency)
            currency_pair: BotCurrencyPair = self.pair_from_currency(currency)
            price_in_quote = self.token_price(currency_pair=currency_pair)
            if price_in_quote > Price.ZERO:
                balance_quantity = Quantity(currency_pair=currency_pair, quantity=float(balance.available))
                value_in_quote = balance_quantity * price_in_quote
                if value_in_quote > value_max:
                    value_max = value_in_quote
                    token_max = Currency(balance.currency)
                    available = balance_quantity
        logger.info(f'Le token le plus largement détenu est : {token_max.currency} '
                    f'avec une quantité de {value_max} '
                    f'et une valeur de {value_max}')
        return Position(token=token_max,
                        amount=float(available.quantity))

    def quote_position(self) -> Position:
        amount = Quote.ZERO
        currency = Currency(self.quote)
        balances = self.list_spot_accounts(self.quote)
        for balance in [balance for balance in balances]:
            # Information de position, on peut sortir 0.0...
            amount: Quote = create_currency_quote(amount=float(balance.available),
                                                  quote=self.quote)
            break
        logger.info(f'{currency.currency} : {amount} dans le wallet')
        return Position(token=currency,
                        amount=amount.amount)

    def token_position(self, token=None) -> Position:
        available = Quantity.ZERO
        currency = Currency(currency=token)
        currency_pair = self.pair_from_currency(currency)
        balances = self.list_spot_accounts(token)
        for balance in [balance for balance in balances]:
            # Information de position, on peut sortir 0.0...
            available: Quantity = Quantity(currency_pair=currency_pair, quantity=float(balance.available))
            break
        logger.info(f'{token} : {available} dans le wallet')
        return Position(token=currency,
                        amount=available.quantity)

    def sell(self, currency_pair: BotCurrencyPair) -> (bool, Price):
        # noinspection PyUnusedLocal
        sell_price: Price = Price.ZERO
        logger.log_currency_warning(currency_pair, f'Méthode {type(self).__name__} \'sell\'')
        position = self.token_position(token=currency_pair.base)
        token_balance = Quantity(currency_pair=currency_pair, quantity=position.amount)
        if token_balance > Quantity.ZERO or self.debug:  # On fait "comme si" pour débugger...
            sell_order_fulfilled: Order = self.create_market_sell_order(currency_pair=currency_pair,
                                                                        token_balance=token_balance)
            logger.info(f'Ordre de vente : {sell_order_fulfilled}')
            if sell_order_fulfilled is not None:
                sell_price = Price(price=float(sell_order_fulfilled.price),
                                   quote=self.quote)
                logger.log_currency_warning(currency_pair, f'Vente {currency_pair.id} à {sell_price}')
                successful = True
            else:
                sell_price = Price.ZERO
                logger.log_currency_warning(currency_pair, f'Vente {currency_pair.id} impossible')
                successful = False
        else:
            sell_price = Price.ZERO
            logger.log_currency_warning(currency_pair, 'Quantité insuffisante pour vendre')
            successful = False
        return successful, sell_price

    def buy(self, currency_pair: BotCurrencyPair, free_slots: int, advisor: Optional[type]) -> (bool, Price):  # 16/03/2024
        # noinspection PyUnusedLocal
        buy_price: Price = Price.ZERO
        logger.log_currency_warning(currency_pair, f'Méthode {type(self).__name__} \'release\'')
        quote = self.quote_position()
        quote_balance: Quote = create_currency_quote(amount=quote.amount,
                                                     quote=self.quote)
        if quote_balance > Quote.ZERO or self.debug:  # On fait "comme si" pour débugger...
            buy_order_fulfilled: Order = self.create_market_buy_order(currency_pair=currency_pair,
                                                                      quote_balance=quote_balance,
                                                                      free_slots=free_slots)
            logger.info(f'Ordre d\'achat : {buy_order_fulfilled}')
            if buy_order_fulfilled is not None:
                buy_price = Price(price=float(buy_order_fulfilled.price),
                                  quote=self.quote)

                # Release
                # self.telegram_service.chat(currency_pair=currency_pair,
                #                            message=' - '.join([item.to_string() for item in currency_pair.get_events()]))  # Release

                # Release
                self.telegram_service.chat(currency_pair=currency_pair,
                                           message=f'Achat à {buy_price} par {advisor.__name__ if advisor is not None else type(self).__name__}')  # Release
                successful = True
            else:
                buy_price = Price.ZERO
                self.telegram_service.chat(currency_pair=currency_pair,
                                           message='Achat impossible')
                successful = False
        else:
            buy_price = Price.ZERO
            logger.log_currency_warning(currency_pair, 'Balance insuffisante pour acheter')
            successful = False
        return successful, buy_price

    def token_price(self, currency_pair: BotCurrencyPair) -> Price:
        if currency_pair.id in self.trading_pairs_dictionnary:
            ticker = self.spot_api_instance.list_tickers(currency_pair=currency_pair.id)
            quote = quote_currency(currency_pair.id)
            output = Price(price=float(ticker[0].last),
                           quote=quote)
        else:
            output = Price.ZERO
        return output

    # @log_thread_activity
    def fetch_candles(self, currency_pair: BotCurrencyPair, interval: GateioTimeFrame, number_of_candles: int, closed: bool = None):
        """
        Récupère les bougies (candlesticks) pour un symbole spécifique sur un intervalle de temps donné.
        """
        japanese_candlesticks = self.__list_candlesticks(currency_pair=currency_pair,
                                                         interval=interval,
                                                         number_of_candles=number_of_candles,
                                                         limit_per_call=1000,
                                                         closed=closed)
        return japanese_candlesticks

    def __get_orderbook_bid_ask(self, currency_pair: BotCurrencyPair, precision: int):
        average_bid_price = 0.0
        average_ask_price = 0.0
        try:
            # Obtenir le carnet d'ordres
            order_book = self.spot_api_instance.list_order_book(currency_pair.id, limit=2)

            # Extraire le prix d'achat le plus élevé (le premier de la liste des "bids")
            bid_prices = [float(bid[0]) for bid in order_book.bids[:5]]
            average_bid_price = sum(bid_prices) / len(bid_prices)
            average_bid_price = round(average_bid_price, precision)

            # Extraire le prix de vente le plus bas (le premier de la liste des "asks") => Le prix que paie...
            ask_prices = [float(ask[0]) for ask in order_book.asks[:5]]
            average_ask_price = sum(ask_prices) / len(ask_prices)
            average_ask_price = round(average_ask_price, precision)

        except ApiException as e:
            logger.log_currency_warning(currency_pair, f'Exception when calling API: %s\n' % e)
        return average_bid_price, average_ask_price

    def get_buy_price(self, currency_pair: BotCurrencyPair) -> (str, Price):
        precision = self.quotation_amount_precision(currency_pair)
        _, lowest_ask = self.__get_orderbook_bid_ask(currency_pair=currency_pair,
                                                     precision=precision)
        return str(lowest_ask), Price(price=lowest_ask,
                                      quote=self.quote)

    def get_sell_price(self, currency_pair: BotCurrencyPair) -> (str, Price):
        precision = self.quotation_amount_precision(currency_pair)
        highest_bid, _ = self.__get_orderbook_bid_ask(currency_pair=currency_pair,
                                                      precision=precision)
        return str(highest_bid), Price(price=highest_bid,
                                       quote=self.quote)

    def get_ath(self, currency_pair: BotCurrencyPair, interval: GateioTimeFrame, number_of_candles: int, columns: list) -> float:
        df = self.fetch_candles(currency_pair=currency_pair,
                                interval=interval,
                                number_of_candles=number_of_candles,
                                closed=False)
        if len(columns) == 1:
            values = df[columns[0]].diff().fillna(0.0)
        else:
            values = df[columns].mean(axis=1).diff().fillna(0.0)
        ath = values.max()
        return ath

    def quote_to_token_quantity(self, currency_pair: BotCurrencyPair, quote: Quote, price: Price) -> Quantity:
        # Quote to Quantity...
        trading_pairs_dictionnary = self.trading_pairs_dictionnary[currency_pair.id]
        quantity = quote.amount / price.price
        quantity = Quantity(currency_pair=currency_pair, quantity=round_down(quantity, trading_pairs_dictionnary.amount_precision))
        return quantity
