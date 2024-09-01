import time


class CacheExpire:
    """
    Classe CacheExpire pour gérer un cache avec expiration.

    Cette classe permet de stocker des paires clé-valeur dans un cache, avec la possibilité de définir une expiration pour chaque clé.
    Les valeurs expirées sont automatiquement supprimées du cache lors de l'accès.
    """

    def __init__(self):
        """
        Initialise une instance de CacheExpire avec deux dictionnaires :
        - `cache` pour stocker les paires clé-valeur.
        - `expire_times` pour stocker les moments d'expiration de chaque clé.
        """
        self.cache = {}  # Dictionnaire pour stocker les données mises en cache
        self.expire_times = {}  # Dictionnaire pour stocker les moments d'expiration des clés

    def set(self, key, value, expire_in_seconds: int):
        """
        Ajoute une valeur au cache avec une clé spécifiée et définit un temps d'expiration pour cette clé.

        Paramètres :
        key : La clé à utiliser pour stocker la valeur.
        value : La valeur à stocker dans le cache.
        expire_in_seconds (int) : Le temps en secondes après lequel la clé expire.

        Remarque :
        Si le temps d'expiration est défini dans le passé (expire_in_seconds est inférieur au temps actuel),
        une variable d'erreur non utilisée est définie (peut-être pour une future gestion d'erreur ou de log).
        """
        if expire_in_seconds > time.time():
            # noinspection PyUnusedLocal
            error = True  # Indicateur que quelque chose ne va pas (potentiellement à gérer plus tard)

        # Stocke la valeur dans le cache
        self.cache[key] = value

        # Définir le moment d'expiration pour la clé, en fonction du temps d'expiration spécifié
        self.expire_times[key] = time.time() + expire_in_seconds

    def get(self, key):
        """
        Récupère une valeur du cache par sa clé. Si la clé a expiré, elle est supprimée du cache.

        Paramètres :
        key : La clé de la valeur à récupérer.

        Retourne :
        La valeur associée à la clé si elle est encore valide, sinon None.
        """
        if key in self.cache:
            # Vérifie si la clé a expiré
            if time.time() >= self.expire_times[key]:
                # Supprime la clé et sa valeur associée du cache si elle a expiré
                del self.cache[key]
                del self.expire_times[key]
                return None
            else:
                # Retourne la valeur si elle est encore valide
                return self.cache[key]
        return None
