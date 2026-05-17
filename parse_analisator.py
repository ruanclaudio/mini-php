import re

def read_source_code(file_code_path):
    with open(file_code_path, 'r') as file:
        return file.read()

class PHPSemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}

    def declare_variable(self, var_name: str):
        self.symbol_table[var_name] = True

    def is_variable_initialized(self, var_name: str) -> bool:
        if var_name not in self.symbol_table:
            print(f"Semantic Error: Variable '{var_name}' used before it was initialized.")
            return False
        return True

    # def analyze(self):
    #     for i, (token_type, value) in enumerate(self.tokens):
    #         if token_type == 'ID':
    #             if value not in self.symbol_table:
    #                 print(f"Semantic Error: variable '{value}' used before has declarative.")
    #         elif token_type == 'TYPE':
    #             if i + 1 < len(self.tokens) and self.tokens[i + 1][0] == 'ID':
    #                 self.symbol_table[self.tokens[i + 1][1]] = self.tokens[i][1]


class PHPSyntaxValidator:
    def __init__(self, tokens: list) -> None:
        self.tokens = tokens
        self.i = 0
        self.semantic_analyzer = PHPSemanticAnalyzer()

    @staticmethod
    def generate_tokens(file_source_code: str) -> list:
        token_specification = [
            ('NUMBER', r'\d+(\.\d*)?'),
            ('ASSIGN', r'='),
            ('END', r';'),
            ('ID', r'\$[a-zA-Z_][a-zA-Z0-9_]*'),
            ('INVALID_ID', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('OPERATOR', r'[+\-*/]'),
            ('NEWLINE', r'\n'),
            ('SKIP', r'[ \t]+'),
            ('CHAR_LITERAL', r"'.?'"),
            ('MISMATCH', r'.'),
        ]
        tokens = []

        while file_source_code:
            patern_founded = False
            for type, patern in token_specification:
                match = re.match(patern, file_source_code)
                if match:
                    value = match.group(0)

                    if type == "INVALID_ID":
                        print(
                            f"Lexical Error: The identifier '{value}' is invalid."
                            f" PHP variables must start with '$'. The correct form is '${value}'.")
                        return []

                    if type != "SKIP":
                        tokens.append((type, value))
                    file_source_code = file_source_code[len(value):]
                    patern_founded = True
                    break

            if not patern_founded:
                print(f"Unrecognized text: {file_source_code}")
                break
        return tokens

    def validate_assignment(self) -> bool:
        if self.i < len(self.tokens) and self.tokens[self.i][0] == 'ID':
            var_name = self.tokens[self.i][1]
            self.i +=1
            if self.validate_assign():
                self.semantic_analyzer.declare_variable(var_name)
                return True
            return False
        print("Error: Expected a variable starting with '$'")
        return False

    def validate_assign(self) -> bool:
        if self.i < len(self.tokens) and self.tokens[self.i][0] == 'ASSIGN':
            self.i += 1
            return self.validate_value()
        print("Error: Expected assignment operator '=' after variable")
        return False

    def validate_value(self) -> bool:
        if self.i < len(self.tokens):
            token_type, token_value = self.tokens[self.i]
            if token_type in ['NUMBER', 'ID', 'CHAR_LITERAL']:
                if token_type == "ID":
                    if not self.semantic_analyzer.is_variable_initialized(token_value):
                        return False
                self.i += 1
                if self.i < len(self.tokens):
                    if self.tokens[self.i][0] == 'OPERATOR':
                        self.i += 1
                        return self.validate_value()
                    elif self.tokens[self.i][0] == 'END':
                        return self._end()
                print("Error: Expected value or ';' to end instruction")
                return False

        print("Error: Expected a number, variable, or character literal")
        return False

    def _end(self) -> bool:
        if self.i < len(self.tokens) and self.tokens[self.i][0] == 'END':
            self.i += 1
            return True
        print("Error: Expected ';' at the end of instruction")
        return False

    def parse(self) -> bool:
        while self.i < len(self.tokens):
            token_type = self.tokens[self.i][0]
            if token_type == 'NEWLINE':
                self.i += 1
                continue

            if token_type == 'ID':
                if not self.validate_assignment():
                    return False
            else:
                print(f"Error: Unexpected token {token_type} at start of instruction")
                return False
        print("Success: Code is syntactically valid PHP assignment.")
        return True


if __name__ == "__main__":
    file_path = "source_code.txt"
    source_code = read_source_code(file_path)
    print(f"Source code:\n{source_code}")

    generated_tokens = PHPSyntaxValidator.generate_tokens(source_code)
    if generated_tokens:
        syntax_validator = PHPSyntaxValidator(tokens=generated_tokens)

        print("Identified tokens:")
        for token in generated_tokens:
            print(token)
        print("\nSyntactic Analysis:")
        syntax_validator.parse()
