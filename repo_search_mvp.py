import git
import os
import re
import json
from pathlib import Path

# Configurações
token = os.getenv("GITHUB_TOKEN")
user = "Lucasbettio"

REPOS = [
    "Lucasbettio/teste_pratico",
    "Lucasbettio/ToDoListProject",
    "Lucasbettio/mvc_project",
]

SEARCH_STRING = "README"
BASE_DIR = Path("repos_temp")
BASE_DIR.mkdir(exist_ok=True)

results = []

def build_url(repo_name: str):
    return f"https://{user}:{token}@github.com/{repo_name}.git"

for repo_name in REPOS:
    repo_url = build_url(repo_name)
    repo_dirname = repo_name.split("/")[-1]
    repo_path = BASE_DIR / repo_dirname

    print(f"\n🔍 Buscando em {repo_dirname}...")

    if not repo_path.exists():
        repo = git.Repo.clone_from(repo_url, repo_path)
    else:
        repo = git.Repo(repo_path)
        origin = repo.remotes.origin

        if origin.url != repo_url:
            config_lock = repo_path / ".git" / "config.lock"
            if config_lock.exists():
                config_lock.unlink()

            origin.set_url(repo_url)

        origin.pull(rebase=True)

    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = Path(root) / file
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f):
                        if re.search(SEARCH_STRING, line):
                            results.append({
                                "repo": repo_dirname,
                                "file": str(file_path.relative_to(repo_path)),
                                "line_number": i + 1,
                                "line": line.strip()
                            })
            except:
                pass

with open("resultado_busca.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\n✅ Busca concluída! Resultados salvos em resultado_busca.json")
