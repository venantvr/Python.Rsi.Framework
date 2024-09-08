import json
import os
import threading
from typing import Self

import yaml
from Python.Rsi.Tools.Business import BotCurrencyPair
from Python.Rsi.Tools.Tooling import resolve_path_json_pairs, gateio_currency_pair


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
