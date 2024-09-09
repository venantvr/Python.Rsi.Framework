from venantvr.business.bot_currency_pair import BotCurrencyPair
from venantvr.logs.logs_utils import logger
from venantvr.parameters.parameterized import Parameterized


class SecurityWait(Parameterized('bot')):
    """
    Classe SecurityWait pour gérer la file d'attente de sécurité des paires de devises.

    Cette classe hérite d'une classe de base générée dynamiquement par la fonction Parameterized,
    qui charge les paramètres de configuration pour le bot à partir de la section 'bot' du fichier de configuration.
    Elle est utilisée pour gérer les paires de devises en attente dans un système de trading, avec une logique
    de swap pour déterminer quand la file d'attente est remplie.

    Attributs:
        currency_pairs (list): Liste des identifiants des paires de devises actuellement en attente.
        currency_pairs_before_swap (int): Nombre de paires de devises avant de déclencher un swap.

    Méthodes:
        add(currency_pair: BotCurrencyPair): Ajoute une paire de devises à la file d'attente de sécurité.
        is_over(debug=False): Vérifie si la file d'attente est remplie selon les paramètres configurés.

    ### Correspondance des noms (Ancien → Nouveau → Signification)
    | Ancien Nom                   | Nouveau Nom                  | Signification                                                 |
    |------------------------------|------------------------------|---------------------------------------------------------------|
    | `currency_pairs`             | `currency_pairs`             | Liste des identifiants des paires de devises en attente       |
    | `currency_pairs_before_swap` | `currency_pairs_before_swap` | Nombre de paires avant de déclencher un swap                  |
    | `add`                        | `add`                        | Ajoute une paire de devises à la liste d'attente              |
    | `is_over`                    | `is_over`                    | Détermine si la liste des devises en attente est remplie      |
    """

    def __init__(self):
        """
        Initialise une instance de SecurityWait avec les paramètres de configuration chargés.

        Attributs:
            currency_pairs (list): Liste des identifiants des paires de devises actuellement en attente.
            currency_pairs_before_swap (int): Nombre de paires de devises avant de déclencher un swap.
        """
        super().__init__()
        self.currency_pairs = []  # Initialisation de la liste des paires de devises
        self.currency_pairs_before_swap = self.section['wait']['swaps']  # Nombre de swaps avant un changement

    def add(self, currency_pair: BotCurrencyPair):
        """
        Ajoute une paire de devises à la file d'attente de sécurité.

        Args:
            currency_pair (BotCurrencyPair): La paire de devises à ajouter.

        Returns:
            SecurityWait: L'instance actuelle de SecurityWait (pour le chaînage des appels).
        """
        logger.debug('Ajout de la paire de devises cible à la file d\'attente de sécurité')
        self.currency_pairs.append(currency_pair.id)  # Ajout de l'ID de la paire de devises à la liste
        return self

    def is_over(self, debug=False):
        """
        Détermine si la file d'attente de sécurité est remplie, en fonction du nombre de swaps configuré.

        Args:
            debug (bool): Si True, retourne toujours True pour des fins de débogage.

        Returns:
            bool: True si la file d'attente est remplie ou si le mode débogage est activé, False sinon.
        """
        if debug:
            output = True  # Retourne toujours True en mode débogage
        else:
            unique = set(self.currency_pairs)  # Convertit la liste des paires en un ensemble unique
            output = len(unique) > self.currency_pairs_before_swap  # Vérifie si le nombre de paires uniques dépasse le seuil
        return output
