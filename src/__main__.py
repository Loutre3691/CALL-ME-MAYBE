import sys
import json
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/input/function_calling_tests.json")
    args = parser.parse_args()
    try:
        with open(args.input) as file:
            data_json = json.load(file)

        print(data_json[0]["prompt"])

    except PermissionError:
        print("\033[0;31mError: permission not valid\n\033[0m")
        sys.exit(1)

    except FileNotFoundError:
        print("\033[0;31mError: Storage vault not found\n\033[0m")
        sys.exit(1)

    # permet lors de l'input de gerer lerreur si dossier et pas fichier
    except IsADirectoryError:
        print("\033[0;31mError: must be a file, not a directory\n\033[0m")
        sys.exit(1)

