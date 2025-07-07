# Customização do Admin - Zenith Jiu Jitsu

## 🎨 Tema Personalizado

O admin do Django Unfold foi personalizado para refletir a identidade visual da Zenith Jiu Jitsu, baseado no logo oficial.

### Cores do Tema

**Paleta Amarelo e Azul (Primary)** - Inspirada nas cores do escudo:
- `50`: #FFFFF0 (Amarelo muito claro)
- `100`: #FEF9C3 (Amarelo claro)
- `200`: #FEF08A (Amarelo suave)
- `300`: #FDE047 (Amarelo médio)
- `400`: #FACC15 (Amarelo vibrante)
- `500`: #EAB308 (Amarelo principal) ⭐ **Cor principal**
- `600`: #CA8A04 (Amarelo escuro)
- `700`: #A16207 (Amarelo mais escuro)
- `800`: #854D0E (Amarelo muito escuro)
- `900`: #713F12 (Amarelo quase laranja)
- `950`: #422006 (Amarelo mais escuro)

**Cores Complementares:**
- 🔵 **Azul Principal**: #1E40AF (Azul do escudo)
- 🔵 **Azul Escuro**: #1E3A8A (Azul mais profundo)
- 🔵 **Azul Claro**: #3B82F6 (Azul para acentos)

### Logo

- **Arquivo**: `logo.png` (escudo da Zenith)
- **Localização**: `static/images/logo.png`
- **Configuração**: Usado tanto no tema claro quanto escuro

### Configuração Aplicada

```python
# Django Unfold Configuration
UNFOLD = {
    "SITE_TITLE": "Zenith Jiu Jitsu",
    "SITE_HEADER": "Zenith JJ Admin", 
    "SITE_URL": "/",
    "SITE_LOGO": "images/logo.png",
    "SITE_ICON": {
        "light": "/static/images/logo.png",
        "dark": "/static/images/logo.png",
    },
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32", 
            "type": "image/png",
            "href": lambda request: request.build_absolute_uri("/static/images/logo.png"),
        },
    ],
    "THEME": "light",
    "COLORS": {
        "primary": {
            # Paleta amarelo inspirada no escudo...
            "50": "255 255 240",   # Amarelo muito claro
            "100": "254 249 195",  # Amarelo claro
            "200": "254 240 138",  # Amarelo suave
            "300": "253 224 71",   # Amarelo médio
            "400": "250 204 21",   # Amarelo vibrante
            "500": "234 179 8",    # Amarelo principal
            "600": "202 138 4",    # Amarelo escuro
            "700": "161 98 7",     # Amarelo mais escuro
            "800": "133 77 14",    # Amarelo muito escuro
            "900": "113 63 18",    # Amarelo quase laranja
            "950": "66 32 6"       # Amarelo mais escuro
        }
    }
}

# Configurações adicionais do admin Django
ADMIN_SITE_HEADER = "Zenith Jiu Jitsu - Administração"
ADMIN_SITE_TITLE = "Zenith JJ Admin"
ADMIN_INDEX_TITLE = "Painel Administrativo"
```

### Arquivos Modificados

- `config/settings/base.py` - Configuração do tema Unfold e admin Django
- `config/urls.py` - Aplicação das configurações de título do admin
- `static/images/logo.png` - Logo da Zenith adicionado
- `static/css/custom-admin.css` - CSS personalizado para aprimorar o tema dourado
- `STATICFILES_DIRS` - Configurado para incluir arquivos estáticos personalizados

### Como Visualizar

