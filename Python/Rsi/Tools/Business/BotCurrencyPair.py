import importlib
import itertools
import os
from os import path
from tempfile import gettempdir

import numpy as np
from gate_api import CurrencyPair
from pandas import DataFrame

from Python.Rsi.Tools.Quotes import Price
from Python.Rsi.Tools.Quotes.Currencies import file_exists
from Python.Rsi.Tools.Types import GateioTimeFrame


class BotCurrencyPair(CurrencyPair):

    # noinspection PyShadowingBuiltins
    def __init__(self,
                 id=None,
                 base=None,
                 quote=None,
                 fee=None,
                 min_base_amount=None,
                 min_quote_amount=None,
                 max_base_amount=None,
                 max_quote_amount=None,
                 amount_precision=None,
                 precision=None,
                 trade_status=None,
                 sell_start=None,
                 buy_start=None,
                 local_vars_configuration=None,
                 directory=None):
        super().__init__(
            id,
            base,
            quote,
            fee,
            min_base_amount,
            min_quote_amount,
            max_base_amount,
            max_quote_amount,
            amount_precision,
            precision,
            trade_status,
            sell_start,
            buy_start,
            local_vars_configuration)
        self.__passthrough: dict[str, list] = {}
        self.__min_price: Price = Price.ZERO
        self.__max_price: Price = Price.ZERO
        self.__can_start: bool = False
        # self.__event_store: EventStore = EventStore()
        self.directory: str = directory if directory is not None else gettempdir()
        self.active = True
        # file_id = self.id.lower()
        self.dataframe_backup: str = path.join(self.__entity_path('dataframes'), f'{self.id.lower()}_backup.csv')
        self.dump_file: str = path.join(self.__entity_path('events'), f'{self.id.lower()}_dump_file.json')
        self.ml_models = dict()

    # noinspection PyMethodMayBeStatic
    def __load_class(self, full_class_string: str):
        """
        Dynamically load a class from a string
        """
        class_data = full_class_string.split(".")
        module_path = ".".join(class_data[:-1])
        class_str = class_data[-1]

        module = importlib.import_module(module_path)
        return getattr(module, class_str)

    def set_ml_models(self, ml_models: dict):
        for key, value in ml_models.items():
            base_path = value['base_path']
            model_suffix = value['model_suffix']
            event_type = value['event_type']
            model_path = path.join(self.__entity_path(base_path), f'{self.id.lower()}{model_suffix}')  # model_suffix: _model_01.joblib
            event_class = self.__load_class(full_class_string=event_type)
            self.ml_models[key] = {
                'path': model_path,
                'event': event_class
            }

    # def get_events(self) -> list[GenericEvent]:
    #     events = []
    #     for tranform_key, items in self.ml_models.items():
    #         event_class: type = items['event']
    #         event_data: dict = self.get_event(tranform_key)
    #         if event_data is not None:
    #             events.append(event_class(event_data))
    #     return events

    def __entity_path(self, _type: str):
        __path = path.join(self.directory, _type)
        if not os.path.exists(__path):
            os.makedirs(__path)
        return __path

    def raw_dataframe_to_csv(self, dataframe: DataFrame, timeframe: GateioTimeFrame):
        file_id = self.id.lower()
        file = path.join(self.__entity_path('timeframes'), f'{file_id}_{timeframe}_backup.csv')
        dataframe.to_csv(file, index=True)

    def processed_dataframe_to_csv(self, dataframe: DataFrame, timeframes: list[GateioTimeFrame], columns: list[str]):
        if not file_exists(self.dataframe_backup):
            if len(columns) == 0:
                dataframe.to_csv(self.dataframe_backup, index=True)
            else:
                timeframed_columns = itertools.product(timeframes, columns)
                _ = [f'{timeframe}_{column}' for timeframe, column in timeframed_columns]
                dataframe[_].to_csv(self.dataframe_backup, index=True)

    # @staticmethod
    # def dataframe_from_csv(path_to_csv: str) -> DataFrame:
    #     return pd.read_csv(path_to_csv)

    def set_start(self, result: bool) -> bool:
        if not self.__can_start and not result:
            self.__can_start = True
            return True
        else:
            return False

    def get_start(self) -> bool:
        return self.__can_start

    # def set_event(self, message: dict):
    #     self.__event_store.set_event(message)

    # def get_event(self, event: str) -> Optional[GenericEvent]:
    #     return self.__event_store.get_event(event)

    def passthrough_condition(self, actor: str, conditions: list[str]):
        # Fonction pour ajouter des conditions à une clé spécifique dans le dictionnaire
        key = actor.lower()
        values = [condition.lower() for condition in conditions]
        if key in self.__passthrough:
            self.__passthrough[key].extend(values)
        else:
            self.__passthrough[key] = values

    def avoid_condition(self, actor: str, condition: str):
        key = actor.lower()
        return key in self.__passthrough and condition.lower() in self.__passthrough[key]

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return self.id

    def __repr__(self):
        return self.id

    # noinspection PyMethodMayBeStatic
    def default_converter(self, obj):
        """Convertit les types non sérialisables."""
        if isinstance(obj, np.bool_):
            return bool(obj)
        raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')
