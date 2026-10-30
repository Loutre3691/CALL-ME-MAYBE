*Ce projet a été réalisé dans le cadre du cursus 42 par fde-chec.*
 
# CALL ME MAYBE
 
## 📖 Description
 
**Call me maybe** est une introduction au *function calling* (appel de fonctions) avec les LLM.
 
Le programme reçoit des questions écrites en langage naturel (par exemple *"What is the sum of 2 and 3?"*) et, au lieu d'y répondre, il traduit chaque question en un appel de fonction structuré :
 
```json
{
  "prompt": "What is the sum of 2 and 3?",
  "name": "fn_add_numbers",
  "parameters": {"a": 2.0, "b": 3.0}
}
```
 
Deux fichiers JSON sont donnés en entrée :
- `functions_definition.json` : la liste des fonctions disponibles (nom, description, paramètres et leurs types)
- `function_calling_tests.json` : la liste des questions à traiter
Le modèle utilisé est **Qwen3-0.6B**, un petit LLM qui n'est pas fiable quand on lui demande simplement de produire du JSON. Pour garantir une sortie valide à 100 %, le projet utilise le **décodage contraint** (*constrained decoding*) : à chaque étape de la génération, les tokens qui casseraient la structure JSON ou le schéma attendu sont interdits, donc le LLM ne peut choisir que parmi des tokens valides.
 
---
 
## ⚙️ Instructions
 
### 📦 Installation
 
Prérequis :
 
* Python 3.10+
* le gestionnaire de paquets `uv`
* flake8 7.3.0
* mypy 1.20.2
* pydantic 2.13.3
* pytest 9.0.3
Installer les dépendances :
 
```bash
make install
```
 
### ▶️ Lancer le projet
 
Avec les chemins par défaut (`data/input/` et `data/output/`) :
 
```bash
make run
```
 
Avec des chemins personnalisés :
 
```bash
uv run python -m src \
    --functions_definition data/input/functions_definition.json \
    --input data/input/function_calling_tests.json \
    --output data/output/function_calls.json
```
 
### 🎁 Lancer le bonus
 
```bash
uv run python python -m src --visualiser
uv run pytest
```
 
### 🛠 Commandes disponibles
 
| Commande           | Description                              |
| ------------------ | ---------------------------------------- |
| `make run`         | Lance le programme de function calling   |
| `make install`     | Prépare l'environnement                  |
| `make debug`       | Lance avec le débogueur (pdb)            |
| `make clean`       | Supprime le cache et le venv             |
| `make lint`        | Vérification du code (flake8 + mypy)     |
| `make lint-strict` | Vérification stricte des types           |
 
---
 
## 🧠 Explication de l'algorithme : le décodage contraint
 
Un LLM écrit **un token à la fois**. À chaque étape, il renvoie une liste de **logits** : un score pour chaque token de son vocabulaire. Normalement, on choisit le token qui a le score le plus élevé.
 
Sans aucune contrainte, le modèle peut donner un score élevé à un token qui n'a aucun sens pour notre tâche (du texte avant le JSON, un nom de fonction qui n'existe pas, une lettre là où on attend un nombre...).
 
Le décodage contraint fonctionne comme un **formulaire à trous** :
 
```
{"name": "______", "parameters": {"a": ____, "b": ____}}
          ▲                             ▲         ▲
          trou 1                        trou 2    trou 3
```
 
- Les **parties fixes** (accolades, clés, guillemets, virgules) sont écrites par le programme lui-même.
- Les **trous** sont remplis par le LLM, mais uniquement avec des tokens autorisés par les règles.
À chaque étape :
1. Le modèle produit les logits pour tous les tokens.
2. Le programme vérifie, grâce au fichier de vocabulaire, quels tokens sont valides à cette position.
3. Les logits de tous les tokens invalides sont mis à `-inf`.
4. On choisit le token qui a le plus haut score parmi ceux qui restent.
Règles utilisées pour les trous :
- **Nom de fonction** : le texte en cours de génération doit toujours être le début d'un nom de fonction existant dans `functions_definition.json`.
- **Paramètres de type nombre** : seuls les chiffres, `-` et `.` sont autorisés, pour que la valeur puisse toujours être convertie en float.
- **Paramètres de type chaîne** : la valeur est générée jusqu'au guillemet fermant.
Ainsi, la sortie est toujours un JSON lisible qui respecte le schéma.
 
