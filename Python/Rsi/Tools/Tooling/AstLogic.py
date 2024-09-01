import ast
import operator
from functools import reduce


class AstLogic:
    """
    Classe AstLogic pour évaluer des expressions logiques contenues dans une chaîne de caractères.

    Cette classe utilise le module `ast` de Python pour analyser les expressions en arbres syntaxiques
    et les évalue en utilisant des opérateurs logiques. Les variables utilisées dans l'expression peuvent
    être fournies via un dictionnaire.
    """

    def __init__(self, variables: dict, expression: str):
        """
        Initialise une instance de AstLogic.

        Args:
            variables (dict): Un dictionnaire contenant les variables et leurs valeurs pour l'évaluation.
            expression (str): L'expression logique sous forme de chaîne à évaluer.
        """
        self.variables = variables  # Dictionnaire des variables et leurs valeurs
        self.expression = expression  # Expression logique à évaluer

    def eval_expr(self) -> bool:
        """
        Évalue l'expression logique stockée dans l'instance en utilisant ast et operator.

        Returns:
            bool: Résultat de l'évaluation de l'expression logique.
        """
        # Opérateurs logiques disponibles
        operators = {
            ast.And: operator.and_,  # Opérateur logique ET
            ast.Or: operator.or_,  # Opérateur logique OU
            ast.Not: operator.not_  # Opérateur logique NON
        }

        # Analyse de l'expression en un arbre syntaxique
        tree = ast.parse(self.expression, mode='eval').body

        # Fonction récursive pour évaluer l'arbre syntaxique
        def eval_(node):
            if isinstance(node, ast.BoolOp):
                # Récupère l'opérateur correspondant (ET ou OU)
                op = operators[type(node.op)]
                # Applique l'opérateur sur toutes les valeurs enfants de l'opérateur booléen
                return reduce(op, (eval_(v) for v in node.values))
            elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
                # Applique l'opérateur NON sur l'opérande
                return operators[ast.Not](eval_(node.operand))
            elif isinstance(node, ast.Name):
                # Retourne la valeur de la variable du dictionnaire ou False si non définie
                return self.variables.get(node.id, False)
            else:
                # Lève une exception si le type de nœud n'est pas supporté
                raise TypeError(f'Unsupported type : {type(node)}')

        # Évaluation de l'arbre syntaxique avec le contexte des variables
        return eval_(tree)
