# GitLab Repository Search

Ferramenta para buscar strings ou padrões em múltiplos repositórios GitLab, permitindo seleção de grupos específicos para busca.

## 🚀 Funcionalidades

- ✅ Busca em múltiplos repositórios GitLab simultaneamente
- ✅ Seleção de grupos do GitLab para filtrar repositórios
- ✅ Interface gráfica intuitiva
- ✅ Suporte a busca por string ou regex
- ✅ Visualização de resultados com preview do código
- ✅ Exportação de resultados em JSON
- ✅ Clonagem e atualização automática de repositórios
- ✅ Tratamento robusto de erros

## 📋 Requisitos

- Python 3.7+
- Git instalado no sistema
- Token de acesso pessoal do GitLab (com permissão read_api)

## 🔧 Instalação

1. Clone ou baixe este repositório

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Crie um arquivo `.env` na raiz do projeto:
```env
GITLAB_TOKEN=seu_token_gitlab_aqui
GITLAB_URL=https://gitlab.nelogica.com.br/
```

### Como obter um token do GitLab

1. Acesse seu GitLab: https://gitlab.nelogica.com.br/-/user_settings/personal_access_tokens
2. Crie um novo token pessoal
3. Dê um nome ao token (ex: "repo_search")
4. Selecione as permissões necessárias:
   - `read_api` (acesso de leitura à API)
   - `read_repository` (acesso de leitura aos repositórios)
5. Clique em "Create personal access token"
6. Copie o token e cole no arquivo `.env`

## 💻 Uso

### Interface Gráfica (Recomendado)

Execute a interface gráfica:
```bash
python gui.py
```

A interface permite:
- Configurar token e URL do GitLab
- Carregar grupos disponíveis do GitLab
- Selecionar grupos específicos para buscar (QA, COMDINHEIRO, PROFIT, Docker Images, etc.)
- Buscar strings ou padrões regex
- Visualizar resultados com preview do código
- Salvar resultados em JSON
- Ver detalhes completos de cada resultado

### Passo a passo

1. Abra a aplicação executando `python gui.py`
2. Informe o token do GitLab (ou carregue do .env)
3. Informe a URL do GitLab (padrão: https://gitlab.nelogica.com.br/)
4. Clique em "Carregar Grupos" para listar todos os grupos disponíveis
5. Selecione um ou mais grupos que deseja buscar
6. Informe o termo de busca
7. Clique em "Buscar" para iniciar a busca

## 🏗️ Gerar Executável

Para criar um executável Windows (.exe) que pode ser distribuído:

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute o script de build:
```bash
python build_exe.py
```

Ou no Windows:
```bash
build.bat
```

3. O executável será gerado em `dist/RepoSearch.exe`

4. Para distribuir:
   - Copie o arquivo `RepoSearch.exe`
   - Crie um arquivo `.env` com `GITLAB_TOKEN` e `GITLAB_URL` (opcional)
   - O usuário precisa ter Git instalado no sistema

## 📁 Estrutura do Projeto

```
repo_search/
├── gui.py                 # Interface gráfica
├── repo_searcher.py       # Módulo de busca
├── gitlab_collector.py    # Coletor de repositórios GitLab
├── build_exe.py           # Script para gerar executável
├── requirements.txt       # Dependências de produção
├── requirements-dev.txt   # Dependências de desenvolvimento
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

### Selecionar grupos específicos
Na interface gráfica:
1. Carregue os grupos
2. Selecione os grupos desejados (ex: QA, COMDINHEIRO, PROFIT)
3. Execute a busca

## 📊 Formato dos Resultados

Os resultados são salvos em JSON com a seguinte estrutura:

```json
[
  {
    "repo": "grupo/repositorio",
    "file": "caminho/do/arquivo.py",
    "line_number": 42,
    "line": "código da linha encontrada"
  }
]
```

## ⚠️ Solução de Problemas

### Erro de permissão
- Verifique se o token do GitLab tem as permissões corretas (read_api, read_repository)
- Certifique-se de que o Git está instalado e configurado
- Verifique se você tem acesso aos grupos selecionados

### Token não encontrado
- Certifique-se de que o arquivo `.env` existe na raiz do projeto
- Verifique se o arquivo `.env` contém `GITLAB_TOKEN=seu_token`

### Erro ao carregar grupos
- Verifique se a URL do GitLab está correta
- Verifique se o token tem permissão para listar grupos
- Verifique sua conexão com a rede/VPN

### Erro ao clonar repositório
- Verifique se você tem acesso aos repositórios do grupo
- Certifique-se de que o Git está instalado
- Verifique sua conexão com a internet/VPN

## 🔒 Segurança

- **NUNCA** commite o arquivo `.env` no Git
- O arquivo `.env` já está no `.gitignore`
- Mantenha seu token do GitLab seguro e privado
- Se o token for comprometido, revogue-o imediatamente no GitLab

## 📝 Licença

Este projeto é de uso livre para fins educacionais e de desenvolvimento.

## 🤝 Contribuições

Sinta-se à vontade para sugerir melhorias ou reportar problemas!
