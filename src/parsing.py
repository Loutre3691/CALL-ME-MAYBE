from pydantic import BaseModel, ValidationError
import sys


class ParsingInput(BaseModel):
    prompt: str


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

    def parse_prompt_input(self, prompt_input: list[dict]) -> List:
        for i in prompt_input:
            try:
                obj = ParsingInput.model_validate(i)
                self.prompt_list_input.append(obj)

            except ValidationError:
                print(f"\033[0;31mError: Prompt_input is not valid\n\033[0m")
                sys.exit(1)
        return self.prompt_list_input

    def parse_prompt_functions(self, prompt_functions: list[dict]) -> List:
        for i in prompt_functions:
            try:
                obj = ParsingFunction.model_validate(i)
                self.prompt_list_functions.append(obj)
        

            except ValidationError:
                print("\033[0;31mError: Prompt_functions "
                      "is not valid\n\033[0m")
                sys.exit(1)

        return self.prompt_list_functions
