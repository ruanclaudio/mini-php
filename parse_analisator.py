import re
from dataclasses import dataclass

def read_source_code(file_code_path):
    with open(file_code_path, 'r', encoding='utf-8') as file:
        return file.read()


@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int

    def __iter__(self):
        yield self.type
        yield self.value

    def __getitem__(self, index):
        if index == 0:
            return self.type
        if index == 1:
            return self.value
        if index == 2:
            return self.line
        if index == 3:
            return self.column
        raise IndexError(index)

    def __repr__(self):
        return f"({self.type}, {self.value!r}, line={self.line}, col={self.column})"


class PHPSemanticAnalyzer:
    def __init__(self):
        self.symbol_table = set()
        self.functions = set()

    def declare_variable(self, var_name: str):
        self.symbol_table.add(var_name)

    def declare_function(self, function_name: str):
        self.functions.add(function_name)

    def is_variable_initialized(self, var_name: str) -> bool:
        return var_name in self.symbol_table


class PHPSyntaxValidator:
    def __init__(self, tokens: list) -> None:
        self.tokens = tokens
        self.i = 0
        self.semantic_analyzer = PHPSemanticAnalyzer()
        self.errors = []

    @staticmethod
    def generate_tokens(file_source_code: str) -> list:
        token_specification = [
            ('NEWLINE', r'\n'),
            ('SKIP', r'[ \t\r]+'),
            ('COMMENT', r'//[^\n]*'),
            ('FUNCTION', r'\bfunction\b'),
            ('IF', r'\bif\b'),
            ('ELSE', r'\belse\b'),
            ('WHILE', r'\bwhile\b'),
            ('RETURN', r'\breturn\b'),
            ('NUMBER', r'\d+(\.\d+)?'),
            ('STRING', r'"([^"\\]|\\.)*"'),
            ('CHAR_LITERAL', r"'([^'\\]|\\.)*'"),
            ('RELATIONAL_OPERATOR', r'==|!=|>|<'),
            ('LOGICAL_OPERATOR', r'&&|\|\||!'),
            ('ASSIGN', r'='),
            ('OPERATOR', r'[+\-*/]'),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('LBRACE', r'\{'),
            ('RBRACE', r'\}'),
            ('COMMA', r','),
            ('END', r';'),
            ('ID', r'\$[a-zA-Z_][a-zA-Z0-9_]*'),
            ('FUNCTION_NAME', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('MISMATCH', r'.'),
        ]

        tokens = []
        errors = []
        line = 1
        column = 1
        position = 0

        while position < len(file_source_code):
            match_found = False

            for token_type, pattern in token_specification:
                match = re.match(pattern, file_source_code[position:])
                if not match:
                    continue

                value = match.group(0)
                match_found = True

                if token_type == 'NEWLINE':
                    line += 1
                    column = 1
                elif token_type in ['SKIP', 'COMMENT']:
                    column += len(value)
                elif token_type == 'MISMATCH':
                    errors.append(
                        f"Lexical Error [line {line}, column {column}]: Unrecognized symbol '{value}'."
                    )
                    column += len(value)
                else:
                    tokens.append(Token(token_type, value, line, column))
                    column += len(value)

                position += len(value)
                break

            if not match_found:
                errors.append(
                    f"Lexical Error [line {line}, column {column}]: Unrecognized text."
                )
                position += 1
                column += 1

        for error in errors:
            print(error)

        return tokens

    def current(self):
        if self.i < len(self.tokens):
            return self.tokens[self.i]
        return None

    def previous(self):
        if self.i - 1 >= 0:
            return self.tokens[self.i - 1]
        return None

    def check(self, token_type: str, value: str | None = None) -> bool:
        token = self.current()
        if token is None:
            return False
        if token.type != token_type:
            return False
        if value is not None and token.value != value:
            return False
        return True

    def advance(self):
        token = self.current()
        if token is not None:
            self.i += 1
        return token

    def error(self, message: str, token=None):
        if token is None:
            token = self.current() or self.previous()
        if token is None:
            self.errors.append(f"Error: {message}")
        else:
            self.errors.append(
                f"Error [line {token.line}, column {token.column}]: {message} Found '{token.value}'."
            )

    def consume(self, token_type: str, message: str, value: str | None = None) -> bool:
        if self.check(token_type, value):
            self.advance()
            return True
        self.error(message)
        return False

    def synchronize(self):
        while self.current() is not None:
            if self.check('END'):
                self.advance()
                return
            if self.check('RBRACE'):
                return
            if self.check('IF') or self.check('WHILE') or self.check('FUNCTION') or self.check('RETURN') or self.check('ID'):
                return
            self.advance()

    def parse(self) -> bool:
        while self.current() is not None:
            if not self.validate_statement():
                self.synchronize()

        if self.errors:
            print("\nCompilation finished with errors:")
            for error in self.errors:
                print(error)
            return False

        print("\nSuccess: Code is lexically, syntactically and semantically valid for Mini-PHP.")
        return True

    def validate_statement(self) -> bool:
        if self.current() is None:
            return True

        token = self.current()

        if token.type == 'ID':
            return self.validate_assignment()
        if token.type == 'IF':
            return self.validate_if()
        if token.type == 'WHILE':
            return self.validate_while()
        if token.type == 'FUNCTION':
            return self.validate_function()
        if token.type == 'RETURN':
            return self.validate_return()
        if token.type == 'LBRACE':
            return self.validate_block()
        if token.type == 'RBRACE':
            self.error("Closing block '}' without matching opening block", token)
            self.advance()
            return False
        if token.type == 'FUNCTION_NAME':
            self.error(
                f"Invalid identifier '{token.value}'. PHP variables must start with '$'. Correct form: '${token.value}'",
                token
            )
            self.advance()
            return False

        self.error(f"Unexpected token at start of instruction: {token.type}", token)
        self.advance()
        return False

    def validate_block(self) -> bool:
        if not self.consume('LBRACE', "Expected '{' to start block"):
            return False

        ok = True
        while self.current() is not None and not self.check('RBRACE'):
            if not self.validate_statement():
                ok = False
                self.synchronize()

        if not self.consume('RBRACE', "Expected '}' to close block"):
            return False
        return ok

    def validate_assignment(self) -> bool:
        var_token = self.advance()  # ID

        if not self.consume('ASSIGN', "Expected assignment operator '=' after variable"):
            return False

        if not self.validate_expression(stop_tokens={'END'}):
            return False

        if not self.consume('END', "Expected ';' at the end of assignment"):
            return False

        self.semantic_analyzer.declare_variable(var_token.value)
        return True

    def validate_if(self) -> bool:
        self.advance()

        ok = True
        ok = self.consume('LPAREN', "Expected '(' after if") and ok
        ok = self.validate_expression(stop_tokens={'RPAREN'}) and ok
        ok = self.consume('RPAREN', "Expected ')' after if condition") and ok
        ok = self.validate_block() and ok

        if self.check('ELSE'):
            self.advance()
            if self.check('IF'):
                ok = self.validate_if() and ok
            else:
                ok = self.validate_block() and ok

        return ok

    def validate_while(self) -> bool:
        self.advance()

        ok = True
        ok = self.consume('LPAREN', "Expected '(' after while") and ok
        ok = self.validate_expression(stop_tokens={'RPAREN'}) and ok
        ok = self.consume('RPAREN', "Expected ')' after while condition") and ok
        ok = self.validate_block() and ok
        return ok

    def validate_function(self) -> bool:
        self.advance()

        ok = True

        if self.check('FUNCTION_NAME'):
            function_name = self.advance().value
            self.semantic_analyzer.declare_function(function_name)
        elif self.check('ID'):
            self.error("Function name must not start with '$'", self.current())
            self.advance()
            ok = False
        else:
            self.error("Expected function name after 'function'")
            ok = False

        ok = self.consume('LPAREN', "Expected '(' after function name") and ok

        if not self.check('RPAREN'):
            ok = self.validate_parameters() and ok

        ok = self.consume('RPAREN', "Expected ')' after function parameters") and ok
        ok = self.validate_block() and ok
        return ok

    def validate_parameters(self) -> bool:
        ok = True

        while self.current() is not None:
            if self.check('ID'):
                self.semantic_analyzer.declare_variable(self.current().value)
                self.advance()
            elif self.check('FUNCTION_NAME'):
                self.error(
                    f"Invalid parameter '{self.current().value}'. Function parameters must start with '$'",
                    self.current()
                )
                self.advance()
                ok = False
            else:
                self.error("Expected function parameter starting with '$'")
                ok = False
                return ok

            if self.check('COMMA'):
                self.advance()
                continue
            break

        return ok

    def validate_return(self) -> bool:
        self.advance()

        ok = self.validate_expression(stop_tokens={'END'})
        ok = self.consume('END', "Expected ';' after return") and ok
        return ok

    def validate_expression(self, stop_tokens: set) -> bool:
      
        expecting_operand = True
        parentheses = 0
        found_anything = False
        ok = True

        while self.current() is not None:
            token = self.current()

            if token.type in stop_tokens and parentheses == 0:
                break

            if expecting_operand:
                if token.type == 'LOGICAL_OPERATOR' and token.value == '!':
                    self.advance()
                    found_anything = True
                    continue

                if token.type == 'LPAREN':
                    parentheses += 1
                    self.advance()
                    found_anything = True
                    continue

                if token.type in ['NUMBER', 'STRING', 'CHAR_LITERAL']:
                    self.advance()
                    expecting_operand = False
                    found_anything = True
                    continue

                if token.type == 'ID':
                    if not self.semantic_analyzer.is_variable_initialized(token.value):
                        self.error(f"Semantic Error: Variable '{token.value}' used before it was initialized", token)
                        ok = False
                    self.advance()
                    expecting_operand = False
                    found_anything = True
                    continue

                if token.type == 'FUNCTION_NAME':
                    self.error(
                        f"Invalid identifier '{token.value}' in expression. Variables must start with '$'",
                        token
                    )
                    self.advance()
                    ok = False
                    found_anything = True
                    expecting_operand = False
                    continue

                self.error("Expected number, string, variable or '(' in expression", token)
                self.advance()
                return False

            else:
                if token.type == 'RPAREN' and parentheses > 0:
                    parentheses -= 1
                    self.advance()
                    expecting_operand = False
                    found_anything = True
                    continue

                if token.type in ['OPERATOR', 'RELATIONAL_OPERATOR', 'LOGICAL_OPERATOR']:
            
                    if token.type == 'LOGICAL_OPERATOR' and token.value == '!':
                        self.error("Unexpected unary operator '!' after an operand", token)
                        self.advance()
                        ok = False
                        continue
                    self.advance()
                    expecting_operand = True
                    found_anything = True
                    continue

                if token.type in stop_tokens and parentheses == 0:
                    break

                self.error("Expected operator or end of expression", token)
                self.advance()
                ok = False
                break

        if not found_anything:
            self.error("Expected expression")
            return False

        if expecting_operand:
            self.error("Expression cannot end with an operator")
            return False

        if parentheses > 0:
            self.error("Expression has unclosed parenthesis")
            return False

        return ok


if __name__ == "__main__":
    file_path = "source_code.txt"
    source_code = read_source_code(file_path)
    print(f"Source code:\n{source_code}")

    generated_tokens = PHPSyntaxValidator.generate_tokens(source_code)
    syntax_validator = PHPSyntaxValidator(tokens=generated_tokens)

    print("Identified tokens:")
    for token in generated_tokens:
        print(token)
    print("\nSyntactic/Semantic Analysis:")
    syntax_validator.parse()
