import json
from typing import LiteralString

import requests

from Python.Rsi.Tools.Business import GateioProxy
from Python.Rsi.Tools.Logs import logger
from Python.Rsi.Tools.Tooling import verify_pair


def fetch_all_currency_pairs(file_path: LiteralString | str | bytes, number_of_pages: int, quote_currency: str = 'USDT'):
    """
    Récupère toutes les paires de devises disponibles et les enregistre dans un fichier JSON.

    Args:
        file_path (LiteralString | str | bytes): Le chemin vers le fichier où les données seront enregistrées.
        number_of_pages (int): Nombre de pages à parcourir pour récupérer les données.
        quote_currency (str): La devise de référence à utiliser (par défaut 'USDT').

    """
    all_currency_pairs = []
    gateio_proxy_instance = GateioProxy.get()
    all_currency_pairs = gateio_proxy_instance.list_currency_pairs()
    if len(all_currency_pairs):
        with open(file_path, 'w') as json_file:
            json.dump([currency_pair.id for currency_pair in all_currency_pairs], json_file, indent=2, sort_keys=True)
            logger.info(f'Data successfully saved to {file_path}')


def fetch_popular_currency_pairs(file_path: LiteralString | str | bytes, number_of_pages: int, quote_currency: str = 'USDT'):
    """
    Récupère les paires de devises les plus populaires et les enregistre dans un fichier JSON.

    Args:
        file_path (LiteralString | str | bytes): Le chemin vers le fichier où les données seront enregistrées.
        number_of_pages (int): Nombre de pages à parcourir pour récupérer les données.
        quote_currency (str): La devise de référence à utiliser (par défaut 'USDT').

    Returns:
        list: Liste des paires de devises populaires.
    """
    popular_currency_pairs = []
    for page_number in range(1, number_of_pages):
        url = f'https://www.gate.io/apiweb/v1/home/sortList?sortType=2&page={page_number}&pageSize=10'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            currency_items = data['data']['sortList']
            for currency_pair in currency_items:
                if currency_pair['symbol'].upper() != quote_currency.upper():
                    pair = currency_pair['symbol'].upper() + '/' + quote_currency.upper()
                    if verify_pair(pair):
                        popular_currency_pairs.append(pair)
        else:
            logger.error(f'Request error: {response.status_code}')

    if len(popular_currency_pairs):
        with open(file_path, 'w') as json_file:
            json.dump(popular_currency_pairs, json_file, indent=2, sort_keys=True)
            logger.info(f'Data successfully saved to {file_path}')

    return popular_currency_pairs


def fetch_top_gainers(file_path: LiteralString | str | bytes, number_of_pages: int, quote_currency: str = 'USDT'):
    """
    Récupère les paires de devises ayant les meilleures performances et les enregistre dans un fichier JSON.

    Args:
        file_path (LiteralString | str | bytes): Le chemin vers le fichier où les données seront enregistrées.
        number_of_pages (int): Nombre de pages à parcourir pour récupérer les données.
        quote_currency (str): La devise de référence à utiliser (par défaut 'USDT').

    Returns:
        list: Liste des paires de devises ayant les meilleures performances.
    """
    top_gainers_currency_pairs = []
    for page_number in range(1, number_of_pages):
        url = f'https://www.gate.io/apiweb/v1/home/sortList?sortType=1&page={page_number}&pageSize=10'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            currency_items = data['data']['sortList']
            for currency_pair in currency_items:
                if currency_pair['symbol'].upper() != quote_currency.upper():
                    pair = currency_pair['symbol'].upper() + '/' + quote_currency.upper()
                    if verify_pair(pair):
                        top_gainers_currency_pairs.append(pair)
        else:
            logger.error(f'Request error: {response.status_code}')

    if len(top_gainers_currency_pairs):
        with open(file_path, 'w') as json_file:
            json.dump(top_gainers_currency_pairs, json_file, indent=2, sort_keys=True)
            logger.info(f'Data successfully saved to {file_path}')

    return top_gainers_currency_pairs


