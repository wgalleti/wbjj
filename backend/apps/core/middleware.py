"""
Middleware customizado para aplicar políticas de permissão e cabeçalhos de segurança.
"""


class PermissionsPolicyMiddleware:
    """
    Middleware para aplicar cabeçalhos de Permissions Policy.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Adiciona cabeçalho de Permissions Policy para permitir eventos de unload
        response["Permissions-Policy"] = "unload=(self)"

        return response


class SecurityHeadersMiddleware:
    """
    Middleware para adicionar cabeçalhos de segurança extras.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Cabeçalhos de segurança adicionais
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["X-Content-Type-Options"] = "nosniff"

        # Remove o cabeçalho Server para não revelar informações do servidor
        if "Server" in response:
            del response["Server"]

        return response
