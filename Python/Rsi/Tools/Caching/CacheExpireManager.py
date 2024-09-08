from typing import Literal, Optional, Self

from Python.Rsi.Tools.Caching.CacheExpire import CacheExpire
from Python.Rsi.Tools.Tooling.Timeframes import timeframe_to_seconds, get_seconds_till_close
from Python.Rsi.Tools.Types.Alias import GateioTimeFrame


class CacheExpireManager:
    """
    Classe CacheExpireManager pour gérer les stratégies de mise en cache avec expiration.

    Cette classe gère la mise en cache des valeurs en fonction de différentes politiques de cache,
    telles que 'system', 'random', et 'close', avec la possibilité de définir des délais d'expiration.

    ### Correspondance des noms (Ancien → Nouveau → Signification)
    | Ancien Nom                     | Nouveau Nom                            | Signification                                                   |
    |--------------------------------|----------------------------------------|-----------------------------------------------------------------|
    | `self.cache_expire`            | `cache_manager`                        | Instance de CacheExpire pour gérer la mise en cache             |
    | `self.cache_key`               | `cache_identifier`                     | Clé unique utilisée pour identifier une entrée de cache         |
    | `self.timeout_in_seconds`      | `default_cache_timeout`                | Délai d'expiration par défaut du cache                          |
    | `self.triggered_by_timeframe`  | `is_timeframe_based`                   | Indique si le cache est basé sur un intervalle de temps         |
    | `self.timeframe_in_seconds`    | `timeframe_duration_in_seconds`        | Intervalle de temps converti en secondes                        |
    | `self.value`                   | `cached_value`                         | Valeur à mettre en cache ou à récupérer                         |
    | `set_policy`                   | `set_caching_policy`                   | Définit la politique de mise en cache                           |
    | `__compute_timeout_in_seconds` | `calculate_cache_timeout_in_seconds`   | Calcule le délai d'expiration en fonction de la politique       |
    """

    def __init__(self, cache_expire: CacheExpire, cache_key: str, timeout_in_seconds: int):
        """
        Initialise le gestionnaire de cache avec les paramètres spécifiés.

        Args:
            cache_expire (CacheExpire): L'objet de gestion du cache.
            cache_key (str): La clé pour stocker/retrouver la valeur dans le cache.
            timeout_in_seconds (int): Le délai d'expiration par défaut du cache en secondes.
        """
        self.cache_manager = cache_expire  # Instance de CacheExpire pour la gestion du cache
        self.cache_identifier = cache_key  # Clé utilisée pour stocker/retrouver la valeur dans le cache
        self.default_cache_timeout = timeout_in_seconds  # Délai d'expiration par défaut du cache
        self.is_timeframe_based = False  # Indicateur si le cache est déclenché par un intervalle de temps spécifique
        self.timeframe_duration_in_seconds = None  # Intervalle de temps en secondes (si applicable)
        self.cached_value = None  # Valeur à mettre en cache ou à récupérer

    def set_caching_policy(self, cache_mode: Literal['system', 'random', 'close'], timeframe: Optional[GateioTimeFrame]) -> Self:
        """
        Définit la politique de mise en cache en fonction du mode et éventuellement d'un intervalle de temps.

        Args:
            cache_mode (Literal['system', 'random', 'close']): Mode de mise en cache.
            timeframe (Optional[GateioTimeFrame]): L'intervalle de temps pour le mode 'close'.

        Returns:
            CacheExpireManager: L'instance actuelle pour permettre le chaînage des méthodes.
        """
        if cache_mode == 'close':
            self.is_timeframe_based = True  # Active le mode basé sur le timeframe
            self.timeframe_duration_in_seconds = timeframe_to_seconds(timeframe)  # Convertit le timeframe en secondes
        return self

    def __enter__(self):
        """
        Gestionnaire de contexte pour récupérer la valeur du cache à l'entrée du bloc.

        Returns:
            tuple: Retourne l'instance elle-même et la valeur récupérée du cache.
        """
        self.cached_value = self.cache_manager.get_value_if_not_expired(self.cache_identifier)  # Récupère la valeur du cache
        return self, self.cached_value

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Gestionnaire de contexte pour mettre en cache la valeur à la sortie du bloc, si nécessaire.

        Args:
            exc_type: Le type de l'exception levée (si existant).
            exc_val: La valeur de l'exception levée (si existant).
            exc_tb: La traceback de l'exception levée (si existant).
        """
        if self.cache_manager.get_value_if_not_expired(self.cache_identifier) is None:  # Vérifie si la valeur est absente du cache
            expire_in_seconds = self.calculate_cache_timeout_in_seconds()  # Calcule le délai d'expiration
            # Met en cache la valeur avec le temps d'expiration calculé
            self.cache_manager.set_value_with_expiration(key=self.cache_identifier, value=self.cached_value, expire_in_seconds=expire_in_seconds)

    def calculate_cache_timeout_in_seconds(self):
        """
        Calcule le temps d'expiration basé sur la politique fixée.

        Returns:
            int: Le nombre de secondes avant expiration du cache.
        """
        if not self.is_timeframe_based:
            timeout = self.default_cache_timeout  # Utilise le délai d'expiration par défaut
        else:
            seconds_till_close = get_seconds_till_close(self.timeframe_duration_in_seconds)  # Calcule le temps restant jusqu'à la clôture du timeframe
            timeout = seconds_till_close  # Utilise ce temps comme délai d'expiration
        return timeout
