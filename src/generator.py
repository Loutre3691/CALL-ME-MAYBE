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
    prompt = input_text.prompt
    functions = []
    for f in list_functions:
        functions.append(f.name)

    new_text = " ".join(functions)
    new_text = " ".join([prompt, new_text])
    return new_text


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

    for i in list_input:
        new_text = create_text(i, list_functions)
        tokens = model.encode(new_text)
        # tolist permet de reduire en liste
        tokens = tokens.tolist()
        token = tokens[0]

        print(i.prompt)
        generated = ""
        for _ in range(5):
            print(f"tour : {_}, ")
            # le LLM lit toute la liste d’ids et donne une note 
            # à chaque token possible du vocabulaire”
            logits = model.get_logits_from_input_ids(token)

            # permet de mettre -inf a tous les ids des notes qui en correspondent 
            # pas a ce qui il y a dans les token de la string prompt + function
            # cest le constrained decoding
            for id_token in range(len(logits)):
                # le .get eevite les edge case si l'id du logits est au dessus du nombre 
                # d'id dans le vocab du llm, ca en cree un "" qui sera en -inf juste apres
                text_vocab = vocab_inverse.get(id_token, "")
                
                #  permet de savoir si la function commence par text_vocab sinon met -inf
                if text_vocab == "" or not any(function.startswith(generated + text_vocab) 
                                                for function in functions) :
                    logits[id_token] = -numpy.inf

            # argmax permet de chercher la position du logits max dans les token 
            next_id = int(numpy.argmax(logits))
            token.append(next_id)
            generated += vocab_inverse[next_id]
            print(generated)
            if generated in functions:
                break
            decod = model.decode(token)
        break

                










        
        

    
        
        

    