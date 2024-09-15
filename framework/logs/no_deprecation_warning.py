import logging


class NoDeprecationWarning(logging.Filter):
    """
    Classe NoDeprecationWarning pour filtrer les messages de log de type DeprecationWarning.

    Cette classe hérite de `logging.Filter` et est conçue pour filtrer les messages de log
    qui contiennent des avertissements de dépréciation (DeprecationWarning), empêchant ainsi
    leur affichage dans les logs.
    """

    def filter(self, record):
        """
        Filtre les messages de log en excluant ceux contenant un DeprecationWarning.

        Args:
            record (LogRecord): Un objet LogRecord représentant un événement de log.

        Returns:
            bool: False si le message de log est un DeprecationWarning, True sinon.
        """
        if record.args:  # Vérifie si record.args contient au moins un élément
            # Retourne False si le premier argument est une instance de DeprecationWarning, sinon True
            return not isinstance(record.args[0], DeprecationWarning)
        else:
            return True  # Si record.args est vide, laisse passer le log
