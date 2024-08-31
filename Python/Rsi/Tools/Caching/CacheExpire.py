import time


class CacheExpire:
    def __init__(self):
        self.cache = {}
        self.expire_times = {}

    def set(self, key, value, expire_in_seconds: int):
        if expire_in_seconds > time.time():
            # noinspection PyUnusedLocal
            error = True
        self.cache[key] = value
        # Définir le moment d'expiration pour la clé, en fonction du temps d'expiration spécifié
        self.expire_times[key] = time.time() + expire_in_seconds

    def get(self, key):
        if key in self.cache:
            # Vérifier si la clé a expiré
            if time.time() >= self.expire_times[key]:
                # Supprimer la clé du cache si elle a expiré
                del self.cache[key]
                del self.expire_times[key]
                return None
            else:
                return self.cache[key]
        return None
