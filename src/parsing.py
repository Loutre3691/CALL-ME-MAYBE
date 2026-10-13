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


class ConfigParsing():
    """
    Parsing des prompts json
    """
    def __init__(self, prompt_input: list[dict], prompt_functions: list[dict]) -> None:
        self.prompt_input = prompt_input
        self.prompt_functions = prompt_functions
        self.prompt_list_input = []
        self.prompt_list_functions = []

        self.parse_prompt_input(self.prompt_input)
        self.parse_prompt_functions(self.prompt_functions)
        print(self.prompt_list_input)
        print(self.prompt_list_functions)



    def parse_prompt_input(self, prompt_input: list[dict]) -> None:
        for i in prompt_input:
            try:
                obj = ParsingInput.model_validate(i)
                self.prompt_list_input.append(obj)

            except ValidationError:
                print("\033[0;31mError: Prompt_input is not valid\n\033[0m")
                sys.exit(1)

    def parse_prompt_functions(self, prompt_functions: list[dict]) -> None:
        for i in prompt_functions:
            try:
                obj = ParsingFunction.model_validate(i)
                self.prompt_list_functions.append(obj)
                
            except ValidationError:
                print("\033[0;31mError: Prompt_functions is not valid\n\033[0m")
                sys.exit(1)




    