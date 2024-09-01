class Response:
    """
    Classe Response pour gérer et manipuler les données de réponse.

    Cette classe fournit des méthodes pour stocker, mettre à jour, récupérer, et manipuler
    les données de réponse sous forme de dictionnaire.
    """

    def __init__(self):
        """
        Initialise une nouvelle instance de Response avec un dictionnaire vide pour les données de réponse.
        """
        self.__response = {}  # Attribut privé pour stocker les données de réponse

    def refresh(self, response: dict):
        """
        Met à jour les données de réponse avec un nouveau dictionnaire.

        Args:
            response (dict): Le nouveau dictionnaire contenant les données de réponse à stocker.
        """
        self.__response = response  # Met à jour les données de réponse

    def retrieve(self):
        """
        Récupère les données de réponse actuelles.

        Returns:
            dict: Le dictionnaire actuel des données de réponse.
        """
        return self.__response  # Retourne les données de réponse actuelles

    def common_targets(self, response: dict):
        """
        Calcule l'intersection des cibles actuelles et des nouvelles cibles fournies dans le dictionnaire de réponse.

        Args:
            response (dict): Le dictionnaire contenant les nouvelles données de réponse.

        Returns:
            list: Une liste des cibles communes trouvées dans l'intersection.
        """
        # Calcule l'intersection des cibles actuelles et des nouvelles cibles
        intersection = list(set(response.get('targets', [])))
        self.refresh(response)  # Met à jour les données de réponse avec les nouvelles données
        return intersection  # Retourne l'intersection des cibles
