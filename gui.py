import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import threading

try:
    from repo_searcher import RepoSearcher
    from gitlab_collector import GitLabCollector
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

load_dotenv()

class RepoSearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GitLab Repository Search")
        self.root.geometry("1200x800")
        self.root.minsize(900, 700)
        
        self.searcher = None
        self.search_thread = None
        self.results = []
        self.groups = []
        self.selected_groups = []
        self.gitlab_collector = None
        
        self.setup_style()
        self.create_widgets()
        self.load_config()
    
    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        self.bg_color = "#f0f0f0"
        self.accent_color = "#0078d4"
        self.text_color = "#333333"
        self.root.configure(bg=self.bg_color)
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        title_label = ttk.Label(main_frame, text="🔍 GitLab Repository Search", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        config_frame = ttk.LabelFrame(main_frame, text="Configuração GitLab", padding="10")
        config_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        ttk.Label(config_frame, text="GitLab Token:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.token_var = tk.StringVar()
        token_entry = ttk.Entry(config_frame, textvariable=self.token_var, width=50, show="*")
        token_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        env_token = os.getenv("GITLAB_TOKEN")
        if env_token:
            self.token_var.set(env_token)
            token_entry.configure(state="readonly")
            ttk.Label(config_frame, text="(carregado do .env)", 
                     foreground="gray").grid(row=0, column=2)
        
        self.gitlab_url_var = tk.StringVar(value=os.getenv("GITLAB_URL", "https://gitlab.nelogica.com.br/"))
        ttk.Label(config_frame, text="GitLab URL:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        url_entry = ttk.Entry(config_frame, textvariable=self.gitlab_url_var, width=50)
        url_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        
        button_frame = ttk.Frame(config_frame)
        button_frame.grid(row=1, column=2, pady=(10, 0))
        ttk.Button(button_frame, text="Carregar Grupos", 
                  command=self.load_groups).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Carregar .env", 
                  command=self.load_env).pack(side=tk.LEFT)
        
        groups_frame = ttk.LabelFrame(main_frame, text="Grupos do GitLab", padding="10")
        groups_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        groups_frame.columnconfigure(0, weight=1)
        groups_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        groups_container = ttk.Frame(groups_frame)
        groups_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        groups_container.columnconfigure(0, weight=1)
        groups_container.rowconfigure(0, weight=1)
        
        self.groups_listbox_frame = ttk.Frame(groups_container)
        self.groups_listbox_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.groups_listbox_frame.columnconfigure(0, weight=1)
        self.groups_listbox_frame.rowconfigure(0, weight=1)
        
        listbox_scrollbar = ttk.Scrollbar(self.groups_listbox_frame)
        listbox_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.groups_listbox = tk.Listbox(self.groups_listbox_frame, selectmode=tk.EXTENDED,
                                         yscrollcommand=listbox_scrollbar.set, height=8)
        self.groups_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        listbox_scrollbar.config(command=self.groups_listbox.yview)
        
        self.groups_listbox.bind("<<ListboxSelect>>", self.on_group_select)
        
        groups_buttons = ttk.Frame(groups_frame)
        groups_buttons.grid(row=1, column=0, pady=(10, 0))
        ttk.Button(groups_buttons, text="Selecionar Todos", 
                  command=self.select_all_groups).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(groups_buttons, text="Desselecionar Todos", 
                  command=self.deselect_all_groups).pack(side=tk.LEFT)
        
        search_frame = ttk.LabelFrame(main_frame, text="Busca", padding="10")
        search_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Buscar:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=50)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        search_entry.bind("<Return>", lambda e: self.start_search())
        
        button_frame = ttk.Frame(search_frame)
        button_frame.grid(row=0, column=2)
        
        self.search_button = ttk.Button(button_frame, text="🔍 Buscar", 
                                       command=self.start_search, width=15)
        self.search_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.cancel_button = ttk.Button(button_frame, text="❌ Cancelar", 
                                       command=self.cancel_search, state="disabled", width=15)
        self.cancel_button.pack(side=tk.LEFT)
        
        self.progress_var = tk.StringVar(value="Pronto")
        self.progress_label = ttk.Label(search_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        self.progress_bar = ttk.Progressbar(search_frame, mode='indeterminate')
        self.progress_bar.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        
        results_frame = ttk.LabelFrame(main_frame, text="Resultados", padding="10")
        results_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        columns = ("repo", "file", "line", "preview")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="tree headings", height=15)
        self.results_tree.heading("#0", text="#")
        self.results_tree.heading("repo", text="Repositório")
        self.results_tree.heading("file", text="Arquivo")
        self.results_tree.heading("line", text="Linha")
        self.results_tree.heading("preview", text="Preview")
        
        self.results_tree.column("#0", width=50, minwidth=50)
        self.results_tree.column("repo", width=200, minwidth=150)
        self.results_tree.column("file", width=200, minwidth=150)
        self.results_tree.column("line", width=80, minwidth=60)
        self.results_tree.column("preview", width=400, minwidth=200)
        
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.results_tree.bind("<Double-1>", self.show_result_details)
        
        action_frame = ttk.Frame(results_frame)
        action_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(action_frame, text="💾 Salvar JSON", 
                  command=self.save_results).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="🗑️ Limpar", 
                  command=self.clear_results).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="📋 Copiar Selecionado", 
                  command=self.copy_selected).pack(side=tk.LEFT)
        
        self.status_var = tk.StringVar(value="Pronto")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))
    
    def load_env(self):
        load_dotenv()
        token = os.getenv("GITLAB_TOKEN")
        url = os.getenv("GITLAB_URL", "https://gitlab.nelogica.com.br/")
        
        if token:
            self.token_var.set(token)
            messagebox.showinfo("Sucesso", "Token carregado do arquivo .env")
        else:
            messagebox.showwarning("Aviso", "GITLAB_TOKEN não encontrado no arquivo .env")
        
        if url:
            self.gitlab_url_var.set(url)
    
    def load_groups(self):
        token = self.token_var.get().strip()
        if not token:
            messagebox.showerror("Erro", "Por favor, informe o GitLab Token!")
            return
        
        url = self.gitlab_url_var.get().strip()
        if not url:
            messagebox.showerror("Erro", "Por favor, informe a URL do GitLab!")
            return
        
        try:
            self.progress_var.set("Carregando grupos...")
            self.gitlab_collector = GitLabCollector(token, url)
            self.groups = self.gitlab_collector.list_groups()
            
            self.groups_listbox.delete(0, tk.END)
            for group in self.groups:
                self.groups_listbox.insert(tk.END, group["name"])
            
            self.progress_var.set(f"Carregados {len(self.groups)} grupos")
            self.status_var.set(f"Carregados {len(self.groups)} grupos")
            messagebox.showinfo("Sucesso", f"Carregados {len(self.groups)} grupos do GitLab")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar grupos:\n{e}")
            self.progress_var.set("Erro ao carregar grupos")
    
    def on_group_select(self, event):
        selection = self.groups_listbox.curselection()
        self.selected_groups = [self.groups[i]["path"] for i in selection]
    
    def select_all_groups(self):
        self.groups_listbox.selection_set(0, tk.END)
        self.selected_groups = [group["path"] for group in self.groups]
    
    def deselect_all_groups(self):
        self.groups_listbox.selection_clear(0, tk.END)
        self.selected_groups = []
    
    def load_config(self):
        config_file = Path("config.json")
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    if "selected_groups" in config:
                        self.selected_groups = config["selected_groups"]
            except Exception as e:
                print(f"Erro ao carregar configuração: {e}")
    
    def save_config(self):
        config = {
            "selected_groups": self.selected_groups,
            "gitlab_url": self.gitlab_url_var.get()
        }
        config_file = Path("config.json")
        try:
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")
    
    def validate_inputs(self):
        token = self.token_var.get().strip()
        if not token:
            messagebox.showerror("Erro", "Por favor, informe o GitLab Token!")
            return False
        
        if not self.selected_groups:
            messagebox.showerror("Erro", "Por favor, selecione pelo menos um grupo!")
            return False
        
        search_string = self.search_var.get().strip()
        if not search_string:
            messagebox.showerror("Erro", "Por favor, informe o termo de busca!")
            return False
        
        return True
    
    def progress_callback(self, message):
        self.root.after(0, lambda: self.progress_var.set(message))
        self.root.after(0, lambda: self.status_var.set(message))
    
    def result_callback(self, result):
        self.root.after(0, lambda r=result: self.add_result(r))
    
    def add_result(self, result):
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
        if not self.validate_inputs():
            return

        self.clear_results()

        self.search_button.config(state="disabled")
        self.cancel_button.config(state="normal")

        self.progress_bar.start()
        self.progress_var.set("Iniciando busca...")

        token = self.token_var.get().strip()
        url = self.gitlab_url_var.get().strip()
        search_string = self.search_var.get().strip()

        if not self.gitlab_collector:
            self.gitlab_collector = GitLabCollector(token, url)

        self.search_thread = threading.Thread(
            target=self._search_thread,
            args=(search_string,),
            daemon=True
        )
        self.search_thread.start()
    
    def _search_thread(self, search_string):
        try:
            self.progress_callback("Buscando repositórios nos grupos selecionados...")
            repos = self.gitlab_collector.get_multiple_groups_repositories(self.selected_groups)
            
            if not repos:
                self.root.after(0, lambda: messagebox.showwarning("Aviso", "Nenhum repositório encontrado nos grupos selecionados!"))
                self.root.after(0, self._search_complete, [])
                return
            
            self.progress_callback(f"Encontrados {len(repos)} repositórios. Iniciando busca...")
            
            token = self.token_var.get().strip()
            url = self.gitlab_url_var.get().strip()
            self.searcher = RepoSearcher(token=token, gitlab_url=url)
            
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
        self.progress_bar.stop()
        self.progress_var.set(f"Busca concluída! {len(results)} resultado(s) encontrado(s)")
        self.status_var.set(f"Busca concluída! {len(results)} resultado(s) encontrado(s)")
        self.search_button.config(state="normal")
        self.cancel_button.config(state="disabled")
        self.save_config()
    
    def _search_error(self, error_msg):
        self.progress_bar.stop()
        self.progress_var.set("Erro na busca")
        self.status_var.set(f"Erro: {error_msg}")
        self.search_button.config(state="normal")
        self.cancel_button.config(state="disabled")
        messagebox.showerror("Erro", f"Erro durante a busca:\n{error_msg}")
    
    def cancel_search(self):
        if self.searcher:
            self.searcher.cancel()
        self.progress_bar.stop()
        self.progress_var.set("Busca cancelada")
        self.status_var.set("Busca cancelada pelo usuário")
        self.search_button.config(state="normal")
        self.cancel_button.config(state="disabled")
    
    def clear_results(self):
        self.results_tree.delete(*self.results_tree.get_children())
        self.results = []
        self.status_var.set("Resultados limpos")
    
    def show_result_details(self, event):
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
                repo_name_clean = result["repo"].replace("/", "_")
                repo_path = Path("repos_temp") / repo_name_clean
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
    root = tk.Tk()
    app = RepoSearchGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
