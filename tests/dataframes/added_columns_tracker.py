import unittest

from pandas import DataFrame

from framework.dataframes.added_columns_tracker import AddedColumnsTracker


class TestAddedColumnsTracker(unittest.TestCase):

    def setUp(self):
        """
        Initialisation avant chaque test.
        Crée un DataFrame et un ensemble vide pour stocker les nouvelles colonnes.
        """
        # Créer un DataFrame initial avec des colonnes
        self.dataframe = DataFrame({
            'col1': [1, 2, 3],
            'col2': [4, 5, 6]
        })

        # Initialiser un ensemble vide pour suivre les nouvelles colonnes
        self.target_set = set()

    def test_add_columns(self):
        """
        Teste l'ajout de nouvelles colonnes et vérifie que AddedColumnsTracker capture ces colonnes.
        """
        # Utiliser AddedColumnsTracker dans un bloc 'with'
        with AddedColumnsTracker(self.dataframe, self.target_set):
            # Ajouter de nouvelles colonnes pendant le bloc
            self.dataframe['col3'] = [7, 8, 9]
            self.dataframe['col4'] = [10, 11, 12]

        # Vérifie que les nouvelles colonnes sont ajoutées à l'ensemble cible
        self.assertIn('col3', self.target_set)
        self.assertIn('col4', self.target_set)

    def test_no_new_columns(self):
        """
        Teste le cas où aucune nouvelle colonne n'est ajoutée pendant le bloc.
        """
        # Utiliser AddedColumnsTracker dans un bloc 'with' sans ajouter de nouvelles colonnes
        with AddedColumnsTracker(self.dataframe, self.target_set):
            pass  # Ne rien faire

        # Vérifie que l'ensemble cible est toujours vide (aucune nouvelle colonne ajoutée)
        self.assertEqual(len(self.target_set), 0)

    def test_add_columns_after_block(self):
        """
        Teste l'ajout de colonnes après la fin du bloc 'with', pour vérifier que celles-ci ne sont pas capturées.
        """
        # Utiliser AddedColumnsTracker dans un bloc 'with'
        with AddedColumnsTracker(self.dataframe, self.target_set):
            # Ajouter une colonne pendant le bloc
            self.dataframe['col3'] = [7, 8, 9]

        # Ajouter une colonne après la fin du bloc
        self.dataframe['col4'] = [10, 11, 12]

        # Vérifie que seule la colonne 'col3' a été ajoutée pendant le bloc
        self.assertIn('col3', self.target_set)
        self.assertNotIn('col4', self.target_set)

    def test_initial_columns_not_tracked(self):
        """
        Teste que les colonnes initiales du DataFrame ne sont pas capturées comme nouvelles colonnes.
        """
        # Utiliser AddedColumnsTracker dans un bloc 'with'
        with AddedColumnsTracker(self.dataframe, self.target_set):
            # Ajouter une nouvelle colonne
            self.dataframe['col3'] = [7, 8, 9]

        # Vérifie que les colonnes initiales ne sont pas dans l'ensemble cible
        self.assertNotIn('col1', self.target_set)
        self.assertNotIn('col2', self.target_set)
        self.assertIn('col3', self.target_set)


if __name__ == '__main__':
    unittest.main()