1. Acesse o admin: `http://localhost:8000/admin/`
2. Faça login com suas credenciais (admin@example.com)
3. Observe as personalizações:
   - **Logo da Zenith**: Escudo amarelo/azul no cabeçalho e favicon
   - **Cores amarelas**: Botões principais, badges e elementos de destaque
   - **Cores azuis**: Links, sidebar e elementos de navegação
   - **Títulos personalizados**: "Zenith Jiu Jitsu - Administração"
   - **Tema claro**: Configurado para destacar as cores amarelo/azul
   - **Sidebar**: Menu com gradiente azul escuro para azul
   - **Contraste**: Amarelo vibrante (#EAB308) sobre azul escuro (#1E3A8A)
   - **Elementos visuais**: Formulários, tabelas e navegação com combinação amarelo/azul

### Personalização Adicional

Para fazer mais ajustes no tema:

1. **Cores**: Modifique a paleta `primary` em `UNFOLD.COLORS`
2. **Logo**: Substitua `static/images/logo.png`
3. **Títulos**: Altere `SITE_TITLE` e `SITE_HEADER`

Execute `python manage.py collectstatic` após qualquer mudança em arquivos estáticos.

### Solução de Problemas

**Se o logo não aparecer:**
1. Verifique se o arquivo `static/images/logo.png` existe
2. Execute `python manage.py collectstatic --noinput`
3. Reinicie o servidor Django
4. Limpe o cache do navegador (Ctrl+F5)

**Se as cores não aparecerem corretamente:**
1. Verifique se `THEME: "light"` está configurado no UNFOLD
2. Certifique-se de que o CSS personalizado foi coletado
3. Limpe o cache do navegador (Ctrl+F5)
4. Inspecione o elemento no navegador para verificar se as cores estão sendo aplicadas
5. Verifique se as variáveis CSS estão definidas corretamente no arquivo custom-admin.css

**Para debug:**
- Acesse `/static/images/logo.png` diretamente no navegador
- Verifique o console do navegador para erros de carregamento
- Use as ferramentas de desenvolvedor para inspecionar os estilos CSS aplicados

---

## 🎨 Mudanças de Cores Aplicadas

### Antes (Dourado):
- Paleta baseada em tons dourados/laranja
- Cor principal: #F59E0B (dourado)

### Agora (Amarelo/Azul):
- **Amarelo principal**: #EAB308 - Botões, badges, elementos de destaque
- **Azul principal**: #1E40AF - Links, navegação, textos
- **Azul escuro**: #1E3A8A - Sidebar, contrastes
- **Combinação**: Alta legibilidade com o contraste amarelo sobre azul

### Elementos Atualizados:
✅ **Botões primários**: Amarelo com texto azul escuro  
✅ **Links**: Azul que muda para amarelo no hover  
✅ **Sidebar**: Gradiente azul escuro para azul  
✅ **Formulários**: Bordas amarelas no foco  
✅ **Tabelas**: Cabeçalhos com fundo amarelo claro  
✅ **Navegação ativa**: Amarelo com texto azul escuro  
✅ **Paginação**: Azul com destaque amarelo   

---

## 🔒 Segurança e Permissions Policy

### Correção de Erros no Console

Para resolver erros de "Permissions policy violation" no console do navegador, foram implementados middlewares customizados:

**Arquivos Criados:**
- `apps/core/middleware.py` - Middlewares customizados

**Configurações Aplicadas:**

```python
# Middlewares adicionados
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'apps.core.middleware.PermissionsPolicyMiddleware',  # Para Permissions Policy
    'apps.core.middleware.SecurityHeadersMiddleware',    # Para cabeçalhos de segurança
    # ... outros middlewares
]

# Cabeçalhos de segurança
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'  # Permite iframe no admin
```

**Cabeçalhos HTTP Aplicados:**
- `Permissions-Policy: unload=(self)` - Permite eventos de unload
- `Referrer-Policy: strict-origin-when-cross-origin` - Política de referrer
- `X-Content-Type-Options: nosniff` - Previne MIME sniffing

### Problemas Resolvidos:
✅ **Console limpo**: Sem mais erros de permissions policy  
✅ **Segurança aprimorada**: Cabeçalhos de segurança implementados  
✅ **Admin funcional**: Iframe e eventos de página funcionando corretamente