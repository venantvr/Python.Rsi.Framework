import sys
from typing import Optional

import requests

from venantvr.business import BotCurrencyPair
from venantvr.logs import code_configuration, log_exception_error
from venantvr.parameters import Parameterized
from venantvr.tooling import get_ip_address


class TelegramNotificationService(Parameterized('telegram')):
    """
    Classe TelegramNotificationService pour gérer l'envoi de messages et d'images via Telegram.

    Cette classe utilise l'API Telegram pour envoyer des notifications textuelles et des images.
    Elle sélectionne automatiquement les bons identifiants et tokens en fonction de l'adresse IP locale.

    ### Correspondance des noms (Ancien → Nouveau → Signification)
    | Ancien Nom        | Nouveau Nom                   | Signification                                                     |
    |-------------------|-------------------------------|-------------------------------------------------------------------|
    | `TelegramService` | `TelegramNotificationService` | Nom de la classe décrivant mieux son but d'envoi de notifications |
    | `api`             | `api_base_url`                | L'URL de base de l'API Telegram                                   |
    | `token`           | `bot_token`                   | Token d'accès du bot Telegram                                     |
    | `id`              | `chat_id`                     | Identifiant du chat où envoyer les notifications                  |
    | `chat`            | `send_text_message`           | Méthode pour envoyer un message texte                             |
    | `blob`            | `send_image`                  | Méthode pour envoyer une image sous forme de blob                 |
    | `message`         | `text_message`                | Le contenu textuel du message envoyé                              |
    """

    def __init__(self):
        """
        Initialise l'instance de TelegramNotificationService en chargeant les paramètres de configuration Telegram.
        """
        super().__init__()
        self.system_code = code_configuration()  # Code de configuration unique pour le système
        self.api_base_url = self.section['api']  # URL de base de l'API Telegram
        self.bot_token = self.section['token']  # Token du bot Telegram
        self.chat_id = self.section['id']  # ID du chat où envoyer les notifications

        # Récupère l'IP de la machine
        current_ip = get_ip_address()

        # Vérifie si l'IP correspond à celle définie dans la section 'local'
        if current_ip == self.section.get('local', {}).get('ip'):
            self.bot_token = self.section['local']['token']
            self.chat_id = self.section['local']['id']

        endpoints = self.section['endpoints']
        self.text_endpoint = endpoints['text']  # Point de terminaison pour les messages texte
        self.image_endpoint = endpoints['image']  # Point de terminaison pour les images

    def send_text_message(self, currency_pair: Optional[BotCurrencyPair], text_message: str):
        """
        Envoie un message texte via Telegram.

        Args:
            currency_pair (Optional[BotCurrencyPair]): La paire de devises liée au message (si applicable).
            text_message (str): Le message texte à envoyer.
        """
        # noinspection PyBroadException
        try:
            if currency_pair is not None:
                text_message = f'{currency_pair.base} {text_message}'  # Ajoute la devise de base au message
            if self.system_code is not None:
                text_message = f'({self.system_code}) {text_message}'  # Ajoute le code système au message
            url = f'{self.api_base_url}{self.bot_token}'
            params = {'chat_id': self.chat_id, 'text': str(text_message)}
            # Envoie la requête à l'API Telegram
            response = requests.get(f'{url}{self.text_endpoint}', params=params)
        except Exception as ex:
            exc_type, exc_value, tb = exc_info = sys.exc_info()
            log_exception_error(exc_type, exc_value, tb)

    def send_image(self, currency_pair: Optional[BotCurrencyPair], image_blob):
        """
        Envoie une image sous forme de blob via Telegram.

        Args:
            currency_pair (Optional[BotCurrencyPair]): La paire de devises liée à l'image (si applicable).
            image_blob (bytes): Le contenu de l'image sous forme de blob.
        """
        # noinspection PyBroadException
        try:
            url = f'{self.api_base_url}{self.bot_token}'
            data = {'chat_id': self.chat_id}
            files = {'photo': image_blob}
            # Envoie l'image à l'API Telegram
            response = requests.post(f'{url}{self.image_endpoint}', data=data, files=files)
        except Exception as ex:
            exc_type, exc_value, tb = exc_info = sys.exc_info()
            log_exception_error(exc_type, exc_value, tb)
