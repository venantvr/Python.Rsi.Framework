import numpy as np
from pandas import DataFrame

from Python.Rsi.Tools.Logs import logger
from Python.Rsi.Tools.Tooling.TimeframeAdjuster import TimeframeAdjuster


class DeltaValueNormalizer:
    """
    Classe DeltaValueNormalizer pour normaliser les données basées sur un mapping de colonnes et des poids associés.

    Cette classe permet de normaliser les valeurs dans un DataFrame en fonction des poids spécifiés pour chaque colonne,
    avec la possibilité de les ajuster ensuite.

    ### Correspondance des noms (Ancien → Nouveau → Signification)
    | Ancien Nom            | Nouveau Nom                   | Signification                                                     |
    |-----------------------|-------------------------------|-------------------------------------------------------------------|
    | DeltaNormalizer       | DeltaValueNormalizer          | Renommé pour indiquer la normalisation des valeurs du delta.      |
    | delta_to_column       | column_weight_mapping         | Mapping des colonnes du DataFrame et leurs poids respectifs.      |
    | adjuster              | dataframe_adjuster            | Instance de la classe Adjuster pour ajuster les DataFrames.       |
    | delta_norm            | normalized_column_name        | Nom de la colonne qui contiendra la valeur normalisée.            |
    | __weighted_norm       | __calculate_weighted_norm     | Méthode privée pour calculer la norme pondérée des colonnes.      |
    | normalize             | apply_normalization           | Applique la normalisation aux DataFrames dans le dictionnaire.    |

    """

    # noinspection PyUnresolvedReferences
    def __init__(self, column_weight_mapping: dict, dataframe_adjuster: TimeframeAdjuster):
        """
        Initialise l'instance de DeltaValueNormalizer.

        Args:
            column_weight_mapping (dict): Dictionnaire qui mappe les noms de colonnes de DataFrame à leur poids pour la normalisation.
            dataframe_adjuster (Adjuster): Instance de la classe Adjuster utilisée pour normaliser les dataframes.

        Attributes:
            normalized_column_name (str): Nom de la colonne où le résultat de la normalisation sera stocké.
            column_weight_mapping (dict): Stocke le mapping des colonnes aux poids.
            dataframe_adjuster (Adjuster): Stocke l'instance de Adjuster.
        """
        self.normalized_column_name: str = 'normalized_column'
        self.column_weight_mapping: dict = column_weight_mapping
        self.dataframe_adjuster: TimeframeAdjuster = dataframe_adjuster

    def __calculate_weighted_norm(self, dataframe: DataFrame):
        """
        Méthode privée pour calculer la norme pondérée des valeurs dans un DataFrame selon les poids spécifiés.

        Args:
            dataframe (DataFrame): DataFrame contenant les données à normaliser.

        Returns:
            float: La valeur normalisée, pondérée par les poids des colonnes, arrondie à deux décimales.
        """
        squares_sum = sum(pow(dataframe[column_name] * column_info['weight'], 2)
                          for column_name, column_info in self.column_weight_mapping.items())
        norm = np.sqrt(squares_sum)
        possible_max = np.sqrt(sum(pow(100.0 * column_info['weight'], 2)
                                   for column_info in self.column_weight_mapping.values()))
        pct_norm = (norm / possible_max) * 100.0
        return round(pct_norm, 2)

    def apply_normalization(self, delta_dataframes: dict):
        """
        Normalise les valeurs dans les DataFrames stockés dans le dictionnaire delta.

        Args:
            delta_dataframes (dict): Dictionnaire contenant des paires clé-valeur où la valeur est un DataFrame à normaliser.

        Returns:
            dict: Le dictionnaire delta avec les DataFrames normalisés.
        """
        logger.info(f'Démarrage de la normalisation avec {type(self).__name__}')
        if self.column_weight_mapping != {}:
            for pair_name, dataframe in delta_dataframes.items():
                dataframe[self.normalized_column_name] = self.__calculate_weighted_norm(dataframe=dataframe)
                self.dataframe_adjuster.normalize_dataframe_columns(dataframe=dataframe,
                                                                    columns=[self.normalized_column_name])
        return delta_dataframes
