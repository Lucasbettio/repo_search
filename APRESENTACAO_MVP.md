# 📊 Apresentação do MVP - GitHub Repository Search

## 🎯 Objetivo do Projeto

Ferramenta para buscar strings ou padrões em múltiplos repositórios GitHub simultaneamente, simplificando o desenvolvimento ao encontrar código rapidamente em vários projetos.

---

## 📁 Estrutura do Projeto

### Arquivos Principais

```
repo_search/
├── repo_search_mvp.py    # Script MVP original (linha de comando)
├── repo_searcher.py       # Módulo reutilizável (classe)
├── gui.py                 # Interface gráfica (usa repo_searcher.py)
├── requirements-dev.txt   # Dependências do projeto
├── README.md              # Documentação principal
└── .env                   # Configurações (não versionado)
```

---

## 🔍 Por que existem dois arquivos "repo_search"?

### 1. `repo_search_mvp.py` - Script MVP Original
**Propósito:** Versão inicial do MVP, script simples para linha de comando.

**Características:**
- ✅ Script funcional e direto
- ✅ Execução rápida via terminal
- ✅ Ideal para automação/scripts
- ✅ Código procedural (funções simples)

**Quando usar:**
- Execução rápida via terminal
- Integração em pipelines/scripts
- Quando não precisa de interface gráfica

### 2. `repo_searcher.py` - Módulo Reutilizável
**Propósito:** Refatoração do código em uma classe orientada a objetos, tornando-o reutilizável.

**Características:**
- ✅ Código modular e reutilizável
- ✅ Suporte a callbacks (progresso, resultados)
- ✅ Busca em thread separada (não trava interface)
- ✅ Cancelamento de buscas
- ✅ Tratamento de erros robusto

**Quando usar:**
- Quando precisa integrar em outras aplicações
- Quando precisa de interface gráfica
- Quando precisa de controle mais fino (cancelar, progresso, etc.)

### 3. `gui.py` - Interface Gráfica
**Propósito:** Interface visual que usa o módulo `repo_searcher.py`.

**Características:**
- ✅ Interface amigável
- ✅ Visualização de resultados em tempo real
- ✅ Configuração via UI
- ✅ Exportação de resultados

---

## 📄 Detalhamento dos Arquivos

### 1. `repo_search_mvp.py` - Script MVP

#### **Funções Principais:**

##### `find_git_executable()`
- **O que faz:** Encontra o executável Git no sistema
- **Retorna:** Caminho do Git ou `None`
- **Por quê:** Necessário porque o GitPython precisa saber onde está o Git

##### `build_url(repo_name, user, token)`
- **O que faz:** Constrói URL do repositório com autenticação
- **Exemplo:** `https://user:token@github.com/user/repo.git`
- **Por quê:** GitHub requer autenticação para clonar repositórios privados

##### `clone_or_update_repo(repo_name, repo_url, repo_path)`
- **O que faz:** 
  - Se o repositório não existe localmente → clona
  - Se já existe → atualiza (pull)
- **Tratamento de erros:** Remove locks do Git se necessário
- **Por quê:** Evita clonar novamente repositórios já existentes

##### `search_in_repo(repo_path, search_string, repo_dirname)`
- **O que faz:** 
  - Percorre todos os arquivos do repositório
  - Busca a string usando regex (case-insensitive)
  - Ignora pasta `.git` e arquivos binários
- **Retorna:** Lista de resultados encontrados
- **Formato do resultado:**
  ```python
  {
    "repo": "nome_repo",
    "file": "caminho/arquivo.py",
    "line_number": 42,
    "line": "código da linha"
  }
  ```

##### `main()`
- **O que faz:** Função principal que orquestra todo o processo
- **Fluxo:**
  1. Valida token do GitHub
  2. Para cada repositório:
     - Clona/atualiza
     - Busca a string
     - Coleta resultados
  3. Salva resultados em JSON

