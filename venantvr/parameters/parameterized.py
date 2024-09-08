from venantvr.parameters import Parameters


# noinspection PyPep8Naming
def Parameterized(base_name):
    """
    Crée une classe de base paramétrisée.

    Args:
        base_name (str): Le nom de la section dans le fichier de configuration YAML à utiliser pour initialiser la classe.

    Returns:
        class: Une classe de base qui, lorsqu'initialisée, charge les paramètres de configuration spécifiques à la clé fournie.
    """

    class Base:
        """
        Classe de base générée dynamiquement pour charger des paramètres de configuration spécifiques.

        Cette classe est conçue pour être utilisée comme une classe de base pour d'autres classes
        qui nécessitent un accès aux paramètres de configuration YAML sous une section spécifique.
        """

        def __init__(self):
            """
            Initialise une instance de la classe de base avec des paramètres de configuration.

            Charge les paramètres de configuration depuis le singleton parameters et
            extrait la section spécifique définie par base_name.
            """
            self.key = base_name  # Stocke le nom de la section
            self.get = Parameters.get_instance()  # Récupère l'instance singleton de parameters
            parameters = self.get.yaml  # Accède aux paramètres de configuration YAML
            self.section = parameters[self.key]  # Charge la section spécifique des paramètres

    return Base  # Retourne la classe de base générée dynamiquement
