"""
Hooks de pré e pós-processamento para documentação OpenAPI

Seguindo padrões estabelecidos no CONTEXT.md:
- Documentação OpenAPI automática
- Filtros bem documentados
- Enums padronizados
"""


def preprocess_filter_specs(endpoints):
    """
    Pré-processa especificações de filtros para melhor documentação
    """
    for endpoint in endpoints:
        # Nova estrutura do DRF Spectacular - pode ter mais de 3 valores
        if len(endpoint) >= 3:
            path, method, callback = endpoint[:3]
        else:
            continue

        # Adiciona exemplos de filtros para endpoints com paginação
        if hasattr(callback, "cls") and hasattr(callback.cls, "filter_backends"):
            # Adiciona exemplos de filtros baseados no modelo
            if hasattr(callback.cls, "queryset") and callback.cls.queryset:
                model = callback.cls.queryset.model

                # Adiciona exemplos de filtros comuns
                if hasattr(model, "name"):
                    callback.cls.search_fields = [
                        *getattr(callback.cls, "search_fields", []),
                        "name",
                    ]
                if hasattr(model, "email"):
                    callback.cls.search_fields = [
                        *getattr(callback.cls, "search_fields", []),
                        "email",
                    ]
                if hasattr(model, "status"):
                    callback.cls.ordering_fields = [
                        *getattr(callback.cls, "ordering_fields", []),
                        "status",
                    ]
                if hasattr(model, "created_at"):
                    callback.cls.ordering_fields = [
                        *getattr(callback.cls, "ordering_fields", []),
                        "created_at",
                    ]

    return endpoints


def postprocess_schema_enums(result, generator, request, public):
    """
    Pós-processa schema para melhorar representação de enums e adicionar exemplos
    """
    # Adiciona descrições melhores para enums
    if "components" in result and "schemas" in result["components"]:
        for _, schema in result["components"]["schemas"].items():
            if "properties" in schema:
                for prop_name, prop_schema in schema["properties"].items():
                    # Melhora documentação de choices
                    if "enum" in prop_schema:
                        prop_schema[
                            "description"
                        ] = f"Valores possíveis: {', '.join(prop_schema['enum'])}"

                        # Adiciona exemplos para enums específicos
                        if "belt" in prop_name.lower():
                            prop_schema["example"] = "white"
                        elif "status" in prop_name.lower():
                            prop_schema["example"] = "active"
                        elif "type" in prop_name.lower():
                            prop_schema["example"] = (
                                prop_schema["enum"][0] if prop_schema["enum"] else None
                            )

    # Adiciona informações de autenticação JWT
    if "components" in result:
        if "securitySchemes" not in result["components"]:
            result["components"]["securitySchemes"] = {}

        result["components"]["securitySchemes"]["jwtAuth"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Token JWT obtido através do endpoint /api/v1/auth/login/",
        }

        # Adiciona parâmetros comuns
        if "parameters" not in result["components"]:
            result["components"]["parameters"] = {}

        result["components"]["parameters"]["TenantHeader"] = {
            "name": "X-Tenant-ID",
            "in": "header",
            "required": True,
            "description": "ID do tenant para isolamento de dados (UUID da academia)",
            "schema": {
                "type": "string",
                "format": "uuid",
                "example": "123e4567-e89b-12d3-a456-426614174000",
            },
        }

        result["components"]["parameters"]["PageParam"] = {
            "name": "page",
            "in": "query",
            "description": "Número da página para paginação",
            "required": False,
            "schema": {"type": "integer", "minimum": 1, "default": 1, "example": 1},
        }

        result["components"]["parameters"]["PageSizeParam"] = {
            "name": "page_size",
            "in": "query",
            "description": "Número de itens por página (máximo 100)",
            "required": False,
            "schema": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "default": 20,
                "example": 20,
            },
        }

        result["components"]["parameters"]["SearchParam"] = {
            "name": "search",
            "in": "query",
            "description": "Busca textual nos campos configurados",
            "required": False,
            "schema": {"type": "string", "example": "João Silva"},
        }

        result["components"]["parameters"]["OrderingParam"] = {
            "name": "ordering",
            "in": "query",
            "description": 'Campo para ordenação (use "-" para ordem decrescente)',
            "required": False,
            "schema": {"type": "string", "example": "-created_at"},
        }

    # Adiciona exemplos de resposta de erro padronizadas
    if "components" in result and "schemas" not in result["components"]:
        result["components"]["schemas"] = {}

    result["components"]["schemas"]["Error"] = {
        "type": "object",
        "properties": {
            "error": {
                "type": "boolean",
                "example": True,
                "description": "Indica se é uma resposta de erro",
            },
            "message": {
                "type": "string",
                "example": "Erro de validação",
                "description": "Mensagem de erro principal",
            },
            "details": {
                "type": "object",
                "example": {"field": ["Este campo é obrigatório."]},
                "description": "Detalhes específicos do erro",
            },
            "status_code": {
                "type": "integer",
                "example": 400,
                "description": "Código de status HTTP",
            },
        },
    }

    result["components"]["schemas"]["ValidationError"] = {
        "type": "object",
        "properties": {
            "error": {"type": "boolean", "example": True},
            "message": {"type": "string", "example": "Erro de validação"},
            "details": {
                "type": "object",
                "example": {
                    "email": ["Este email já está em uso."],
                    "password": ["A senha deve ter pelo menos 8 caracteres."],
                },
            },
            "status_code": {"type": "integer", "example": 400},
        },
    }

    # Adiciona segurança global para endpoints autenticados
    if "security" not in result:
        result["security"] = []

    # Adiciona schema de paginação personalizado
    result["components"]["schemas"]["PaginatedResponse"] = {
        "type": "object",
        "properties": {
            "count": {
                "type": "integer",
                "example": 123,
                "description": "Total de itens",
            },
            "next": {
                "type": "string",
                "nullable": True,
                "format": "uri",
                "example": "http://localhost:8000/api/v1/students/?page=2",
                "description": "URL da próxima página",
            },
            "previous": {
                "type": "string",
                "nullable": True,
                "format": "uri",
                "example": "http://localhost:8000/api/v1/students/?page=1",
                "description": "URL da página anterior",
            },
            "page_size": {
                "type": "integer",
                "example": 20,
                "description": "Itens por página",
            },
            "total_pages": {
                "type": "integer",
                "example": 7,
                "description": "Total de páginas",
            },
            "current_page": {
                "type": "integer",
                "example": 2,
                "description": "Página atual",
            },
            "results": {
                "type": "array",
                "items": {},
                "description": "Array com os resultados da página atual",
            },
        },
    }

    return result


def add_authentication_examples(endpoints):
    """
    Adiciona exemplos de autenticação para os endpoints
    """
    authentication_examples = {
        "login": {
            "request": {"email": "admin@academia.com", "password": "senha123"},
            "response": {
                "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "admin@academia.com",
                    "first_name": "Admin",
                    "last_name": "Sistema",
                },
            },
        },
        "refresh": {
            "request": {"refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."},
            "response": {"access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."},
        },
    }

    return authentication_examples
