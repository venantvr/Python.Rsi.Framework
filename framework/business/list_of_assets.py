import json
import os
import threading
from typing import LiteralString
from typing import Self

import requests
import yaml

from framework.business.bot_currency_pair import BotCurrencyPair
from framework.business.gateio_proxy import GateioProxy
from framework.logs.logs_utils import logger
from framework.quotes.quotes_utils import gateio_currency_pair
from framework.tooling.tooling_utils import resolve_path_json_pairs, verify_pair


class ListOfAssets:
    """
    Classe ListOfAssets pour gérer la configuration et le suivi des paires de devises dans un bot de trading.

    Cette classe permet de charger, configurer et gérer des paires de devises à partir de fichiers YAML et JSON,
    en prenant en compte des modèles de machine learning et des conditions spécifiques pour chaque devise.

    ### Correspondance des noms (Ancien → Nouveau → Signification)
    | Ancien Nom                            | Nouveau Nom                                    | Signification                                               |
    |---------------------------------------|------------------------------------------------|-------------------------------------------------------------|
    | `self.__assets_configuration_yaml`    | `self.assets_configuration_yaml_path`          | Chemin vers le fichier YAML contenant la config des actifs. |
    | `self.__path`                         | `self.configuration_absolute_path`             | Chemin absolu du fichier de configuration des actifs.       |
    | `self.__quote`                        | `self.trading_quote_currency`                  | Devise de cotation utilisée pour le trading.                |
    | `self.__limit`                        | `self.asset_limit`                             | Nombre maximum d'actifs à charger.                          |
    | `self.__assets`                       | `self.loaded_assets`                           | Liste des actifs actuellement chargés.                      |
    | `self.__lock`                         | `self.threading_lock`                          | Verrou pour synchroniser l'accès aux actifs chargés.        |
    | `self.__files_timestamp_modifications`| `self.file_modification_timestamps`            | Suivi des horodatages de modification des fichiers JSON.    |
    | `self.__retrieve_pairs_files`         | `self.retrieve_asset_files`                    | Méthode pour récupérer les fichiers contenant les paires.   |
    | `self.__update_tokens`                | `self.update_active_tokens`                    | Met à jour l'état des paires d'actifs (actives/inactives).  |
    | `self.__update_search_structure`      | `self.refresh_currency_pairs_index`            | Actualise l'index de recherche des paires de devises.       |
    | `self.__files_containing_assets_lists`| `self.asset_file_configuration`                | Fichiers de configuration contenant des listes d'actifs.    |
    | `self.currency_pairs_index`           | `self.asset_search_index`                      | Index des paires de devises pour la recherche rapide.       |
    | `load_from_yaml_file`                 | `load_assets_from_yaml_configuration`          | Charge les actifs à partir du fichier de configuration YAML.|
    | `set_ml_models`                       | `apply_machine_learning_models`                | Applique des modèles de machine learning aux actifs.        |
    """

    def __init__(self, assets_configuration_yaml: str, quote: str, limit: int):
        self.assets_configuration_yaml_path = assets_configuration_yaml
        self.configuration_absolute_path = os.path.abspath(self.assets_configuration_yaml_path)
        self.trading_quote_currency = quote
        self.asset_limit = limit
        self.loaded_assets = []
        self.threading_lock = threading.Lock()
        self.file_modification_timestamps = {}
        self.asset_file_configuration = {}
        self.asset_search_index: dict[str, BotCurrencyPair] = {}
        self.load_assets_from_yaml_configuration()

    @property
    def assets(self) -> list[BotCurrencyPair]:
        with self.threading_lock:
            return self.loaded_assets

    def apply_machine_learning_models(self, ml_models: dict) -> Self:
        for asset in self.loaded_assets:
            asset.set_ml_models(ml_models=ml_models)
        return self

    def load_assets_from_yaml_configuration(self) -> Self:
        with self.threading_lock:
            trading_pairs: set[BotCurrencyPair] = set()
            candidates: list[BotCurrencyPair] = []
            self.asset_file_configuration, forbidden_assets = self.retrieve_asset_files()
            effective_assets_lists = {key: value for key, value in self.asset_file_configuration.items() if value['enabled']}
            [self.file_modification_timestamps.setdefault(file, None) for file in effective_assets_lists]
            for file_containing_assets_lists, configuration in effective_assets_lists.items():
                getmtime = os.path.getmtime(file_containing_assets_lists)
                passthrough = configuration['passthrough']
                if getmtime != self.file_modification_timestamps[file_containing_assets_lists]:
                    with open(file_containing_assets_lists, 'r') as fichier:
                        for symbol in json.load(fichier):
                            if symbol not in forbidden_assets:
                                currency_pair = gateio_currency_pair(pair_symbol=symbol, keep_pair_quote=True, trading_quote=self.trading_quote_currency)
                                trading_pairs.add(currency_pair)
                        [trading_pair.add_passthrough_condition(key, conditions)
                         for trading_pair in trading_pairs for key, conditions in (passthrough.items()
                                                                                   if passthrough is not None else [])]
                        candidates = candidates + list(trading_pairs)[:self.asset_limit]
                        self.file_modification_timestamps[file_containing_assets_lists] = getmtime
            self.update_active_tokens(candidates)
            self.refresh_currency_pairs_index()
            return self

    def retrieve_asset_files(self):
        with open(self.assets_configuration_yaml_path, 'r') as f:
            configuration = yaml.load(f, Loader=yaml.FullLoader)
            asset_files = {resolve_path_json_pairs(script_path=self.configuration_absolute_path,
                                                   file_name=key): value for key, value in configuration['files'].items()}
            return asset_files, configuration['forbidden']

    def update_active_tokens(self, new_pairs: list[BotCurrencyPair]):
        # Marquer tous les tokens comme inactifs initialement
        for new_pair in new_pairs:
            if new_pair.id in [asset.id for asset in self.loaded_assets]:
                # Trouver et réactiver le token existant
                for token in self.loaded_assets:
                    if token.id == new_pair.id:
                        token.active = True
                        break
            else:
                # Ajouter le nouveau token s'il n'existe pas déjà
                self.loaded_assets.append(new_pair)
        # Désactiver les tokens non mentionnés dans la nouvelle liste
        for token in self.loaded_assets:
            if token.id not in [new_pair.id for new_pair in new_pairs]:
                token.active = False

    def refresh_currency_pairs_index(self):
        for asset in self.loaded_assets:
            if asset.id not in self.asset_search_index:
                self.asset_search_index[asset.id] = asset


