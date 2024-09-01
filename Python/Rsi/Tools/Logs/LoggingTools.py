from Python.Rsi.Tools.Parameters import Parameters


class LoggingTools:
    """
    Classe utilitaire LoggingTools pour gérer les paramètres de configuration du logging.

    Cette classe fournit des méthodes statiques pour accéder aux paramètres de journalisation
    définis dans un fichier de configuration YAML géré par l'instance singleton de `Parameters`.
    """

    @staticmethod
    def get_logging_settings():
        """
        Récupère les paramètres de configuration du logging à partir du fichier YAML.

        Returns:
            tuple: Un tuple contenant:
                - enabled (bool): Un indicateur qui spécifie si le logging est activé.
                - log_file (str): Le chemin du fichier de log où les messages de journalisation doivent être enregistrés.
        """
        parameters = Parameters.get()  # Récupère l'instance singleton de Parameters
        values = parameters.yaml  # Accède aux paramètres de configuration YAML chargés
        # Retourne l'état d'activation du logging et le chemin du fichier de log
        return values['bot']['log']['enabled'], parameters.log_file
