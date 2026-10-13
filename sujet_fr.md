## INTRODUCTION

### Qu'est ce un appel de fonction?

    Les grand modeles de langage(LLMs) ont le pouvoir de la comprendre et de la generer le langage humain,  mais ils ne produisent pas naturellement de sortie structure et executable pour la machine.
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
- recommande  d'utiliser un environnement virtuel pour isoler les dependences
- classes doivent utiliser `pydantic`
- peut utiliser packages `json et numpy`
- utilisation de `dspy` est interdite (pytorch, huggingface package, transformers, outlines)
- jaurai besoin d'utiliser les models suivant:
        -`Qwen/Qwen3-0.6B (default)`
        - peut utiliser d'autres modèles à condition que votre projet soit compatible avec Qwen/Qwen3-0.6B
- La fonction à appeler doit être choisie à l'aide du LLM
- interdit d'utiliser des méthodes ou des attributs privés du package `llm_sdk`.
- doit creer un environnement virtuel et installer les packages `numpy` et `pydantic` qui utilise `uv`. utiliser `llm_sdk`, tu peux le copier dans le meme dossier que dans celui `src`.
- Le testeur, ainsi que la moulinette, exécuteront simplement `uv sync`

Le programme doit être exécuté à l'aide de la commande suivante:
`uv run python -m src [--functions_definition <function_definition_file>] [--input <input_file>] [--
output <output_file>]`

**Par défaut, le programme lira les fichiers d'entrée depuis le répertoire data/input/ et écrira les fichiers de sortie dans le répertoire data/output/. Vous pouvez spécifier des chemins personnalisés à l'aide des arguments --input et --output.**

`uv run python -m src/
--functions_definition data/input/functions_definition.json/
--input data/input/function_calling_tests.json/
--output data/output/function_calls.json`/


## Partie obligatoire

### sommaire
dans ce projet, tu devra creer un outil d'appel de fonction qui traduit le prompt en langage naturel en appel de fonctions structure


















s. donne une question comme "quelle est la somme de 40 et de 2?", ta solution ne devra pas retourner 42 mais fournir:
- le nom de la fonction: fn_add_numbers
- les arguments: {"a": 40.0, "b": 2.0}

l'implementation devra utiliser un décodage contraint pour garantir une sortie JSON 100 % valide, assurant une fiabilité quasi parfaite même avec un petit modèle de paramètres de 0,6 milliard.

### fichiers d'entree

Votre solution traitera 2 fichiers d'entree situes dans le dossier **data/input/**

- **function_calling_tests.json :** contient un tableau JSON d’invites en langage naturel que votre système doit traiter.

Exemple: 
```python
[
{
"prompt": "What is the sum of 2 and 3?"
},
{
"prompt": "What is the sum of 265 and 345?"
},
{
"prompt": "Greet shrek"
},
{
"prompt": "Greet john"
},
{
"prompt": "Reverse the string 'hello'"
},
...
]

```

- **functions_definition.json:** contient les fonctions disponibles que votre système peut appeler. Chaque fonction comprend :
    - nom de fonction
    - noms et types des arugments
    - type de retour
    - description

    exemple:
```python
[
    {
    "name": "fn_add_numbers",
    "description": "Add two numbers together and return their sum.",
    "parameters": {
            "a": {
                "type": "number"
            },
            "b": {
                "type": "number"
            }
            },
            "returns": {
                "type": "number"
            }
            },
        {
            "name": "fn_greet",
            "description": "Generate a greeting message for a person by name.",
            "parameters": {
            "name": {
            "type": "string"
            }
        },
        "returns": {
        "type": "string"
        }
    },
    {
        "name": "fn_reverse_string",
        "description": "Reverse a string and return the reversed result.",
        "parameters": {
        "s": {
        "type": "string"
        }
    },
    "returns": {
        "type": "string"
        }
    },
    ...
]
```

` Ces exemples définissent le niveau de complexité attendu. Cependant, votre solution sera testée avec différentes invites et ensembles de fonctions. Vous devez implémenter une gestion correcte des erreurs JSON pour les fichiers d'entrée, car ils peuvent contenir du JSON invalide ou être totalement manquants.`


## LLM interaction

### le LLM SDK

Lie a ce projet, tu trouvera une class wrapper **Small_LLM_Model** dans le package **llm_sdk**  que ttu peux utiliser pour interagir avec la LLM.

Le SDK fournit plusieurs methodes essentielles:
    - **get_logits_from_input_ids(input_ids: List[int]) -> List[float]**
    Prends une liste d IDs token et retourne les logits produitent par le LLM.
    - **get_path_to_vocab_file() -> str**
    Renvoie le chemin d'accès au fichier de vocabulaire contenant la correspondance entre les IDs des token et les token eux-même.
    -  **encode(text: str) -> Tensor**
    Encode une str en un tenseur d'IDs de token utilisant le model tokenizer
    - **decode(token_ids: List[int])** -> str(optional)
    En option, permet de décoder une liste d'IDs de tokent pour la reconvertir en une str.

### Pipeline

Le processus de génération LLM suit les étapes suivantes :
1. **Prompt**: ta question en langage normal
    Exemple: "Quelle est la somme de 2 et 3?"

2. **Tokenization** : le text est divivse en unite de token. Contrairement à la simple segmentation des mots, les tokeniseurs incluent souvent des espaces en début de mot, gèrent la ponctuation et divisent les mots en composants plus petits à l'aide d'algorithmes tels que **BPE** ou **SentencePiece**
    Exemple: ["**What", "Gis ˙ ", "Gthe ˙ ", "Gsum ˙ ", "Gof ˙ ", "G2˙ ", "Gand ˙ ", "G3˙ ", "?"]**
    Remarque : Le symbole « ˙G » indique un espace précédent ; les analyseurs lexicaux performants préservent ces détails pour reconstruire le texte avec précision.

