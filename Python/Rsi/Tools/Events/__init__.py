# Events/__init__.py

# Importer explicitement les classes, fonctions, etc., que vous voulez exposer
from .EventStore import *
from .GenericEvent import *

# Définir __all__ pour exporter ces noms spécifiques
__all__ = ['EventStore',
           'GenericEvent']
