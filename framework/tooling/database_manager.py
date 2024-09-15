import sqlite3
from datetime import datetime, timezone

from framework.business.bot_currency_pair import BotCurrencyPair
from framework.parameters.parameterized import Parameterized
from framework.quotes.price import Price
from framework.quotes.quotes_utils import gateio_currency_pair


class DatabaseManager(Parameterized('bot')):
    """
    Classe DatabaseManager pour gérer les opérations de base de données liées aux trades et aux indicateurs.

    Cette classe permet de créer des tables, d'ajouter des colonnes dynamiquement, d'insérer des trades,
    et de récupérer des informations sur les trades en cours.

    ### Correspondance des noms (Ancien → Nouveau → Signification)
    | Ancien Nom          | Nouveau Nom                     | Signification                                                   |
    |---------------------|---------------------------------|-----------------------------------------------------------------|
    | `path`              | `database_path`                 | Chemin du fichier de base de données SQLite.                    |
    | `write_trade`       | `log_trade_in_database`         | Méthode pour enregistrer un trade dans la base de données.      |
    | `get_running_trades`| `fetch_open_trades`             | Méthode pour récupérer les trades en cours.                     |
    | `conn`              | `connection`                    | Objet représentant la connexion à la base de données.           |
    | `cur`               | `cursor`                        | Curseur pour exécuter des requêtes SQL sur la base de données.  |
    | `ligne`             | `trade_row`                     | Chaque ligne récupérée représentant un trade en cours.          |
    | `resultats`         | `results`                       | Liste contenant les résultats des requêtes SQL.                 |
    """

    def __init__(self):
        """
        Initialise l'instance de DatabaseManager, crée les tables et colonnes si nécessaire.
        """
        super().__init__()

        self.database_enabled = self.section['database']['enabled']  # Vérifie si la base de données est activée
        self.database_path = self.get.database  # Chemin vers la base de données

        # Création et modification des tables si la base de données est activée
        if self.database_enabled:
            # Création de la table "indicators" avec les conditions 1 à 7, et ajout des conditions 8 à 10 si nécessaire
            with sqlite3.connect(self.database_path) as connection:
                cursor = connection.cursor()
                cursor.execute('''CREATE TABLE IF NOT EXISTS "indicators" (
                    "id"	        INTEGER NOT NULL UNIQUE,
                    "pair"	        TEXT,
                    "timeframe"	    TEXT,
                    "sequence_id"	INTEGER,
                    "date"	        TEXT,
                    "price"	        TEXT,
                    "condition_1"	INTEGER,
                    "condition_2"	INTEGER,
                    "condition_3"	INTEGER,
                    "condition_4"	INTEGER,
                    "condition_5"	INTEGER,
                    "condition_6"	INTEGER,
                    "condition_7"	INTEGER,
                    PRIMARY KEY("id" AUTOINCREMENT)
                )''')
                connection.commit()

            # Ajout des nouvelles colonnes condition_8, condition_9, condition_10 si elles n'existent pas
            self.__add_missing_column('indicators', 'condition_8')
            self.__add_missing_column('indicators', 'condition_9')
            self.__add_missing_column('indicators', 'condition_10')

            # Création de la table "trades" pour enregistrer les transactions (buy/sell)
            with sqlite3.connect(self.database_path) as connection:
                cursor = connection.cursor()
                cursor.execute('''CREATE TABLE IF NOT EXISTS "trades" (
                    "id"	    INTEGER NOT NULL,
                    "pair"	    TEXT,
                    "action"	TEXT,
                    "price"	    NUMERIC,
                    "date"	    TEXT,
                    "thread"    TEXT,
                    PRIMARY KEY("id" AUTOINCREMENT)
                )''')
                connection.commit()

            # Ajout des index pour accélérer les recherches sur les colonnes "action" et "thread"
            self.__add_index('trades', 'action')
            self.__add_index('trades', 'thread')

            # Ajout de la colonne "detail" à la table "trades" si elle n'existe pas
            self.__add_missing_column('trades', 'detail')

    def __add_missing_column(self, table_name: str, column_name: str):
        """
        Ajoute une colonne à une table dans la base de données si elle n'existe pas.

        Args:
            table_name (str): Le nom de la table à modifier.
            column_name (str): Le nom de la colonne à ajouter.
        """
        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()
            cursor.execute(f'PRAGMA table_info({table_name})')
            columns = [info[1] for info in cursor.fetchall()]
            if column_name not in columns:
                cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN {column_name} INTEGER')
                connection.commit()

    def __add_index(self, table_name: str, column_name: str):
        """
        Ajoute un index à une colonne d'une table si l'index n'existe pas déjà.

        Args:
            table_name (str): Le nom de la table à modifier.
            column_name (str): Le nom de la colonne sur laquelle ajouter un index.
        """
        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()
            cursor.execute(f'''CREATE INDEX IF NOT EXISTS idx_{column_name} ON {table_name} ({column_name})''')
            connection.commit()

    def log_trade_in_database(self, currency_pair: BotCurrencyPair, action: str, price: Price, thread: str, detail: str):
        """
        Enregistre une transaction (trade) dans la base de données.

        Args:
            currency_pair (BotCurrencyPair): La paire de devises pour laquelle le trade est enregistré.
            action (str): L'action de la transaction ('BUY' ou 'SELL').
            price (Price): Le prix de la transaction.
            thread (str): Le thread associé à la transaction.
            detail (str): Détails supplémentaires de la transaction.
        """
        if self.database_enabled:
            current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')
            sql = '''INSERT INTO trades (
                pair, 
                action, 
                price,
                date, 
                thread,
                detail) VALUES (?, ?, ?, ?, ?, ?)'''
            with sqlite3.connect(self.database_path) as connection:
                cursor = connection.cursor()
                cursor.execute(sql, (
                    currency_pair.id,
                    action,
                    price.price,
                    current_time,
                    thread,
                    detail
                ))
                connection.commit()

    def fetch_open_trades(self, quote='USDT'):
        """
        Récupère tous les trades en cours (les trades qui ont été achetés mais pas encore vendus).

        Args:
            quote (str, optionnel): Le symbole de la devise de cotation (par défaut 'USDT').

        Returns:
            dict: Un dictionnaire contenant les trades en cours avec la paire de devises, le prix d'achat, et le thread.
        """
        open_trades = []
        if self.database_enabled:
            sql = '''SELECT buy.pair, buy.price, buy.thread
                    FROM trades buy
                    LEFT JOIN trades sell ON buy.thread = sell.thread AND sell.action = 'SELL'
                    WHERE buy.action = 'BUY' AND sell.thread IS NULL'''
            with sqlite3.connect(self.database_path) as connection:
                cursor = connection.cursor()
                cursor.execute(sql)
                open_trades = cursor.fetchall()
                # for trade_row in open_trades:
                #     logger.info(f'Trade non clôturé : {trade_row}')

        return {
            trade_row[0]: {
                'pair': gateio_currency_pair(pair_symbol=trade_row[0], keep_pair_quote=False, trading_quote=quote),
                'price': trade_row[1],
                'thread': trade_row[2],
            }
            for trade_row in open_trades
        }
