"""Génération des appels de fonction par décodage contraint du LLM."""

from typing import Any
from llm_sdk import Small_LLM_Model  # type: ignore[attr-defined]
from src.parsing import ParsingInput, ParsingFunction
import numpy
import json
import os

MAX_NAME_TOKENS = 20
MAX_TOKENS = 100


def ft_vocab_inverse(vocab: dict[str, int]) -> dict[int, str]:
    """Inverse le vocabulaire : (token -> id) devient (id -> token).

    Args:
        vocab: vocabulaire du modèle, associe chaque token à son id.

    Returns:
        Le dictionnaire inversé, qui associe chaque id à son token.
    """
    inverse: dict[int, str] = {}
    for key, value in vocab.items():
        inverse[value] = key
    return inverse


def create_text(input_text: ParsingInput,
                list_functions: list[ParsingFunction]) -> str:
    """Construit le texte envoyé au LLM pour une question donnée.

    Le texte contient la liste des fonctions disponibles (nom et
    description), la question, puis l'amorce « Function to call: ».

    Args:
        input_text: le prompt de l'utilisateur.
        list_functions: les fonctions que le LLM peut choisir.

    Returns:
        Le texte complet à encoder.
    """
    prompt = "\nQuestion: " + input_text.prompt
    funct_desc = []
    funct_desc.append("Functions: ")
    for f in list_functions:
        funct_desc.append(f"- {f.name}: {f.description}")

    new_text = "\n".join(funct_desc)
    new_text = "\n".join([new_text, prompt, "Function to call: "])
    return new_text


def rules_name_function(candidat: str, functions: list[str]) -> bool:
    """Indique si le candidat peut encore devenir un nom de fonction.

    Args:
        candidat: début de nom généré jusqu'ici (token testé inclus).
        functions: noms de fonctions autorisés.

    Returns:
        True si au moins un nom de fonction commence par le candidat.
    """
    return any(function.startswith(candidat) for function in functions)


def rules_number_parameters(text: str) -> bool:
    """Indique si le texte peut être le début d'un nombre JSON valide.

    Seuls les caractères « 0123456789.-}, » sont acceptés. Le texte ne
    doit pas commencer par un point, ni contenir deux points, ni un
    « - » ailleurs qu'au début. Les caractères « , » et « } »
    terminent le nombre et exigent au moins un chiffre avant eux.

    Args:
        text: valeur numérique générée jusqu'ici (token testé inclus).

    Returns:
        True si le texte est autorisé, False sinon.
    """
    for c in text:
        if c not in "0123456789.-}," or text[0] == "." or text.count(".") > 1:
            return False
        if "-" in text[1:]:
            return False

    number = text.rstrip(",}")

    if "," in number or "}" in number:
        return False

    if number != text and not any(c.isdigit() for c in number):
        return False
    return True


def create_list_json(result: dict[str, Any], list_json: list[dict[str, Any]],
                     generated: str, prompt: ParsingInput) -> dict[str, Any]:
    """Construit l'entrée JSON de sortie pour un prompt.

    Args:
        result: paramètres générés par le LLM.
        list_json: résultats déjà accumulés (non utilisé ici).
        generated: nom de la fonction choisie.
        prompt: le prompt d'origine.

    Returns:
        Un dict avec les clés « prompt », « name » et « parameters ».
    """
    dict_json = {
        "prompt": prompt.prompt,
        "name": generated,
        "parameters": result
    }

    return dict_json


def is_finished(generated: str, mode: str) -> bool:
    """Indique si la valeur générée est complète pour son type.

    Une chaîne est terminée dès qu'un guillemet fermant apparaît ;
    un nombre dès qu'une virgule ou une accolade fermante apparaît.

    Args:
        generated: valeur générée jusqu'ici.
        mode: type du paramètre ("string" ou "number").

    Returns:
        True si la valeur est terminée.
    """
    if mode == "string":
        if '"' not in generated:
            return False

    elif mode == "number" or mode == "integer":
        if "}" not in generated and "," not in generated:
            return False
    return True


def constrained_decoding(model: Small_LLM_Model, token: list[int],
                         vocab_inverse: dict[int, str], generated: str,
                         functions: list[str], mode: str) -> int:
    """Choisit le prochain token en masquant ceux qui sont interdits.

    Les logits des tokens qui ne respectent pas les règles du mode
    sont mis à -inf, puis on prend le token au logit maximal.

    Args:
        model: le modèle de langage.
        token: ids de tous les tokens lus par le modèle jusqu'ici.
        vocab_inverse: vocabulaire inversé (id -> texte).
        generated: texte déjà généré pour la valeur en cours.
        functions: noms de fonctions autorisés (mode "name").
        mode: "name", "number" ou "string".

    Returns:
        L'id du prochain token à ajouter.
    """
    # le LLM lit toute la liste d’ids et donne une note
    # à chaque token possible du vocabulaire”
    logits = model.get_logits_from_input_ids(token)

    for pos in range(len(logits)):
        # le .get eevite les edge case si l'id du logits est au dessus du
        # nombre d'id dans le vocab du llm, ca en cree un "" qui sera en
        # -inf juste apres
        text_vocab = vocab_inverse.get(pos, "")

        if mode == "string":
            rule = True
        elif mode == "number" or mode == "integer":
            rule = rules_number_parameters((generated + text_vocab))
        else:
            rule = rules_name_function((generated + text_vocab), functions)

        # permet de mettre -inf a tous les ids des notes qui en correspondent
        # pas a ce qui il y a dans les token de la string prompt + function
        if text_vocab == "" or not rule:
            logits[pos] = -numpy.inf

    # argmax permet de chercher la position du logits max dans les token
    # next_id recupere l'id du logits max
    next_id = int(numpy.argmax(logits))
    return next_id


