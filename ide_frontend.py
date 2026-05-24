import tkinter as tk
from tkinter import scrolledtext
import io
from contextlib import redirect_stdout

from parse_analisator import PHPSyntaxValidator


def run_analysis():
    code = editor.get("1.0", tk.END).strip()

    console.config(state=tk.NORMAL)
    console.delete("1.0", tk.END)

    if not code:
        console.insert(tk.END, "Por favor, insira algum código PHP para analisar.")
        console.config(state=tk.DISABLED)
        return

    f = io.StringIO()

    with redirect_stdout(f):
        print(f"Source code:\n{code}\n")

        generated_tokens = PHPSyntaxValidator.generate_tokens(code)
        syntax_validator = PHPSyntaxValidator(tokens=generated_tokens)

        print("Identified tokens:")
        for token in generated_tokens:
            print(token)

        print("\nSyntactic/Semantic Analysis:")
        syntax_validator.parse()

    output = f.getvalue()
    console.insert(tk.END, output)
    console.config(state=tk.DISABLED)


root = tk.Tk()
root.title("Mini PHP IDE")
root.geometry("900x650")
root.configure(bg="#2b2b2b")

tk.Label(root, text="Editor de Código (Mini-PHP):", fg="white", bg="#2b2b2b", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
editor = scrolledtext.ScrolledText(root, height=18, bg="#1e1e1e", fg="#d4d4d4", font=("Courier New", 12), insertbackground="white")
editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

codigo_exemplo = '''$numero = 10;
$limite = 20;

function processar($valor) {
    if ($valor < 100) {
        $valor = $valor * 2;
    }

    return $valor;
}
'''
editor.insert(tk.END, codigo_exemplo)

btn_run = tk.Button(root, text="▶ Rodar Analisador", bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), command=run_analysis)
btn_run.pack(pady=5)

tk.Label(root, text="Console (Saída do Compilador):", fg="white", bg="#2b2b2b", font=("Arial", 12, "bold")).pack(anchor="w", padx=10)
console = scrolledtext.ScrolledText(root, height=12, bg="#000000", fg="#00ff00", font=("Courier New", 11), state=tk.DISABLED)
console.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

root.mainloop()
