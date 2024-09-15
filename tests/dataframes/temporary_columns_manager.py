import unittest

from pandas import DataFrame

from venantvr.dataframes.temporary_columns_manager import TemporaryColumnsManager


class TestTemporaryColumnsManager(unittest.TestCase):

    def setUp(self):
        """
        Initialisation avant chaque test.
        Crée un DataFrame pour les tests.
        """
        # Créer un DataFrame initial avec des colonnes
        self.dataframe = DataFrame({
            'col1': [1, 2, 3],
            'col2': [4, 5, 6]
        })

    def test_temporary_columns_add_and_remove(self):
        """
        Teste l'ajout et la suppression des colonnes temporaires pendant le bloc 'with'.
        """
        # Utiliser TemporaryColumnsManager avec une colonne temporaire à ajouter et supprimer
        with TemporaryColumnsManager(self.dataframe, drop=['temp_col']):
            # Vérifier que la colonne temporaire est ajoutée pendant le bloc
            self.assertIn('temp_col', self.dataframe.columns)
            self.assertIsNone(self.dataframe['temp_col'].iloc[0])

        # Vérifier que la colonne temporaire est supprimée après le bloc
        self.assertNotIn('temp_col', self.dataframe.columns)

    def test_keep_columns_after_operation(self):
        """
        Teste que les colonnes spécifiées dans 'keep' sont conservées après l'opération contextuelle.
        """
        # Utiliser TemporaryColumnsManager avec des colonnes à garder après le bloc
        with TemporaryColumnsManager(self.dataframe, keep=['col1', 'col3'], drop=['temp_col']):
            # Ajouter des colonnes pendant le bloc
            self.dataframe['col3'] = [7, 8, 9]
            self.assertIn('temp_col', self.dataframe.columns)

        # Vérifier que seule 'col1' et 'col3' sont conservées après le bloc
        self.assertIn('col1', self.dataframe.columns)
        self.assertIn('col3', self.dataframe.columns)
        self.assertNotIn('temp_col', self.dataframe.columns)

    def test_no_columns_to_remove(self):
        """
        Teste le comportement lorsque aucune colonne n'est spécifiée pour être supprimée.
        """
        # Utiliser TemporaryColumnsManager sans colonnes à supprimer
        with TemporaryColumnsManager(self.dataframe, keep=['col1', 'col2']):
            self.dataframe['col3'] = [7, 8, 9]  # Ajouter une colonne pendant le bloc

        # Vérifier que toutes les colonnes initiales sont conservées et aucune n'est supprimée
        self.assertIn('col1', self.dataframe.columns)
        self.assertIn('col2', self.dataframe.columns)
        self.assertNotIn('col3', self.dataframe.columns)

    def test_no_columns_to_keep(self):
        """
        Teste que les colonnes temporaires sont supprimées si aucune colonne n'est spécifiée pour être gardée.
        """
        # Utiliser TemporaryColumnsManager sans colonnes à garder
        with TemporaryColumnsManager(self.dataframe, drop=['temp_col']):
            self.assertIn('temp_col', self.dataframe.columns)

        # Vérifier que la colonne temporaire a été supprimée après le bloc
        self.assertNotIn('temp_col', self.dataframe.columns)

    def test_existing_columns_not_removed(self):
        """
        Teste que les colonnes existantes ne sont pas supprimées si elles ne sont pas spécifiées pour être supprimées.
        """
        # Utiliser TemporaryColumnsManager sans affecter les colonnes existantes
        with TemporaryColumnsManager(self.dataframe, keep=['col1', 'col2'], drop=['temp_col']):
            self.dataframe['temp_col'] = [7, 8, 9]

        # Vérifier que les colonnes existantes sont toujours présentes
        self.assertIn('col1', self.dataframe.columns)
        self.assertIn('col2', self.dataframe.columns)
        # La colonne temporaire doit avoir été supprimée
        self.assertNotIn('temp_col', self.dataframe.columns)


if __name__ == '__main__':
    unittest.main()