def fetch_most_profitable_currency_pairs(file_path: LiteralString | str | bytes, number_of_pages: int, quote_currency: str = 'USDT'):
    """
    Récupère les paires de devises les plus rentables et les enregistre dans un fichier JSON.

    Args:
        file_path (LiteralString | str | bytes): Le chemin vers le fichier où les données seront enregistrées.
        number_of_pages (int): Nombre de pages à parcourir pour récupérer les données.
        quote_currency (str): La devise de référence à utiliser (par défaut 'USDT').

    Returns:
        list: Liste des paires de devises les plus rentables.
    """
    most_profitable_currency_pairs = []
    for page_number in range(1, number_of_pages):
        url = f'https://www.gate.io/api/web/v1/site/getHomeCoinList?type=6&page={page_number}&pageSize=10'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            currency_items = data['data']['list']
            for currency_pair in currency_items:
                if currency_pair['asset'].upper() != quote_currency.upper():
                    pair = currency_pair['asset'].upper() + '/' + quote_currency.upper()
                    if verify_pair(pair):
                        most_profitable_currency_pairs.append(pair)
        else:
            logger.error(f'Request error: {response.status_code}')

    if len(most_profitable_currency_pairs):
        with open(file_path, 'w') as json_file:
            json.dump(most_profitable_currency_pairs, json_file, indent=2, sort_keys=True)
            logger.info(f'Data successfully saved to {file_path}')

    return most_profitable_currency_pairs


def fetch_trending_currency_pairs(file_path: LiteralString | str | bytes, number_of_pages: int):
    """
    Récupère les paires de devises en tendance et les enregistre dans un fichier JSON.

    Args:
        file_path (LiteralString | str | bytes): Le chemin vers le fichier où les données seront enregistrées.
        number_of_pages (int): Nombre de pages à parcourir pour récupérer les données.

    Returns:
        list: Liste des paires de devises en tendance.
    """
    trending_currency_pairs = []
    for page_number in range(1, number_of_pages):
        url = f'https://www.gate.io/apiweb/v1/home/getCoinList?type=1&page={page_number}&pageSize=10&subType=1'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            market_items = data['data']['marketList']
            for currency_pair in market_items:
                pair = currency_pair['pair'].upper().replace('_', '/')
                if verify_pair(pair):
                    trending_currency_pairs.append(pair)
        else:
            logger.error(f'Request error: {response.status_code}')

    if len(trending_currency_pairs):
        with open(file_path, 'w') as json_file:
            json.dump(trending_currency_pairs, json_file, indent=2, sort_keys=True)
            logger.info(f'Data successfully saved to {file_path}')

    return trending_currency_pairs


"""
Table de correspondance des anciens noms et nouveaux noms :

| Ancien nom               | Nouveau nom                          | Signification                                               |
|--------------------------|--------------------------------------|-------------------------------------------------------------|
| get_all                  | fetch_all_currency_pairs             | Récupérer toutes les paires de devises                      |
| get_popular              | fetch_popular_currency_pairs         | Récupérer les paires de devises les plus populaires         |
| get_gainers              | fetch_top_gainers                    | Récupérer les paires de devises ayant les meilleures gains  |
| get_profits              | fetch_most_profitable_currency_pairs | Récupérer les paires de devises les plus rentables          |
| get_trends               | fetch_trending_currency_pairs        | Récupérer les paires de devises en tendance                 |
| file                     | file_path                            | Chemin vers le fichier                                      |
| pages_number             | number_of_pages                      | Nombre de pages à parcourir                                 |
| quote                    | quote_currency                       | Devise de référence                                         |
| currency_pairs           | currency_pairs                       | Liste des paires de devises                                 |
| fichier_json             | json_file                            | Fichier JSON où les données sont sauvegardées               |
| reponse                  | response                             | Réponse de la requête HTTP                                  |
| contenu                  | data                                 | Données JSON extraites de la réponse HTTP                   |
| items                    | currency_items                       | Liste des éléments de devises dans les données récupérées   |
"""
