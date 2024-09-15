import calendar
import math
import os
import re
import socket
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import numpy as np
# noinspection PyUnresolvedReferences
import psutil
from pandas import DataFrame

from venantvr.quotes.price import Price
from venantvr.types.types_alias import GateioTimeFrame, PandasTimeFrame, NumberOrPrice


def convert_gateio_timeframe_to_pandas(timeframe: GateioTimeFrame) -> PandasTimeFrame:
    """
    Convertit un timeframe donné en chaîne de période pour resampling avec pandas.

    Args:
        timeframe (GateioTimeFrame): Le timeframe à convertir (ex. '1h', '30m', '1d').

    Returns:
        PandasTimeFrame: La chaîne de période correspondante pour utilisation avec pandas.resample().
    """
    # Dictionnaire de correspondance entre les unités de temps et les alias pandas
    unit_mapping = {'h': 'h', 'm': 'T', 'd': 'D'}

    # Extraction de la quantité et de l'unité du timeframe
    quantity = ''.join([char for char in timeframe if char.isdigit()])  # Quantité (ex. 1, 30)
    unit = ''.join([char for char in timeframe if char.isalpha()]).lower()  # Unité ('h', 'm', 'd')

    # Conversion de l'unité en alias pandas
    pandas_alias = unit_mapping.get(unit, None)

    if pandas_alias is None:
        raise ValueError(f'Unité de temps non reconnue {unit}')

    return PandasTimeFrame(quantity + pandas_alias)  # Retourne le timeframe pour pandas


def resolve_path_json_pairs(script_path, file_name):
    """
    Résout le chemin d'un fichier JSON en vérifiant s'il existe déjà.

    Paramètres :
    script_path (str) : Le chemin du script en cours d'exécution.
    file_name (str) : Le nom du fichier à vérifier.

    Retourne :
    str : Le chemin complet du fichier s'il n'existe pas déjà, sinon le chemin du fichier existant.
    """
    if not os.path.exists(file_name):
        return os.path.join(script_path, file_name)  # Retourne le chemin complet si le fichier n'existe pas
    else:
        return file_name  # Retourne le chemin du fichier s'il existe déjà


# noinspection PyUnusedLocal
def verify_pair(chaine):
    """
    Vérifie si une chaîne de caractères correspond à un motif de paire de devises avec 'USDT'.

    Paramètres :
    chaine (str) : La chaîne à vérifier.

    Retourne :
    bool : True si la chaîne correspond au motif, False sinon.
    """
    motif = r'^.*/USDT$'
    return bool(re.match(motif, chaine))  # Vérifie si la chaîne se termine par '/USDT'


def day_of_week():
    """
    Retourne le nom du jour de la semaine en cours (en anglais).

    Retourne :
    str : Le nom du jour de la semaine actuelle.
    """
    days_of_the_week = list(calendar.day_name)  # Liste des noms des jours de la semaine
    current_day_number = datetime.now(timezone.utc).weekday()  # Numéro du jour actuel
    return days_of_the_week[current_day_number]  # Retourne le nom du jour de la semaine


def convert_utc_to_local(heure_utc_str, fuseau_horaire_local_str):
    """
    Convertit une heure UTC donnée en format hh:mm en heure locale pour un fuseau horaire spécifié.

    Paramètres :
    heure_utc_str (str) : Heure UTC en format hh:mm comme chaîne de caractères.
    fuseau_horaire_local_str (str) : Identifiant du fuseau horaire local (ex. 'Europe/Paris').

    Retourne :
    str : Heure locale en format hh:mm.
    """
    # Convertir la chaîne en objet datetime, en assumant la date actuelle pour UTC
    heure_utc = datetime.strptime(heure_utc_str, '%H:%M').replace(tzinfo=timezone.utc)

    # Convertir en fuseau horaire local
    fuseau_horaire_local = ZoneInfo(fuseau_horaire_local_str)
    heure_locale = heure_utc.astimezone(fuseau_horaire_local)

    # Retourner l'heure locale en format hh:mm
    return heure_locale.strftime('%H:%M')


def get_ip_address():
    """
    Récupère l'adresse IP de l'interface réseau active non locale.

    Retourne :
    str : L'adresse IP de l'interface réseau active, ou 'Non disponible' si aucune n'est trouvée.
    """
    for interface, addrs in psutil.net_if_addrs().items():
        if interface == 'lo' or interface.startswith('lo'):
            continue  # Ignore les interfaces locales

        for addr in addrs:
            if addr.family == socket.AF_INET:
                if psutil.net_if_stats()[interface].isup:
                    return addr.address  # Retourne l'adresse IP si l'interface est active

    return 'Non disponible'


