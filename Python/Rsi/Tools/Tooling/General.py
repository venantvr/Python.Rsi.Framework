import calendar
import os
import re
import socket
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import numpy as np
# noinspection PyUnresolvedReferences
import psutil

from Python.Rsi.Tools.Quotes import file_exists  # Import de la fonction file_exists à partir d'un module spécifique


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