#### **Configurações (variáveis no topo):**
```python
REPOS = ["user/repo1", "user/repo2"]  # Lista de repositórios
SEARCH_STRING = "README"                # String a buscar
BASE_DIR = Path("repos_temp")           # Onde salvar repositórios
```

---

### 2. `repo_searcher.py` - Módulo Reutilizável

#### **Classe: `RepoSearcher`**

##### `__init__(token, user, base_dir)`
- **O que faz:** Inicializa o buscador
- **Parâmetros:**
  - `token`: Token do GitHub (obrigatório)
  - `user`: Usuário do GitHub (padrão: "Lucasbettio")
  - `base_dir`: Onde salvar repositórios (padrão: "repos_temp")
- **Cria:** Flag de cancelamento para interromper buscas

##### `build_url(repo_name)`
- **O que faz:** Constrói URL com autenticação
- **Diferença do MVP:** Método da classe (usa `self.token`, `self.user`)

##### `clone_or_update_repo(repo_name, repo_url, repo_path, progress_callback)`
- **O que faz:** Clona ou atualiza repositório
- **Novidade:** Aceita `progress_callback` para atualizar UI em tempo real
- **Retorna:** `git.Repo` ou `None` (se erro)
- **Tratamento:** Não levanta exceção, retorna `None` para continuar processando outros repos

##### `search_in_repo(repo_path, search_string, repo_dirname, progress_callback)`
- **O que faz:** Busca string no repositório
- **Novidades:**
  - Suporte a regex (tenta compilar, se falhar usa busca literal)
  - Callback de progresso a cada 100 arquivos
  - Respeita flag de cancelamento
- **Retorna:** Lista de resultados

##### `search_repos(repos, search_string, progress_callback, result_callback)`
- **O que faz:** Busca em múltiplos repositórios
- **Parâmetros:**
  - `repos`: Lista de repositórios
  - `search_string`: String ou regex
  - `progress_callback`: Função chamada para atualizar progresso
  - `result_callback`: Função chamada para cada resultado encontrado
- **Retorna:** Lista completa de todos os resultados
- **Por quê:** Permite atualizar UI em tempo real enquanto busca

##### `cancel()`
- **O que faz:** Cancela a busca em andamento
- **Como:** Ativa flag interna que é verificada durante a busca
- **Por quê:** Permite interromper buscas longas

---

### 3. `gui.py` - Interface Gráfica

#### **Classe: `RepoSearchGUI`**

##### `__init__(root)`
- **O que faz:** Inicializa a interface gráfica
- **Cria:** Todos os widgets (campos, botões, tabela)

##### `create_widgets()`
- **O que faz:** Cria toda a interface
- **Seções:**
  1. **Configuração:** Token e usuário GitHub
  2. **Repositórios:** Text area para listar repos (um por linha)
  3. **Busca:** Campo de busca + botões
  4. **Resultados:** Tabela (Treeview) com resultados
  5. **Ações:** Salvar JSON, limpar, copiar

##### `start_search()`
- **O que faz:** Inicia a busca quando usuário clica em "Buscar"
- **Fluxo:**
  1. Valida entradas
  2. Cria `RepoSearcher`
  3. Inicia thread separada (não trava UI)
  4. Atualiza progresso em tempo real

##### `_search_thread(repos, search_string)`
- **O que faz:** Executa busca em thread separada
- **Por quê:** Evita travar a interface durante a busca
- **Callbacks:**
  - `progress_callback`: Atualiza barra de progresso
  - `result_callback`: Adiciona cada resultado na tabela

##### `add_result(result)`
- **O que faz:** Adiciona um resultado na tabela
- **Formato:** Mostra repo, arquivo, linha, preview do código

##### `show_result_details(event)`
- **O que faz:** Abre janela com detalhes do resultado (duplo clique)
- **Mostra:**
  - Informações do resultado
  - Código com contexto (10 linhas antes/depois)
  - Linha encontrada destacada