def serialize_class_reference(class_reference):
    """
    Retourne une représentation en chaîne du nom complet de la classe.

    Paramètres :
    class_reference (type) : La référence de la classe à sérialiser.

    Retourne :
    str : Le nom de la classe sous forme de chaîne.
    """
    name: str = class_reference.__name__
    return f'{name.split(".")[-1]}'


def deserialize_class_reference(full_class_name):
    """
    Résout une chaîne de nom de classe en une référence de classe.

    Paramètres :
    full_class_name (str) : Le nom complet de la classe sous forme de chaîne.

    Retourne :
    type : La référence de la classe.
    """
    module_name, class_name = full_class_name.rsplit('.', 1)
    module = __import__(module_name, fromlist=[class_name])
    return getattr(module, class_name)


def default_converter(obj):
    """
    Convertit les types non sérialisables pour le JSON.

    Paramètres :
    obj : L'objet à convertir.

    Retourne :
    bool : La valeur booléenne si l'objet est de type np.bool_.

    Lève :
    TypeError : Si l'objet n'est pas sérialisable en JSON.
    """
    if isinstance(obj, np.bool_):
        return bool(obj)
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')


def get_missing_files(file_paths_dict):
    """
    Identifie les fichiers qui n'existent pas dans un dictionnaire donné.

    Paramètres :
    file_paths_dict (dict) : Un dictionnaire où les clés sont des identifiants (comme des noms)
                             et les valeurs sont les chemins de fichiers correspondants.

    Retourne :
    list : Une liste de tuples, chaque tuple contenant la clé et le chemin d'un fichier
           qui n'existe pas sur le système de fichiers.
    """
    output = []  # Initialise une liste vide pour stocker les résultats

    # Parcourt le dictionnaire d'entrée contenant les chemins de fichiers
    for key, path in file_paths_dict.items():
        # Vérifie si le fichier à l'emplacement spécifié n'existe pas
        if not file_exists(path):
            # Ajoute un tuple (clé, chemin) à la liste de sortie si le fichier n'existe pas
            output.append((key, path))

    # Renvoie la liste des fichiers non existants avec leurs clés correspondantes
    return output


def list_diff(list_a: list, list_b: list) -> list:
    """
    Retourne une nouvelle liste contenant tous les éléments de list_a qui ne sont pas présents dans list_b.

    Paramètres :
    list_a (list) : La liste à partir de laquelle les éléments seront soustraits.
    list_b (list) : La liste des éléments à soustraire de list_a.

    Retourne :
    list : Une liste contenant les éléments uniques à list_a.
    """
    # Utiliser la compréhension de liste pour filtrer les éléments
    return [item for item in list_a if item not in list_b]


def file_exists(filepath: str, factor: int = 10) -> bool:
    """
    Vérifie si un fichier existe et a été modifié dans les dernières '24 * facteur' heures.
    Si le fichier est plus ancien, il sera supprimé.

    Paramètres :
    filepath (str) : Le chemin vers le fichier à vérifier.
    factor (int) : Le facteur multiplicatif pour définir l'âge limite du fichier en heures (par défaut 10).

    Retourne :
    bool : True si le fichier existe et a été modifié il y a moins de '24 * facteur' heures, False sinon.
    """
    output = False

    if os.path.exists(filepath):  # Vérifie si le fichier existe
        last_modified = os.path.getmtime(filepath)  # Obtient le temps de dernière modification du fichier
        current_time = time.time()  # Obtient le temps actuel
        time_difference = current_time - last_modified  # Calcule la différence de temps

        # Convertit la différence de temps en heures
        hours_difference = time_difference / 3600

        if hours_difference < 24 * factor:  # Vérifie si le fichier a été modifié dans la période limite
            output = True
        else:
            # Supprime le fichier s'il est plus vieux que la période limite
            os.remove(filepath)

    return output


def round_up(value, decimals=4):
    """
    Arrondit une valeur à la hausse à un certain nombre de décimales.

    Args:
        value (float): La valeur à arrondir.
        decimals (int, optional): Le nombre de décimales (par défaut 4).

    Returns:
        float: La valeur arrondie à la hausse.
    """
    factor = 10 ** decimals
    return math.ceil(value * factor) / factor


def round_down(value, decimals=4):
    """
    Arrondit une valeur à la baisse à un certain nombre de décimales.

    Args:
        value (float): La valeur à arrondir.
        decimals (int, optional): Le nombre de décimales (par défaut 4).

    Returns:
        float: La valeur arrondie à la baisse.
    """
    factor = 10 ** decimals
    return math.floor(value * factor) / factor


