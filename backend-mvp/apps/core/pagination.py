"""
Paginação personalizada para o sistema wBJJ

Seguindo padrões estabelecidos no CONTEXT.md:
- Paginação padronizada
- Metadados úteis para frontend
- Performance otimizada
"""
from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """
    Paginação padronizada para todas as APIs

    Configuração otimizada para frontend com metadados úteis
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        Retorna resposta paginada com metadados úteis
        """
        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("page_size", self.page_size),
                    ("total_pages", self.page.paginator.num_pages),
                    ("current_page", self.page.number),
                    ("results", data),
                ]
            )
        )

    def get_paginated_response_schema(self, schema):
        """
        Schema para documentação automática
        """
        return {
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
                    "example": "http://api.example.org/accounts/?page=4",
                    "description": "URL da próxima página",
                },
                "previous": {
                    "type": "string",
                    "nullable": True,
                    "format": "uri",
                    "example": "http://api.example.org/accounts/?page=2",
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
                    "example": 3,
                    "description": "Página atual",
                },
                "results": schema,
            },
        }


class LargeResultsSetPagination(PageNumberPagination):
    """
    Paginação para datasets grandes

    Usado em relatórios e listagens extensas
    """

    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200

    def get_paginated_response(self, data):
        """
        Retorna resposta paginada com metadados úteis
        """
        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("page_size", self.page_size),
                    ("total_pages", self.page.paginator.num_pages),
                    ("current_page", self.page.number),
                    ("results", data),
                ]
            )
        )


class SmallResultsSetPagination(PageNumberPagination):
    """
    Paginação para datasets pequenos

    Usado em dropdowns e listas de seleção
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

    def get_paginated_response(self, data):
        """
        Retorna resposta paginada com metadados úteis
        """
        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("page_size", self.page_size),
                    ("total_pages", self.page.paginator.num_pages),
                    ("current_page", self.page.number),
                    ("results", data),
                ]
            )
        )
