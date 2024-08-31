import threading


class ThreadSafeDict:
    def __init__(self):
        self.lock = threading.Lock()
        self.dict = {}

    def set(self, key, value):
        with self.lock:
            self.dict[key] = value

    def get(self, key):
        with self.lock:
            return self.dict.get(key)

    def remove(self, key):
        with self.lock:
            if key in self.dict:
                del self.dict[key]

    def keys(self):
        with self.lock:
            return list(self.dict.keys())  # Retourne une liste des clés

    def items(self):
        with self.lock:
            return list(self.dict.items())  # Retourne une liste des paires clé-valeur

    def get_all(self):
        with self.lock:
            return dict(self.dict)  # Retourne une copie du dictionnaire
