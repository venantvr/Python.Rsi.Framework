import logging
import subprocess
import threading
import traceback
import uuid
import warnings
from functools import wraps
from hashlib import md5

from venantvr.logs.currency_logger import CurrencyLogger
from venantvr.logs.logging_tools import LoggingTools
from venantvr.logs.no_deprecation_warning import NoDeprecationWarning
from venantvr.logs.no_urllib3_warning import NoUrllib3Warning
from venantvr.logs.rotating_logger import RotatingLogger

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


def code_configuration():
    """
    Génère un code de configuration unique basé sur l'adresse MAC de la machine.

    Returns:
        str: Un hachage MD5 tronqué de l'adresse MAC.
    """
    mac_address = hex(uuid.getnode()).replace('0x', '').upper()
    mac_address = ':'.join(mac_address[i:i + 2] for i in range(0, 11, 2))
    return md5(mac_address.encode('utf-8')).hexdigest().upper()[:2]


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
logger = logging.getLogger(__name__)
logger.addFilter(NoUrllib3Warning())
logger.addFilter(NoDeprecationWarning())
