import sys
from llm_sdk import Small_LLM_Model
import numpy
import json


def ft_vocab_inverse(vocab: dict) -> dict:
    inverse = {}
    for key, value in vocab.items():
        inverse[value] = key
    return inverse


def create_text(input_text: object, list_functions: list) -> str:
    prompt = "\nQuestion: " + input_text.prompt
    funct_desc = []
    funct_desc.append("Functions: ")
    for f in list_functions:
        funct_desc.append(f"- {f.name}: {f.description}")

    new_text = "\n".join(funct_desc)
    new_text = "\n".join([new_text, prompt, "Function to call: "])
    return new_text


def rules_name_function(candidat: str, functions: list) -> bool:
    return any(function.startswith(candidat) for function in functions)


def rules_number_parameters(text: str, fucntions: list) -> bool:
    for c in text:
        if c not in "0123456789.-}," or text[0] == "." or text.count(".") > 1:
            return False
    return True


def rules_string_parameters(text: str) -> bool:
    if not text.isascii():
        return False
    return True


def constrained_decoding(model: object, token: list, vocab_inverse: dict, generated: str,
                        functions: list, mode: str) -> int:
    # le LLM lit toute la liste d’ids et donne une note 
    # à chaque token possible du vocabulaire”
    logits = model.get_logits_from_input_ids(token)

    for pos in range(len(logits)):
        # le .get eevite les edge case si l'id du logits est au dessus du nombre 
        # d'id dans le vocab du llm, ca en cree un "" qui sera en -inf juste apres        
        text_vocab = vocab_inverse.get(pos, "")

        if mode == "string":
            rule = rules_string_parameters(generated + text_vocab)
        elif mode == "number":
            rule = rules_number_parameters((generated + text_vocab), functions)
        else:
            rule = rules_name_function((generated + text_vocab), functions)

        # permet de mettre -inf a tous les ids des notes qui en correspondent 
        # pas a ce qui il y a dans les token de la string prompt + function 
        if text_vocab == "" or rule == False:
            logits[pos] = -numpy.inf

    # argmax permet de chercher la position du logits max dans les token
    # next_id recupere l'id du logits max
    next_id = int(numpy.argmax(logits))
    return next_id


def write_parameter(parameters: dict, token: list, vocab_inverse: dict, model: object, functions: list) -> dict:
    result = {}
    for key, value in parameters.items():
        mode = value.type
        # ecriture du code JSON
        if not result:
            text = '{"' + key + '": '
        else:
            text = ',"' + key + '": '

        if mode == "string":
            text += '"'

        # texte deviens token puis ajout avec extend a ce que lit le model
        token.extend(model.encode(text).tolist()[0])

        # model ecrit la valeur
        generated = ""
        nbr_tour = 0
        while "}" not in generated and "," not in generated and generated.count('"') < 1 and nbr_tour < 20:
            next_id = constrained_decoding(model, token, vocab_inverse, generated, functions, mode)
            nbr_tour += 1
            token.append(next_id)
            token_str = model.decode(next_id)
            generated = generated + token_str
            new = generated.rstrip('",}')

        # range la valeur
        result[key] = new
        if mode == "number":
            result[key] = float(new)
    return result

        
def transorm_text_in_numero(list_input: list, list_functions: list) -> None :
# 1. encode    : la question devient une liste d'ids
#                 "Reverse the string..." → [45695, 279, 914, ...]
#  2. LLM       : il lit toute la liste et donne une note
#                 à chaque token du vocabulaire (~150 000 notes)
#  3. argmax    : la position de la meilleure note
#                 = l'id du token le plus probable pour la suite
#  4. append    : on ajoute cet id à la fin de la liste
#  5. on recommence à l'étape 2 avec la liste plus longue
    model = Small_LLM_Model()
    functions = []
    for f in list_functions:
        functions.append(f.name)

    path_vocab = model.get_path_to_vocab_file()
    with open(path_vocab) as file:
        vocab = json.load(file)

    vocab_inverse = ft_vocab_inverse(vocab)
    for id, vocab in vocab_inverse.items():
        vocab_inverse[id] = vocab.replace("Ġ", " ")

    for prompt in list_input:
        text_functions = create_text(prompt, list_functions)
        tokens = model.encode(text_functions)
        # tolist permet de reduire en liste
        tokens = tokens.tolist()
        # tokens[0] recuperere la liste interieur qui contiens tous les ids de la phrase
        token = tokens[0]

        generated = ""

        nbr_tour = 0
        while generated not in functions and nbr_tour < 20 :
            next_id = constrained_decoding(model, token, vocab_inverse, generated, functions, "name")
            nbr_tour += 1
            token.append(next_id)
            token_str = model.decode(next_id)
            generated = generated + token_str

        print(f"prompt:{prompt.prompt}")
        print(f"generer: {generated}")
        if generated not in functions:
            print(f"Error: {generated} is not in functions list")

        for f in list_functions:
            if generated == f.name:
                result = write_parameter(f.parameters, token, vocab_inverse, model, functions)
        print(result)
        
        

    