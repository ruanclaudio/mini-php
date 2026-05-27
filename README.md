# mini-php

A Mini-PHP lexical, syntactic, and semantic analyzer with a graphical IDE built in Python.

## Overview

This project implements a compiler front-end for a simplified subset of PHP (Mini-PHP). It performs three analysis phases:

1. **Lexical analysis** — tokenizes source code, reporting unrecognized symbols
2. **Syntactic analysis** — validates the token sequence against Mini-PHP grammar rules
3. **Semantic analysis** — checks variable initialization before use and validates function/parameter naming

A Tkinter-based IDE provides a code editor with line numbers, an output console, and file loading support.

## Supported language constructs

- Variable assignment: `$var = expression;`
- Arithmetic operators: `+`, `-`, `*`, `/`
- Relational operators: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logical operators: `&&`, `||`, `!`
- Conditionals: `if`, `else`, `else if`
- Loops: `while`
- Functions: `function name($param) { ... }`
- Return statements: `return expression;`
- Nested blocks: `{ ... }`
- Strings (`"..."`) and char literals (`'...'`)
- Line comments (`//`, `#`) and block comments (`/* */`)

## Project structure

```
mini-php/
├── main.py               # Entry point
├── ide_frontend.py       # Tkinter IDE
├── parse_analisator.py   # Lexer, parser, and semantic analyzer
└── source_code.txt       # Example source file
```

## Requirements

- Python 3.10+
- Tkinter (included with standard Python distributions)

## Running

```bash
python main.py
```

The IDE opens with an example program preloaded. Click **▶ Rodar Analisador** to analyze the code or **Abrir Arquivo .txt** to load a file.

## Example

```php
$numero = 10;
$limite = 20;

function processar($valor) {
    if ($valor < 100) {
        $valor = $valor * 2;
    }
    return $valor;
}
```

**Expected output:**
```
Success: Code is lexically, syntactically and semantically valid for Mini-PHP.
```

## Error reporting

Errors include the line and column where the problem was found:

```
Lexical Error [line 3, column 5]: Unrecognized symbol '@'.
Error [line 7, column 3]: Expected ';' at the end of assignment. Found '$x'.
Semantic Error: Variable '$y' used before it was initialized
```

## License

See [LICENSE](LICENSE).
