## INTRODUCTION

### Qu'est ce un appel de fonction?

    Les grand modeles de langage(LLMs)  ont le pouvoir de la comprendre et de la generer le langage humain,  mais ils ne produisent pas naturellement de sortie structure et executable pour la machine.
    L'appel de fonctions comble cette lacune en traduisant les requêtes en langage naturel en appels de fonctions précis avec des arguments typé.

exemple de langage naturel d'appel de fonction:

```python
User: "What is the sum of 40 and 2?"
Traditional LLM: "The sum of 40 and 2 is 42."
Function Calling System:
{
"function": "add_numbers",
"arguments": {"a": 40.0, "b": 2.0}
}
```

Le systeme d'appel de fonction ne repond pas directement a la question. il fournit les outils pour le resoudre: le nom de la fonction approprie et les arguments correctes avec des types adequates.

### Pourquoi est ce important?

L'appel de fonction permet au LLMs de:
 
- **interagir avec les systemes externes:** appel APIs, interroger des bases de donnees, controles des peripheriques
- **executer du code:** effectuer des calculs, des transformations des donnees, et des operations sur les fichiers
- **Opérations en chaîne :** Décomposer les tâches complexes en étapes exécutables
- **Fournir une sortie structurée :** générer du JSON, du XML ou d’autres formats lisibles par machine
- **Extraire des données structurées à partir de textes non structurés**: pour exemple, dans un grand livre, extraire des champs tel que {nom du protagoniste, sexe du protagoniste, âge du protagoniste}

Cette technologie alimente les assistants IA modernes, les outils de génération de code et les agents autonomes, tout en permettant des tâches telles que l'extraction automatique d'informations et la structuration des connaissances à partir de textes bruts.

### Le challenge

Les modeles de petit langage (comme le modele 0.6 milliards de parametre  que tu utilisera) sont peu fiables pour générer des résultats structurés. Quand on leur demande de produire du JSON, ils n'y parviennent que dans 30 % des cas. ourtant, les systèmes de production atteignent une fiabilité supérieure à 99 % avec ces mêmes petits modèles.

**Comment ?** La réponse réside dans le décodage contraint — une technique qui guide la sortie du modèle token par token pour garantir une structure valide, sans se fier uniquement aux instructions.

## Instructions

### Regles generales
- Pyhton 3.10 ou plus
- flake8
- Gestion des exceptions, utliser try-except pour les erreurs potentiels
- Toutes les ressources (par exemple, les descripteurs de fichiers, les connexions réseau) doivent être correctement gérées afin d'éviter les fuites. Utilisez des gestionnaires de contexte  *(with open("data.json", "r")* as f)lorsque cela est possible pour une gestion automatique.
- otre code doit inclure des annotations de type pour les paramètres de fonction, les types de retour et les variables, utiliser mypy
- Incluez des chaînes de documentation dans les fonctions et les classes suivant la PEP 257 (par exemple, le style Google ou NumPy) pour documenter leur objectif, leurs paramètres et leurs valeurs de retour.


### Makefile
- install ( pip, uv, pipx)
- run
- debug
- clean 
- lint Execute the commands flake8 . and mypy . --warn-return-any
--warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs
--check-untyped-def
-  lint-strict (optional): Execute the commands flake8 . and mypy . --strict

### Directives supplementaires
- creer des programmes tests pour verifier la fonctionnalite du projet. Utilisez des frameworks comme pytest ou unittest pour les tests unitaires, en couvrant les cas limites.
- .gitignore 
- recommende  d'utiliser un environnement virtuel pour isoler les dependences

- classes doivent utiliser `pydantic`
- peut utiliser packages `json et numpy`
- utilisation de `dspy` est interdite (pytorch, huggingface package, transformers, outlines)
- jaurai besoin d'utiliser les models suivant:
        -`Qwen/Qwen3-0.6B (default)`
        - peut utiliser d'autres modèles à condition que votre projet soit compatible avec Qwen/Qwen3-0.6B
- La fonction à appeler doit être choisie à l'aide du LLM
- interdit d'utiliser des méthodes ou des attributs privés du package `llm_sdk`.
- doit creer un environnement virtuel et installer les packages `numpy` et `pydanti`c qui utilise `uv`. utiliser `llm_sdk`, tu peux le copier dans le meme dossier que dans celui `src`.
- Le testeur, ainsi que la moulinette, exécuteront simplement `uv sync`

Le programme doit être exécuté à l'aide de la commande suivante:
`uv run python -m src [--functions_definition <function_definition_file>] [--input <input_file>] [--
output <output_file>]`

**Par défaut, le programme lira les fichiers d'entrée depuis le répertoire data/input/ et écrira les fichiers de sortie dans le répertoire data/output/. Vous pouvez spécifier des chemins personnalisés à l'aide des arguments --input et --output.**