import threading


class ThreadSafeDict:
    """
    Classe ThreadSafeDict fournissant un dictionnaire sécurisé pour les threads.

    Cette classe utilise un verrou (`Lock`) pour assurer que toutes les opérations de lecture et d'écriture
    sur le dictionnaire sont thread-safe.

    ### Correspondance des noms (Ancien → Nouveau → Signification)
    | Ancien Nom      | Nouveau Nom                | Signification                                                   |
    |-----------------|----------------------------|-----------------------------------------------------------------|
    | `self.lock`     | `thread_safety_lock`       | Verrou pour synchroniser l'accès au dictionnaire                |
    | `self.dict`     | `thread_safe_dictionary`   | Dictionnaire interne utilisé pour stocker les données           |
    | `set`           | `add_or_update_entry`      | Ajoute ou met à jour une entrée dans le dictionnaire            |
    | `get`           | `retrieve_entry`           | Récupère une valeur associée à une clé                          |
    | `remove`        | `delete_entry`             | Supprime une clé et sa valeur associée                          |
    | `keys`          | `retrieve_all_keys`        | Récupère toutes les clés présentes dans le dictionnaire         |
    | `items`         | `retrieve_all_items`       | Récupère toutes les paires clé-valeur dans le dictionnaire      |
    | `get_all`       | `retrieve_copy_of_dict`    | Retourne une copie du dictionnaire complet                      |
    """

    def __init__(self):
        """
        Initialise une instance de ThreadSafeDict avec un dictionnaire vide et un verrou pour assurer la sécurité des threads.
        """
        self.thread_safety_lock = threading.Lock()  # Verrou pour synchroniser l'accès au dictionnaire
        self.thread_safe_dictionary = {}  # Dictionnaire interne pour stocker les données

    def add_or_update_entry(self, key, value):
        """
        Ajoute ou met à jour une clé avec une valeur dans le dictionnaire de manière thread-safe.

        Paramètres :
        key : La clé à ajouter ou mettre à jour dans le dictionnaire.
        value : La valeur associée à la clé.
        """
        with self.thread_safety_lock:  # Acquiert le verrou avant d'accéder au dictionnaire
            self.thread_safe_dictionary[key] = value  # Met à jour la valeur associée à la clé

    def retrieve_entry(self, key):
        """
        Récupère la valeur associée à une clé dans le dictionnaire de manière thread-safe.

        Paramètres :
        key : La clé dont la valeur doit être récupérée.

        Retourne :
        La valeur associée à la clé, ou None si la clé n'existe pas.
        """
        with self.thread_safety_lock:  # Acquiert le verrou avant d'accéder au dictionnaire
            return self.thread_safe_dictionary.get(key)  # Récupère la valeur associée à la clé

    def delete_entry(self, key):
        """
        Supprime une clé et sa valeur associée du dictionnaire de manière thread-safe.

        Paramètres :
        key : La clé à supprimer du dictionnaire.
        """
        with self.thread_safety_lock:  # Acquiert le verrou avant d'accéder au dictionnaire
            if key in self.thread_safe_dictionary:  # Vérifie si la clé existe dans le dictionnaire
                del self.thread_safe_dictionary[key]  # Supprime la clé et sa valeur associée

    def retrieve_all_keys(self):
        """
        Retourne une liste de toutes les clés dans le dictionnaire de manière thread-safe.

        Retourne :
        list : Une liste de toutes les clés du dictionnaire.
        """
        with self.thread_safety_lock:  # Acquiert le verrou avant d'accéder au dictionnaire
            return list(self.thread_safe_dictionary.keys())  # Retourne une liste des clés

    def retrieve_all_items(self):
        """
        Retourne une liste de toutes les paires clé-valeur dans le dictionnaire de manière thread-safe.

        Retourne :
        list : Une liste de toutes les paires clé-valeur du dictionnaire.
        """
        with self.thread_safety_lock:  # Acquiert le verrou avant d'accéder au dictionnaire
            return list(self.thread_safe_dictionary.items())  # Retourne une liste des paires clé-valeur

    def retrieve_copy_of_dict(self):
        """
        Retourne une copie du dictionnaire entier de manière thread-safe.

        Retourne :
        dict : Une copie du dictionnaire interne.
        """
        with self.thread_safety_lock:  # Acquiert le verrou avant d'accéder au dictionnaire
            return dict(self.thread_safe_dictionary)  # Retourne une copie du dictionnaire