def fetch_all_currency_pairs(file_path: LiteralString | str | bytes, number_of_pages: int, quote_currency: str = 'USDT'):
    """
    Récupère toutes les paires de devises disponibles et les enregistre dans un fichier JSON.

    Args:
        file_path (LiteralString | str | bytes): Le chemin vers le fichier où les données seront enregistrées.
        number_of_pages (int): Nombre de pages à parcourir pour récupérer les données.
        quote_currency (str): La devise de référence à utiliser (par défaut 'USDT').

    """
    all_currency_pairs = []
    gateio_proxy_instance = GateioProxy.get()
    all_currency_pairs = gateio_proxy_instance.list_currency_pairs()
    if len(all_currency_pairs):
        with open(file_path, 'w') as json_file:
            json.dump([currency_pair.id for currency_pair in all_currency_pairs], json_file, indent=2, sort_keys=True)
            logger.info(f'Data successfully saved to {file_path}')


def fetch_popular_currency_pairs(file_path: LiteralString | str | bytes, number_of_pages: int, quote_currency: str = 'USDT'):
    """
    Récupère les paires de devises les plus populaires et les enregistre dans un fichier JSON.

    Args:
        file_path (LiteralString | str | bytes): Le chemin vers le fichier où les données seront enregistrées.
        number_of_pages (int): Nombre de pages à parcourir pour récupérer les données.
        quote_currency (str): La devise de référence à utiliser (par défaut 'USDT').

    Returns:
        list: Liste des paires de devises populaires.
    """
    popular_currency_pairs = []
    for page_number in range(1, number_of_pages):
        url = f'https://www.gate.io/apiweb/v1/home/sortList?sortType=2&page={page_number}&pageSize=10'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            currency_items = data['data']['sortList']
            for currency_pair in currency_items:
                if currency_pair['symbol'].upper() != quote_currency.upper():
                    pair = currency_pair['symbol'].upper() + '/' + quote_currency.upper()
                    if verify_pair(pair):
                        popular_currency_pairs.append(pair)
        else:
            logger.error(f'Request error: {response.status_code}')

    if len(popular_currency_pairs):
        with open(file_path, 'w') as json_file:
            json.dump(popular_currency_pairs, json_file, indent=2, sort_keys=True)
            logger.info(f'Data successfully saved to {file_path}')

    return popular_currency_pairs


