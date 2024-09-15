import os
import time
from datetime import datetime, timezone
from logging.handlers import TimedRotatingFileHandler


class RotatingLogger(TimedRotatingFileHandler):
    """
    Sous-classe de TimedRotatingFileHandler pour gérer la rotation des fichiers de log avec un préfixe de date.

    Cette classe étend `TimedRotatingFileHandler` pour ajouter un préfixe de date (au format 'YYYY-MM-DD-')
    au nom des fichiers de log lors de la rotation. Cela permet une meilleure gestion des fichiers de log
    avec une indication claire de la date d'enregistrement des logs.
    """

    def __init__(self, filename, when, interval, backup_count=0, encoding=None, delay=False, utc=False, at_time=None):
        """
        Initialise une nouvelle instance de RotatingLogger.

        Args:
            filename (str): Le nom de base du fichier de log.
            when (str): Chaîne qui spécifie la fréquence de rotation ('S', 'M', 'H', 'D', 'W0'-'W6', 'midnight').
            interval (int): L'intervalle de temps entre les rotations.
            backup_count (int): Le nombre de fichiers de sauvegarde à conserver.
            encoding (str, optional): L'encodage du fichier de log.
            delay (bool): Si True, le fichier de log est ouvert lors de la première écriture.
            utc (bool): Si True, utilise l'heure UTC pour la gestion du temps.
            at_time (datetime.time, optional): Si spécifié, la rotation a lieu à cette heure.
        """
        # Sépare le répertoire et le nom de fichier du chemin donné
        self.dir_log, self.file_name = os.path.split(filename)
        self.prefix = None  # Initialise le préfixe à None
        filename = self.compute_filename()  # Calcule le nom de fichier avec préfixe de date
        # Appelle le constructeur de la classe parente avec le nouveau nom de fichier
        super(RotatingLogger, self).__init__(
            os.path.join(self.dir_log, filename), when, interval, backup_count, encoding, delay, utc, at_time
        )

    def compute_filename(self):
        """
        Calcule le nom de fichier pour le fichier de log actuel, en ajoutant un préfixe de date.

        Returns:
            str: Le nom de fichier modifié avec le préfixe de date.
        """
        # Ajoute la date actuelle (format 'YYYY-MM-DD-') comme préfixe au nom du fichier
        self.prefix = datetime.now(timezone.utc).strftime('%Y-%m-%d-')
        filename = self.prefix + self.file_name
        return filename

    def doRollover(self):
        """
        Effectue la rotation des fichiers de log.

        Cette méthode génère un nouveau nom de fichier pour le fichier de log archivé,
        ajoute le préfixe de date, ferme le fichier actuel, et ouvre un nouveau fichier
        pour la suite de l'enregistrement des logs.
        """
        if self.stream:
            self.stream.close()  # Ferme le fichier de log actuel
            self.stream = None  # Réinitialise le flux de log

        # Construit un nouveau nom de fichier avec la date actuelle
        current_time = int(time.time())
        filename = self.compute_filename()
        self.baseFilename = os.path.join(self.dir_log, filename)

        # Supprime les anciens fichiers de log s'il y a des fichiers de sauvegarde à gérer
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)

        # Ouvre un nouveau fichier de log si le mode différé n'est pas activé
        if not self.delay:
            self.stream = self._open()

        # Calcule le moment de la prochaine rotation
        new_rollover_at = self.computeRollover(current_time)
        while new_rollover_at <= current_time:
            new_rollover_at += self.interval
        self.rolloverAt = new_rollover_at
