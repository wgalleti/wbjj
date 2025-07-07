# wBJJ - Sistema de Gestão para Academias de Jiu-Jitsu

## Visão Geral
O wBJJ é um sistema completo de gestão para academias de jiu-jitsu, projetado com arquitetura multitenancy para suportar múltiplas filiais (franquias) de forma escalável e eficiente.

## Objetivos do Projeto
- **Gestão de Filiais**: Controle centralizado de múltiplas unidades de franquias
- **Gestão Financeira**: Controle de mensalidades, gastos, vendas e fluxo de caixa
- **Gestão de Atletas**: Cadastros, graduações, histórico e anotações pedagógicas
- **Gestão Operacional**: Funcionários, despesas, investimentos e recursos
- **Comunicação**: Canal direto com alunos via aplicativo móvel

## Arquitetura do Sistema

### Conceito Multitenancy
O sistema utiliza arquitetura multitenancy em todas as camadas:
- **Backend**: Isolamento de dados por tenant (filial)
- **Web**: Interface administrativa por filial com branding personalizado
- **App**: Experiência personalizada por academia

### Componentes do Sistema

#### 1. Backend (API/Servidor)
- **Tecnologia MVP**: Python + Django + Django Rest Framework
- **Tecnologia V2.0**: Golang (migração pós-validação)
- **Responsabilidades**:
  - Gerenciamento de dados e regras de negócio
  - API RESTful para comunicação
  - Autenticação e autorização multitenancy
  - Processamento de pagamentos
  - Notificações push

#### 2. Web (Painel Administrativo)
- **Tecnologia MVP**: Vue.js 3 + JavaScript + Tailwind + Shadcn
- **Tecnologia V2.0**: Vue 3 + TypeScript ou framework moderno
- **Responsabilidades**:
  - Dashboard administrativo por filial
  - Gestão de atletas e graduações
  - Controle financeiro e relatórios
  - Landing pages personalizadas por filial
  - Configurações de branding

#### 3. App Mobile (Comunicação com Atletas)
- **Tecnologia**: Flutter + Dart + Material Design 3
- **Responsabilidades**:
  - Comunicação direta com alunos
  - Histórico de treinos e graduações
  - Agendamentos e check-ins
  - Planos de treino personalizados
  - Notificações e lembretes

## Estrutura da Documentação
```
doc/
├── README.md              # Este arquivo
├── ARCHITECTURE.md        # Arquitetura detalhada
├── ROADMAP.md            # Cronograma e fases
├── backend/              # Documentação do backend
├── web/                  # Documentação do web
└── app/                  # Documentação do app
```

## Estratégia MVP Definida

### Decisões Tecnológicas Finalizadas
- **Backend**: Django + DRF (produtividade máxima para MVP)
- **Frontend**: Vue.js 3 + JavaScript (desenvolvimento ágil)
- **Mobile**: Flutter (UI consistente e performance)
- **Foco**: Entrega rápida com débito técnico controlado

### Cronograma
- **Fase 1**: Backend (6 semanas) - R$ 9.120
- **Fase 2**: Frontend Web (4 semanas) - R$ 10.320  
- **Fase 3**: Mobile (5 semanas) - R$ 10.080
- **Fase 4**: Integrações (3 semanas) - R$ 8.160
- **Total**: 18 semanas - **R$ 37.680**

### Roadmap V2.0 (Pós-MVP)
- Migração para Golang no backend
- TypeScript no frontend
- Funcionalidades avançadas
- **Investimento adicional**: R$ 60.000

> 📋 **Todas as tarefas detalhadas em**: `doc/TASKS.md`

## Contribuição
Este projeto segue as melhores práticas de desenvolvimento:
- Código limpo e legível
- Padrões de projeto (DRY, KISS, SOLID)
- Testes automatizados
- Documentação atualizada
- Revisão de código 