##### `save_results()`
- **O que faz:** Salva resultados em arquivo JSON
- **Usa:** `filedialog` para escolher local

##### `load_config()` / `save_config()`
- **O que faz:** Salva/carrega lista de repositórios em `config.json`
- **Por quê:** Lembra repositórios entre execuções

---

## 🔄 Fluxo de Execução

### Script MVP (`repo_search_mvp.py`):
```
1. Carrega .env → Valida token
2. Para cada repositório:
   ├─ Clona/atualiza
   ├─ Busca string
   └─ Coleta resultados
3. Salva JSON
```

### Interface Gráfica (`gui.py`):
```
1. Usuário configura token/repos
2. Usuário digita busca → Clica "Buscar"
3. GUI cria RepoSearcher
4. Thread separada executa busca:
   ├─ Para cada repo: clona/atualiza
   ├─ Busca string
   └─ Callbacks atualizam UI em tempo real
5. Resultados aparecem na tabela
6. Usuário pode ver detalhes, salvar, etc.
```

---

## 🎯 Decisões de Arquitetura

### Por que separar em módulos?

1. **Reutilização:** `repo_searcher.py` pode ser usado em outros projetos
2. **Manutenibilidade:** Código organizado e fácil de entender
3. **Testabilidade:** Cada módulo pode ser testado separadamente
4. **Escalabilidade:** Fácil adicionar novas funcionalidades

### Por que manter `repo_search_mvp.py`?

1. **Simplicidade:** Script direto, sem dependências de UI
2. **Automação:** Fácil integrar em pipelines/scripts
3. **Histórico:** Mostra evolução do código

---

## 📊 Comparação: MVP vs Módulo

| Característica | `repo_search_mvp.py` | `repo_searcher.py` |
|----------------|----------------------|-------------------|
| **Tipo** | Script procedural | Classe OOP |
| **Interface** | Terminal | N/A (módulo) |
| **Callbacks** | ❌ Não | ✅ Sim |
| **Threading** | ❌ Não | ✅ Sim |
| **Cancelamento** | ❌ Não | ✅ Sim |
| **Reutilização** | ❌ Baixa | ✅ Alta |
| **Complexidade** | ⭐ Simples | ⭐⭐ Média |

---

## 🚀 Como Apresentar

### 1. Demonstração Rápida (2 min)
```bash
# Mostrar script MVP
python repo_search_mvp.py

# Mostrar interface gráfica
python gui.py
```

### 2. Explicar Arquitetura (3 min)
- Mostrar os 3 arquivos principais
- Explicar por que existem dois "repo_search"
- Mostrar evolução: MVP → Módulo → GUI

### 3. Destaques Técnicos (2 min)
- Detecção automática do Git
- Tratamento de erros robusto
- Busca em thread separada (não trava UI)
- Suporte a regex
- Callbacks para atualização em tempo real

### 4. Casos de Uso (1 min)
- Buscar código em múltiplos projetos
- Encontrar padrões de código
- Validar implementações
- Documentação/README em vários repos

---

## 💡 Melhorias Futuras (Opcional para mencionar)

- [ ] Busca por tipo de arquivo (só .py, só .js, etc.)
- [ ] Filtros avançados (data, autor, etc.)
- [ ] Histórico de buscas
- [ ] Exportação em outros formatos (CSV, Excel)
- [ ] Integração com APIs do GitHub (sem clonar)
- [ ] Busca em branches específicos

---

## 📝 Resumo Executivo

**O que faz:** Busca strings/padrões em múltiplos repositórios GitHub

**Arquitetura:**
- `repo_search_mvp.py`: Script original (linha de comando)
- `repo_searcher.py`: Módulo reutilizável (classe)
- `gui.py`: Interface gráfica (usa o módulo)

**Diferenciais:**
- ✅ Busca em múltiplos repos simultaneamente
- ✅ Interface gráfica intuitiva
- ✅ Suporte a regex
- ✅ Resultados em tempo real
- ✅ Código modular e reutilizável

