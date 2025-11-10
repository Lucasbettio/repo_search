import os
import re
import json
import sys
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Tentar encontrar e configurar Git antes de importar
def find_git_executable():
    """Encontra o executável Git no sistema."""
    # Tentar encontrar Git no PATH
    git_path = shutil.which("git")
    if git_path:
        return git_path
    
    # Tentar localizações comuns no Windows
    common_paths = [
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Program Files (x86)\Git\bin\git.exe",
        r"C:\Program Files\Git\cmd\git.exe",
    ]
    
    for git_exe in common_paths:
        if os.path.exists(git_exe):
            return git_exe
    
    return None

# Configurar variável de ambiente se Git foi encontrado
git_exe = find_git_executable()
if git_exe and not os.getenv("GIT_PYTHON_GIT_EXECUTABLE"):
    os.environ["GIT_PYTHON_GIT_EXECUTABLE"] = git_exe

# Importar git (pode falhar se Git não estiver instalado)
try:
    import git
    # Tentar refresh silencioso
    try:
        git.refresh()
    except:
        pass
except (ImportError, Exception) as e:
    print("❌ Erro: Git não encontrado no sistema!")
    print("\nPor favor, instale o Git:")
    print("  https://git-scm.com/download/win")
    print("\nOu configure a variável de ambiente GIT_PYTHON_GIT_EXECUTABLE")
    print(f"\nErro detalhado: {e}")
    sys.exit(1)

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações
token = os.getenv("GITHUB_TOKEN")
user = os.getenv("GITHUB_USER", "Lucasbettio")

# Validar token
if not token:
    print("❌ Erro: GITHUB_TOKEN não encontrado!")
    print("Por favor, crie um arquivo .env na raiz do projeto com:")
    print("GITHUB_TOKEN=seu_token_aqui")
    print("GITHUB_USER=seu_usuario (opcional)")
    sys.exit(1)

REPOS = [
    "Lucasbettio/teste_pratico",
    "Lucasbettio/ToDoListProject",
    "Lucasbettio/mvc_project",
]

SEARCH_STRING = "README"
BASE_DIR = Path("repos_temp")
BASE_DIR.mkdir(exist_ok=True)

def build_url(repo_name: str, user: str, token: str) -> str:
    """Constrói a URL do repositório com autenticação."""
    return f"https://{user}:{token}@github.com/{repo_name}.git"

def clone_or_update_repo(repo_name: str, repo_url: str, repo_path: Path) -> git.Repo:
    """Clona ou atualiza um repositório."""
    try:
        if not repo_path.exists():
            print(f"  📥 Clonando repositório...")
            repo = git.Repo.clone_from(repo_url, repo_path)
        else:
            repo = git.Repo(repo_path)
            origin = repo.remotes.origin

            # Verificar e atualizar URL se necessário
            if origin.url != repo_url:
                config_lock = repo_path / ".git" / "config.lock"
                if config_lock.exists():
                    config_lock.unlink()
                origin.set_url(repo_url)

            print(f"  🔄 Atualizando repositório...")
            origin.pull(rebase=True)
        
        return repo
    except git.exc.GitCommandError as e:
        print(f"  ❌ Erro ao clonar/atualizar: {e}")
        raise
    except Exception as e:
        print(f"  ❌ Erro inesperado: {e}")
        raise

def search_in_repo(repo_path: Path, search_string: str, repo_dirname: str) -> list:
    """Busca uma string em todos os arquivos do repositório."""
    results = []
    pattern = re.compile(search_string, re.IGNORECASE)
    
    for root, _, files in os.walk(repo_path):
        # Ignorar pasta .git
        if ".git" in root:
            continue
            
        for file in files:
            file_path = Path(root) / file
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, start=1):
                        if pattern.search(line):
                            results.append({
                                "repo": repo_dirname,
                                "file": str(file_path.relative_to(repo_path)),
                                "line_number": i,
                                "line": line.strip()
                            })
            except (PermissionError, UnicodeDecodeError, IOError) as e:
                # Ignorar arquivos binários ou sem permissão
                continue
    
    return results

def main():
    """Função principal para executar a busca."""
    print(f"\n🔍 Iniciando busca por '{SEARCH_STRING}' em {len(REPOS)} repositório(s)...\n")
    
    results = []
    
    for repo_name in REPOS:
        repo_url = build_url(repo_name, user, token)
        repo_dirname = repo_name.split("/")[-1]
        repo_path = BASE_DIR / repo_dirname

        print(f"🔍 Buscando em {repo_dirname}...")

        try:
            clone_or_update_repo(repo_name, repo_url, repo_path)
            repo_results = search_in_repo(repo_path, SEARCH_STRING, repo_dirname)
            results.extend(repo_results)
            print(f"  ✅ Encontrados {len(repo_results)} resultado(s)")
        except Exception as e:
            print(f"  ❌ Erro ao processar {repo_dirname}: {e}")
            continue

    # Salvar resultados
    output_file = "resultado_busca.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Busca concluída! {len(results)} resultado(s) encontrado(s)")
    print(f"📄 Resultados salvos em {output_file}")

if __name__ == "__main__":
    main()
