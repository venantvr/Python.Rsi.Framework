import time


class CacheExpire:
    """
    Classe CacheExpire pour gérer un cache avec expiration.

    Cette classe permet de stocker des paires clé-valeur dans un cache, avec la possibilité de définir une expiration pour chaque clé.
    Les valeurs expirées sont automatiquement supprimées du cache lors de l'accès.

    ### Correspondance des noms (Ancien → Nouveau → Signification)
    | Ancien Nom              | Nouveau Nom                         | Signification                                                    |
    |-------------------------|-------------------------------------|------------------------------------------------------------------|
    | `self.cache`            | `cached_data`                       | Dictionnaire pour stocker les données mises en cache             |
    | `self.expire_times`     | `expiration_timestamps`             | Dictionnaire pour stocker les moments d'expiration des clés      |
    | `set`                   | `set_value_with_expiration`         | Ajoute une valeur au cache avec une expiration                   |
    | `get`                   | `get_value_if_not_expired`          | Récupère une valeur si elle n'a pas expiré, sinon la supprime    |
    """

    def __init__(self):
        """
        Initialise une instance de CacheExpire avec deux dictionnaires :
        - `cached_data` pour stocker les paires clé-valeur.
        - `expiration_timestamps` pour stocker les moments d'expiration de chaque clé.
        """
        self.cached_data = {}  # Dictionnaire pour stocker les données mises en cache
        self.expiration_timestamps = {}  # Dictionnaire pour stocker les moments d'expiration des clés

    def set_value_with_expiration(self, key, value, expire_in_seconds: int):
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
        self.cached_data[key] = value

        # Définir le moment d'expiration pour la clé, en fonction du temps d'expiration spécifié
        self.expiration_timestamps[key] = time.time() + expire_in_seconds

    def get_value_if_not_expired(self, key):
        """
        Récupère une valeur du cache par sa clé. Si la clé a expiré, elle est supprimée du cache.

        Paramètres :
        key : La clé de la valeur à récupérer.

        Retourne :
        La valeur associée à la clé si elle est encore valide, sinon None.
        """
        if key in self.cached_data:
            # Vérifie si la clé a expiré
            if time.time() >= self.expiration_timestamps[key]:
                # Supprime la clé et sa valeur associée du cache si elle a expiré
                del self.cached_data[key]
                del self.expiration_timestamps[key]
                return None
            else:
                # Retourne la valeur si elle est encore valide
                return self.cached_data[key]
        return None