def convert_percentage_to_decimal(percentage: str):
    """
    Convertit une chaîne de pourcentage en une valeur décimale.

    Args:
        percentage (str): La chaîne représentant un pourcentage (ex. "25%").

    Returns:
        float: La valeur du pourcentage sous forme décimale.
    """
    return float(percentage.strip('%'))


def calculate_stoploss_index(percentage: str):
    """
    Calcule l'indice de stop-loss à partir d'un pourcentage donné.

    Args:
        percentage (str): La chaîne représentant un pourcentage (ex. "5%").

    Returns:
        float: L'indice de stop-loss calculé.
    """
    return (100.0 - convert_percentage_to_decimal(percentage)) / 100.0


def calculate_profit_index(percentage: str):
    """
    Calcule l'indice de profit à partir d'un pourcentage donné.

    Args:
        percentage (str): La chaîne représentant un pourcentage (ex. "5%").

    Returns:
        float: L'indice de profit calculé.
    """
    return (100.0 + convert_percentage_to_decimal(percentage)) / 100.0


def calculate_max_quote_index(percentage: str):
    """
    Calcule l'indice de quote maximum à partir d'un pourcentage donné.

    Args:
        percentage (str): La chaîne représentant un pourcentage (ex. "25%").

    Returns:
        float: L'indice de quote maximum calculé.
    """
    return convert_percentage_to_decimal(percentage) / 100.0


def calculate_percentage(a: NumberOrPrice, b: NumberOrPrice) -> float:
    """
    Calcule le pourcentage de `a` par rapport à `b`.

    Args:
        a (float | Price): La première valeur ou un objet Price.
        b (float | Price): La deuxième valeur ou un objet Price.

    Returns:
        float: Le pourcentage de `a` par rapport à `b`.

    Raises:
        ValueError: Si `b` est zéro.
    """
    # Si a ou b est une instance de Price, on récupère la valeur 'price'
    if isinstance(a, Price):
        a = a.price
    if isinstance(b, Price):
        b = b.price

    # Vérification que 'b' n'est pas égal à zéro pour éviter la division par zéro
    if b == 0:
        raise ValueError("Le second argument 'b' ne peut pas être zéro lors du calcul du pourcentage.")

    # Calcul du pourcentage
    return round(100.0 * a / b, 2)


