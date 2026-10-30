*This project has been created as part of the 42 curriculum by fde-chec.*
 
# CALL ME MAYBE
 
## 📖 Description
 
**Call me maybe** is an introduction to *function calling* with LLMs.
 
The program receives questions written in natural language (for example *"What is the sum of 2 and 3?"*) and, instead of answering them, translates each question into a structured function call:
 
```json
{
  "prompt": "What is the sum of 2 and 3?",
  "name": "fn_add_numbers",
  "parameters": {"a": 2.0, "b": 3.0}
}
```
 
Two JSON files are given as input:
- `functions_definition.json`: the list of available functions (name, description, parameters and their types)
- `function_calling_tests.json`: the list of questions to process

The model used is **Qwen3-0.6B**, a small LLM that is not reliable when simply asked to produce JSON. To guarantee 100% valid output, the project uses **constrained decoding**: at each generation step, the tokens that would break the JSON structure or the expected schema are forbidden, so the LLM can only choose among valid tokens.
 
---
 
## ⚙️ Instructions
 
### 📦 Installation
 
Requirements:
 
* Python 3.10+
* the `uv` package manager
* flake8 7.3.0
* mypy 1.20.2
* pydantic 2.13.3
* pytest 9.0.3

Install the dependencies:
 
```bash
make install
```
 
### ▶️ Run the project
 
With the default paths (`data/input/` and `data/output/`):
 
```bash
make run
```
 
With custom paths:
 
```bash
uv run python -m src \
    --functions_definition data/input/functions_definition.json \
    --input data/input/function_calling_tests.json \
    --output data/output/function_calls.json
```
 
### 🎁 Run the bonus
 
```bash
uv run python -m src --visualizer
uv run pytest
```
 
### 🛠 Available commands
 
| Command            | Description                              |
| ------------------ | ---------------------------------------- |
| `make run`         | Runs the function calling program        |
| `make install`     | Sets up the environment                  |
| `make debug`       | Runs with the debugger (pdb)             |
| `make clean`       | Removes the cache and the venv           |
| `make lint`        | Code check (flake8 + mypy)               |
| `make lint-strict` | Strict type check                        |
 
---
 
## 🧠 Algorithm explanation: constrained decoding
 
An LLM writes **one token at a time**. At each step, it returns a list of **logits**: a score for each token of its vocabulary. Normally, we pick the token with the highest score.
 
Without any constraint, the model can give a high score to a token that makes no sense for our task (text before the JSON, a function name that does not exist, a letter where a number is expected...).
 
Constrained decoding works like a **fill-in-the-blanks form**:
 
```
{"name": "______", "parameters": {"a": ____, "b": ____}}
          ▲                             ▲         ▲
          blank 1                       blank 2   blank 3
```
 
- The **fixed parts** (braces, keys, quotes, commas) are written by the program itself.
- The **blanks** are filled by the LLM, but only with tokens allowed by the rules.

At each step:
1. The model produces the logits for all tokens.
2. The program checks, using the vocabulary file, which tokens are valid at this position.
3. The logits of all invalid tokens are set to `-inf`.
4. We pick the token with the highest score among the remaining ones.

Rules used for the blanks:
- **Function name**: the text being generated must always be the beginning of an existing function name from `functions_definition.json`.
- **Number parameters**: only digits, `-` and `.` are allowed, so that the value can always be converted to a float.
- **String parameters**: the value is generated until the closing quote.

This way, the output is always readable JSON that respects the schema.
 
---
 
## 🏗 Design choices
 
- The code is split into 3 files, each with a clear role:
  - `parsing.py`: reads and validates the input JSON files (with pydantic)
  - `generator.py`: the interaction with the LLM and the constrained decoding
  - `__main__.py`: the command-line arguments and the main flow
- `generator.py` stays short enough to keep all the generation logic in a single file, which makes it easier to read.
- The JSON is built like a fill-in-the-blanks form: the program writes the structure, the LLM only fills in the values. This guarantees the structure without depending on the prompt.
- Each rule (function name, number, string) only applies to its own blank, so a rule never blocks the valid tokens of another blank.
---
 
## 📊 Performance analysis
 
- **Accuracy**: XX / XX correct prompts (XX%). The subject asks for 90% or more.
- **Speed**: all prompts are processed in XX seconds, under the 5 minutes required. To measure it:
```bash
  time make run
```
- **Reliability**: thanks to constrained decoding, 100% of the outputs are valid JSON.
---
 
## 🧗 Challenges faced
 
- **Parameter generation** was the hardest part: each type (number, string) needs its own rules, and finding these rules did not come naturally at first.
- **Rules applied at the wrong time**: at some point, the function name rule and the parameter rule were applied at the same time, which blocked valid tokens such as digits. Separating the rules for each blank fixed the problem.
- **Crashes on numbers**: values like `""` or `"-"` made `float()` crash. These cases are now handled.
- **Empty lists in the parsing**: spotted thanks to the pytest tests, now handled.
---
 
## 🧪 Testing strategy
 
- **Prints** during development to follow the generation token by token.
- **pytest** tests (bonus), in the `tests/` folder:
  - `test_load_json.py`: missing file, invalid JSON, empty file
  - `test_parsing.py`: validation of the input data
  - `test_generator.py`: the generated data
- **Edge cases** tested: empty strings, negative numbers, special characters, empty lists.
---
 
## 🎁 Bonus
 
- **Visualizer**: shows in the terminal how the LLM progresses step by step during the generation.
- **Test suite** with pytest, which also helped find unhandled errors (for example an empty list in the parsing).
---
 
## 📂 Project structure
 
```
README.md
Makefile
pyproject.toml
uv.lock
src/
    __main__.py
    parsing.py
    generator.py
tests/
    test_load_json.py
    test_parsing.py
    test_generator.py
llm_sdk/        (provided by the subject)
data/input/     (provided by the subject)
```
 
---
 
## 💡 Usage example
 
Input (`function_calling_tests.json`):
 
```json
[
  {"prompt": "What is the sum of 2 and 3?"},
  {"prompt": "Reverse the string 'hello'"}
]
```
 
Output (`data/output/function_calls.json`):
 
```json
[
  {
    "prompt": "What is the sum of 2 and 3?",
    "name": "fn_add_numbers",
    "parameters": {"a": 2.0, "b": 3.0}
  },
  {
    "prompt": "Reverse the string 'hello'",
    "name": "fn_reverse_string",
    "parameters": {"s": "hello"}
  }
]
```
 
---
 
## 📚 Resources
 
- **42 Python modules**: I regularly went back to them to set up the code and review notions I had forgotten.
- **AI**: used to understand the key concepts (LLM, tokens, logits, constrained decoding), to review `generator.py`, to find edge cases (empty strings, negative numbers, empty lists), and to help write and translate this README. I used it very little at the beginning, then more towards the end, mostly to check my ideas before going too far in the wrong direction.
- **Peers**: explanations about the project and the subject.
- **Pydantic documentation**: https://docs.pydantic.dev
