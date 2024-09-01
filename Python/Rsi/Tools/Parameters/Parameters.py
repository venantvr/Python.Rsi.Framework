import argparse
import os
import subprocess
from pathlib import Path

import yaml


class Parameters:
    """
    Classe singleton Parameters pour gérer la configuration d'un bot de trading.

    Cette classe utilise des fichiers de configuration YAML pour configurer le bot, y compris
    les paramètres de runtime, les journaux, la base de données et les tokens cibles. Elle
    supporte également la gestion des inclusions de fichiers YAML.
    """

    configuration_path = None
    script_path = None
    __instance = None
    yaml = {}

    @staticmethod
    def get_git_root(path):
        """
        Trouve le répertoire racine du dépôt git contenant le chemin spécifié.

        Args:
            path (str): Le chemin à partir duquel rechercher la racine du dépôt git.

        Returns:
            str or None: Le chemin vers le répertoire racine du dépôt git ou None si non trouvé.
        """
        try:
            # Exécutez la commande git pour obtenir le répertoire racine
            git_root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], cwd=path, text=True).strip()
            return git_root
        except subprocess.CalledProcessError:
            # Retourne None si le chemin n'est pas dans un dépôt git
            return None

    def __new__(cls):
        """
        Méthode spéciale pour implémenter le pattern singleton.

        Returns:
            Parameters: Une instance de la classe Parameters.
        """
        if cls.__instance is None:
            cls.__instance = super(Parameters, cls).__new__(cls)
            current_directory = os.getcwd()
            cls.script_path: str = str(cls.get_git_root(current_directory))
            # Analyse les arguments de ligne de commande
            parsed_args = Parameters.get().__parse_args()
            file, extension = os.path.splitext(parsed_args.configuration)

            # Détermine le fichier de configuration à utiliser
            if parsed_args.runtime in ['release', 'debug']:
                if os.path.exists(f'{file}-{parsed_args.runtime}{extension}'):
                    configuration_file = f'{file}-{parsed_args.runtime}{extension}'
                else:
                    configuration_file = f'{file}{extension}'
            else:
                configuration_file = f'{file}{extension}'

            # Configure le chemin des logs et assure que le répertoire existe
            log_path = os.path.join(parsed_args.logs, 'Python.Rsi.Bot')
            os.makedirs(log_path, exist_ok=True)

            cls.parsed_args = parsed_args
            cls.configuration_path = os.path.join(cls.script_path, configuration_file)
            cls.log_file = cls.__change_file_path(cls.configuration_path, log_path, '.log')
            cls.database = cls.__change_file_path(cls.configuration_path, log_path, '.db')

            # Ajouter le constructeur personnalisé à PyYAML
            yaml.add_constructor('!include', cls.__include_loader, Loader=yaml.FullLoader)
            # Charger le fichier de configuration principal
            cls.yaml = cls.__load_config(cls.configuration_path)
            # Charger le fichier de configuration des tokens
            target_tokens_yaml: str | bytes = os.path.join(cls.script_path, cls.yaml['bot']['pairs']['file'])
            target_tokens_configuration = cls.__load_config(target_tokens_yaml)
            cls.target_tokens_yaml = target_tokens_yaml
            cls.forbidden = target_tokens_configuration['forbidden']
            cls.port = parsed_args.port
        return cls.__instance

    @staticmethod
    def __change_file_path(file_path, new_directory, new_extension):
        """
        Change le répertoire et l'extension d'un chemin de fichier.

        Args:
            file_path (str): Chemin de fichier original.
            new_directory (str): Nouveau répertoire pour le fichier.
            new_extension (str): Nouvelle extension pour le fichier.

        Returns:
            str: Nouveau chemin de fichier avec le répertoire et l'extension modifiés.
        """
        # Convertit le chemin de fichier en objet Path
        path = Path(file_path)
        # Construit le nouveau chemin avec le nouveau répertoire et la nouvelle extension
        new_path = Path(new_directory) / path.with_suffix(new_extension).name
        return str(new_path)

    @staticmethod
    def __parse_args():
        """
        Analyse les arguments de ligne de commande.

        Returns:
            Namespace: Un objet Namespace contenant les arguments de ligne de commande analysés.
        """
        parser = argparse.ArgumentParser(description='Exemple de script avec paramètre...')
        parser.add_argument('configuration', type=str, help='Fichier de configuration YAML...')
        parser.add_argument('port', type=int, help='Port d\'écoute...')
        parser.add_argument('--runtime', type=str, help='Debug ou release...', default='release')
        parser.add_argument('--logs', type=str, help='Emplacement des logs...', default='/media/sdcard/')
        args = parser.parse_args()
        return args

    @classmethod
    def get(cls):
        """
        Retourne l'instance singleton de Parameters.

        Returns:
            Parameters: L'instance singleton de Parameters.
        """
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    @classmethod
    def dispose(cls):
        """
        Réinitialise l'instance singleton à None.
        """
        cls.__instance = None

    @classmethod
    def __include_loader(cls, loader, node):
        """
        Constructeur personnalisé pour gérer l'inclusion de fichiers YAML.

        Args:
            loader (Loader): Le chargeur YAML utilisé pour lire les fichiers.
            node (Node): Le nœud YAML qui contient le chemin du fichier à inclure.

        Returns:
            dict: Les données chargées à partir du fichier inclus.
        """
        # Obtenir le chemin du fichier à inclure
        file_name = os.path.join(os.path.dirname(loader.name), node.value)
        # Charger le contenu du fichier inclus
        with open(file_name, 'r') as f:
            return yaml.load(f, Loader=yaml.FullLoader)

    @classmethod
    def __load_config(cls, file_name):
        """
        Charge le fichier de configuration principal ou des tokens.

        Args:
            file_name (str): Le chemin du fichier de configuration à charger.

        Returns:
            dict: Le contenu du fichier de configuration.
        """
        with open(file_name, 'r') as f:
            return yaml.load(f, Loader=yaml.FullLoader)
