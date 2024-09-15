import logging


class NoUrllib3Warning(logging.Filter):
    """
    Classe NoUrllib3Warning pour filtrer les messages de log provenant de la bibliothèque urllib3.

    Cette classe hérite de `logging.Filter` et est conçue pour filtrer les messages de log
    qui proviennent de la bibliothèque `urllib3`, empêchant ainsi leur affichage dans les logs.
    """

    def filter(self, record):
        """
        Filtre les messages de log en excluant ceux provenant de `urllib3`.

        Args:
            record (LogRecord): Un objet LogRecord représentant un événement de log.

        Returns:
            bool: False si le message de log provient de `urllib3`, True sinon.
        """
        # Vérifie si le nom du logger (record.name) commence par 'urllib3'
        return not record.name.startswith('urllib3')