---
 
## 🏗 Choix de conception
 
- Le code est découpé en 3 fichiers, chacun avec un rôle clair :
  - `parsing.py` : lit et valide les fichiers JSON d'entrée (avec pydantic)
  - `generator.py` : l'interaction avec le LLM et le décodage contraint
  - `__main__.py` : les arguments de la ligne de commande et le déroulement principal
- `generator.py` reste assez court pour garder toute la logique de génération dans un seul fichier, ce qui le rend plus facile à lire.
- Le JSON est construit comme un formulaire à trous : le programme écrit la structure, le LLM ne remplit que les valeurs. Cela garantit la structure sans dépendre du prompt.
- Chaque règle (nom de fonction, nombre, chaîne) ne s'applique qu'à son propre trou, donc une règle ne bloque jamais les tokens valides d'un autre trou.
---
 
## 📊 Analyse des performances
 
- **Précision** : XX / XX prompts corrects (XX %). Le sujet demande 90 % ou plus.
- **Vitesse** : tous les prompts sont traités en XX secondes, sous les 5 minutes demandées. Pour le mesurer :
```bash
  time make run
```
- **Fiabilité** : grâce au décodage contraint, 100 % des sorties sont du JSON valide.
---
 
## 🧗 Difficultés rencontrées
 
- **La génération des paramètres** a été la partie la plus difficile : chaque type (nombre, chaîne) a besoin de ses propres règles, et trouver ces règles n'a pas été naturel au début.
- **Des règles appliquées au mauvais moment** : à un moment, la règle du nom de fonction et la règle des paramètres étaient appliquées en même temps, ce qui bloquait des tokens valides comme les chiffres. Séparer les règles pour chaque trou a réglé le problème.
- **Des plantages sur les nombres** : des valeurs comme `""` ou `"-"` faisaient planter `float()`. Ces cas sont maintenant gérés.
- **Des listes vides dans le parsing** : repérées grâce aux tests pytest, maintenant gérées.
---
 
## 🧪 Stratégie de test
 
- Des **prints** pendant le développement pour suivre la génération token par token.
- Des tests **pytest** (bonus), dans le dossier `tests/` :
  - `test_load_json.py` : fichier manquant, JSON invalide, fichier vide
  - `test_parsing.py` : validation des données d'entrée
  - `test_generator.py` : les données générées
- **Cas limites** testés : chaînes vides, nombres négatifs, caractères spéciaux, listes vides.
---
 
## 🎁 Bonus
 
- **Visualiseur** : montre dans le terminal comment le LLM avance étape par étape pendant la génération.
- **Suite de tests** avec pytest, qui a aussi aidé à trouver des erreurs non gérées (par exemple une liste vide dans le parsing).
---
 
## 📂 Structure du projet
 
```
README.md
Makefile
pyproject.toml
uv.lock
src/
    __main__.py
    parsing.py
    generator.py
tests/
    test_load_json.py
    test_parsing.py
    test_generator.py
llm_sdk/        (fourni par le sujet)
data/input/     (fourni par le sujet)
```
 
---
 
## 💡 Exemple d'utilisation
 
Entrée (`function_calling_tests.json`) :
 
```json
[
  {"prompt": "What is the sum of 2 and 3?"},
  {"prompt": "Reverse the string 'hello'"}
]
```
 
Sortie (`data/output/function_calls.json`) :
 
```json
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
 
---
 
## 📚 Ressources
 
- **Modules Python de 42** : j'y suis régulièrement retournée pour mettre en place le code et revoir des notions que j'avais oubliées.
- **IA** : utilisée pour comprendre les concepts clés (LLM, tokens, logits, décodage contraint), pour relire `generator.py`, pour trouver des cas limites (chaînes vides, nombres négatifs, listes vides), et pour aider à écrire et traduire ce README. Je l'ai très peu utilisée au début, puis davantage vers la fin, surtout pour vérifier mes idées avant de partir trop loin dans la mauvaise direction.
- **Camarades** : explications sur le projet et le sujet.
- **Documentation Pydantic** : https://docs.pydantic.dev
 
Claude a terminé sa réponse.
