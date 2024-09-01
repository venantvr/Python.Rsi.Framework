import importlib
import itertools
import os
from os import path
from tempfile import gettempdir

import numpy as np
from gate_api import CurrencyPair  # Importation de la classe CurrencyPair de l'API Gate.io
from pandas import DataFrame

from Python.Rsi.Tools.Quotes import Price
from Python.Rsi.Tools.Quotes.Currencies import file_exists
from Python.Rsi.Tools.Types import GateioTimeFrame


class BotCurrencyPair(CurrencyPair):
    """
    Classe BotCurrencyPair qui hérite de CurrencyPair de l'API Gate.io.

    Cette classe représente une paire de devises gérée par un bot de trading, avec des fonctionnalités
    supplémentaires pour la manipulation des données, l'intégration de modèles de machine learning,
    et la gestion des fichiers de données.
    """

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
        """
        Initialise une instance de BotCurrencyPair avec des paramètres spécifiques.

        Args:
            id (str): Identifiant de la paire de devises.
            base (str): Devise de base.
            quote (str): Devise de cotation.
            fee (float | None): Frais de trading.
            min_base_amount (float | None): Montant minimal pour la devise de base.
            min_quote_amount (float | None): Montant minimal pour la devise de cotation.
            max_base_amount (float | None): Montant maximal pour la devise de base.
            max_quote_amount (float | None): Montant maximal pour la devise de cotation.
            amount_precision (float | None): Précision du montant.
            precision (int): Précision générale.
            trade_status (str): Statut de la paire pour le trading.
            sell_start (float | None): Début de la vente.
            buy_start (float | None): Début de l'achat.
            local_vars_configuration (dict | None): Configuration locale des variables.
            directory (str): Répertoire pour stocker les fichiers liés à cette paire.
        """
        # Appel au constructeur parent pour initialiser les attributs de la paire de devises
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

        # Initialisation des attributs supplémentaires spécifiques au bot de trading
        self.__passthrough: dict[str, list] = {}  # Dictionnaire pour les conditions de passthrough par acteur
        self.__min_price: Price = Price.ZERO  # Prix minimal pour la paire
        self.__max_price: Price = Price.ZERO  # Prix maximal pour la paire
        self.__can_start: bool = False  # Indicateur si le bot peut démarrer
        self.directory: str = directory if directory is not None else gettempdir()  # Répertoire de stockage par défaut
        self.active = True  # Indicateur de l'état actif du bot
        self.dataframe_backup: str = path.join(self.__entity_path('dataframes'), f'{self.id.lower()}_backup.csv')  # Chemin du backup des DataFrames
        self.dump_file: str = path.join(self.__entity_path('events'), f'{self.id.lower()}_dump_file.json')  # Chemin du fichier dump pour les événements
        self.ml_models = dict()  # Dictionnaire pour les modèles de machine learning

    # noinspection PyMethodMayBeStatic
    def __load_class(self, full_class_string: str):
        """
        Charge dynamiquement une classe à partir d'une chaîne de caractères.

        Args:
            full_class_string (str): Chemin complet de la classe à charger.

        Returns:
            type: La classe chargée.
        """
        class_data = full_class_string.split(".")
        module_path = ".".join(class_data[:-1])
        class_str = class_data[-1]

        module = importlib.import_module(module_path)  # Importe dynamiquement le module
        return getattr(module, class_str)  # Retourne la classe

    def set_ml_models(self, ml_models: dict):
        """
        Définit les modèles de machine learning pour cette paire de devises.

        Args:
            ml_models (dict): Dictionnaire contenant les chemins des modèles et les types d'événements associés.
        """
        for key, value in ml_models.items():
            base_path = value['base_path']
            model_suffix = value['model_suffix']
            event_type = value['event_type']
            model_path = path.join(self.__entity_path(base_path), f'{self.id.lower()}{model_suffix}')  # Chemin complet du modèle
            event_class = self.__load_class(full_class_string=event_type)  # Charge dynamiquement la classe d'événement
            self.ml_models[key] = {
                'path': model_path,
                'event': event_class
            }

    def __entity_path(self, _type: str):
        """
        Crée et retourne le chemin d'un répertoire pour un type d'entité donné.

        Args:
            _type (str): Le type d'entité (ex. 'dataframes', 'events').

        Returns:
            str: Le chemin du répertoire pour le type d'entité.
        """
        __path = path.join(self.directory, _type)
        if not os.path.exists(__path):
            os.makedirs(__path)  # Crée le répertoire s'il n'existe pas
        return __path

    def raw_dataframe_to_csv(self, dataframe: DataFrame, timeframe: GateioTimeFrame):
        """
        Enregistre un DataFrame brut dans un fichier CSV pour un intervalle de temps donné.

        Args:
            dataframe (DataFrame): Le DataFrame à sauvegarder.
            timeframe (GateioTimeFrame): L'intervalle de temps associé au DataFrame.
        """
        file_id = self.id.lower()
        file = path.join(self.__entity_path('timeframes'), f'{file_id}_{timeframe}_backup.csv')
        dataframe.to_csv(file, index=True)

    def processed_dataframe_to_csv(self, dataframe: DataFrame, timeframes: list[GateioTimeFrame], columns: list[str]):
        """
        Enregistre un DataFrame traité dans un fichier CSV avec des colonnes spécifiques pour des intervalles de temps donnés.

        Args:
            dataframe (DataFrame): Le DataFrame à sauvegarder.
            timeframes (list[GateioTimeFrame]): Liste des intervalles de temps pour le resampling.
            columns (list[str]): Liste des colonnes à inclure.
        """
        if not file_exists(self.dataframe_backup):  # Vérifie si le backup existe déjà
            if len(columns) == 0:
                dataframe.to_csv(self.dataframe_backup, index=True)  # Sauvegarde toutes les colonnes
            else:
                timeframed_columns = itertools.product(timeframes, columns)  # Produit cartésien des timeframes et colonnes
                _ = [f'{timeframe}_{column}' for timeframe, column in timeframed_columns]
                dataframe[_].to_csv(self.dataframe_backup, index=True)  # Sauvegarde seulement les colonnes spécifiées

    def set_start(self, result: bool) -> bool:
        """
        Détermine si le bot peut démarrer ou non en fonction d'une condition.

        Args:
            result (bool): Condition pour démarrer le bot.

        Returns:
            bool: True si le bot peut démarrer, sinon False.
        """
        if not self.__can_start and not result:
            self.__can_start = True
            return True
        else:
            return False

    def get_start(self) -> bool:
        """
        Vérifie si le bot peut démarrer.

        Returns:
            bool: True si le bot peut démarrer, sinon False.
        """
        return self.__can_start

    def passthrough_condition(self, actor: str, conditions: list[str]):
        """
        Ajoute des conditions pour un acteur spécifique dans le dictionnaire de passthrough.

        Args:
            actor (str): L'acteur pour lequel les conditions s'appliquent.
            conditions (list[str]): Liste des conditions à ajouter.
        """
        key = actor.lower()
        values = [condition.lower() for condition in conditions]
        if key in self.__passthrough:
            self.__passthrough[key].extend(values)
        else:
            self.__passthrough[key] = values

    def avoid_condition(self, actor: str, condition: str):
        """
        Vérifie si une condition doit être évitée pour un acteur donné.

        Args:
            actor (str): L'acteur à vérifier.
            condition (str): La condition à vérifier.

        Returns:
            bool: True si la condition doit être évitée, sinon False.
        """
        key = actor.lower()
        return key in self.__passthrough and condition.lower() in self.__passthrough[key]

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
    def default_converter(self, obj):
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
