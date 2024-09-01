from functools import wraps


class DoOnce:
    """
    Classe DoOnce utilisée comme un décorateur pour exécuter une fonction ou une méthode une seule fois.
    """

    def __init__(self, func):
        """
        Initialise l'instance de DoOnce.

        Paramètres :
        func (callable) : La fonction à exécuter une seule fois.
        """
        self.func = func  # La fonction qui sera décorée
        self.has_run = False  # Indicateur pour vérifier si la fonction a déjà été exécutée

    def __call__(self, *args, **kwargs):
        """
        Appelle la fonction décorée une seule fois. Si la fonction a déjà été exécutée, elle ne fait rien.

        Paramètres :
        *args : Arguments positionnels à passer à la fonction.
        **kwargs : Arguments nommés à passer à la fonction.

        Retourne :
        Le résultat de la fonction si elle est exécutée, sinon None.
        """
        if not self.has_run:
            self.has_run = True  # Marque la fonction comme exécutée
            return self.func(*args, **kwargs)  # Appelle la fonction décorée


def do_once_decorator(method):
    """
    Décorateur de méthode pour assurer que la méthode est exécutée une seule fois par instance de classe.

    Paramètres :
    method (callable) : La méthode à exécuter une seule fois.

    Retourne :
    callable : Une fonction wrapper qui gère l'exécution unique de la méthode.
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        # Initialise un attribut _do_once_flag pour l'instance si non présent
        if not hasattr(self, '_do_once_flag'):
            self._do_once_flag = {}

        # Vérifie si la méthode a déjà été exécutée
        if method.__name__ not in self._do_once_flag:
            self._do_once_flag[method.__name__] = True  # Marque la méthode comme exécutée
            return method(self, *args, **kwargs)  # Appelle la méthode

    return wrapper
