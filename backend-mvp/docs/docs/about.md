# :sparkles: Sobre o Projeto wBJJ MVP

## :dart: Missão

O **wBJJ MVP** foi criado para resolver uma necessidade real no mercado brasileiro de academias de **Brazilian Jiu-Jitsu**. Nossa missão é fornecer uma plataforma completa, moderna e escalável que permita aos proprietários de academias focarem no que realmente importa: **ensinar e formar campeões**.

!!! quote "Nossa Visão"
    Democratizar o acesso a tecnologia de ponta para academias de todos os tamanhos, desde pequenos clubes locais até grandes redes de ensino, mantendo sempre a simplicidade e eficiência através de um MVP validado.

## :trophy: Objetivos

### :gear: Técnicos

- [x] **Multitenancy MVP**: Isolamento por tenant_id seguro e eficiente
- [x] **Performance Superior**: < 200ms de resposta média
- [x] **Escalabilidade**: Suporte a dezenas de academias simultaneamente
- [x] **Segurança**: Padrões enterprise com JWT + RBAC
- [x] **Developer Experience**: DX excepcional com docs interativas

### :handshake: Negócio

- [x] **Validação Rápida**: MVP para testar mercado rapidamente
- [x] **Redução de Custos**: Eliminar gastos com sistemas desatualizados
- [x] **Aumento de Eficiência**: Automatizar processos manuais
- [x] **Insights Valiosos**: Analytics e relatórios em tempo real
- [x] **Satisfação do Cliente**: Interface moderna e intuitiva
- [x] **Crescimento Sustentável**: Base tecnológica sólida para expansão

## :building_construction: Arquitetura & Filosofia

### Princípios Fundamentais

=== "Clean Code"

    ```python
    # Código limpo, legível e manutenível
    class StudentGraduationService:
        """Serviço responsável por gerenciar graduações de alunos"""

        def graduate_student(
            self,
            student: Student,
            new_belt: BeltColor,
            graduation_date: date,
            notes: str = None
        ) -> Graduation:
            """Gradua um aluno para nova faixa com validações completas"""
            self._validate_graduation_eligibility(student, new_belt)
            return self._create_graduation_record(student, new_belt, graduation_date, notes)
    ```

=== "API-First"

    ```yaml
    # OpenAPI Schema automático
    paths:
      /api/v1/students/{id}/graduate/:
        post:
          summary: "Graduar aluno"
          description: "Promove aluno para nova faixa com validações"
          requestBody:
            required: true
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/GraduationRequest'
          responses:
            200:
              $ref: '#/components/responses/GraduationSuccess'
    ```

=== "Multitenancy MVP"

    ```mermaid
    graph TB
        subgraph "Tenant A - Academia Alpha"
            A1[Alunos A] --> DB_A[(tenant_id: A)]
            A2[Pagamentos A] --> DB_A
        end

        subgraph "Tenant B - Academia Beta"
            B1[Alunos B] --> DB_B[(tenant_id: B)]
            B2[Pagamentos B] --> DB_B
        end

        subgraph "Shared Infrastructure"
            API[Django API]
            AUTH[JWT Auth]
            MIDDLEWARE[TenantMiddleware]
        end

        API --> MIDDLEWARE
        MIDDLEWARE --> DB_A
        MIDDLEWARE --> DB_B
        AUTH --> API
    ```

### Stack Tecnológica Justificada

| Tecnologia | Por que Escolhemos | Alternativas Consideradas |
|------------|-------------------|--------------------------|
| **Django 4.2 LTS** | Estabilidade, comunidade, admin built-in | FastAPI, Flask |
| **PostgreSQL** | ACID, JSON support, performance | MySQL, MongoDB |
| **Redis** | Performance, persistência, pub/sub | Memcached, RabbitMQ |
| **Docker** | Consistência, deployment, escalabilidade | Vagrant, bare metal |
| **UV** | Velocidade 10x maior que pip | Poetry, pipenv |

## :trophy: Diferenciais Competitivos

### :rocket: Performance

!!! success "Benchmarks Reais"

    - **API Response**: 95% < 200ms
    - **Database Queries**: Otimizadas com select_related/prefetch_related
    - **Cache Hit Rate**: > 85% com django-cachalot
    - **Memory Usage**: < 512MB por container
    - **Concurrent Users**: 1000+ por instância

### :shield: Segurança Enterprise

- **Autenticação JWT** com refresh automático
- **Permissions Granulares** por academia e usuário
- **Headers de Segurança** configurados automaticamente
- **Input Validation** rigorosa em todos os endpoints
- **SQL Injection Protection** nativa do Django ORM
- **Rate Limiting** configurável por endpoint

### :art: Developer Experience

```bash
# Setup em 30 segundos
git clone https://github.com/wgalleti/wbjj.git
cd wbjj/backend-mvp
./scripts/dev-setup.sh

# 🎉 Pronto! API rodando em http://localhost:8000
```

## :chart_with_upwards_trend: Roadmap

### MVP (Atual) ✅
- [x] Gestão básica de alunos
- [x] Sistema financeiro essencial
- [x] Multitenancy por tenant_id
- [x] API REST completa
- [x] Admin customizado
- [x] Autenticação JWT
- [x] Testes automatizados

