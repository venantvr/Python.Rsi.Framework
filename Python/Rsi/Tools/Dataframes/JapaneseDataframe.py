from pandas import DataFrame


class JapaneseDataframe(DataFrame):
    """
    Une sous-classe de pandas DataFrame pour représenter des données spécifiques au format japonais ou
    pour ajouter des fonctionnalités supplémentaires adaptées aux besoins spécifiques.
    """

    def __init__(self, data, *args, **kwargs):
        """
        Initialise une instance de JapaneseDataframe en utilisant les mêmes paramètres que le DataFrame de pandas.

        Paramètres :
        data : Données utilisées pour créer le DataFrame (peut être de divers types compatibles avec pandas).
        *args : Arguments supplémentaires à passer au constructeur de DataFrame.
        **kwargs : Arguments nommés supplémentaires à passer au constructeur de DataFrame.
        """
        # Appelle le constructeur de la classe parente (DataFrame) pour initialiser l'instance
        super().__init__(data, *args, **kwargs)

    @classmethod
    def from_dataframe(cls, df):
        """
        Crée une instance de JapaneseDataframe à partir d'un DataFrame pandas existant.

        Paramètres :
        df (DataFrame) : Un DataFrame pandas existant à convertir en JapaneseDataframe.

        Retourne :
        JapaneseDataframe : Une nouvelle instance de JapaneseDataframe avec les mêmes données, index et colonnes que le DataFrame d'origine.
        """
        # Utilise les valeurs, l'index et les colonnes du DataFrame existant pour créer une nouvelle instance de JapaneseDataframe
        return cls(df.values, index=df.index, columns=df.columns)
