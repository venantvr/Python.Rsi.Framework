from abc import abstractmethod


class GenericEvent(dict):
    """
    Classe de base abstraite représentant un événement générique.

    Cette classe hérite de `dict`, permettant aux instances d'être utilisées comme des dictionnaires
    pour stocker des paires clé-valeur représentant des attributs de l'événement.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialise une instance de GenericEvent en appelant le constructeur de la classe parent `dict`.

        Args:
            *args: Arguments positionnels passés au constructeur du dictionnaire.
            **kwargs: Arguments nommés passés au constructeur du dictionnaire.
        """
        super().__init__(*args, **kwargs)  # Appelle le constructeur de la classe `dict`

    @abstractmethod
    def to_string(self) -> str:
        """
        Méthode abstraite qui doit être implémentée par les sous-classes pour fournir
        une représentation sous forme de chaîne de l'événement.

        Returns:
            str: La représentation de l'événement sous forme de chaîne.
        """
        pass
