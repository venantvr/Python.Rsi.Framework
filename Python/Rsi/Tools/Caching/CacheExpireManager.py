from typing import Literal, Optional, Self

from Python.Rsi.Tools.Caching.CacheExpire import CacheExpire
from Python.Rsi.Tools.Tooling.Timeframes import timeframe_to_seconds, get_seconds_till_close
from Python.Rsi.Tools.Types.Alias import GateioTimeFrame


class CacheExpireManager:
    def __init__(self, cache_expire: CacheExpire, cache_key: str, timeout_in_seconds: int):
        """
        Initialise le gestionnaire de cache avec les paramètres spécifiés.

        Args:
            cache_expire (CacheExpire): L'objet de gestion du cache.
            cache_key (str): La clé pour stocker/retrouver la valeur dans le cache.
            timeout_in_seconds (int): Le délai d'expiration du cache en secondes.
        """
        self.cache_expire = cache_expire
        self.cache_key = cache_key
        self.timeout_in_seconds = timeout_in_seconds
        self.triggered_by_timeframe = False
        self.timeframe_in_seconds = None
        self.value = None

    def set_policy(self, cache_mode: Literal['system', 'random', 'close'], timeframe: Optional[GateioTimeFrame]) -> Self:
        """
        Définit la politique de mise en cache en fonction du mode et éventuellement d'un intervalle de temps.

        Args:
            cache_mode (Literal['system', 'random', 'close']): Mode de mise en cache.
            timeframe (Optional[str]): L'intervalle de temps pour le mode 'close'.

        Returns:
            CacheExpireManager: L'instance actuelle pour permettre le chaînage des méthodes.
        """
        if cache_mode == 'close':
            self.triggered_by_timeframe = True
            self.timeframe_in_seconds = timeframe_to_seconds(timeframe)
        return self

    def __enter__(self):
        """
        Gestionnaire de contexte pour récupérer la valeur du cache à l'entrée du bloc.

        Returns:
            tuple: Retourne l'instance elle-même et la valeur récupérée du cache.
        """
        self.value = self.cache_expire.get(self.cache_key)
        return self, self.value

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Gestionnaire de contexte pour mettre en cache la valeur à la sortie du bloc, si nécessaire.

        Args:
            exc_type: Le type de l'exception levée (si existant).
            exc_val: La valeur de l'exception levée (si existant).
            exc_tb: La traceback de l'exception levée (si existant).
        """
        if self.cache_expire.get(self.cache_key) is None:
            expire_in_seconds = self.__compute_timeout_in_seconds()
            self.cache_expire.set(key=self.cache_key, value=self.value, expire_in_seconds=expire_in_seconds)

    def __compute_timeout_in_seconds(self):
        """
        Calcule le temps d'expiration basé sur la politique fixée.

        Returns:
            int: Le nombre de secondes avant expiration du cache.
        """
        if not self.triggered_by_timeframe:
            timeout = self.timeout_in_seconds
        else:
            seconds_till_close = get_seconds_till_close(self.timeframe_in_seconds)
            timeout = seconds_till_close
        return timeout
