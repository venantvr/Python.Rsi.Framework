class Trigger:
    """
    Classe Trigger pour gérer un état activé/désactivé avec une fonctionnalité de réinitialisation.

    Cette classe permet de suivre un état binaire (activé ou désactivé) qui peut être réinitialisé automatiquement
    après avoir été consulté.
    """

    def __init__(self):
        """
        Initialise une nouvelle instance de Trigger avec l'état désactivé.
        """
        self.__activated = False  # Attribut privé pour stocker l'état activé/désactivé

    @property
    def forced(self):
        """
        Propriété pour obtenir l'état activé, puis réinitialiser l'état à désactivé.

        Returns:
            bool: La valeur actuelle de l'état activé avant la réinitialisation.
        """
        current_value = self.__activated  # Stocke la valeur actuelle de l'état
        self.__activated = False  # Réinitialise l'état à désactivé
        return current_value  # Retourne l'état avant la réinitialisation

    @forced.setter
    def forced(self, valeur):
        """
        Setter pour la propriété 'forced' permettant de définir l'état activé/désactivé.

        Args:
            valeur (bool): La nouvelle valeur pour l'état activé/désactivé.
        """
        self.__activated = valeur  # Met à jour l'état avec la nouvelle valeur fournie


"""
### Correspondance des noms (Ancien → Nouveau → Signification)
| Ancien Nom            | Nouveau Nom             | Signification                                                                |
|-----------------------|-------------------------|------------------------------------------------------------------------------|
| `__activated`         | `__activated`           | Variable privée pour stocker l'état activé ou désactivé de l'objet `Trigger` |
| `forced` (getter)     | `forced` (getter)       | Propriété pour obtenir l'état activé/désactivé puis réinitialiser l'état     |
| `forced` (setter)     | `forced` (setter)       | Propriété pour définir l'état activé ou désactivé                            |
"""
