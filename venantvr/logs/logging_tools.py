from venantvr.parameters import Parameters


class LoggingTools:
    """
    Classe utilitaire LoggingTools pour gérer les paramètres de configuration du logging.

    Cette classe fournit des méthodes statiques pour accéder aux paramètres de journalisation
    définis dans un fichier de configuration YAML géré par l'instance singleton de `parameters`.

    ### Correspondance des noms (Ancien → Nouveau → Signification)
    | Ancien Nom                 | Nouveau Nom                        | Signification                                                   |
    |----------------------------|------------------------------------|-----------------------------------------------------------------|
    | `parameters.yaml`          | `configuration_values`             | Les paramètres chargés depuis le fichier YAML                   |
    | `parameters.log_file`      | `log_file_path`                    | Le chemin du fichier où les logs sont écrits                    |
    | `get_logging_settings`     | `retrieve_logging_configuration`   | Récupère les paramètres de configuration du logging             |
    """

    @staticmethod
    def retrieve_logging_configuration():
        """
        Récupère les paramètres de configuration du logging à partir du fichier YAML.

        Returns:
            tuple: Un tuple contenant:
                - enabled (bool): Un indicateur qui spécifie si le logging est activé.
                - log_file_path (str): Le chemin du fichier de log où les messages de journalisation doivent être enregistrés.
        """
        parameters = Parameters.get_instance()  # Récupère l'instance singleton de parameters
        configuration_values = parameters.yaml  # Accède aux paramètres de configuration YAML chargés
        # Retourne l'état d'activation du logging et le chemin du fichier de log
        return configuration_values['bot']['log']['enabled'], parameters.log_file
