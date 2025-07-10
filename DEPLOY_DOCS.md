# 🚀 Deploy da Documentação - GitHub Pages

Este documento explica como configurar e fazer deploy da documentação do **wBJJ** no GitHub Pages.

## 📋 Configuração Inicial do GitHub Pages

### 1. Ativar GitHub Pages

1. **Acesse as configurações do repositório:**
   ```
   https://github.com/wgalleti/wbjj/settings/pages
   ```

2. **Configure a origem:**
   - **Source**: `Deploy from a branch`
   - **Branch**: `gh-pages`
   - **Folder**: `/ (root)`

3. **Salve as configurações**

### 2. Verificar Permissões

Certifique-se de que as **Actions** têm permissão para escrever:

1. Vá para `Settings` > `Actions` > `General`
2. Em **Workflow permissions**, selecione:
   - ✅ `Read and write permissions`
   - ✅ `Allow GitHub Actions to create and approve pull requests`

## 🔄 Como Funciona o Deploy Automático

### Workflow Configurado

O arquivo `.github/workflows/docs.yml` executa automaticamente quando:

- ✅ **Push na main** com mudanças em `backend/docs/**`
- ✅ **Pull Request** com mudanças na documentação
- ✅ **Execução manual** via GitHub Actions

### Processo de Build

1. **Checkout** do código (`actions/checkout@v4`)
2. **Setup Python 3.11** + UV package manager (`actions/setup-python@v5`)
3. **Instalar dependências** (`uv sync --dev`)
4. **Build MkDocs** (`mkdocs build --clean --strict`)
5. **Upload artifacts** (`actions/upload-pages-artifact@v3`)
6. **Deploy** para branch `gh-pages` (`actions/deploy-pages@v4`)

> ✅ **Todas as actions atualizadas** para as versões mais recentes (2024)

### URLs

- **Documentação Online**: https://wgalleti.github.io/wbjj/
- **Workflow Actions**: https://github.com/wgalleti/wbjj/actions/workflows/docs.yml

## 🛠️ Desenvolvimento Local

### Usando Scripts

```bash
# A partir do diretório backend/

# Desenvolvimento local
./scripts/serve-docs.sh

# Testar build (como no CI)
./scripts/test-docs-build.sh
```

### Comandos Manuais

```bash
# Navegar para backend
cd backend

# Instalar dependências
uv sync --dev

# Servir documentação
cd docs
uv run mkdocs serve --dev-addr=127.0.0.1:8001
```

Acesse: http://127.0.0.1:8001

## 📁 Estrutura dos Arquivos

```
wbjj/                                    # ← Raiz do projeto
├── .github/workflows/docs.yml           # ← Workflow do GitHub Pages
├── DEPLOY_DOCS.md                      # ← Este arquivo
└── backend/                            # ← Subpasta do backend
    ├── docs/                           # ← Documentação
    │   ├── mkdocs.yml                  # ← Configuração MkDocs
    │   ├── docs/                       # ← Conteúdo (.md files)
    │   └── site/                       # ← Build output
    ├── scripts/serve-docs.sh           # ← Script para dev local
    └── pyproject.toml                  # ← Dependências Python
```

## 🚨 Troubleshooting

### Problema: Build falha

1. **Verificar logs** em Actions do GitHub
2. **Testar localmente:**
   ```bash
   # Teste completo (recomendado)
   ./scripts/test-docs-build.sh

   # Ou manual
   cd backend/docs
   uv run mkdocs build --clean --strict
   ```

### Problema: Actions deprecated

Se encontrar erros como "deprecated version of actions/upload-artifact":

1. **Verificar versões** no workflow (já corrigido):
   - ✅ `actions/checkout@v4`
   - ✅ `actions/setup-python@v5`
   - ✅ `actions/upload-pages-artifact@v3`
   - ✅ `actions/deploy-pages@v4`

2. **Forçar novo deploy** depois da correção

### Problema: Pages não ativa

1. **Verificar permissões** (seção 2 acima)
2. **Forçar novo deploy:**
   - Vá para Actions
   - Execute manualmente o workflow

### Problema: CSS/JS não carrega

1. **Verificar site_url** em `mkdocs.yml`
2. **Certificar paths** em arquivos estáticos
3. **Limpar cache** do navegador

## ✅ Checklist de Deploy

- [ ] **Repositório configurado** com GitHub Pages
- [ ] **Workflow permissions** habilitadas
- [ ] **Branch gh-pages** será criada automaticamente
- [ ] **Primeiro deploy** pode levar 5-10 minutos
- [ ] **URL final**: https://wgalleti.github.io/wbjj/

## 📞 Suporte

- **Issues**: https://github.com/wgalleti/wbjj/issues
- **Actions**: https://github.com/wgalleti/wbjj/actions
- **MkDocs Docs**: https://squidfunk.github.io/mkdocs-material/

---

**🎯 Deploy configurado e pronto para usar!**
