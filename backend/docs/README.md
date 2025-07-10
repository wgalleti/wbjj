# 📚 Documentação wBJJ

Documentação oficial do **wBJJ** - Sistema de Gestão para Academias de Brazilian Jiu-Jitsu.

## 🚀 Deploy Automático no GitHub Pages

A documentação é automaticamente implantada no GitHub Pages através do GitHub Actions sempre que há mudanças no diretório `backend/docs/` na branch `main`.

### 📋 Como Ativar o GitHub Pages

1. **Acesse as configurações do repositório:**
   - Vá para `Settings` > `Pages`

2. **Configure a origem:**
   - **Source**: Deploy from a branch
   - **Branch**: `gh-pages`
   - **Folder**: `/ (root)`

3. **Aguarde o deploy:**
   - O primeiro deploy pode levar alguns minutos
   - Acesse: `https://wgalleti.github.io/wbjj/`

### 🔄 Workflow Automático

O workflow `.github/workflows/docs.yml` é executado quando:

- ✅ Push na branch `main` com mudanças em `backend/docs/**`
- ✅ Pull request com mudanças na documentação
- ✅ Execução manual via `workflow_dispatch`

### 🛠️ Desenvolvimento Local

```bash
# Navegar para o backend
cd backend

# Instalar dependências
uv sync --dev

# Servir documentação localmente
cd docs
uv run mkdocs serve --dev-addr=127.0.0.1:8001
```

Acesse: `http://127.0.0.1:8001`

### 📁 Estrutura

```
backend/docs/
├── mkdocs.yml          # Configuração do MkDocs
├── docs/               # Conteúdo da documentação
│   ├── index.md       # Página inicial
│   ├── about.md       # Sobre o projeto
│   ├── api.md         # Documentação da API
│   ├── docker.md      # Guia Docker
│   ├── context.md     # Contexto e padrões
│   ├── usage.md       # Exemplos de uso
│   ├── customization.md # Customização
│   └── javascripts/   # Scripts customizados
└── site/              # Build output (ignorado no git)
```

### 🎨 Customização

A documentação usa o **Material for MkDocs** com:

- ✅ **Tema**: Material Design
- ✅ **Cores**: Azul e amarelo (identidade wBJJ)
- ✅ **Fontes**: Open Sans + Fira Code
- ✅ **Recursos**: Navegação SPA, busca, modo escuro
- ✅ **Idioma**: Português brasileiro

### 📝 Contribuindo

1. **Edite os arquivos** em `backend/docs/docs/`
2. **Teste localmente** com `mkdocs serve`
3. **Commit e push** para `main`
4. **Deploy automático** via GitHub Actions

### ⚡ Build e Deploy

```bash
# Build manual
cd backend/docs
uv run mkdocs build --clean --strict

# Deploy manual (se necessário)
uv run mkdocs gh-deploy --force
```

### 🔗 Links Úteis

- **Documentação Online**: https://wgalleti.github.io/wbjj/
- **Repositório**: https://github.com/wgalleti/wbjj
- **Material for MkDocs**: https://squidfunk.github.io/mkdocs-material/
