from pydantic import BaseModel, ValidationError, Field
import sys
from typing import Any



class ParsingInput(BaseModel):
    prompt: str = Field(min_length=1)


class ParsingType(BaseModel):
    type: str


class ParsingFunction(BaseModel):
    name: str
    description: str
    parameters: dict[str, ParsingType]
    returns: ParsingType


class ConfigParsing(BaseModel):
    """
    Parsing des prompts json
    """
    prompt_list_input: list[ParsingInput] = []
    prompt_list_functions: list[ParsingFunction] = []

    def parse_prompt_input(self, prompt_input: list[dict[str, Any]]
                           ) -> list[ParsingInput]:
        if not isinstance(prompt_input, list):
            print("\033[0;31mError: input file must contain a JSON list\n\033[0m")
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
