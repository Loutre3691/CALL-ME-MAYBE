import sys
from llm_sdk import Small_LLM_Model
import numpy


def create_text(input_text, function_text) -> str:
    prompt = input_text.prompt
    function = function_text.name

    new_text = " ".join([prompt, function])

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
    for i in list_input:
        for f in list_functions:
            new_text = create_text(i, f)
            token = model.encode(new_text)
            token = token.tolist()

            for _ in range(20):
                for t in token:
                    # le LLM lit toute la liste d’ids et donne une note 
                    # à chaque token possible du vocabulaire”
                    logits = model.get_logits_from_input_ids(t)
                    # argmax permet de chercher la position du logits max dans les token 
                    next_id = int(numpy.argmax(logits))
                    t.append(next_id)
                    decod = model.decode(t)
                    print(decod)








        
        

    
        
        

    