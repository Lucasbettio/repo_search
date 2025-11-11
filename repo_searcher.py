import os
import re
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import threading


def find_git_executable():
    git_path = shutil.which("git")
    if git_path:
        return git_path

    common_paths = [
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Program Files (x86)\Git\bin\git.exe",
        r"C:\Program Files\Git\cmd\git.exe",
    ]
    
    for git_exe in common_paths:
        if os.path.exists(git_exe):
            return git_exe
    
    return None

git_exe = find_git_executable()
if git_exe and not os.getenv("GIT_PYTHON_GIT_EXECUTABLE"):
    os.environ["GIT_PYTHON_GIT_EXECUTABLE"] = git_exe

try:
    import git
    try:
        git.refresh()
    except:
        pass
except ImportError as e:
    raise ImportError(
        "Git não encontrado no sistema. "
        "Por favor, instale o Git: https://git-scm.com/download/win\n"
        f"Erro original: {e}"
    )


class RepoSearcher:
    def __init__(self, token: str, base_dir: Path = None, gitlab_url: str = None):
        self.token = token
        self.base_dir = base_dir or Path("repos_temp")
        self.base_dir.mkdir(exist_ok=True)
        self._cancel_flag = threading.Event()
        self.gitlab_url = gitlab_url
        self.is_gitlab = gitlab_url is not None
    
    def build_url(self, repo_name: str) -> str:
        if self.is_gitlab:
            gitlab_domain = self.gitlab_url.rstrip("/").replace("https://", "").replace("http://", "")
            return f"https://oauth2:{self.token}@{gitlab_domain}/{repo_name}.git"
        else:
            username = "oauth2"
            return f"https://{username}:{self.token}@github.com/{repo_name}.git"
    
    def clone_or_update_repo(self, repo_name: str, repo_url: str, repo_path: Path, 
                            progress_callback=None) -> Optional[git.Repo]:
        if self._cancel_flag.is_set():
            return None
            
        try:
            if not repo_path.exists():
                if progress_callback:
                    progress_callback(f"Clonando {repo_name}...")
                repo = git.Repo.clone_from(repo_url, repo_path)
            else:
                repo = git.Repo(repo_path)
                origin = repo.remotes.origin

                if origin.url != repo_url:
                    config_lock = repo_path / ".git" / "config.lock"
                    if config_lock.exists():
                        config_lock.unlink()
                    origin.set_url(repo_url)

                if progress_callback:
                    progress_callback(f"Atualizando {repo_name}...")
                origin.pull(rebase=True)
            
            return repo
        except git.exc.GitCommandError as e:
            if progress_callback:
                progress_callback(f"Erro ao clonar/atualizar {repo_name}: {e}")
            return None
        except Exception as e:
            if progress_callback:
                progress_callback(f"Erro inesperado em {repo_name}: {e}")
            return None
    
    def search_in_repo(self, repo_path: Path, search_string: str, 
                      repo_dirname: str, progress_callback=None) -> List[Dict]:
        results = []
        try:
            pattern = re.compile(search_string, re.IGNORECASE)
        except re.error:
            pattern = re.compile(re.escape(search_string), re.IGNORECASE)
        
        file_count = 0
        for root, _, files in os.walk(repo_path):
            if self._cancel_flag.is_set():
                break

            if ".git" in root:
                continue
                
            for file in files:
                if self._cancel_flag.is_set():
                    break
                    
                file_path = Path(root) / file
                file_count += 1
                
                if file_count % 100 == 0 and progress_callback:
                    progress_callback(f"Processando arquivos... ({file_count})")
                
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for i, line in enumerate(f, start=1):
                            if self._cancel_flag.is_set():
                                break
                            if pattern.search(line):
                                results.append({
                                    "repo": repo_dirname,
                                    "file": str(file_path.relative_to(repo_path)),
                                    "line_number": i,
                                    "line": line.strip()
                                })
                except (PermissionError, UnicodeDecodeError, IOError):
                    continue
        
        return results
    
    def search_repos(self, repos: List[str], search_string: str, 
                    progress_callback=None, result_callback=None) -> List[Dict]:
        self._cancel_flag.clear()
        all_results = []
        
        total_repos = len(repos)
        for idx, repo_name in enumerate(repos, 1):
            if self._cancel_flag.is_set():
                break
                
            if progress_callback:
                progress_callback(f"Processando repositório {idx}/{total_repos}: {repo_name}")
            
            repo_url = self.build_url(repo_name)
            repo_path = self.base_dir / repo_name.replace("/", "_")

            repo = self.clone_or_update_repo(repo_name, repo_url, repo_path, progress_callback)
            if repo is None:
                continue

            repo_results = self.search_in_repo(repo_path, search_string, repo_name, progress_callback)
            all_results.extend(repo_results)
            
            if result_callback:
                for result in repo_results:
                    result_callback(result)
            
            if progress_callback:
                progress_callback(f"Encontrados {len(repo_results)} resultado(s) em {repo_name}")
        
        return all_results
    
    def cancel(self):
        self._cancel_flag.set()