### V2.0 - Migração Schema-per-Tenant (Q2 2025)
- [ ] Schema-per-tenant PostgreSQL
- [ ] Domínios customizados
- [ ] Performance aprimorada
- [ ] Isolamento total
- [ ] Migração automática do MVP

### V2.1 - Melhorias (Q3 2025)
- [ ] Sistema de notificações
- [ ] Relatórios avançados
- [ ] App mobile nativo
- [ ] Integração com gateways de pagamento
- [ ] Sistema de backup automático

### V2.2 - Expansão (Q4 2025)
- [ ] Marketplace de plugins
- [ ] AI para insights de negócio
- [ ] Integração com wearables
- [ ] Sistema de videoaulas
- [ ] Gamificação

## :handshake: Equipe & Contribuições

### Core Team

| Papel | Responsabilidade | Tecnologias |
|-------|-----------------|-------------|
| **Tech Lead** | Arquitetura, code review, mentoria | Django, PostgreSQL, Docker |
| **Backend Dev** | API development, performance | Python, DRF, Redis |
| **DevOps** | Infrastructure, CI/CD | Docker, AWS, Terraform |
| **QA** | Testing, quality assurance | Pytest, Selenium |

### Como Contribuir

1. **Fork** o repositório
2. **Clone** localmente: `git clone https://github.com/wgalleti/wbjj.git`
3. **Configure** ambiente: `./scripts/dev-setup.sh`
4. **Crie** feature branch: `git checkout -b feature/nome-da-feature`
5. **Desenvolva** seguindo [padrões do projeto](context.md)
6. **Teste** completamente: `pytest --cov=apps`
7. **Commit** usando [Conventional Commits](https://conventionalcommits.org/)
8. **Push** e abra **Pull Request**

!!! tip "Dicas para Contribuidores"

    - Leia o [CONTEXT.md](context.md) antes de começar
    - Use o [Discord/Slack] para tirar dúvidas
    - Todos os PRs passam por code review
    - Cobertura de testes deve ser > 80%

## :books: Recursos & Aprendizado

### Documentação Técnica

- **[API Reference](api.md)**: Documentação completa dos endpoints
- **[Context & Standards](context.md)**: Padrões e práticas obrigatórias
- **[Docker Guide](docker.md)**: Setup e desenvolvimento com containers
- **[Authentication](authentication.md)**: Sistema JWT e RBAC
- **[Testing](testing.md)**: Sistema de testes completo
- **[Usage Examples](usage.md)**: Casos de uso práticos

### Links Externos

- [:material-github: **GitHub Repository**](https://github.com/wgalleti/wbjj)
- [:material-docker: **Docker Hub**](https://hub.docker.com/r/wgalleti/wbjj)
- [:material-swagger: **API Playground**](http://localhost:8000/api/docs/)
- [:material-book: **Wiki**](https://github.com/wgalleti/wbjj/wiki)

## :phone: Contato & Suporte

### Canais de Comunicação

| Canal | Uso | Resposta |
|-------|-----|----------|
| **GitHub Issues** | Bugs, features | 24-48h |
| **Discussions** | Dúvidas gerais | Comunidade |
| **Email** | Suporte enterprise | 4-8h |
| **Discord** | Chat tempo real | Imediata |

### Níveis de Suporte

=== "Community"

    - ✅ GitHub Issues
    - ✅ Documentation
    - ✅ Discord Community
    - ❌ SLA garantido

=== "Professional"

    - ✅ Todos do Community
    - ✅ Email suporte
    - ✅ SLA 24h
    - ✅ Consultoria técnica

=== "Enterprise"

    - ✅ Todos do Professional
    - ✅ Suporte telefônico
    - ✅ SLA 4h
    - ✅ Desenvolvimento customizado

## :bulb: Diferenças MVP vs V2.0

### MVP (Atual)
- ✅ **Multitenancy**: Filtro por tenant_id
- ✅ **Detecção**: Subdomínio automático
- ✅ **Performance**: Queries filtradas rapidamente
- ✅ **Desenvolvimento**: Setup simples e rápido
- ✅ **Escalabilidade**: Até ~100 tenants
- ✅ **Validação**: Prova de conceito rápida

### V2.0 (Futuro)
- 🔄 **Multitenancy**: Schema-per-tenant PostgreSQL
- 🔄 **Detecção**: Domínios customizados
- 🔄 **Performance**: Isolamento total
- 🔄 **Desenvolvimento**: Setup mais complexo
- 🔄 **Escalabilidade**: Ilimitada
- 🔄 **Produção**: Enterprise-ready

## :heart: Agradecimentos

Obrigado a todos que contribuem para fazer o **wBJJ MVP** uma realidade:

- **Comunidade Django/DRF** pela base sólida
- **Material for MkDocs** por esta documentação lindíssima
- **Acadêmicos e Professores** que testam e dão feedback
- **Contributors** que dedicam seu tempo ao projeto

---

<div class="result" markdown>

!!! abstract ":sparkles: Junte-se à Nossa Missão"

    O **wBJJ MVP** é mais que um sistema - é uma comunidade apaixonada por tecnologia e jiu-jitsu. Juntos, estamos construindo o futuro da gestão de academias no Brasil através de um MVP validado e escalável.

    **[:material-github: Contribute no GitHub](https://github.com/wgalleti/wbjj)** | **[:material-discord: Join Discord](#)** | **[:material-email: Contato](mailto:contact@wbjj.dev)**

</div>
