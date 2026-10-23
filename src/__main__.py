from src.parsing import ConfigParsing
import sys
import json
import argparse
from typing import Any
from src.generator import transorm_text_in_numero


def load_json(path: str) -> Any:
    """Fonction reutilisabe pour le chargement et ouverture des json
    Args:
        path: path du JSON file
    Returns:
        le contenu du fichier json(list ou dict)
    """
    try:
        with open(path) as file:
            data_json = json.load(file)

    except PermissionError:
        print("\033[0;31mError: permission not valid\n\033[0m")
        sys.exit(1)

    except FileNotFoundError:
        print(f"\033[0;31mError: file '{path}' not found\n\033[0m")
        sys.exit(1)

    # permet lors de l'input de gerer lerreur si dossier et pas fichier
    except IsADirectoryError:
        print("\033[0;31mError: must be a file, not a directory\n\033[0m")
        sys.exit(1)

    except json.JSONDecodeError:
        print("\033[0;31mError: Json file is not valid\n\033[0m")
        sys.exit(1)

    return data_json


if __name__ == "__main__":
    """
    argparse permet a l'user de choice her files, add_argument
    permet d'add arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--functions_definition",
                        default="data/input/functions_definition.json")
    parser.add_argument("--output", default="data/output/function_calls.json")
    parser.add_argument("--input",
                        default="data/input/function_calling_tests.json")
    args = parser.parse_args()
    config = ConfigParsing()

    data_fcalling_tests = load_json(args.input)
    data_fdefinition = load_json(args.functions_definition)

    list_input = config.parse_prompt_input(data_fcalling_tests)
    list_functions = config.parse_prompt_functions(data_fdefinition)


    transorm_text_in_numero(list_input, list_functions, args.output)
