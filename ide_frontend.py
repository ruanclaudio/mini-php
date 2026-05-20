import tkinter as tk
from tkinter import scrolledtext
import io
from contextlib import redirect_stdout

# Importando a classe do seu arquivo original
# Certifique-se de que o seu arquivo chama-se 'parse_analisator.py'
from parse_analisator import PHPSyntaxValidator

def run_analysis():
    # 1. Pegar o código digitado no editor
    code = editor.get("1.0", tk.END).strip()
    
    # 2. Limpar o console para a nova execução
    console.config(state=tk.NORMAL)
    console.delete("1.0", tk.END)
    
    if not code:
        console.insert(tk.END, "Por favor, insira algum código PHP para analisar.")
        console.config(state=tk.DISABLED)
        return

    # 3. Criar um buffer para capturar os "prints" do seu analisador
    f = io.StringIO()
    
    # 4. Rodar o analisador redirecionando a saída do terminal para o buffer
    with redirect_stdout(f):
        print(f"Source code:\n{code}\n")
        
        # Chama a sua lógica
        generated_tokens = PHPSyntaxValidator.generate_tokens(code)
        if generated_tokens:
            syntax_validator = PHPSyntaxValidator(tokens=generated_tokens)
            
            print("Identified tokens:")
            for token in generated_tokens:
                print(token)
            print("\nSyntactic Analysis:")
            syntax_validator.parse()

    # 5. Pegar tudo que foi "printado" e jogar no console da interface
    output = f.getvalue()
    console.insert(tk.END, output)
    console.config(state=tk.DISABLED) # Trava o console para não ser editável

# ==========================================
# CONFIGURAÇÃO DA INTERFACE GRÁFICA (Tkinter)
# ==========================================
root = tk.Tk()
root.title("Mini PHP IDE")
root.geometry("800x600")
root.configure(bg="#2b2b2b")

# Frame do Editor
tk.Label(root, text="Editor de Código (PHP):", fg="white", bg="#2b2b2b", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
editor = scrolledtext.ScrolledText(root, height=15, bg="#1e1e1e", fg="#d4d4d4", font=("Courier New", 12), insertbackground="white")
editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Inserindo um código de exemplo padrão no editor
codigo_exemplo = "$preco = 100;\nvalor = 15;\n$total = $preco + valor;"
editor.insert(tk.END, codigo_exemplo)

# Botão de Execução
btn_run = tk.Button(root, text="▶ Rodar Analisador", bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), command=run_analysis)
btn_run.pack(pady=5)

# Frame do Console
tk.Label(root, text="Console (Saída do Compilador):", fg="white", bg="#2b2b2b", font=("Arial", 12, "bold")).pack(anchor="w", padx=10)
console = scrolledtext.ScrolledText(root, height=10, bg="#000000", fg="#00ff00", font=("Courier New", 11), state=tk.DISABLED)
console.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

# Iniciar a aplicação
root.mainloop()