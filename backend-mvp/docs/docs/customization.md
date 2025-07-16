# Customização do Admin - wBJJ MVP

## 🎨 Tema Personalizado

O admin do Django foi personalizado para refletir a identidade visual do wBJJ MVP, baseado no design moderno e funcional.

### Cores do Tema

**Paleta Azul e Amarelo (Primary)** - Inspirada na identidade visual:
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
- 🔵 **Azul Principal**: #1E40AF (Azul do sistema)
- 🔵 **Azul Escuro**: #1E3A8A (Azul mais profundo)
- 🔵 **Azul Claro**: #3B82F6 (Azul para acentos)

### Logo

- **Arquivo**: `logo.png` (logo do wBJJ MVP)
- **Localização**: `static/images/logo.png`
- **Configuração**: Usado tanto no tema claro quanto escuro

### Configuração Aplicada

```python
# Django Admin Configuration
ADMIN_SITE_HEADER = "wBJJ MVP - Administração"
ADMIN_SITE_TITLE = "wBJJ MVP Admin"
ADMIN_INDEX_TITLE = "Painel Administrativo"

# Customização de CSS
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# CSS customizado
STATIC_URL = '/static/'
```

### Arquivos Modificados

- `config/settings/base.py` - Configuração do admin Django
- `config/urls.py` - Aplicação das configurações de título do admin
- `static/images/logo.png` - Logo do wBJJ MVP
- `static/css/custom-admin.css` - CSS personalizado para aprimorar o tema
- `STATICFILES_DIRS` - Configurado para incluir arquivos estáticos personalizados

### Como Visualizar

