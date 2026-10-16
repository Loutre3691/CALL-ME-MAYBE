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


def write_parameter(parameters: dict, token: list, vocab_inverse: dict, model: object) -> None:
    allowed = "0123456789.-},"

    for key, value in parameters.items():
        value_generated = ""
        nbr_tour = 0
        while "}" not in value_generated and "," not in value_generated and nbr_tour < 20:
            logits = model.get_logits_from_input_ids(token)

            for pos in range(len(logits)):
                text_vocab = vocab_inverse.get(pos, "")

                if text_vocab == "" or not all(c in allowed for c in text_vocab):
                    logits[pos] = -numpy.inf

            next_id = int(numpy.argmax(logits))
            token.append(next_id)
            value_generated += vocab_inverse[next_id]
            nbr_tour += 1









        
        
 

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

    for prompt in list_input:
        new_text = create_text(prompt, list_functions)
        tokens = model.encode(new_text)
        # tolist permet de reduire en liste
        tokens = tokens.tolist()
        # tokens[0] recuperere la liste interieur qui contiens tous les ids de la phrase
        token = tokens[0]

        generated = ""
        nbr_tour = 0
        while generated not in functions and nbr_tour < 20:
            # le LLM lit toute la liste d’ids et donne une note 
            # à chaque token possible du vocabulaire”
            logits = model.get_logits_from_input_ids(token)

            # permet de mettre -inf a tous les ids des notes qui en correspondent 
            # pas a ce qui il y a dans les token de la string prompt + function
            # cest le constrained decoding
            for pos in range(len(logits)):
                # le .get eevite les edge case si l'id du logits est au dessus du nombre 
                # d'id dans le vocab du llm, ca en cree un "" qui sera en -inf juste apres
                text_vocab = vocab_inverse.get(pos, "")
                
                #  permet de savoir si la function commence par text_vocab + generated sinon met -inf
                if text_vocab == "" or not any(function.startswith(generated + text_vocab) 
                                                for function in functions) :
                    logits[pos] = -numpy.inf

            # argmax permet de chercher la position du logits max dans les token
            #  next_id recupere l'id du logits max
            next_id = int(numpy.argmax(logits))
            token.append(next_id)
            generated += vocab_inverse[next_id]
            decod = model.decode(token)
            nbr_tour += 1

        if generated not in functions:
            print(f"Error: {generated} is not in functions list")

        for f in list_functions:
            if generated == f.name:
                write_parameter(f.parameters, token, vocab_inverse, model)


                










        
        

    
        
        

    