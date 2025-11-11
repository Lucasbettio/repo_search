import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_executable():
    print("🔨 Iniciando build do executável...")
    
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("📦 Instalando PyInstaller...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    print("🔍 Limpando builds anteriores...")
    for dir_name in ["build", "dist", "__pycache__"]:
        dir_path = script_dir / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"   Removido: {dir_name}/")
    
    spec_file = script_dir / "repo_search.spec"
    if spec_file.exists():
        spec_file.unlink()
    
    print("📝 Criando executável...")
    
    config_file = script_dir / "config.json"
    add_data = f"config.json;." if config_file.exists() else ""
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "gui.py",
        "--name=RepoSearch",
        "--onefile",
        "--windowed",
        "--hidden-import=gitlab",
        "--hidden-import=git",
        "--hidden-import=dotenv",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.scrolledtext",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=tkinter.filedialog",
        "--collect-all=tkinter",
        "--clean",
        "--noconfirm"
    ]
    
    if add_data:
        cmd.insert(-2, f"--add-data={add_data}")
    
    subprocess.run(cmd, check=True)
    
    exe_path = script_dir / "dist" / "RepoSearch.exe"
    if exe_path.exists():
        print("\n✅ Build concluído!")
        print(f"📁 Executável gerado em: {exe_path}")
        print(f"📦 Tamanho: {exe_path.stat().st_size / (1024*1024):.2f} MB")
        print("\n💡 Para distribuir:")
        print("   1. Copie o arquivo RepoSearch.exe")
        print("   2. Crie um arquivo .env com GITLAB_TOKEN e GITLAB_URL (opcional)")
        print("   3. O usuário precisa ter Git instalado no sistema")
    else:
        print("\n❌ Erro: Executável não foi gerado!")
        sys.exit(1)

if __name__ == "__main__":
    try:
        build_executable()
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erro durante o build: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)

