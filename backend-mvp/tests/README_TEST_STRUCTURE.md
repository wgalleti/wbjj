# 📋 Estrutura de Testes Separados

Esta estrutura de testes foi criada para otimizar o desenvolvimento e CI/CD separando testes que precisam de banco de dados dos que não precisam.

## 🗂️ Estrutura

```
tests/
├── without_db/          # ⚡ Testes SEM banco de dados (rápidos)
│   ├── core/           # Testes de validação, utilities
│   │   ├── test_openapi.py
│   │   └── test_serializers_validation.py
│   ├── utils/          # Testes de funções puras
│   ├── conftest.py     # Configurações para testes sem DB
│   └── base.py         # Base classes simplificadas
│
├── with_db/            # 🗄️ Testes COM banco de dados (completos)
│   ├── core/           # Testes que precisam de DB
│   ├── models/         # Testes de models
│   ├── serializers/    # Testes de serializers com factories
│   ├── views/          # Testes de views/APIs
│   ├── middleware/     # Testes de middleware
│   ├── factories/      # Factory definitions
│   ├── fixtures/       # Fixtures de dados
│   ├── conftest.py     # Configurações para testes com DB
│   └── base.py         # Base classes completas
│
├── README_TEST_STRUCTURE.md  # Este arquivo
├── __init__.py         # Pacote Python
└── base.py             # Base classes compartilhadas
```

## 🎯 Quando usar cada tipo

### ⚡ WITHOUT_DB (`tests/without_db/`)

**Use para:**
- ✅ Validações de serializers (sem criar objetos)
- ✅ Testes de funções puras/utilities
- ✅ Testes de lógica de negócio sem DB
- ✅ Testes de formatação/parsing
- ✅ Validações de CPF, telefone, CEP
- ✅ Testes de regras de negócio

**Características:**
- 🚀 **Rápidos**: Sem setup de banco
- 🔄 **CI/CD**: Ideais para GitHub Actions
- 📦 **Mocks**: Usa mocks ao invés de objetos reais
- ⚡ **Instantâneos**: Execução em segundos

### 🗄️ WITH_DB (`tests/with_db/`)

**Use para:**
- ✅ Testes de models/relacionamentos
- ✅ Testes de views/endpoints
- ✅ Testes de serializers que criam objetos
- ✅ Testes de middleware
- ✅ Testes de factories
- ✅ Testes de integração
- ✅ Testes que precisam de tenant context

**Características:**
- 🔗 **Completos**: Testam fluxo real
- 🏢 **Multitenancy**: Suporte a tenant context
- 📊 **Coverage**: Relatórios de cobertura
- 🛡️ **Robustos**: Detectam problemas reais

## 🚀 Como executar

### Testes Rápidos (sem DB)
```bash
# Método 1: Script pronto
./scripts/test-without-db.sh

# Método 2: Comando direto
uv run pytest tests/without_db/ --no-migrations -v

# Método 3: Durante desenvolvimento
pytest tests/without_db/core/test_serializers_validation.py -v
```

### Testes Completos (com DB)
```bash
# Método 1: Script pronto (recomendado)
./scripts/test-with-db.sh

# Método 2: Comando direto
DJANGO_SETTINGS_MODULE=config.settings.testing uv run pytest tests/with_db/ --create-db --reuse-db -v

# Método 3: Apenas models
DJANGO_SETTINGS_MODULE=config.settings.testing uv run pytest tests/with_db/models/ -v
```

### Executar TODOS os testes
```bash
# Primeiro os rápidos, depois os completos
./scripts/test-without-db.sh && ./scripts/test-with-db.sh
```

## 🔧 Configurações

### Para testes WITHOUT_DB (`pytest-without-db.ini`)
- Sem migrations
- Sem banco de dados
- Mocks e fixtures simples
- Execução rápida

### Para testes WITH_DB (`pytest-with-db.ini`)
- Com banco PostgreSQL
- Com migrations
- Coverage report
- Tenant context configurado

## 💡 Dicas de Desenvolvimento

### 1. **Desenvolvimento Rápido**
Durante desenvolvimento, rode primeiro os testes without_db:
```bash
# Rápido feedback durante codificação
./scripts/test-without-db.sh
```

### 2. **CI/CD Otimizado**
No GitHub Actions, execute primeiro without_db e só depois with_db se necessário:
```yaml
- name: Quick Tests
  run: ./scripts/test-without-db.sh

- name: Full Tests (if needed)
  run: ./scripts/test-with-db.sh
  if: github.event_name == 'push'
```

### 3. **Debug Específico**
```bash
# Testar apenas validações específicas
pytest tests/without_db/core/test_serializers_validation.py::TestGraduateStudentValidations::test_graduate_student_future_date_invalid -v

# Testar apenas um model
DJANGO_SETTINGS_MODULE=config.settings.testing pytest tests/with_db/models/test_students.py -v
```

## 🎨 Padrões de Código

### WITHOUT_DB - Use pytest classes
```python
class TestUserSerializerValidations:
    def test_cpf_validation(self):
        serializer = UserCreateSerializer(data={'cpf': 'invalid'})
        assert not serializer.is_valid()
        assert 'cpf' in serializer.errors
```

### WITH_DB - Use BaseModelTestCase
```python
@pytest.mark.usefixtures("tenant_models_context")
class TestStudentModel(BaseModelTestCase):
    model_class = Student

    def test_create_student(self):
        student = StudentFactory()
        self.assertIsNotNone(student.id)
```

## 🏆 Benefícios

1. **⚡ Desenvolvimento Ágil**: Feedback rápido durante codificação
2. **🔄 CI/CD Eficiente**: Testes rápidos em servidores sem DB
3. **🎯 Foco**: Separação clara entre validação e integração
4. **💰 Economia**: Menos recursos para testes básicos
5. **🛡️ Robustez**: Cobertura completa quando necessário

## 📊 Estatísticas

- **WITHOUT_DB**: 12 testes, execução < 1 segundo
- **WITH_DB**: 327 testes, execução ~13 segundos
- **Total**: 339 testes organizados por necessidade

## 🧹 Estrutura Limpa

Esta estrutura substitui completamente a organização anterior. Os arquivos antigos foram removidos para evitar confusão:

✅ **Removido**: `tests/core/`, `tests/models/`, `tests/serializers/`, etc.
✅ **Mantido**: Apenas `without_db/`, `with_db/`, `base.py` e este README

## 🔄 Migração de Testes Existentes

### Para adicionar novos testes WITHOUT_DB:
1. Coloque em `tests/without_db/core/` ou `tests/without_db/utils/`
2. Use apenas validação, sem criar objetos no banco
3. Use mocks para dependências externas

### Para adicionar novos testes WITH_DB:
1. Coloque na pasta apropriada (`models/`, `views/`, `serializers/`)
2. Use `from tests.with_db.factories import ...`
3. Herde de `BaseModelTestCase` para testes com tenant context

## 🚨 Troubleshooting

### Erro: "No module named 'tests.factories'"
**Solução**: Use `from tests.with_db.factories import ...`

### Erro: Database not found
**Solução**: Execute `./scripts/test-with-db.sh` que configura o banco automaticamente

### Testes lentos
**Solução**: Verifique se está usando `without_db` para testes de validação pura
