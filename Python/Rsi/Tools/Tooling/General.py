import calendar
import os
import re
import socket
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import numpy as np
# noinspection PyUnresolvedReferences
import psutil

from Python.Rsi.Tools.Quotes import file_exists


def resolve_path_json_pairs(script_path, file_name):
    if not os.path.exists(file_name):
        return os.path.join(script_path, file_name)
    else:
        return file_name


# noinspection PyUnusedLocal


def verify_pair(chaine):
    motif = r'^.*/USDT$'
    return bool(re.match(motif, chaine))


def day_of_week():
    days_of_the_week = list(calendar.day_name)
    current_day_number = datetime.now(timezone.utc).weekday()
    return days_of_the_week[current_day_number]


def convert_utc_to_local(heure_utc_str, fuseau_horaire_local_str):
    """
    Convertit une heure UTC donnée en format hh:mm en heure locale pour un fuseau horaire spécifié.

    :param heure_utc_str: Heure UTC en format hh:mm comme chaîne de caractères
    :param fuseau_horaire_local_str: Identifiant du fuseau horaire local (ex. 'Europe/Paris')
    :return: Heure locale en format hh:mm
    """
    # Convertir la chaîne en objet datetime, en assumant la date actuelle pour UTC
    heure_utc = datetime.strptime(heure_utc_str, '%H:%M').replace(tzinfo=timezone.utc)

    # Convertir en fuseau horaire local
    fuseau_horaire_local = ZoneInfo(fuseau_horaire_local_str)
    heure_locale = heure_utc.astimezone(fuseau_horaire_local)

    # Retourner l'heure locale en format hh:mm
    return heure_locale.strftime('%H:%M')


def get_ip_address():
    for interface, addrs in psutil.net_if_addrs().items():
        if interface == 'lo' or interface.startswith('lo'):
            continue
        for addr in addrs:
            if addr.family == socket.AF_INET:
                if psutil.net_if_stats()[interface].isup:
                    return addr.address
    return 'Non disponible'


def serialize_class_reference(class_reference):
    """Retourne une représentation en chaîne du nom complet de la classe."""
    name: str = class_reference.__name__
    return f'{name.split('.')[-1]}'


def deserialize_class_reference(full_class_name):
    """Résout une chaîne de nom de classe en une référence de classe."""
    module_name, class_name = full_class_name.rsplit('.', 1)
    module = __import__(module_name, fromlist=[class_name])
    return getattr(module, class_name)


def default_converter(obj):
    """Convertit les types non sérialisables."""
    if isinstance(obj, np.bool_):
        return bool(obj)
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')


def get_missing_files(file_paths_dict):
    """
    Identifie les fichiers qui n'existent pas dans un dictionnaire donné.

    Args:
    file_paths_dict (dict): Un dictionnaire où les clés sont des identifiants (comme des noms)
                            et les valeurs sont les chemins de fichiers correspondants.

    Returns:
    list: Une liste de tuples, chaque tuple contenant la clé et le chemin d'un fichier
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

    Args:
        list_a (list): La liste à partir de laquelle les éléments seront soustraits.
        list_b (list): La liste des éléments à soustraire de list_a.

    Returns:
        list: Une liste contenant les éléments uniques à list_a.
    """
    # Utiliser la compréhension de liste pour filtrer les éléments
    return [item for item in list_a if item not in list_b]