def write_parameter(parameters: dict[str, Any], token: list[int],
                    vocab_inverse: dict[int, str], model: Small_LLM_Model,
                    functions: list[str], visualizer: bool) -> dict[str, Any]:
    """Génère les valeurs des paramètres d'une fonction, un par un.

    Écrit le JSON clé par clé, puis laisse le LLM générer chaque
    valeur sous contrainte (chaîne ou nombre).

    Args:
        parameters: paramètres de la fonction (nom -> type).
        token: ids lus par le modèle (modifié en place).
        vocab_inverse: vocabulaire inversé (id -> texte).
        model: le modèle de langage.
        functions: noms de fonctions autorisés.
        visualize: si True, affiche la génération en direct.

    Returns:
        Les paramètres générés (nom -> valeur).
    """
    result: dict[str, Any] = {}
    generated = ""
    for key, value in parameters.items():
        mode = value.type
        # ecriture du code JSON
        if not result:
            text = '{"' + key + '":'
        elif generated.endswith(","):
            text = '"' + key + '":'
        else:
            text = ',"' + key + '":'

        if mode == "string":
            text += '"'

        # texte deviens token puis ajout avec extend a ce que lit le model
        token.extend(model.encode(text).tolist()[0])

        generated = ""
        nbr_tour = 0
        if visualizer:
            print(text, end="", flush=True)
        while (nbr_tour < MAX_TOKENS and not is_finished(generated, mode)):
            next_id = constrained_decoding(model, token, vocab_inverse,
                                           generated, functions, mode)
            nbr_tour += 1
            token.append(next_id)
            token_str = model.decode(next_id)
            if visualizer:
                print(token_str, end="", flush=True)

            generated = generated + token_str

            if mode == "string":
                new = generated.split('"')[0]
            else:
                new = generated.rstrip('",}')

        if mode == "string":
            try:
                # json.loads() permet de gerer les \ pour le
                # output du regex avec les decimal \d+
                new = json.loads('"' + new + '"')
            except json.JSONDecodeError:
                print("Error: json text not valid")

        # range la valeur
        result[key] = new

        if mode == "number":
            try:
                result[key] = float(new)
            except ValueError:
                result[key] = 0.0
                print(f"Error: Convert {new} in int not possible")
                continue
        if mode == "integer":
            try:
                result[key] = int(new)
            except ValueError:
                result[key] = 0
                print(f"Error: Convert {new} in int not possible")
                continue

    return result


def transorm_text_in_numero(list_input: list[ParsingInput],
                            list_functions: list[ParsingFunction],
                            output_path: str, visualizer: bool) -> None:
    """Transforme chaque prompt en appel de fonction et l'écrit en JSON.

    Pour chaque prompt : le texte est encodé en ids, le LLM choisit le
    nom de la fonction puis ses paramètres (décodage contraint), et le
    résultat est sauvegardé dans le fichier de sortie.

    Args:
        list_input: prompts à traiter.
        list_functions: fonctions disponibles.
        output_path: chemin du JSON de sortie (dossiers créés au besoin).
        visualize: si True, affiche la génération en direct.
    """
    # 1. encode    : la question devient une liste d'ids
    #                 "Reverse the string..." → [45695, 279, 914, ...]
    #  2. LLM       : il lit toute la liste et donne une note
    #                 à chaque token du vocabulaire (~150 000 notes)
    #  3. argmax    : la position de
    #                 = l'id du token le plus probable pour la suite
    #  4. append    : on ajoute cet id à la fin de la liste
    #  5. on recommence à l'étape 2 avec la liste plus longue
    functions = []
    for f in list_functions:
        functions.append(f.name)

    if not functions:
        print("Error: prompt functions_definitions is empty")
        exit(1)

    try:
        model = Small_LLM_Model()
        path_vocab = model.get_path_to_vocab_file()

        with open(path_vocab) as file:
            vocab = json.load(file)

        vocab_inverse = ft_vocab_inverse(vocab)

    except Exception as e:
        print(f"Error: {e}")
        exit(1)

    for id, vocab in vocab_inverse.items():
        vocab_inverse[id] = vocab.replace("Ġ", " ")

    list_json: list[dict[str, Any]] = []
    for prompt in list_input:
        text_functions = create_text(prompt, list_functions)

        tokens = model.encode(text_functions)
        # tolist permet de reduire en liste
        tokens = tokens.tolist()
        # tokens[0] recuperere la liste interieur qui contiens tous les ids
        # de la phrase
        token = tokens[0]

        generated = ""

        nbr_tour = 0
        if visualizer:
            print()
            print(prompt.prompt)
        while generated not in functions and nbr_tour < MAX_NAME_TOKENS:
            next_id = constrained_decoding(model, token, vocab_inverse,
                                           generated, functions, "name")
            nbr_tour += 1
            token.append(next_id)
            token_str = model.decode(next_id)
            generated = generated + token_str
            # print flush=True force l’envoi immédiat
            if visualizer:
                print(token_str, end="", flush=True)

        if generated not in functions:
            print(f"Error: {generated} is not in functions list")
            continue

        for f in list_functions:
            if generated == f.name:
                result = write_parameter(f.parameters, token, vocab_inverse,
                                         model, functions, visualizer)

        list_json.append(create_list_json(result, list_json, generated,
                                          prompt))

    try:
        # os.makedirs -> create directory data/output
        directory = os.path.dirname(output_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(output_path, "w") as file:
            json.dump(list_json, file, indent=4, ensure_ascii=False)
    # OSError atrape filenotfounderror permissionerror et
    # isadirectoryerror ensemble
    except OSError as e:
        print(f"Error: {e} problem")
        exit(1)
