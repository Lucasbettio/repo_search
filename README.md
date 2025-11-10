# GitHub Repository Search

Ferramenta para buscar strings ou padrões em múltiplos repositórios GitHub, simplificando o desenvolvimento ao encontrar código rapidamente.

## 🚀 Funcionalidades

- ✅ Busca em múltiplos repositórios GitHub simultaneamente
- ✅ Interface gráfica intuitiva
- ✅ Suporte a busca por string ou regex
- ✅ Visualização de resultados com preview do código
- ✅ Exportação de resultados em JSON
- ✅ Clonagem e atualização automática de repositórios
- ✅ Tratamento robusto de erros

## 📋 Requisitos

- Python 3.7+
- Git instalado no sistema
- Token de acesso pessoal do GitHub

## 🔧 Instalação

1. Clone ou baixe este repositório

2. Instale as dependências:
```bash
pip install -r requirements-dev.txt
```

3. Crie um arquivo `.env` na raiz do projeto:
```env
GITHUB_TOKEN=seu_token_github_aqui
GITHUB_USER=seu_usuario (opcional)
```

### Como obter um token do GitHub

1. Acesse: https://github.com/settings/tokens
2. Clique em "Generate new token" → "Generate new token (classic)"
3. Dê um nome ao token (ex: "repo_search")
4. Selecione as permissões necessárias:
   - `repo` (acesso completo aos repositórios)
5. Clique em "Generate token"
6. Copie o token e cole no arquivo `.env`

## 💻 Uso

### Interface Gráfica (Recomendado)

Execute a interface gráfica:
```bash
python gui.py
```

A interface permite:
- Configurar token e usuário do GitHub
- Adicionar múltiplos repositórios (um por linha, formato: `user/repo`)
- Buscar strings ou padrões regex
- Visualizar resultados com preview do código
- Salvar resultados em JSON
- Ver detalhes completos de cada resultado

### Linha de Comando

Execute o script MVP:
```bash
python repo_search_mvp.py
```

Edite o arquivo `repo_search_mvp.py` para configurar:
- Lista de repositórios (`REPOS`)
- String de busca (`SEARCH_STRING`)

Os resultados serão salvos em `resultado_busca.json`.

## 📁 Estrutura do Projeto

```
repo_search/
├── gui.py                 # Interface gráfica
├── repo_searcher.py       # Módulo de busca (reutilizável)
├── repo_search_mvp.py     # Script MVP (linha de comando)
├── requirements-dev.txt   # Dependências
├── README.md              # Este arquivo
├── .env                   # Variáveis de ambiente (não versionado)
└── repos_temp/            # Repositórios clonados (criado automaticamente)
```

## 🎯 Exemplos de Uso

### Buscar por string simples
```
README
```

### Buscar por padrão regex
```
def\s+\w+\(
```

### Buscar em múltiplos repositórios
Na interface gráfica, adicione um repositório por linha:
```
Lucasbettio/teste_pratico
Lucasbettio/ToDoListProject
Lucasbettio/mvc_project
```

## 📊 Formato dos Resultados

Os resultados são salvos em JSON com a seguinte estrutura:

```json
[
  {
    "repo": "nome_do_repositorio",
    "file": "caminho/do/arquivo.py",
    "line_number": 42,
    "line": "código da linha encontrada"
  }
]
```

## ⚠️ Solução de Problemas

### Erro de permissão
- Verifique se o token do GitHub tem as permissões corretas
- Certifique-se de que o Git está instalado e configurado
- Verifique se você tem acesso aos repositórios listados

### Token não encontrado
- Certifique-se de que o arquivo `.env` existe na raiz do projeto
- Verifique se o arquivo `.env` contém `GITHUB_TOKEN=seu_token`

### Erro ao clonar repositório
- Verifique se o nome do repositório está no formato correto: `user/repo`
- Certifique-se de que o repositório existe e você tem acesso
- Verifique sua conexão com a internet

## 🔒 Segurança

- **NUNCA** commite o arquivo `.env` no Git
- O arquivo `.env` já está no `.gitignore`
- Mantenha seu token do GitHub seguro e privado
- Se o token for comprometido, revogue-o imediatamente no GitHub

## 📝 Licença

Este projeto é de uso livre para fins educacionais e de desenvolvimento.

## 🤝 Contribuições

Sinta-se à vontade para sugerir melhorias ou reportar problemas!
