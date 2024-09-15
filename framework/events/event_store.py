import json
import threading
from datetime import datetime, timezone
from typing import Optional

from framework.events.generic_event import GenericEvent


class EventStore(dict):
    """
    Classe EventStore pour stocker et gérer des événements sous forme de dictionnaire.

    Hérite de la classe dict, ce qui permet de stocker des événements comme des paires clé-valeur
    où la clé est un identifiant de thread ou un identifiant de bot, et la valeur est une liste d'événements.

    ### Correspondance des noms (Ancien → Nouveau → Signification)
    | Ancien Nom             | Nouveau Nom                           | Signification                                                          |
    |------------------------|---------------------------------------|------------------------------------------------------------------------|
    | `self.bot`             | `default_bot_identifier`              | Identifiant par défaut pour le bot utilisé pour stocker les événements |
    | `to_json`              | `serialize_to_json`                   | Sérialise le store d'événements en JSON                                |
    | `from_json`            | `deserialize_from_json`               | Désérialise une chaîne JSON en EventStore                              |
    | `set_event`            | `add_event_to_store`                  | Ajoute un événement au store avec un timestamp en UTC                  |
    | `get_event`            | `retrieve_event`                      | Récupère un événement correspondant à une clé spécifique               |
    """

    def __init__(self, *args, **kwargs):
        """
        Initialise une instance de EventStore.

        Args:
            *args: Arguments positionnels pour initialiser le dictionnaire parent.
            **kwargs: Arguments nommés pour initialiser le dictionnaire parent.
        """
        super().__init__(*args, **kwargs)
        self.default_bot_identifier = 'Python.Rsi.Bot'  # Identifiant par défaut pour le bot utilisé pour le stockage des événements

    def serialize_to_json(self):
        """
        Sérialise l'objet EventStore en une chaîne JSON.

        Returns:
            str: La représentation JSON de l'objet EventStore.
        """
        return json.dumps(self, default=lambda o: o.__dict__, ensure_ascii=False)

    @classmethod
    def deserialize_from_json(cls, json_str):
        """
        Désérialise une chaîne JSON en une instance de EventStore.

        Args:
            json_str (str): La chaîne JSON représentant un EventStore.

        Returns:
            EventStore: Une instance de EventStore désérialisée de la chaîne JSON.
        """
        # Convertit la chaîne JSON en un dictionnaire Python standard
        data = json.loads(json_str)
        # Crée une instance de EventStore à partir du dictionnaire
        return cls(data)

    def add_event_to_store(self, message: dict, use_thread: bool = False):
        """
        Ajoute un événement au store avec un timestamp actuel en UTC.

        Args:
            message (dict): Le message de l'événement à stocker.
            use_thread (bool, optional): Si True, utilise l'identifiant du thread actuel comme clé,
                                         sinon utilise l'identifiant du bot (par défaut False).
        """
        # Détermine la clé à utiliser (identifiant du thread ou du bot)
        thread = threading.get_ident() if use_thread else self.default_bot_identifier
        now_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')  # Heure actuelle en UTC
        if thread not in self:
            self[thread] = []  # Initialise une liste pour ce thread si elle n'existe pas déjà
        array: list = self[thread]
        # Ajoute un nouvel événement au début de la liste pour ce thread
        array.insert(0, {'date': now_utc, 'message': message})

    def retrieve_event(self, event: str, use_thread: bool = False) -> Optional[GenericEvent]:
        """
        Récupère le premier événement correspondant à une clé donnée.

        Args:
            event (str): Le nom de l'événement à rechercher.
            use_thread (bool, optional): Si True, utilise l'identifiant du thread actuel comme clé,
                                         sinon utilise l'identifiant du bot (par défaut False).

        Returns:
            Optional[GenericEvent]: L'événement trouvé correspondant, ou None s'il n'est pas trouvé.
        """
        # Détermine la clé à utiliser (identifiant du thread ou du bot)
        thread = threading.get_ident() if use_thread else self.default_bot_identifier
        if thread not in self:
            self[thread] = []  # Initialise une liste pour ce thread si elle n'existe pas déjà

        output = None
        for item in self[thread]:
            if event in item['message']:
                output = item['message'][event]
                break  # Arrête après avoir trouvé le premier élément pertinent
        return output
