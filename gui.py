"""
Interface gráfica para busca em repositórios GitHub.
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import threading

# Verificar Git antes de importar
try:
    from repo_searcher import RepoSearcher
except ImportError as e:
    if "git" in str(e).lower() or "Bad git executable" in str(e):
        messagebox.showerror(
            "Git não encontrado",
            "O Git não está instalado ou não está no PATH.\n\n"
            "Por favor, instale o Git:\n"
            "https://git-scm.com/download/win\n\n"
            "Após instalar, reinicie a aplicação."
        )
        sys.exit(1)
    else:
        raise

# Carregar variáveis de ambiente
load_dotenv()


class RepoSearchGUI:
    """Interface gráfica para busca em repositórios."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub Repository Search")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Variáveis
        self.searcher = None
        self.search_thread = None
        self.results = []
        
        # Configurar estilo
        self.setup_style()
        
        # Criar interface
        self.create_widgets()
        
        # Carregar configurações
        self.load_config()
    
    def setup_style(self):
        """Configura o estilo da interface."""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Cores personalizadas
        self.bg_color = "#f0f0f0"
        self.accent_color = "#0078d4"
        self.text_color = "#333333"
        
        self.root.configure(bg=self.bg_color)
    
    def create_widgets(self):
        """Cria os widgets da interface."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="🔍 GitHub Repository Search", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Seção de configuração
        config_frame = ttk.LabelFrame(main_frame, text="Configuração", padding="10")
        config_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Token
        ttk.Label(config_frame, text="GitHub Token:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.token_var = tk.StringVar()
        token_entry = ttk.Entry(config_frame, textvariable=self.token_var, width=50, show="*")
        token_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Carregar token do .env se existir
        env_token = os.getenv("GITHUB_TOKEN")
        if env_token:
            self.token_var.set(env_token)
            token_entry.configure(state="readonly")
            ttk.Label(config_frame, text="(carregado do .env)", 
                     foreground="gray").grid(row=0, column=2)
        
        # Usuário
        ttk.Label(config_frame, text="GitHub User:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.user_var = tk.StringVar(value=os.getenv("GITHUB_USER", "Lucasbettio"))
        user_entry = ttk.Entry(config_frame, textvariable=self.user_var, width=50)
        user_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        
        # Botão para carregar .env
        if not env_token:
            ttk.Button(config_frame, text="Carregar .env", 
                      command=self.load_env).grid(row=0, column=2, padx=(0, 0))
        
        # Seção de repositórios
        repos_frame = ttk.LabelFrame(main_frame, text="Repositórios (formato: user/repo)", padding="10")
        repos_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        repos_frame.columnconfigure(0, weight=1)
        
        # Text area para repositórios
        self.repos_text = scrolledtext.ScrolledText(repos_frame, height=5, wrap=tk.WORD)
        self.repos_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.repos_text.insert("1.0", "Lucasbettio/teste_pratico\nLucasbettio/ToDoListProject\nLucasbettio/mvc_project")
        
        # Seção de busca
        search_frame = ttk.LabelFrame(main_frame, text="Busca", padding="10")
        search_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Buscar:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=50)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        search_entry.bind("<Return>", lambda e: self.start_search())
        
        # Botões
        button_frame = ttk.Frame(search_frame)
        button_frame.grid(row=0, column=2)
        
        self.search_button = ttk.Button(button_frame, text="🔍 Buscar", 
                                       command=self.start_search, width=15)
        self.search_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.cancel_button = ttk.Button(button_frame, text="❌ Cancelar", 
                                       command=self.cancel_search, state="disabled", width=15)
        self.cancel_button.pack(side=tk.LEFT)
        
        # Barra de progresso
        self.progress_var = tk.StringVar(value="Pronto")
        self.progress_label = ttk.Label(search_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        self.progress_bar = ttk.Progressbar(search_frame, mode='indeterminate')
        self.progress_bar.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Seção de resultados
        results_frame = ttk.LabelFrame(main_frame, text="Resultados", padding="10")
        results_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Treeview para resultados
        columns = ("repo", "file", "line", "preview")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="tree headings", height=15)
        self.results_tree.heading("#0", text="#")
        self.results_tree.heading("repo", text="Repositório")
        self.results_tree.heading("file", text="Arquivo")
        self.results_tree.heading("line", text="Linha")
        self.results_tree.heading("preview", text="Preview")
        
        self.results_tree.column("#0", width=50, minwidth=50)
        self.results_tree.column("repo", width=150, minwidth=100)
        self.results_tree.column("file", width=200, minwidth=150)
        self.results_tree.column("line", width=80, minwidth=60)
        self.results_tree.column("preview", width=400, minwidth=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind duplo clique para mostrar detalhes
        self.results_tree.bind("<Double-1>", self.show_result_details)
        
        # Botões de ação
        action_frame = ttk.Frame(results_frame)
        action_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(action_frame, text="💾 Salvar JSON", 
                  command=self.save_results).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="🗑️ Limpar", 
                  command=self.clear_results).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="📋 Copiar Selecionado", 
                  command=self.copy_selected).pack(side=tk.LEFT)
        
        # Status bar
        self.status_var = tk.StringVar(value="Pronto")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))
    
    def load_env(self):
        """Carrega variáveis do arquivo .env."""
        load_dotenv()
        token = os.getenv("GITHUB_TOKEN")
        user = os.getenv("GITHUB_USER", "Lucasbettio")
        
        if token:
            self.token_var.set(token)
            messagebox.showinfo("Sucesso", "Token carregado do arquivo .env")
        else:
            messagebox.showwarning("Aviso", "GITHUB_TOKEN não encontrado no arquivo .env")
        
        if user:
            self.user_var.set(user)
    
    def load_config(self):
        """Carrega configurações salvas."""
        config_file = Path("config.json")
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    if "repos" in config:
                        self.repos_text.delete("1.0", tk.END)
                        self.repos_text.insert("1.0", "\n".join(config["repos"]))
            except Exception as e:
                print(f"Erro ao carregar configuração: {e}")
    
    def save_config(self):
        """Salva configurações."""
        repos_text = self.repos_text.get("1.0", tk.END).strip()
        repos = [r.strip() for r in repos_text.split("\n") if r.strip()]
        
        config = {"repos": repos}
        config_file = Path("config.json")
        try:
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")
    
    def get_repos(self):
        """Obtém lista de repositórios do texto."""
        repos_text = self.repos_text.get("1.0", tk.END).strip()
        repos = [r.strip() for r in repos_text.split("\n") if r.strip()]
        return repos
    
    def validate_inputs(self):
        """Valida as entradas do usuário."""
        token = self.token_var.get().strip()
        if not token:
            messagebox.showerror("Erro", "Por favor, informe o GitHub Token!")
            return False
        
        repos = self.get_repos()
        if not repos:
            messagebox.showerror("Erro", "Por favor, informe pelo menos um repositório!")
            return False
        
        search_string = self.search_var.get().strip()
        if not search_string:
            messagebox.showerror("Erro", "Por favor, informe o termo de busca!")
            return False
        
        return True
    
    def progress_callback(self, message):
        """Callback para atualizar progresso."""
        self.root.after(0, lambda: self.progress_var.set(message))
        self.root.after(0, lambda: self.status_var.set(message))
    
    def result_callback(self, result):
        """Callback para cada resultado encontrado."""
        self.root.after(0, lambda r=result: self.add_result(r))
    
    def add_result(self, result):
        """Adiciona um resultado à árvore."""
        item_id = self.results_tree.insert("", tk.END, 
                                          text=str(len(self.results) + 1),
                                          values=(
                                              result["repo"],
                                              result["file"],
                                              result["line_number"],
                                              result["line"][:80] + "..." if len(result["line"]) > 80 else result["line"]
                                          ))
        self.results.append(result)
        self.status_var.set(f"{len(self.results)} resultado(s) encontrado(s)")
    
    def start_search(self):
        """Inicia a busca."""
        if not self.validate_inputs():
            return

        self.clear_results()

        self.search_button.config(state="disabled")
        self.cancel_button.config(state="normal")

        self.progress_bar.start()
        self.progress_var.set("Iniciando busca...")

        token = self.token_var.get().strip()
        user = self.user_var.get().strip() or "Lucasbettio"
        repos = self.get_repos()
        search_string = self.search_var.get().strip()

        self.searcher = RepoSearcher(token, user)

        self.search_thread = threading.Thread(
            target=self._search_thread,
            args=(repos, search_string),
            daemon=True
        )
        self.search_thread.start()
    
    def _search_thread(self, repos, search_string):
        """Executa a busca em thread separada."""
        try:
            results = self.searcher.search_repos(
                repos,
                search_string,
                progress_callback=self.progress_callback,
                result_callback=self.result_callback
            )

            self.root.after(0, self._search_complete, results)
        except Exception as e:
            self.root.after(0, lambda: self._search_error(str(e)))
    
    def _search_complete(self, results):
        """Chamado quando a busca é concluída."""
        self.progress_bar.stop()
        self.progress_var.set(f"Busca concluída! {len(results)} resultado(s) encontrado(s)")
        self.status_var.set(f"Busca concluída! {len(results)} resultado(s) encontrado(s)")
        self.search_button.config(state="normal")
        self.cancel_button.config(state="disabled")
        self.save_config()
    
    def _search_error(self, error_msg):
        """Chamado quando ocorre um erro na busca."""
        self.progress_bar.stop()
        self.progress_var.set("Erro na busca")
        self.status_var.set(f"Erro: {error_msg}")
        self.search_button.config(state="normal")
        self.cancel_button.config(state="disabled")
        messagebox.showerror("Erro", f"Erro durante a busca:\n{error_msg}")
    
    def cancel_search(self):
        """Cancela a busca em andamento."""
        if self.searcher:
            self.searcher.cancel()
        self.progress_bar.stop()
        self.progress_var.set("Busca cancelada")
        self.status_var.set("Busca cancelada pelo usuário")
        self.search_button.config(state="normal")
        self.cancel_button.config(state="disabled")
    
    def clear_results(self):
        """Limpa os resultados."""
        self.results_tree.delete(*self.results_tree.get_children())
        self.results = []
        self.status_var.set("Resultados limpos")
    
    def show_result_details(self, event):
        """Mostra detalhes do resultado selecionado."""
        selection = self.results_tree.selection()
        if not selection:
            return
        
        item = self.results_tree.item(selection[0])
        idx = int(item["text"]) - 1
        
        if 0 <= idx < len(self.results):
            result = self.results[idx]

            detail_window = tk.Toplevel(self.root)
            detail_window.title(f"Detalhes - {result['file']}")
            detail_window.geometry("800x600")

            main_frame = ttk.Frame(detail_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)

            info_frame = ttk.LabelFrame(main_frame, text="Informações", padding="10")
            info_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(info_frame, text=f"Repositório: {result['repo']}", 
                 font=("Arial", 10, "bold")).pack(anchor=tk.W)
            ttk.Label(info_frame, text=f"Arquivo: {result['file']}", 
                 font=("Arial", 10, "bold")).pack(anchor=tk.W)
            ttk.Label(info_frame, text=f"Linha: {result['line_number']}", 
                 font=("Arial", 10, "bold")).pack(anchor=tk.W)

            code_frame = ttk.LabelFrame(main_frame, text="Código", padding="10")
            code_frame.pack(fill=tk.BOTH, expand=True)
            
            code_text = scrolledtext.ScrolledText(code_frame, wrap=tk.WORD, 
                                                  font=("Consolas", 10))
            code_text.pack(fill=tk.BOTH, expand=True)

            try:
                repo_path = Path("repos_temp") / result["repo"]
                file_path = repo_path / result["file"]
                
                if file_path.exists():
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()

                    line_num = result["line_number"]
                    start = max(0, line_num - 10)
                    end = min(len(lines), line_num + 10)
                    
                    for i in range(start, end):
                        prefix = ">>> " if i + 1 == line_num else "    "
                        code_text.insert(tk.END, f"{prefix}{i+1:4d} | {lines[i]}")

                    code_text.tag_add("highlight", 
                                    f"{line_num - start + 1}.0", 
                                    f"{line_num - start + 1}.end")
                    code_text.tag_config("highlight", background="yellow")
            except Exception as e:
                code_text.insert(tk.END, f"Erro ao ler arquivo: {e}\n\n")
                code_text.insert(tk.END, f"Linha encontrada:\n{result['line']}")
            
            code_text.config(state="disabled")
    
    def copy_selected(self):
        """Copia o resultado selecionado."""
        selection = self.results_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Nenhum resultado selecionado!")
            return
        
        item = self.results_tree.item(selection[0])
        idx = int(item["text"]) - 1
        
        if 0 <= idx < len(self.results):
            result = self.results[idx]
            text = f"Repositório: {result['repo']}\n"
            text += f"Arquivo: {result['file']}\n"
            text += f"Linha: {result['line_number']}\n"
            text += f"Código: {result['line']}"
            
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Sucesso", "Resultado copiado para a área de transferência!")
    
    def save_results(self):
        """Salva os resultados em um arquivo JSON."""
        if not self.results:
            messagebox.showwarning("Aviso", "Nenhum resultado para salvar!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(self.results, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Sucesso", f"Resultados salvos em {filename}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar arquivo:\n{e}")


def main():
    """Função principal para iniciar a GUI."""
    root = tk.Tk()
    app = RepoSearchGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

