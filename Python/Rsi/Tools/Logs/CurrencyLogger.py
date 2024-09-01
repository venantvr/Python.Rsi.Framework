# Définir une sous-classe de logging.Logger
import logging

from Python.Rsi.Tools.Business import BotCurrencyPair


class CurrencyLogger(logging.Logger):
    """
    Sous-classe de logging.Logger pour ajouter des méthodes de journalisation spécifiques à des paires de devises.

    Cette classe étend la classe standard `logging.Logger` pour fournir des méthodes de journalisation personnalisées
    qui incluent des informations spécifiques sur les paires de devises (`BotCurrencyPair`).
    """

    def log_warning_for(self, currency_pair: BotCurrencyPair, message):
        """
        Journalise un message de niveau WARNING pour une paire de devises spécifique.

        Args:
            currency_pair (BotCurrencyPair): La paire de devises associée au message de journalisation.
            message (str): Le message à journaliser.
        """
        # Utilise la méthode warning de Logger pour journaliser un message au niveau WARNING
        self.warning(f'{currency_pair} : {message}')

    def log_info_for(self, currency_pair: BotCurrencyPair, message):
        """
        Journalise un message de niveau INFO pour une paire de devises spécifique.

        Args:
            currency_pair (BotCurrencyPair): La paire de devises associée au message de journalisation.
            message (str): Le message à journaliser.
        """
        # Utilise la méthode info de Logger pour journaliser un message au niveau INFO
        self.info(f'{currency_pair} : {message}')
