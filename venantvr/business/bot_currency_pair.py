import importlib
import itertools
import os
from os import path
from tempfile import gettempdir
from typing import Optional

import numpy as np
from gate_api import CurrencyPair
from pandas import DataFrame

from venantvr.events.event_store import EventStore
from venantvr.events.generic_event import GenericEvent
from venantvr.quotes import Price
from venantvr.quotes.quotes_utils import file_exists
from venantvr.types import GateioTimeFrame


class BotCurrencyPair(CurrencyPair):
    """
    Classe représentant une paire de devises gérée par un bot de trading.
    Hérite de CurrencyPair de l'API Gate.io et ajoute des fonctionnalités supplémentaires.

    ### Correspondance des noms (Ancien → Nouveau → Signification)
    | Ancien Nom                  | Nouveau Nom                          | Signification                                   |
    |-----------------------------|--------------------------------------|-------------------------------------------------|
    | `__passthrough`             | `passthrough_conditions`             | Dictionnaire pour les conditions de passthrough |
    | `__min_price`               | `minimum_price`                      | Prix minimal pour la paire                      |
    | `__max_price`               | `maximum_price`                      | Prix maximal pour la paire                      |
    | `__can_start`               | `is_ready`                           | Indique si le bot peut démarrer                 |
    | `__event_store`             | `event_store`                        | Stockage des événements                         |
    | `directory`                 | `data_directory`                     | Répertoire de stockage des fichiers             |
    | `dataframe_backup`          | `dataframe_backup_path`              | Chemin vers le fichier de backup des DataFrames |
    | `dump_file`                 | `events_dump_path`                   | Chemin vers le fichier de dump des événements   |
    | `ml_models`                 | `machine_learning_models`            | Modèles de machine learning                     |
    | `__load_class`              | `load_class_dynamically`             | Chargement dynamique de classe                  |
    | `set_ml_models`             | `configure_machine_learning_models`  | Configuration des modèles de machine learning   |
    | `__entity_path`             | `get_entity_directory`               | Récupère le chemin du répertoire d'une entité   |
    | `raw_dataframe_to_csv`      | `save_raw_dataframe`                 | Sauvegarde un DataFrame brut en CSV             |
    | `processed_dataframe_to_csv`| `save_processed_dataframe`           | Sauvegarde un DataFrame traité en CSV           |
    | `set_start`                 | `set_ready_state`                    | Définit si le bot peut démarrer                 |
    | `get_start`                 | `get_ready_state`                    | Vérifie si le bot peut démarrer                 |
    | `set_event`                 | `add_event`                          | Ajoute un événement dans le EventStore          |
    | `get_event`                 | `get_event_data`                     | Récupère un événement spécifique                |
    | `get_events`                | `fetch_events`                       | Récupère une liste d'événements                 |
    | `passthrough_condition`     | `add_passthrough_condition`          | Ajoute des conditions de passthrough            |
    | `avoid_condition`           | `should_avoid_condition`             | Vérifie si une condition doit être évitée       |
    | `default_converter`         | `json_converter`                     | Convertit en JSON les types non sérialisables   |
    """

    def __init__(self,
                 pair_id=None,
                 base_currency=None,
                 quote_currency=None,
                 trade_fee=None,
                 min_base=None,
                 min_quote=None,
                 max_base=None,
                 max_quote=None,
                 amount_precision=None,
                 price_precision=None,
                 status=None,
                 sell_threshold=None,
                 buy_threshold=None,
                 config_vars=None,
                 data_dir=None):
        """
        Initialise une instance de BotCurrencyPair avec des paramètres spécifiques.

        Args:
            pair_id (str): Identifiant de la paire de devises.
            base_currency (str): Devise de base.
            quote_currency (str): Devise de cotation.
            trade_fee (float | None): Frais de trading.
            min_base (float | None): Montant minimal pour la devise de base.
            min_quote (float | None): Montant minimal pour la devise de cotation.
            max_base (float | None): Montant maximal pour la devise de base.
            max_quote (float | None): Montant maximal pour la devise de cotation.
            amount_precision (float | None): Précision du montant.
            price_precision (int): Précision générale des prix.
            status (str): Statut de la paire pour le trading.
            sell_threshold (float | None): Seuil de vente.
            buy_threshold (float | None): Seuil d'achat.
            config_vars (dict | None): Configuration locale des variables.
            data_dir (str): Répertoire pour stocker les fichiers liés à cette paire.
        """
        super().__init__(
            pair_id,
            base_currency,
            quote_currency,
            trade_fee,
            min_base,
            min_quote,
            max_base,
            max_quote,
            amount_precision,
            price_precision,
            status,
            sell_threshold,
            buy_threshold,
            config_vars)

        # Initialisation des attributs spécifiques au bot de trading
        self.passthrough_conditions: dict[str, list] = {}  # Dictionnaire pour les conditions de passthrough par acteur
        self.minimum_price: Price = Price.ZERO  # Prix minimal pour la paire
        self.maximum_price: Price = Price.ZERO  # Prix maximal pour la paire
        self.is_ready: bool = False  # Indicateur si le bot peut démarrer
        self.event_store: EventStore = EventStore()  # Stockage des événements pour la paire
        self.data_directory: str = data_dir if data_dir is not None else gettempdir()  # Répertoire de stockage par défaut
        self.is_active = True  # Indicateur de l'état actif du bot
        self.dataframe_backup_path: str = path.join(self.get_entity_directory('dataframes'), f'{self.id.lower()}_backup.csv')
        # Chemin du backup des DataFrames
        self.events_dump_path: str = path.join(self.get_entity_directory('events'), f'{self.id.lower()}_dump_file.json')
        # Chemin du fichier dump pour les événements
        self.machine_learning_models = {}  # Dictionnaire pour les modèles de machine learning

    # noinspection PyMethodMayBeStatic
    def load_class_dynamically(self, class_path: str):
        """
        Charge dynamiquement une classe à partir d'une chaîne de caractères.

        Args:
            class_path (str): Chemin complet de la classe à charger.

        Returns:
            type: La classe chargée.
        """
        class_data = class_path.split(".")
        module_path = ".".join(class_data[:-1])
        class_name = class_data[-1]

        module = importlib.import_module(module_path)  # Importe dynamiquement le module
        return getattr(module, class_name)  # Retourne la classe

    def configure_machine_learning_models(self, models_config: dict):
        """
        Définit les modèles de machine learning pour cette paire de devises.

        Args:
            models_config (dict): Dictionnaire contenant les chemins des modèles et les types d'événements associés.
        """
        for model_key, model_info in models_config.items():
            base_path = model_info['base_path']
            model_suffix = model_info['model_suffix']
            event_type = model_info['event_type']
            model_full_path = path.join(self.get_entity_directory(base_path), f'{self.id.lower()}{model_suffix}')  # Chemin complet du modèle
            event_class = self.load_class_dynamically(class_path=event_type)  # Charge dynamiquement la classe d'événement
            self.machine_learning_models[model_key] = {
                'model_path': model_full_path,
                'event_class': event_class
            }

    def get_entity_directory(self, entity_type: str):
        """
        Crée et retourne le chemin d'un répertoire pour un type d'entité donné.

        Args:
            entity_type (str): Le type d'entité (ex. 'dataframes', 'events').

        Returns:
            str: Le chemin du répertoire pour le type d'entité.
        """
        directory_path = path.join(self.data_directory, entity_type)
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)  # Crée le répertoire s'il n'existe pas
        return directory_path

    def save_raw_dataframe(self, dataframe: DataFrame, timeframe: GateioTimeFrame):
        """
        Enregistre un DataFrame brut dans un fichier CSV pour un intervalle de temps donné.

        Args:
            dataframe (DataFrame): Le DataFrame à sauvegarder.
            timeframe (GateioTimeFrame): L'intervalle de temps associé au DataFrame.
        """
        file_id = self.id.lower()
        file_path = path.join(self.get_entity_directory('timeframes'), f'{file_id}_{timeframe}_backup.csv')
        dataframe.to_csv(file_path, index=True)

    def save_processed_dataframe(self, dataframe: DataFrame, timeframes: list[GateioTimeFrame], selected_columns: list[str]):
        """
        Enregistre un DataFrame traité dans un fichier CSV avec des colonnes spécifiques pour des intervalles de temps donnés.

        Args:
            dataframe (DataFrame): Le DataFrame à sauvegarder.
            timeframes (list[GateioTimeFrame]): Liste des intervalles de temps pour le resampling.
            selected_columns (list[str]): Liste des colonnes à inclure.
        """
        if not file_exists(self.dataframe_backup_path):  # Vérifie si le backup existe déjà
            if len(selected_columns) == 0:
                dataframe.to_csv(self.dataframe_backup_path, index=True)  # Sauvegarde toutes les colonnes
            else:
                columns_with_timeframes = itertools.product(timeframes, selected_columns)  # Produit cartésien des timeframes et colonnes
                formatted_columns = [f'{timeframe}_{column}' for timeframe, column in columns_with_timeframes]
                dataframe[formatted_columns].to_csv(self.dataframe_backup_path, index=True)  # Sauvegarde seulement les colonnes spécifiées

    def set_ready_state(self, result: bool) -> bool:
        """
        Détermine si le bot peut démarrer ou non en fonction d'une condition.

        Args:
            result (bool): Condition pour démarrer le bot.

        Returns:
            bool: True si le bot peut démarrer, sinon False.
        """
        if not self.is_ready and not result:
            self.is_ready = True
            return True
        return False

    def get_ready_state(self) -> bool:
        """
        Vérifie si le bot peut démarrer.

        Returns:
            bool: True si le bot peut démarrer, sinon False.
        """
        return self.is_ready

    def add_event(self, event_message: dict):
        """
        Ajoute un événement au EventStore associé à cette instance.

        Args:
            event_message (dict): Le message de l'événement à stocker.
        """
        self.event_store.add_event_to_store(event_message)

    def get_event_data(self, event_name: str) -> Optional[GenericEvent]:
        """
        Récupère un événement spécifique depuis l'EventStore associé à cette instance.

        Args:
            event_name (str): Le nom de l'événement à récupérer.

        Returns:
            Optional[GenericEvent]: L'événement trouvé correspondant ou None s'il n'est pas trouvé.
        """
        return self.event_store.retrieve_event(event_name)

    def fetch_events(self) -> list[GenericEvent]:
        """
        Récupère et retourne une liste d'événements transformés en utilisant des modèles de machine learning (ML).

        Returns:
            list[GenericEvent]: Une liste d'instances de `GenericEvent` créées à partir des données d'événements stockées.
        """
        events_list = []  # Initialise une liste vide pour stocker les événements
        for model_key, model_info in self.machine_learning_models.items():
            event_class: type = model_info['event_class']
            event_data: dict = self.get_event_data(model_key)

            if event_data is not None:
                events_list.append(event_class(event_data))

        return events_list  # Retourne la liste des événements

    def add_passthrough_condition(self, actor: str, conditions: list[str]):
        """
        Ajoute des conditions pour un acteur spécifique dans le dictionnaire de passthrough.

        Args:
            actor (str): L'acteur pour lequel les conditions s'appliquent.
            conditions (list[str]): Liste des conditions à ajouter.
        """
        key = actor.lower()
        values = [condition.lower() for condition in conditions]
        if key in self.passthrough_conditions:
            self.passthrough_conditions[key].extend(values)
        else:
            self.passthrough_conditions[key] = values

    def should_avoid_condition(self, actor: str, condition: str):
        """
        Vérifie si une condition doit être évitée pour un acteur donné.

        Args:
            actor (str): L'acteur à vérifier.
            condition (str): La condition à vérifier.

        Returns:
            bool: True si la condition doit être évitée, sinon False.
        """
        key = actor.lower()
        return key in self.passthrough_conditions and condition.lower() in self.passthrough_conditions[key]

    def __hash__(self):
        """
        Calcule le hash de l'objet basé sur son identifiant.

        Returns:
            int: Hash de l'objet.
        """
        return hash(self.id)

    def __eq__(self, other):
        """
        Vérifie l'égalité entre deux objets BotCurrencyPair basés sur leur identifiant.

        Args:
            other (BotCurrencyPair): L'autre objet à comparer.

        Returns:
            bool: True si les objets sont égaux, sinon False.
        """
        return self.id == other.id

    def __str__(self):
        """
        Retourne une représentation sous forme de chaîne de l'objet.

        Returns:
            str: L'identifiant de l'objet.
        """
        return self.id

    def __repr__(self):
        """
        Retourne une représentation officielle de l'objet.

        Returns:
            str: L'identifiant de l'objet.
        """
        return self.id

    # noinspection PyMethodMayBeStatic
    def json_converter(self, obj):
        """
        Convertit les types non sérialisables en JSON.

        Args:
            obj : L'objet à convertir.

        Returns:
            bool : Représentation booléenne de l'objet si c'est un np.bool_.

        Raises:
            TypeError: Si l'objet n'est pas sérialisable.
        """
        if isinstance(obj, np.bool_):
            return bool(obj)
        raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')
