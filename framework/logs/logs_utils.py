import logging
import subprocess
import threading
import traceback
import warnings
from functools import wraps

from framework.logs.currency_logger import CurrencyLogger
from framework.logs.no_deprecation_warning import NoDeprecationWarning
from framework.logs.no_urllib3_warning import NoUrllib3Warning
from framework.logs.rotating_logger import RotatingLogger
from framework.parameters.parameters import Parameters


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


# Ignorer tous les DeprecationWarning
warnings.filterwarnings('ignore', category=DeprecationWarning)


def log_exception_info(exc_type, exc_value, tb):
    """
    Formatte et log l'exception et la stack d'appels avec logger.error.

    Args:
        exc_type (Type[BaseException]): Le type de l'exception.
        exc_value (BaseException): L'instance de l'exception.
        tb (TracebackType): La trace de l'exception.
    """
    tb_str = ''.join(traceback.format_exception(exc_type, exc_value, tb))
    logger.error('Exception caught:\nType: %s\nValue: %s\nStack trace:\n%s', exc_type, exc_value, tb_str)


def log_exception_error(exc_type, exc_value, tb):
    """
    Formatte et log l'exception et la stack d'appels avec logger.error.

    Args:
        exc_type (Type[BaseException]): Le type de l'exception.
        exc_value (BaseException): L'instance de l'exception.
        tb (TracebackType): La trace de l'exception.
    """
    tb_str = ''.join(traceback.format_exception(exc_type, exc_value, tb))
    logger.error('Exception caught:\nType: %s\nValue: %s\nStack trace:\n%s', exc_type, exc_value, tb_str)


def log_thread_activity(func):
    """
    Décorateur pour log l'activité d'un thread, incluant le début et la fin de l'exécution de la fonction.

    Args:
        func (Callable): La fonction à décorer.

    Returns:
        Callable: La fonction décorée avec l'ajout du log.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        class_name = ''
        if args:  # Vérifie que args n'est pas vide
            if hasattr(args[0], '__class__'):
                class_name = args[0].__class__.__name__

        log = class_name not in ['WallStreetCron', 'MarketsCron']
        if log:
            logging.warning(f'Le thread {threading.current_thread().name} ({threading.current_thread().ident}) démarre {class_name}.{func.__name__}')

        result = func(*args, **kwargs)

        if log:
            logging.warning(f'Le thread {threading.current_thread().name} ({threading.current_thread().ident}) termine {class_name}.{func.__name__}')

        return result

    return wrapper


def get_wifi_name():
    """
    Récupère le nom du réseau Wi-Fi auquel la machine est connectée.

    Returns:
        str: Le nom du réseau Wi-Fi ou un message indiquant qu'aucun réseau n'est connecté.
    """
    try:
        wifi_name = subprocess.check_output(['iwgetid', '-r']).decode().strip()
        return wifi_name if wifi_name else 'Non connecté à un réseau Wi-Fi'
    except subprocess.CalledProcessError:
        return 'Non connecté à un réseau Wi-Fi ou commande non disponible'


# Obtient les paramètres de configuration de logging
enabled, file = LoggingTools.retrieve_logging_configuration()

if not enabled:
    logging_exceptions = logging.CRITICAL + 1
    logging_level = logging.CRITICAL + 1
else:
    logging_exceptions = logging.WARNING
    logging_level = logging.WARNING

# Définit la classe de logger par défaut
logging.setLoggerClass(CurrencyLogger)

# Configure les niveaux de log pour certaines bibliothèques pour ignorer leurs messages
logging.getLogger('urllib3').setLevel(logging_exceptions)
logging.getLogger('urllib3.connectionpool').setLevel(logging_exceptions)
logging.getLogger('werkzeug').setLevel(logging_exceptions)

if enabled and file != '':
    logging.basicConfig(level=logging_level,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[
                            RotatingLogger(filename=file, when='midnight', interval=1, backup_count=5),
                            logging.StreamHandler()
                        ])

# Crée une instance de logger
# noinspection PyTypeChecker
logger: CurrencyLogger = logging.getLogger(__name__)
logger.addFilter(NoUrllib3Warning())
logger.addFilter(NoDeprecationWarning())