def resample_dataframe(dataframe: DataFrame, resample_period: GateioTimeFrame, expected_length: int):
    """
    Resample un DataFrame sur une période donnée et retourne le nombre de lignes attendu.

    Args:
        dataframe (DataFrame): Le DataFrame à resampler.
        resample_period (GateioTimeFrame): La période de resampling.
        expected_length (int): Le nombre de lignes attendu après le resampling.

    Returns:
        tuple: Un tuple contenant le DataFrame resamplé et le DataFrame original.
    """
    pandas_period: PandasTimeFrame = convert_gateio_timeframe_to_pandas(resample_period)
    original_dataframe = dataframe.copy()  # Copie le DataFrame original pour une utilisation ultérieure
    dataframe = (dataframe.resample(pandas_period, closed='right')
                 .agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'}))
    resampled_dataframe: DataFrame = dataframe.tail(expected_length)  # Récupère les dernières lignes après le resampling
    return resampled_dataframe, original_dataframe  # Retourne le DataFrame resamplé et le DataFrame original


"""
### Correspondance des noms (Ancien → Nouveau → Signification)
| Ancien Nom                       | Nouveau Nom                      | Signification                                                   |
|----------------------------------|----------------------------------|-----------------------------------------------------------------|
| `pourcentage_value`              | `convert_percentage_to_decimal`  | Convertit une chaîne de pourcentage en valeur décimale          |
| `pourcentage_to_stoploss_indice` | `calculate_stoploss_index`       | Calcule l'indice de stop-loss à partir d'un pourcentage         |
| `pourcentage_to_profit_indice`   | `calculate_profit_index`         | Calcule l'indice de profit à partir d'un pourcentage            |
| `pourcentage_to_max_quote_indice`| `calculate_max_quote_index`      | Calcule l'indice de quote maximum à partir d'un pourcentage     |
| `pct`                            | `calculate_percentage`           | Calcule le pourcentage de `a` par rapport à `b`                 |
| `resample`                       | `resample_dataframe`             | Resample un DataFrame sur une période donnée                    |
"""


def diviser_timeframe(timeframe: GateioTimeFrame, division: int) -> GateioTimeFrame:
    """
    Divise un timeframe par un facteur spécifié et renvoie le nouveau timeframe.

    Args:
        timeframe (GateioTimeFrame): Timeframe à diviser (ex. '1h', '30m').
        division (int): Facteur de division.

    Returns:
        GateioTimeFrame: Nouveau timeframe divisé.
    """
    unit = timeframe[-1]  # Extrait l'unité de temps ('m', 'h', 'd')
    amount = int(timeframe[:-1])  # Extrait la quantité de temps (ex. 1, 30)

    # Convertit le timeframe en minutes totales en fonction de l'unité
    if unit == 'm':
        total_minutes = amount
    elif unit == 'h':
        total_minutes = amount * 60
    elif unit == 'd':
        total_minutes = amount * 1440
    else:
        raise ValueError('Unité de timeframe non prise en charge')

    new_minutes = total_minutes // division  # Divise le total de minutes par le facteur de division

    # Détermine la nouvelle unité et valeur de temps
    if new_minutes % 1440 == 0:
        value = new_minutes // 1440
        unit = 'd'
    elif new_minutes % 60 == 0:
        value = new_minutes // 60
        unit = 'h'
    else:
        value = new_minutes
        unit = 'm'

    return GateioTimeFrame(f'{value}{unit}')  # Retourne le nouveau timeframe


def seconds_to_timeframe(seconds: int) -> GateioTimeFrame:
    """
    Convertit un nombre de secondes en un format de timeframe.

    Args:
        seconds (int): Nombre de secondes à convertir.

    Returns:
        GateioTimeFrame: Le timeframe correspondant au nombre de secondes.
    """
    if seconds >= 2592000:  # Mois
        output = str(seconds // 2592000) + 'M'
    elif seconds >= 604800:  # Semaine
        output = str(seconds // 604800) + 'w'
    elif seconds >= 86400:  # Jour
        output = str(seconds // 86400) + 'd'
    elif seconds >= 3600:  # Heure
        output = str(seconds // 3600) + 'h'
    elif seconds >= 60:  # Minute
        output = str(seconds // 60) + 'm'
    else:  # Seconde
        output = str(seconds) + 's'

    return GateioTimeFrame(output)


def timeframe_to_seconds(timeframe: GateioTimeFrame) -> int:
    """
    Convertit un timeframe en secondes.

    Args:
        timeframe (GateioTimeFrame): Le timeframe à convertir (ex. '1h', '30m').

    Returns:
        int: Le nombre de secondes correspondant au timeframe.
    """
    unit = timeframe[-1]  # Extrait l'unité de temps
    amount = int(timeframe[:-1])  # Extrait la quantité de temps

    # Convertit le timeframe en secondes selon l'unité
    if unit == 'm':
        seconds = amount * 60
    elif unit == 'h':
        seconds = amount * 3600
    elif unit == 'd':
        seconds = amount * 86400
    elif unit == 'w':
        seconds = amount * 604800
    elif unit == 'M':
        seconds = amount * 2592000
    else:
        seconds = None  # Unité non reconnue

    return seconds


def get_seconds_till_close(timeframe_in_seconds: int) -> int:
    """
    Calcule le nombre de secondes restantes jusqu'à la fin du timeframe en cours.

    Args:
        timeframe_in_seconds (int): Le nombre de secondes du timeframe.

    Returns:
        int: Nombre de secondes restantes jusqu'à la fermeture du timeframe en cours.
    """
    now = datetime.now()
    return timeframe_in_seconds - (now.minute * 60 + now.second) % timeframe_in_seconds


"""
### Correspondance des noms (Ancien → Nouveau → Signification)
| Ancien Nom                           | Nouveau Nom                             | Signification                                                      |
|--------------------------------------|-----------------------------------------|--------------------------------------------------------------------|
| `diviser_timeframe`                  | `diviser_timeframe`                     | Divise un timeframe par un facteur spécifié                        |
| `seconds_to_timeframe`               | `seconds_to_timeframe`                  | Convertit un nombre de secondes en un timeframe                    |
| `timeframe_to_seconds`               | `timeframe_to_seconds`                  | Convertit un timeframe en secondes                                 |
| `convert_gateio_timeframe_to_pandas` | `convert_gateio_timeframe_to_pandas`    | Convertit un timeframe Gate.io en un format Pandas                 |
| `get_seconds_till_close`             | `get_seconds_till_close`                | Calcule le nombre de secondes restantes avant la fin du timeframe  |
"""
