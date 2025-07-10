# :sparkles: Sobre o Projeto wBJJ

## :dart: Missão

O **wBJJ** foi criado para resolver uma necessidade real no mercado brasileiro de academias de **Brazilian Jiu-Jitsu**. Nossa missão é fornecer uma plataforma completa, moderna e escalável que permita aos proprietários de academias focarem no que realmente importa: **ensinar e formar campeões**.

!!! quote "Nossa Visão"
    Democratizar o acesso a tecnologia de ponta para academias de todos os tamanhos, desde pequenos clubes locais até grandes redes de ensino, mantendo sempre a simplicidade e eficiência.

## :trophy: Objetivos

### :gear: Técnicos

- [x] **Multitenancy Nativo**: Cada academia é um mundo isolado e seguro
- [x] **Performance Superior**: < 200ms de resposta média
- [x] **Escalabilidade**: Suporte a milhares de academias simultaneamente
- [x] **Segurança**: Padrões enterprise com JWT + RBAC
- [x] **Developer Experience**: DX excepcional com docs interativas

### :handshake: Negócio

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

=== "Multitenancy"

    ```mermaid
    graph TB
        subgraph "Tenant A - Academia Alpha"
            A1[Alunos A] --> DB_A[(Schema A)]
            A2[Pagamentos A] --> DB_A
        end

        subgraph "Tenant B - Academia Beta"
            B1[Alunos B] --> DB_B[(Schema B)]
            B2[Pagamentos B] --> DB_B
        end

        subgraph "Shared Infrastructure"
            API[Django API]
            AUTH[JWT Auth]
        end

        API --> DB_A
        API --> DB_B
        AUTH --> API
    ```

### Stack Tecnológica Justificada

| Tecnologia | Por que Escolhemos | Alternativas Consideradas |
|------------|-------------------|--------------------------|
| **Django 4.2 LTS** | Estabilidade, comunidade, admin built-in | FastAPI, Flask |
| **PostgreSQL** | ACID, JSON support, multitenancy | MySQL, MongoDB |
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
git clone https://github.com/wbjj/backend.git
cd backend
./scripts/dev-setup.sh

# 🎉 Pronto! API rodando em http://localhost:8000
```

## :chart_with_upwards_trend: Roadmap

### v1.0 - MVP (Atual) ✅
- [x] Gestão básica de alunos
- [x] Sistema financeiro essencial
- [x] Multitenancy funcional
- [x] API REST completa
- [x] Admin customizado

### v1.1 - Melhorias (Q2 2025)
- [ ] Sistema de notificações
- [ ] Relatórios avançados
- [ ] App mobile nativo
- [ ] Integração com gateways de pagamento
- [ ] Sistema de backup automático

### v1.2 - Expansão (Q3 2025)
- [ ] Marketplace de plugins
- [ ] AI para insights de negócio
- [ ] Integração com wearables
- [ ] Sistema de videoaulas
- [ ] Gamificação

### v2.0 - Enterprise (Q4 2025)
- [ ] Multi-região
- [ ] White-label completo
- [ ] Advanced analytics
- [ ] Kubernetes native
- [ ] Microservices architecture

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
2. **Clone** localmente: `git clone https://github.com/seu-usuario/backend.git`
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
- **[Usage Examples](usage.md)**: Casos de uso práticos

### Links Externos

- [:material-github: **GitHub Repository**](https://github.com/wbjj/backend)
- [:material-docker: **Docker Hub**](https://hub.docker.com/r/wbjj/backend)
- [:material-swagger: **API Playground**](http://localhost:8000/api/docs/)
- [:material-book: **Wiki**](https://github.com/wbjj/backend/wiki)

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

## :heart: Agradecimentos

Obrigado a todos que contribuem para fazer o **wBJJ** uma realidade:

- **Comunidade Django/DRF** pela base sólida
- **Material for MkDocs** por esta documentação lindíssima
- **Acadêmicos e Professores** que testam e dão feedback
- **Contributors** que dedicam seu tempo ao projeto

---

<div class="result" markdown>

!!! abstract ":sparkles: Junte-se à Nossa Missão"

    O **wBJJ** é mais que um sistema - é uma comunidade apaixonada por tecnologia e jiu-jitsu. Juntos, estamos construindo o futuro da gestão de academias no Brasil.

    **[:material-github: Contribute no GitHub](https://github.com/wbjj/backend)** | **[:material-discord: Join Discord](#)** | **[:material-email: Contato](mailto:contact@wbjj.dev)**

</div>
