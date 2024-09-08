import warnings

from pandas import DataFrame


class TemporaryColumnsManager:
    """
    Classe ColumnsManager pour gérer les colonnes temporaires dans un DataFrame de manière contextuelle.

    Cette classe permet d'assurer la présence de colonnes temporaires pendant une opération spécifique
    et de les supprimer à la fin de cette opération.

    ### Correspondance des noms (Ancien → Nouveau → Signification)
    | Ancien Nom         | Nouveau Nom        | Signification                                                                     |
    |--------------------|--------------------|-----------------------------------------------------------------------------------|
    | `df`               | `df`               | DataFrame à manipuler                                                             |
    | `keep_temp_columns`| `keep_temp_columns`| Liste des colonnes à conserver après l'opération                                  |
    | `drop_temp_columns`| `drop_temp_columns`| Liste des colonnes à supprimer après l'opération                                  |
    | `__enter__`        | `__enter__`        | Méthode pour assurer la présence des colonnes avant l'opération contextuelle      |
    | `__exit__`         | `__exit__`         | Méthode pour supprimer ou conserver les colonnes après l'opération contextuelle   |
    """

    def __init__(self, dataframe: DataFrame, keep: list = None, drop: list = None):
        """
        Initialise le gestionnaire de colonnes avec les colonnes à conserver et à supprimer.

        Paramètres :
        dataframe (DataFrame) : Le DataFrame à manipuler.
        keep (list) : Liste des colonnes à conserver après l'opération. (par défaut : None)
        drop (list) : Liste des colonnes temporaires à supprimer après l'opération. (par défaut : None)
        """
        self.df = dataframe
        self.keep_temp_columns = keep or []  # Liste des colonnes à garder après l'opération
        self.drop_temp_columns = drop or []  # Liste des colonnes à supprimer après l'opération

    def __enter__(self):
        """
        Assure que les colonnes spécifiées dans keep et drop sont présentes dans le DataFrame
        avant l'opération.

        Retourne :
        DataFrame : Le DataFrame avec les colonnes temporaires ajoutées (si nécessaire).
        """
        # Ajoute les colonnes temporaires (si elles n'existent pas déjà) sans initialiser de données
        for column_name in self.keep_temp_columns + self.drop_temp_columns:
            if column_name not in self.df.columns:
                # Utilise un gestionnaire de contextes pour ignorer les avertissements
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    # Ajoute la colonne temporaire avec des valeurs None
                    self.df.loc[:, column_name] = None
        return self.df

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Supprime les colonnes temporaires du DataFrame après l'opération contextuelle.

        Paramètres :
        exc_type : Type de l'exception (si une exception est levée)
        exc_val : Valeur de l'exception
        exc_tb : Traceback de l'exception
        """
        # Si la liste drop_temp_columns n'est pas vide, on supprime ces colonnes du DataFrame
        if self.drop_temp_columns:
            self.df.drop(columns=self.drop_temp_columns, inplace=True)
        else:
            # Sinon, on conserve uniquement les colonnes spécifiées dans keep_temp_columns
            columns = self.df.columns
            self.df.drop(columns=columns.difference(self.keep_temp_columns), inplace=True)