3. **IDs d'entree:**: les token sont convertis en identifiants numériques compréhensibles par le modèle. 
    Exemple : [892, 318, 262, 4771, 286, 16, 290, 17, 30]

4. **Processus LLM :** Le modèle traite ces nombres via son réseau neuronal.

5. **Logits**: Le modèle génère des scores de probabilité pour chaque token suivant possible. 
    Exemple : token_5 : 0,001, token_42 : 0,85, token_100 : 0,02, …

6. **Selection des token**: le token suivant est choisi en fonction de ces probabilités, généralement celui qui a le score le plus élevé.\
*À ce stade, des techniques comme le ****constrained decoding**** peuvent être appliquées pour restreindre les choix de token et garantir que les sorties suivent une structure spécifique, comme la génération d'un JSON 100 % valide.*


`⚠️ Ce processus se repete jeton par jeton. chaque jeton genere est ajoute au prompt, et les étapes 2 à 6 se répètent jusqu'à ce que la réponse complète soit générée.`

**Vue simplifiee** :
            `Prompt -> Tokenization -> Input IDs -> LLM -> Logits -> Next Token Selection`

### Comprehension CONSTRAINED DECODING

Les modeles de langage genere du texte un token a la fois. A chaque etape, le modele produit  une probalitite de distribution (logits) sur tous les token suivants. Normallement, on effectuerait un échantillonnage à partir de cette distribution ou on choisirait le token ayant la probabilité la plus élevée.

**Constrained decoding** intervient dans ce processus en modifiant les logits avant la selection des token:
1. Le modele produit des logits pour tous les token possibles
2. Vous identifiez les TOKEN qui maintiendraient à la fois une structure JSON valide et la conformité au schéma attendu.
3. Vous définissez les logits pour les token invalides (ceux qui enfreignent le schéma ou la structure) à l'infini négatif (-inf)
4. Vous ne prélevez qu'un échantillon des token valides restants.

Dans ce projet, **constrained deconding** doit non seulement garantir un JSON syntaxiquement valide, mais aussi imposer un schéma spécifique. Par exemple, si un champ est limité à un nombre dans `functions_definition.json`, le décodeur restreint la sélection des token aux valeurs de type flottant, préservant ainsi la validité JSON et la conformité au schéma.
Ca garantit que chaque token generes maintient une valditite structurelle et semantique, tout en respectant le shema requis. Par conséquent, le JSON produit est récupérable à 100 % et peut toujours être analysé sans erreur.

`Réfléchissez à la manière dont vous pouvez utiliser le fichier JSON du vocabulaire pour établir une correspondance entre les tokent et leurs représentations textuelles. Ceci est essentiel pour déterminer quels token sont valides à chaque étape de génération.`
 
## format du fichier de sortie

Le programme devra produire un fichier seul JSON: data/output/functions_calls.json
Pour chaque prompt, ajouter un objet JSON a ce fichier. Chaque objet dans le tableau doit contenir exactemment les clees suivantes:
    - **prompt** (string): La requête originale en langage naturel
    - **name** (string): le nom de la fonction a appeler
    - **parametres** (objet): Tous les arguments requis avec les types corrects

Exemple de sortie: 

```python
[
    {
    "prompt": "What is the sum of 2 and 3?",
    "name": "fn_add_numbers",
    "parameters": {"a": 2.0, "b": 3.0}
    },
    {
    "prompt": "Reverse the string 'hello'",
    "name": "fn_reverse_string",
    "parameters": {"s": "hello"}
    }
]
```

### Regles de validation

- Le fichier doit etre  un JSON valide (sans virgules finales, sans commentaires )
- cles et types doivent correspondre exactement au schema dans **function_definition.json**
- Aucun texte supplémentaire ni aucune prose ne sont autorisés dans le résultat. 
- Tous les arguments requis doivent être présents.
- Les types d'arguments doivent correspondre à la définition de la fonction (nombre, chaîne de caractères, booléen, etc.).

`Les fichiers d'entrée fournis peuvent être modifiés lors de l'évaluation par les pairs. Veuillez ne pas reproduire fidèlement les solutions proposées dans les exemples fournis.`

## Performance et fiabilite

ton implementation doit permettre d'atteindre:
- **Precision quasi parfaite:** Sélection de fonctions et extraction d'arguments correctes à plus de 90 %
- **100% JSON valid:**chaque sortie doit être analysable et conforme au schéma.
- **Vitesse raisonnable:** Traiter toutes les prompt de test en moins de 5 minutes sur un matériel standard
- **Gestion des erreurs robustes**: gerer les entrees malfaites, oublie de fichiers, et cas limites

`⚠️ Le modèle Qwen3-0.6B ne compte que 500 millions de paramètres, mais grâce à un décodage contraint approprié, il atteint une fiabilité comparable à celle de modèles beaucoup plus volumineux. Ceci démontre l'importance du guidage structurel par rapport à la taille brute du modèle.`

## Tester l'implementation

Pour vérifier que votre solution fonctionne correctement : 
    1. Assurez-vous que les fichiers d'entrée se trouvent dans le répertoire data/input/.
    2. Exécutez : uv run python -m src [–functions_definition <fichier_de_définition_fonction>] [–input <fichier_entrée>] [–output <fichier_sortie>]. 
    3. Vérifiez que le fichier output/function_calls.json est créé. 
    4. Validez la structure et le contenu du fichier JSON. 
    5. Vérifiez que les noms des fonctions et les types des arguments correspondent aux définitions. 
    
    `Testez avec différents cas limites : chaînes vides, grands nombres, caractères spéciaux, types incorrects, invites ambiguës, etc.…`

## README