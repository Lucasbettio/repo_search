# 🎯 Resumo Rápido - MVP GitHub Repository Search

## 📋 O que o projeto faz?

Busca uma string ou padrão em **múltiplos repositórios GitHub** simultaneamente e retorna onde foi encontrado (arquivo, linha, código).

---

## 🤔 Por que existem dois arquivos "repo_search"?

### `repo_search_mvp.py` - Script Original
- ✅ Versão inicial do MVP
- ✅ Script simples para terminal
- ✅ Código direto, fácil de entender
- ✅ Ideal para automação

### `repo_searcher.py` - Módulo Reutilizável  
- ✅ Refatoração em classe
- ✅ Usado pela interface gráfica
- ✅ Suporte a callbacks (progresso, resultados)
- ✅ Busca em thread (não trava)
- ✅ Pode ser reutilizado em outros projetos

**Resumo:** O MVP foi refatorado em um módulo reutilizável que é usado pela interface gráfica.

---

## 📁 Estrutura dos Arquivos

```
repo_search/
│
├── repo_search_mvp.py    ← Script original (terminal)
│   └── Funções: clone, busca, salva JSON
│
├── repo_searcher.py       ← Módulo reutilizável (classe)
│   └── Classe RepoSearcher com métodos:
│       • clone_or_update_repo()
│       • search_in_repo()
│       • search_repos() ← Busca em múltiplos repos
│       • cancel() ← Cancela busca
│
└── gui.py                 ← Interface gráfica
    └── Usa repo_searcher.py
    └── Interface com:
        • Campo de busca
        • Lista de repositórios
        • Tabela de resultados
        • Preview do código
```

---

## 🔄 Fluxo de Funcionamento

### Script MVP:
```
1. Lê .env (token GitHub)
2. Para cada repositório:
   ├─ Clona (se não existe) ou atualiza
   ├─ Busca string em todos os arquivos
   └─ Coleta resultados
3. Salva em resultado_busca.json
```

### Interface Gráfica:
```
1. Usuário configura token e repositórios
2. Usuário digita busca → Clica "Buscar"
3. Thread separada executa busca (não trava UI)
4. Resultados aparecem em tempo real na tabela
5. Usuário pode ver detalhes, salvar JSON, etc.
```

---

## 🛠️ Métodos Principais

### `repo_search_mvp.py`:

| Função | O que faz |
|--------|-----------|
| `find_git_executable()` | Encontra Git no sistema |
| `build_url()` | Cria URL com autenticação |
| `clone_or_update_repo()` | Clona ou atualiza repositório |
| `search_in_repo()` | Busca string nos arquivos |
| `main()` | Orquestra todo o processo |

### `repo_searcher.py` (Classe RepoSearcher):

| Método | O que faz |
|--------|-----------|
| `__init__()` | Inicializa com token/usuário |
| `clone_or_update_repo()` | Clona/atualiza (com callback) |
| `search_in_repo()` | Busca string (com progresso) |
| `search_repos()` | Busca em múltiplos repos |
| `cancel()` | Cancela busca em andamento |

### `gui.py` (Classe RepoSearchGUI):

| Método | O que faz |
|--------|-----------|
| `create_widgets()` | Cria interface |
| `start_search()` | Inicia busca |
| `_search_thread()` | Executa busca em thread |
| `add_result()` | Adiciona resultado na tabela |
| `show_result_details()` | Mostra código completo |
| `save_results()` | Exporta para JSON |

---

## 💡 Diferenciais Técnicos

1. **Detecção automática do Git** - Encontra Git mesmo se não estiver no PATH
2. **Tratamento robusto de erros** - Continua mesmo se um repo falhar
3. **Busca em thread separada** - Interface não trava durante busca
4. **Callbacks em tempo real** - Atualiza progresso e resultados enquanto busca
5. **Suporte a regex** - Busca padrões complexos
6. **Cancelamento** - Pode interromper buscas longas

---

## 🎬 Demonstração Rápida

### 1. Script MVP (30 seg)
```bash
python repo_search_mvp.py
# Busca "README" nos repos configurados
# Salva em resultado_busca.json
```

### 2. Interface Gráfica (1 min)
```bash
python gui.py
# Mostrar:
# - Configuração de token
# - Lista de repositórios
# - Campo de busca
# - Resultados em tempo real
# - Preview do código (duplo clique)
```

---

## 📊 Formato dos Resultados

```json
[
  {
    "repo": "nome_repositorio",
    "file": "caminho/arquivo.py",
    "line_number": 42,
    "line": "código da linha encontrada"
  }
]
```

---

## 🎯 Casos de Uso

- ✅ Buscar implementação de função em vários projetos
- ✅ Encontrar onde uma string é usada
- ✅ Validar padrões de código
- ✅ Buscar documentação (README, comentários)
- ✅ Encontrar imports ou dependências

---

## 🚀 Próximos Passos (Opcional)

- Filtros por tipo de arquivo
- Busca em branches específicos
- Histórico de buscas
- Integração com API do GitHub (sem clonar)

---

## 📝 Resumo em 1 Frase

**"Ferramenta que busca strings/padrões em múltiplos repositórios GitHub, com interface gráfica e resultados em tempo real."**

