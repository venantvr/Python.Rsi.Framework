import threading
from concurrent.futures import ThreadPoolExecutor


class BotThreadPoolExecutor:
    """
    Classe BotThreadPoolExecutor implémentant un ThreadPoolExecutor sous forme de singleton.

    Cette classe permet de gérer un pool de threads pour l'exécution de tâches asynchrones tout en garantissant
    qu'une seule instance de ThreadPoolExecutor est utilisée dans l'application (singleton).
    """

    __instance = None  # Variable de classe pour stocker l'instance unique
    __lock = threading.Lock()  # Verrou pour assurer une création d'instance thread-safe

    def __new__(cls, *args, **kwargs):
        """
        Méthode spéciale __new__ pour créer une instance de la classe. Elle garantit que seule une instance
        de BotThreadPoolExecutor est créée (implémentation du singleton).

        Retourne :
        instance (BotThreadPoolExecutor) : L'instance unique de la classe.
        """
        if not cls.__instance:
            with cls.__lock:  # Assure que la création de l'instance est thread-safe
                if not cls.__instance:  # Double vérification pour s'assurer qu'aucune autre instance n'a été créée
                    cls.__instance = super(BotThreadPoolExecutor, cls).__new__(cls)
        return cls.__instance

    def __init__(self, max_workers=None):
        """
        Initialise l'instance de BotThreadPoolExecutor. Si l'instance est déjà initialisée,
        elle ne refait pas l'initialisation pour éviter de recréer le ThreadPoolExecutor.

        Paramètres :
        max_workers (int, optionnel) : Le nombre maximum de threads à utiliser dans le pool.
        """
        if not hasattr(self, 'executor'):
            # Initialise un ThreadPoolExecutor avec le nombre maximum de threads spécifié
            self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def submit(self, func, *args, **kwargs):
        """
        Soumet une fonction à exécuter dans le pool de threads.

        Paramètres :
        func (callable) : La fonction à exécuter.
        *args : Arguments positionnels pour la fonction.
        **kwargs : Arguments nommés pour la fonction.

        Retourne :
        Future : Un objet Future représentant l'exécution asynchrone de la fonction.
        """
        return self.executor.submit(func, *args, **kwargs)

    def map(self, func, *iterables, timeout=None, chunksize=1):
        """
        Applique une fonction à chaque élément d'un ou plusieurs itérables, de manière concurrente.

        Paramètres :
        func (callable) : La fonction à appliquer.
        *iterables : Itérables à traiter.
        timeout (float, optionnel) : Temps maximum d'attente pour que toutes les futures soient complétées.
        chunksize (int, optionnel) : Taille des chunks pour le dispatch des tâches dans le pool de threads.

        Retourne :
        iterator : Un itérateur des résultats.
        """
        return self.executor.map(func, *iterables, timeout=timeout, chunksize=chunksize)

    def shutdown(self, wait=True):
        """
        Arrête le pool de threads, empêchant toute nouvelle tâche d'être soumise.

        Paramètres :
        wait (bool, optionnel) : Si True, attend que toutes les tâches en cours soient terminées avant de fermer.
        """
        self.executor.shutdown(wait=wait)
