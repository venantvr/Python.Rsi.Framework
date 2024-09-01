from pandas import DataFrame


class NewColumnsTracker:
    """
    Classe NewColumnsTracker pour suivre les nouvelles colonnes ajoutées à un DataFrame
    pendant l'exécution d'un bloc de code.

    Cette classe permet de surveiller les colonnes qui sont ajoutées au DataFrame et
    d'enregistrer ces nouvelles colonnes dans un ensemble cible (`target_set`).
    """

    def __init__(self, dataframe: DataFrame, target_set: set[str]):
        """
        Initialise une instance de NewColumnsTracker.

        Paramètres :
        dataframe (DataFrame) : Le DataFrame à surveiller.
        target_set (set[str]) : Un ensemble cible où les nouvelles colonnes seront ajoutées.
        """
        self.dataframe = dataframe
        self.target_set = target_set
        # Stocke les colonnes initiales du DataFrame
        self.initial_columns = set(dataframe.columns)

    def __enter__(self):
        """
        Méthode appelée au début d'un bloc 'with'.
        Retourne l'instance de NewColumnsTracker pour être utilisée dans le bloc.

        Retourne :
        self (NewColumnsTracker) : L'instance actuelle de la classe.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Méthode appelée à la fin d'un bloc 'with'.
        Met à jour l'ensemble cible avec toutes les nouvelles colonnes ajoutées au DataFrame
        pendant l'exécution du bloc.

        Paramètres :
        exc_type : Type de l'exception (si une exception est levée).
        exc_val : Valeur de l'exception.
        exc_tb : Traceback de l'exception.
        """
        # Calcule la différence entre les colonnes actuelles et les colonnes initiales
        new_columns = set(self.dataframe.columns) - self.initial_columns
        # Met à jour l'ensemble cible avec les nouvelles colonnes détectées
        self.target_set.update(new_columns)
