import threading


class ThreadSafeDict:
    """
    Classe ThreadSafeDict fournissant un dictionnaire sécurisé pour les threads.

    Cette classe utilise un verrou (`Lock`) pour assurer que toutes les opérations de lecture et d'écriture
    sur le dictionnaire sont thread-safe.
    """

    def __init__(self):
        """
        Initialise une instance de ThreadSafeDict avec un dictionnaire vide et un verrou pour assurer la sécurité des threads.
        """
        self.lock = threading.Lock()  # Verrou pour synchroniser l'accès au dictionnaire
        self.dict = {}  # Dictionnaire interne pour stocker les données

    def set(self, key, value):
        """
        Ajoute ou met à jour une clé avec une valeur dans le dictionnaire de manière thread-safe.

        Paramètres :
        key : La clé à ajouter ou mettre à jour dans le dictionnaire.
        value : La valeur associée à la clé.
        """
        with self.lock:  # Acquiert le verrou avant d'accéder au dictionnaire
            self.dict[key] = value  # Met à jour la valeur associée à la clé

    def get(self, key):
        """
        Récupère la valeur associée à une clé dans le dictionnaire de manière thread-safe.

        Paramètres :
        key : La clé dont la valeur doit être récupérée.

        Retourne :
        La valeur associée à la clé, ou None si la clé n'existe pas.
        """
        with self.lock:  # Acquiert le verrou avant d'accéder au dictionnaire
            return self.dict.get(key)  # Récupère la valeur associée à la clé

    def remove(self, key):
        """
        Supprime une clé et sa valeur associée du dictionnaire de manière thread-safe.

        Paramètres :
        key : La clé à supprimer du dictionnaire.
        """
        with self.lock:  # Acquiert le verrou avant d'accéder au dictionnaire
            if key in self.dict:  # Vérifie si la clé existe dans le dictionnaire
                del self.dict[key]  # Supprime la clé et sa valeur associée

    def keys(self):
        """
        Retourne une liste de toutes les clés dans le dictionnaire de manière thread-safe.

        Retourne :
        list : Une liste de toutes les clés du dictionnaire.
        """
        with self.lock:  # Acquiert le verrou avant d'accéder au dictionnaire
            return list(self.dict.keys())  # Retourne une liste des clés

    def items(self):
        """
        Retourne une liste de toutes les paires clé-valeur dans le dictionnaire de manière thread-safe.

        Retourne :
        list : Une liste de toutes les paires clé-valeur du dictionnaire.
        """
        with self.lock:  # Acquiert le verrou avant d'accéder au dictionnaire
            return list(self.dict.items())  # Retourne une liste des paires clé-valeur

    def get_all(self):
        """
        Retourne une copie du dictionnaire entier de manière thread-safe.

        Retourne :
        dict : Une copie du dictionnaire interne.
        """
        with self.lock:  # Acquiert le verrou avant d'accéder au dictionnaire
            return dict(self.dict)  # Retourne une copie du dictionnaire
