import argparse
import os
import subprocess
from pathlib import Path

import yaml


class Parameters:
    """
    Classe singleton parameters pour gérer la configuration d'un bot de trading.

    Cette classe utilise des fichiers de configuration YAML pour configurer le bot, y compris
    les paramètres de runtime, les journaux, la base de données et les tokens cibles. Elle
    supporte également la gestion des inclusions de fichiers YAML.

    ### Correspondance des noms (Ancien → Nouveau → Signification)
    | Ancien Nom               | Nouveau Nom                      | Signification                                                  |
    |--------------------------|----------------------------------|----------------------------------------------------------------|
    | `get_git_root`           | `find_git_root_directory`        | Trouve le répertoire racine du dépôt git.                      |
    | `__new__`                | `__new__`                        | Implémente le pattern singleton pour créer une seule instance. |
    | `__change_file_path`     | `update_file_path_with_extension`| Change le chemin de fichier et l'extension.                    |
    | `__parse_args`           | `parse_command_line_arguments`   | Analyse les arguments de ligne de commande.                    |
    | `get`                    | `get_instance`                   | Retourne l'instance singleton de la classe parameters.         |
    | `dispose`                | `reset_singleton_instance`       | Réinitialise l'instance singleton à None.                      |
    | `__include_loader`       | `handle_yaml_file_inclusion`     | Gestion des inclusions de fichiers YAML dans la config.        |
    | `__load_config`          | `load_configuration_from_file`   | Charge le fichier de configuration principal ou des tokens.    |
    """

    configuration_path = None
    script_path = None
    singleton_instance = None
    yaml = {}

    @staticmethod
    def find_git_root_directory(path):
        """
        Trouve le répertoire racine du dépôt git contenant le chemin spécifié.

        Args:
            path (str): Le chemin à partir duquel rechercher la racine du dépôt git.

        Returns:
            str or None: Le chemin vers le répertoire racine du dépôt git ou None si non trouvé.
        """
        try:
            git_root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], cwd=path, text=True).strip()
            return git_root
        except subprocess.CalledProcessError:
            return None

    def __new__(cls):
        if cls.singleton_instance is None:
            cls.singleton_instance = super(Parameters, cls).__new__(cls)
            current_directory = os.getcwd()
            cls.script_path: str = str(cls.find_git_root_directory(current_directory))
            parsed_args = Parameters.get_instance().parse_command_line_arguments()
            file, extension = os.path.splitext(parsed_args.configuration)
            if parsed_args.runtime in ['release', 'debug']:
                if os.path.exists(f'{file}-{parsed_args.runtime}{extension}'):
                    configuration_file = f'{file}-{parsed_args.runtime}{extension}'
                else:
                    configuration_file = f'{file}{extension}'
            else:
                configuration_file = f'{file}{extension}'
            log_path = os.path.join(parsed_args.logs, 'Python.Rsi.Bot')
            os.makedirs(log_path, exist_ok=True)

            cls.parsed_args = parsed_args
            cls.configuration_path = os.path.join(cls.script_path, configuration_file)
            cls.log_file = cls.update_file_path_with_extension(cls.configuration_path, log_path, '.log')
            cls.database = cls.update_file_path_with_extension(cls.configuration_path, log_path, '.db')

            yaml.add_constructor('!include', cls.handle_yaml_file_inclusion, Loader=yaml.FullLoader)
            cls.yaml = cls.load_configuration_from_file(cls.configuration_path)
            target_tokens_yaml: str | bytes = os.path.join(cls.script_path, cls.yaml['bot']['pairs']['file'])
            target_tokens_configuration = cls.load_configuration_from_file(target_tokens_yaml)
            cls.target_tokens_yaml = target_tokens_yaml
            cls.forbidden = target_tokens_configuration['forbidden']
            cls.port = parsed_args.port
        return cls.singleton_instance

    @staticmethod
    def update_file_path_with_extension(file_path, new_directory, new_extension):
        """
        Change le répertoire et l'extension d'un chemin de fichier.

        Args:
            file_path (str): Chemin de fichier original.
            new_directory (str): Nouveau répertoire pour le fichier.
            new_extension (str): Nouvelle extension pour le fichier.

        Returns:
            str: Nouveau chemin de fichier avec le répertoire et l'extension modifiés.
        """
        path = Path(file_path)
        new_path = Path(new_directory) / path.with_suffix(new_extension).name
        return str(new_path)

    @staticmethod
    def parse_command_line_arguments():
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
    def get_instance(cls):
        """
        Retourne l'instance singleton de parameters.

        Returns:
            Parameters: L'instance singleton de parameters.
        """
        if cls.singleton_instance is None:
            cls.singleton_instance = cls()
        return cls.singleton_instance

    @classmethod
    def reset_singleton_instance(cls):
        """
        Réinitialise l'instance singleton à None.
        """
        cls.singleton_instance = None

    @classmethod
    def handle_yaml_file_inclusion(cls, loader, node):
        """
        Gestion des inclusions de fichiers YAML.

        Args:
            loader (Loader): Le chargeur YAML utilisé pour lire les fichiers.
            node (Node): Le nœud YAML qui contient le chemin du fichier à inclure.

        Returns:
            dict: Les données chargées à partir du fichier inclus.
        """
        file_name = os.path.join(os.path.dirname(loader.name), node.value)
        with open(file_name, 'r') as f:
            return yaml.load(f, Loader=yaml.FullLoader)

    @classmethod
    def load_configuration_from_file(cls, file_name):
        """
        Charge le fichier de configuration principal ou des tokens.

        Args:
            file_name (str): Le chemin du fichier de configuration à charger.

        Returns:
            dict: Le contenu du fichier de configuration.
        """
        with open(file_name, 'r') as f:
            return yaml.load(f, Loader=yaml.FullLoader)
