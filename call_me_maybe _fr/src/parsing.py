"""Validation (via pydantic) des fichiers JSON de prompts et de fonctions."""

from pydantic import BaseModel, ValidationError, Field
import sys
from typing import Any, Literal


class ParsingInput(BaseModel):
    """Un prompt d'entrée : une question en langage naturel non vide."""

    prompt: str = Field(min_length=1)


class ParsingType(BaseModel):
    """Type d'un paramètre ou d'une valeur de retour (ex: "string")."""

    type: Literal["string", "number", "integer", "boolean"]


class ParsingFunction(BaseModel):
    """Définition d'une fonction appelable par le LLM."""

    name: str
    description: str
    parameters: dict[str, ParsingType]
    returns: ParsingType


class ConfigParsing(BaseModel):
    """Parsing et validation des prompts et des définitions de fonctions.

    Attributes:
        prompt_list_input: prompts validés.
        prompt_list_functions: définitions de fonctions validées.
    """

    prompt_list_input: list[ParsingInput] = []
    prompt_list_functions: list[ParsingFunction] = []

    def parse_prompt_input(self, prompt_input: list[dict[str, Any]]
                           ) -> list[ParsingInput]:
        """Valide la liste des prompts d'entrée.

        Quitte le programme (code 1) si l'entrée n'est pas une liste,
        si un prompt est invalide ou si la liste est vide.

        Args:
            prompt_input: contenu du JSON des prompts (liste de dict).

        Returns:
            La liste des prompts validés.
        """
        if not isinstance(prompt_input, list):
            print("\033[0;31mError: input file must contain "
                  "a JSON list\n\033[0m")
            sys.exit(1)

        for i in prompt_input:
            try:
                obj = ParsingInput.model_validate(i)
                self.prompt_list_input.append(obj)

            except ValidationError:
                print("\033[0;31mError: Prompt_input is not valid\n\033[0m")
                sys.exit(1)

        if not self.prompt_list_input:
            print("\033[0;31mError: list empty\n\033[0m")
            sys.exit(1)

        return self.prompt_list_input

    def parse_prompt_functions(self, prompt_functions: list[dict[str, Any]]
                               ) -> list[ParsingFunction]:
        """Valide la liste des définitions de fonctions.

        Quitte le programme (code 1) si l'entrée n'est pas une liste,
        si une définition est invalide ou si la liste est vide.

        Args:
            prompt_functions: contenu du JSON des fonctions (liste de dict).

        Returns:
            La liste des définitions de fonctions validées.
        """
        if not isinstance(prompt_functions, list):
            print("\033[0;31mError: functions file must contain "
                  "a JSON list\n\033[0m")
            sys.exit(1)

        for i in prompt_functions:
            try:
                obj = ParsingFunction.model_validate(i)
                self.prompt_list_functions.append(obj)

            except ValidationError:
                print("\033[0;31mError: Prompt_functions "
                      "is not valid\n\033[0m")
                sys.exit(1)

        if not self.prompt_list_functions:
            print("\033[0;31mError: functions list is empty\n\033[0m")
            sys.exit(1)

        return self.prompt_list_functions