1. Acesse o admin: `http://localhost:8000/admin/`
2. Faça login com suas credenciais (admin@test.com)
3. Observe as personalizações:
   - **Logo do wBJJ MVP**: Logo no cabeçalho e favicon
   - **Cores amarelas**: Botões principais, badges e elementos de destaque
   - **Cores azuis**: Links, sidebar e elementos de navegação
   - **Títulos personalizados**: "wBJJ MVP - Administração"
   - **Tema claro**: Configurado para destacar as cores amarelo/azul
   - **Sidebar**: Menu com gradiente azul escuro para azul
   - **Contraste**: Amarelo vibrante (#EAB308) sobre azul escuro (#1E3A8A)
   - **Elementos visuais**: Formulários, tabelas e navegação com combinação amarelo/azul

### Personalização Adicional

Para fazer mais ajustes no tema:

1. **Cores**: Modifique as variáveis CSS em `static/css/custom-admin.css`
2. **Logo**: Substitua `static/images/logo.png`
3. **Títulos**: Altere as configurações em `config/settings/base.py`

Execute `python manage.py collectstatic` após qualquer mudança em arquivos estáticos.

### Solução de Problemas

**Se o logo não aparecer:**
1. Verifique se o arquivo `static/images/logo.png` existe
2. Execute `python manage.py collectstatic --noinput`
3. Reinicie o servidor Django
4. Limpe o cache do navegador (Ctrl+F5)

**Se as cores não aparecerem corretamente:**
1. Verifique se o CSS personalizado foi coletado
2. Certifique-se de que o arquivo `custom-admin.css` existe
3. Limpe o cache do navegador (Ctrl+F5)
4. Inspecione o elemento no navegador para verificar se as cores estão sendo aplicadas
5. Verifique se as variáveis CSS estão definidas corretamente

**Para debug:**
- Acesse `/static/images/logo.png` diretamente no navegador
- Verifique o console do navegador para erros de carregamento
- Use as ferramentas de desenvolvedor para inspecionar os estilos CSS aplicados

---

## 🎨 Mudanças de Cores Aplicadas

### Antes (Padrão Django):
- Paleta baseada em tons azuis padrão
- Cor principal: #417690 (azul padrão)

### Agora (Amarelo/Azul MVP):
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
    'apps.core.middleware.TenantMiddleware',  # Para detecção de tenant
    'apps.authentication.middleware.SecurityAuthorizationMiddleware',  # Para segurança
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

---

## 🏛️ Multitenancy no Admin

### Isolamento por Tenant

O admin Django foi configurado para trabalhar com o sistema de multitenancy MVP:

**Configuração Automática:**
- Todos os models que herdam de `TenantMixin` são automaticamente filtrados
- Dados mostrados apenas do tenant atual
- Criação automática de registros com tenant correto

**Exemplo de Admin Configurado:**

```python
# apps/students/admin.py
from django.contrib import admin
from typing import ClassVar
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin para estudantes com filtro por tenant"""

    list_display: ClassVar = ['user__first_name', 'user__last_name', 'belt_color', 'status']
    list_filter: ClassVar = ['belt_color', 'status', 'created_at']
    search_fields: ClassVar = ['user__first_name', 'user__last_name', 'user__email']
    readonly_fields: ClassVar = ['id', 'created_at', 'updated_at']

    def get_queryset(self, request):
        """Filtrar por tenant automaticamente"""
        qs = super().get_queryset(request)
        if hasattr(request, 'tenant') and request.tenant:
            return qs.filter(tenant=request.tenant)
        return qs.none()

    def save_model(self, request, obj, form, change):
        """Adicionar tenant automaticamente"""
        if not change and hasattr(request, 'tenant'):
            obj.tenant = request.tenant
        super().save_model(request, obj, form, change)
```

### Detecção de Tenant no Admin

O admin detecta o tenant automaticamente através do middleware:

```python
# Middleware configurado
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'apps.core.middleware.TenantMiddleware',  # Detecta tenant por subdomínio
    'apps.authentication.middleware.SecurityAuthorizationMiddleware',
    # ... outros middlewares
]
```

**Como funciona:**
1. **URL**: `https://academia-alpha.wbjj.com/admin/`
2. **Middleware**: Detecta tenant `academia-alpha`
3. **Admin**: Filtra dados automaticamente para esse tenant
4. **Segurança**: Impossível ver dados de outras academias

### Exemplo de Uso

```bash
# Academia Alpha
https://academia-alpha.wbjj.com/admin/
# Mostra apenas dados da Academia Alpha

# Academia Beta
https://academia-beta.wbjj.com/admin/
# Mostra apenas dados da Academia Beta

# Desenvolvimento
http://localhost:8000/admin/
# Pode precisar configurar tenant manualmente
```

---

## 📊 Dashboard Customizado

### Widgets Personalizados

O admin pode ser estendido com widgets personalizados para cada tenant:

```python
# apps/core/admin.py
from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path

class CustomAdminSite(admin.AdminSite):
    """Admin customizado com dashboard por tenant"""

    def index(self, request, extra_context=None):
        """Dashboard personalizado"""
        extra_context = extra_context or {}

        if hasattr(request, 'tenant') and request.tenant:
            # Estatísticas do tenant atual
            from apps.students.models import Student
            from apps.payments.models import Payment

            extra_context.update({
                'tenant_name': request.tenant.name,
                'total_students': Student.objects.filter(tenant=request.tenant).count(),
                'active_students': Student.objects.filter(
                    tenant=request.tenant,
                    status='active'
                ).count(),
                'recent_payments': Payment.objects.filter(
                    tenant=request.tenant
                ).order_by('-created_at')[:5],
            })

        return super().index(request, extra_context)

# Substituir admin padrão
admin.site = CustomAdminSite(name='custom_admin')
```

### Templates Customizados

Criar templates personalizados para o admin:

```html
<!-- templates/admin/index.html -->
{% extends "admin/index.html" %}

{% block content %}
<div class="dashboard">
    {% if tenant_name %}
        <h2>{{ tenant_name }} - Dashboard</h2>

        <div class="stats">
            <div class="stat-card">
                <h3>{{ total_students }}</h3>
                <p>Total de Alunos</p>
            </div>

            <div class="stat-card">
                <h3>{{ active_students }}</h3>
                <p>Alunos Ativos</p>
            </div>
        </div>

        <div class="recent-payments">
            <h3>Pagamentos Recentes</h3>
            {% for payment in recent_payments %}
                <div class="payment-item">
                    {{ payment.student.user.full_name }} - R$ {{ payment.amount }}
                </div>
            {% endfor %}
        </div>
    {% endif %}
</div>

{{ block.super }}
{% endblock %}
```

---

## 🔄 Diferenças MVP vs V2.0

### MVP (Atual)
- ✅ **Admin**: Filtro por tenant_id
- ✅ **Detecção**: Subdomínio automático
- ✅ **Customização**: CSS e templates simples
- ✅ **Dashboard**: Estatísticas básicas por tenant
- ✅ **Performance**: Queries filtradas rapidamente

### V2.0 (Futuro)
- 🔄 **Admin**: Schema-per-tenant completo
- 🔄 **Detecção**: Domínios customizados
- 🔄 **Customização**: Temas por tenant
- 🔄 **Dashboard**: Analytics avançados
- 🔄 **Performance**: Isolamento total por schema

---

**Customização wBJJ MVP: Interface administrativa moderna e funcional** 🎨

*Admin Django personalizado com multitenancy simplificado e design responsivo.*