def fetch_top_gainers(file_path: LiteralString | str | bytes, number_of_pages: int, quote_currency: str = 'USDT'):
    """
    Récupère les paires de devises ayant les meilleures performances et les enregistre dans un fichier JSON.

    Args:
        file_path (LiteralString | str | bytes): Le chemin vers le fichier où les données seront enregistrées.
        number_of_pages (int): Nombre de pages à parcourir pour récupérer les données.
        quote_currency (str): La devise de référence à utiliser (par défaut 'USDT').

    Returns:
        list: Liste des paires de devises ayant les meilleures performances.
    """
    top_gainers_currency_pairs = []
    for page_number in range(1, number_of_pages):
        url = f'https://www.gate.io/apiweb/v1/home/sortList?sortType=1&page={page_number}&pageSize=10'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            currency_items = data['data']['sortList']
            for currency_pair in currency_items:
                if currency_pair['symbol'].upper() != quote_currency.upper():
                    pair = currency_pair['symbol'].upper() + '/' + quote_currency.upper()
                    if verify_pair(pair):
                        top_gainers_currency_pairs.append(pair)
        else:
            logger.error(f'Request error: {response.status_code}')

    if len(top_gainers_currency_pairs):
        with open(file_path, 'w') as json_file:
            json.dump(top_gainers_currency_pairs, json_file, indent=2, sort_keys=True)
            logger.info(f'Data successfully saved to {file_path}')

    return top_gainers_currency_pairs


def fetch_most_profitable_currency_pairs(file_path: LiteralString | str | bytes, number_of_pages: int, quote_currency: str = 'USDT'):
    """
    Récupère les paires de devises les plus rentables et les enregistre dans un fichier JSON.

    Args:
        file_path (LiteralString | str | bytes): Le chemin vers le fichier où les données seront enregistrées.
        number_of_pages (int): Nombre de pages à parcourir pour récupérer les données.
        quote_currency (str): La devise de référence à utiliser (par défaut 'USDT').

    Returns:
        list: Liste des paires de devises les plus rentables.
    """
    most_profitable_currency_pairs = []
    for page_number in range(1, number_of_pages):
        url = f'https://www.gate.io/api/web/v1/site/getHomeCoinList?type=6&page={page_number}&pageSize=10'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            currency_items = data['data']['list']
            for currency_pair in currency_items:
                if currency_pair['asset'].upper() != quote_currency.upper():
                    pair = currency_pair['asset'].upper() + '/' + quote_currency.upper()
                    if verify_pair(pair):
                        most_profitable_currency_pairs.append(pair)
        else:
            logger.error(f'Request error: {response.status_code}')

    if len(most_profitable_currency_pairs):
        with open(file_path, 'w') as json_file:
            json.dump(most_profitable_currency_pairs, json_file, indent=2, sort_keys=True)
            logger.info(f'Data successfully saved to {file_path}')

    return most_profitable_currency_pairs


def fetch_trending_currency_pairs(file_path: LiteralString | str | bytes, number_of_pages: int):
    """
    Récupère les paires de devises en tendance et les enregistre dans un fichier JSON.

    Args:
        file_path (LiteralString | str | bytes): Le chemin vers le fichier où les données seront enregistrées.
        number_of_pages (int): Nombre de pages à parcourir pour récupérer les données.

    Returns:
        list: Liste des paires de devises en tendance.
    """
    trending_currency_pairs = []
    for page_number in range(1, number_of_pages):
        url = f'https://www.gate.io/apiweb/v1/home/getCoinList?type=1&page={page_number}&pageSize=10&subType=1'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            market_items = data['data']['marketList']
            for currency_pair in market_items:
                pair = currency_pair['pair'].upper().replace('_', '/')
                if verify_pair(pair):
                    trending_currency_pairs.append(pair)
        else:
            logger.error(f'Request error: {response.status_code}')

    if len(trending_currency_pairs):
        with open(file_path, 'w') as json_file:
            json.dump(trending_currency_pairs, json_file, indent=2, sort_keys=True)
            logger.info(f'Data successfully saved to {file_path}')

    return trending_currency_pairs


"""
Table de correspondance des anciens noms et nouveaux noms :

| Ancien nom               | Nouveau nom                          | Signification                                               |
|--------------------------|--------------------------------------|-------------------------------------------------------------|
| get_all                  | fetch_all_currency_pairs             | Récupérer toutes les paires de devises                      |
| get_popular              | fetch_popular_currency_pairs         | Récupérer les paires de devises les plus populaires         |
| get_gainers              | fetch_top_gainers                    | Récupérer les paires de devises ayant les meilleures gains  |
| get_profits              | fetch_most_profitable_currency_pairs | Récupérer les paires de devises les plus rentables          |
| get_trends               | fetch_trending_currency_pairs        | Récupérer les paires de devises en tendance                 |
| file                     | file_path                            | Chemin vers le fichier                                      |
| pages_number             | number_of_pages                      | Nombre de pages à parcourir                                 |
| quote                    | quote_currency                       | Devise de référence                                         |
| currency_pairs           | currency_pairs                       | Liste des paires de devises                                 |
| fichier_json             | json_file                            | Fichier JSON où les données sont sauvegardées               |
| reponse                  | response                             | Réponse de la requête HTTP                                  |
| contenu                  | data                                 | Données JSON extraites de la réponse HTTP                   |
| items                    | currency_items                       | Liste des éléments de devises dans les données récupérées   |
"""
