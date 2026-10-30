"""Program entry point: loads the JSON files, then starts the generation."""

from src.parsing import ConfigParsing
import sys
import json
import argparse
from typing import Any
from src.generator import transorm_text_in_numero


def load_json(path: str) -> Any:
    """Load and open a JSON file in a reusable way.

    Print an error message and exit the program if the file is
    missing, unreadable, a directory, or does not contain valid JSON.

    Args:
        path: path of the JSON file to load.

    Returns:
        The content of the JSON file (list or dictionary).
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

    # handles the error when the input is a directory instead of a file
    except IsADirectoryError:
        print("\033[0;31mError: must be a file, not a directory\n\033[0m")
        sys.exit(1)

    except json.JSONDecodeError:
        print("\033[0;31mError: Json file is not valid\n\033[0m")
        sys.exit(1)

    return data_json


if __name__ == "__main__":
    # argparse lets the user choose their files,
    # add_argument registers each command-line argument
    parser = argparse.ArgumentParser()
    parser.add_argument("--functions_definition",
                        default="data/input/functions_definition.json")
    parser.add_argument("--output", default="data/output/function_calls.json")
    parser.add_argument("--input",
                        default="data/input/function_calling_tests.json")
    parser.add_argument("--visualizer", action="store_true")
    args = parser.parse_args()
    config = ConfigParsing()

    data_fcalling_tests = load_json(args.input)
    data_fdefinition = load_json(args.functions_definition)

    list_input = config.parse_prompt_input(data_fcalling_tests)
    list_functions = config.parse_prompt_functions(data_fdefinition)
    transorm_text_in_numero(list_input, list_functions, args.output,
                            args.visualizer)
