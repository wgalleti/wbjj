"""
Views para funcionalidades base do sistema

Seguindo padrões estabelecidos no CONTEXT.md:
- SEMPRE herdar de TenantViewSet
- SEMPRE documentar com drf-spectacular
- SEMPRE usar permissions granulares
"""
import logging
import time
from datetime import datetime

import psutil
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import HealthCheckSerializer

logger = logging.getLogger(__name__)


@extend_schema(
    summary="Health Check Completo",
    description="Verifica o status da API e todas suas dependências de forma detalhada",
    responses={
        200: HealthCheckSerializer,
        503: {
            "type": "object",
            "properties": {
                "status": {"type": "string", "example": "unhealthy"},
                "timestamp": {"type": "string", "format": "date-time"},
                "version": {"type": "string", "example": "1.0.0"},
                "database": {"type": "string", "example": "error: connection failed"},
                "cache": {"type": "string", "example": "error: redis unavailable"},
                "disk_usage": {"type": "object"},
                "memory_usage": {"type": "object"},
                "uptime": {"type": "string"},
                "errors": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
    tags=["core"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Endpoint de health check completo para monitoramento

    Verifica:
    - Status da API
    - Conexão com banco de dados
    - Conexão com cache/Redis
    - Uso de memória e disco
    - Tempo de resposta
    - Uptime da aplicação
    """
    start_time = time.time()
    errors = []

    health_data = {
        "status": "healthy",
        "timestamp": timezone.now(),
        "version": "1.0.0",
        "environment": "development" if settings.DEBUG else "production",
        "database": "ok",
        "cache": "ok",
        "disk_usage": {},
        "memory_usage": {},
        "uptime": None,
        "response_time_ms": None,
        "errors": [],
    }

    # Verificar banco de dados com timeout
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result[0] != 1:
                raise Exception("Database query returned unexpected result")

            # Verificar se consegue fazer uma query mais complexa
            cursor.execute("SELECT COUNT(*) FROM django_migrations")
            migration_count = cursor.fetchone()[0]
            health_data["database"] = f"ok - {migration_count} migrations applied"

    except Exception as e:
        health_data["database"] = f"error: {e!s}"
        health_data["status"] = "unhealthy"
        errors.append(f"Database error: {e!s}")
        logger.error(f"Database health check failed: {e}")

    # Verificar cache com timeout
    try:
        test_key = f"health_check_{int(time.time())}"
        cache.set(test_key, "test_value", 10)
        cache_value = cache.get(test_key)
        if cache_value != "test_value":
            raise Exception("Cache test value mismatch")

        # Limpar teste
        cache.delete(test_key)
        health_data["cache"] = "ok - read/write successful"

    except Exception as e:
        health_data["cache"] = f"error: {e!s}"
        health_data["status"] = "unhealthy"
        errors.append(f"Cache error: {e!s}")
        logger.error(f"Cache health check failed: {e}")

    # Verificar uso de memória
    try:
        memory = psutil.virtual_memory()
        health_data["memory_usage"] = {
            "total": f"{memory.total / (1024**3):.2f} GB",
            "available": f"{memory.available / (1024**3):.2f} GB",
            "percent": memory.percent,
            "status": "ok"
            if memory.percent < 85
            else "warning"
            if memory.percent < 95
            else "critical",
        }

        if memory.percent > 95:
            health_data["status"] = "unhealthy"
            errors.append(f"Critical memory usage: {memory.percent}%")
        elif memory.percent > 85:
            errors.append(f"High memory usage: {memory.percent}%")

    except Exception as e:
        health_data["memory_usage"] = {"error": str(e)}
        logger.warning(f"Memory check failed: {e}")

    # Verificar uso de disco
    try:
        disk = psutil.disk_usage("/")
        health_data["disk_usage"] = {
            "total": f"{disk.total / (1024**3):.2f} GB",
            "used": f"{disk.used / (1024**3):.2f} GB",
            "free": f"{disk.free / (1024**3):.2f} GB",
            "percent": round((disk.used / disk.total) * 100, 2),
            "status": "ok"
            if disk.percent < 85
            else "warning"
            if disk.percent < 95
            else "critical",
        }

        if disk.percent > 95:
            health_data["status"] = "unhealthy"
            errors.append(f"Critical disk usage: {disk.percent}%")
        elif disk.percent > 85:
            errors.append(f"High disk usage: {disk.percent}%")

    except Exception as e:
        health_data["disk_usage"] = {"error": str(e)}
        logger.warning(f"Disk check failed: {e}")

    # Calcular uptime
    try:
        boot_time = psutil.boot_time()
        uptime = datetime.now() - datetime.fromtimestamp(boot_time)
        health_data["uptime"] = str(uptime).split(".")[0]  # Remove microseconds
    except Exception as e:
        health_data["uptime"] = f"error: {e!s}"
        logger.warning(f"Uptime check failed: {e}")

    # Calcular tempo de resposta
    end_time = time.time()
    health_data["response_time_ms"] = round((end_time - start_time) * 1000, 2)

    # Adicionar lista de erros
    health_data["errors"] = errors

    # Retornar status apropriado
    status_code = (
        status.HTTP_200_OK
        if health_data["status"] == "healthy"
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return Response(health_data, status=status_code)


@extend_schema(
    summary="Health Check Rápido",
    description="Verificação rápida de saúde para load balancers",
    responses={
        200: {
            "type": "object",
            "properties": {
                "status": {"type": "string", "example": "ok"},
                "timestamp": {"type": "string", "format": "date-time"},
            },
        }
    },
    tags=["core"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def health_check_quick(request):
    """
    Health check rápido para load balancers

    Verifica apenas se a aplicação está respondendo
    """
    return Response(
        {
            "status": "ok",
            "timestamp": timezone.now(),
        }
    )


@extend_schema(
    summary="Health Check Database",
    description="Verifica exclusivamente a conexão com o banco de dados",
    responses={
        200: {
            "type": "object",
            "properties": {
                "database": {"type": "string", "example": "ok"},
                "timestamp": {"type": "string", "format": "date-time"},
                "connection_pool": {"type": "object"},
                "migrations": {"type": "integer"},
            },
        }
    },
    tags=["core"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def health_check_database(request):
    """
    Health check específico para banco de dados

    Verifica conexão, pool de conexões e migrations
    """
    try:
        start_time = time.time()

        with connection.cursor() as cursor:
            # Verificar se database está funcionando
            cursor.execute("SELECT 1")
            cursor.fetchone()

            # Contar migrations aplicadas
            cursor.execute("SELECT COUNT(*) FROM django_migrations")
            migration_count = cursor.fetchone()[0]

            # Verificar se consegue fazer uma query mais complexa
            cursor.execute("SELECT version()")
            db_version = cursor.fetchone()[0]

        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)

        return Response(
            {
                "database": "ok",
                "timestamp": timezone.now(),
                "response_time_ms": response_time,
                "migrations": migration_count,
                "version": db_version,
                "connection_pool": {
                    "queries": len(connection.queries)
                    if settings.DEBUG
                    else "disabled",
                    "vendor": connection.vendor,
                },
            }
        )

    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return Response(
            {
                "database": f"error: {e!s}",
                "timestamp": timezone.now(),
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@extend_schema(
    summary="Health Check Cache",
    description="Verifica exclusivamente a conexão com o cache/Redis",
    responses={
        200: {
            "type": "object",
            "properties": {
                "cache": {"type": "string", "example": "ok"},
                "timestamp": {"type": "string", "format": "date-time"},
                "cache_info": {"type": "object"},
            },
        }
    },
    tags=["core"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def health_check_cache(request):
    """
    Health check específico para cache

    Verifica conexão com Redis e operações básicas
    """
    try:
        start_time = time.time()

        # Test key único para evitar conflitos
        test_key = f"health_check_cache_{int(time.time())}"
        test_value = f"test_value_{int(time.time())}"

        # Teste de escrita
        cache.set(test_key, test_value, 10)

        # Teste de leitura
        cached_value = cache.get(test_key)
        if cached_value != test_value:
            raise Exception("Cache read/write test failed")

        # Teste de delete
        cache.delete(test_key)

        # Verificar se foi deletado
        deleted_value = cache.get(test_key)
        if deleted_value is not None:
            raise Exception("Cache delete test failed")

        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)

        return Response(
            {
                "cache": "ok",
                "timestamp": timezone.now(),
                "response_time_ms": response_time,
                "cache_info": {
                    "backend": cache.__class__.__name__,
                    "location": getattr(cache, "_cache", {}).get("_server", "unknown"),
                    "operations_tested": ["set", "get", "delete"],
                },
            }
        )

    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        return Response(
            {
                "cache": f"error: {e!s}",
                "timestamp": timezone.now(),
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@extend_schema(
    summary="Métricas do Sistema",
    description="Métricas detalhadas do sistema para monitoramento",
    responses={
        200: {
            "type": "object",
            "properties": {
                "system": {"type": "object"},
                "database": {"type": "object"},
                "cache": {"type": "object"},
                "application": {"type": "object"},
                "timestamp": {"type": "string", "format": "date-time"},
            },
        }
    },
    tags=["core"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def metrics(request):
    """
    Endpoint de métricas para monitoramento detalhado

    Retorna informações detalhadas sobre:
    - Sistema operacional
    - Banco de dados
    - Cache
    - Aplicação Django
    """
    try:
        # Métricas do sistema
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        system_metrics = {
            "cpu_percent": cpu_percent,
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used,
                "free": memory.free,
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": round((disk.used / disk.total) * 100, 2),
            },
            "load_average": psutil.getloadavg()
            if hasattr(psutil, "getloadavg")
            else None,
            "boot_time": psutil.boot_time(),
            "uptime_seconds": time.time() - psutil.boot_time(),
        }

        # Métricas do banco de dados
        db_metrics = {}
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version()")
                db_version = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM django_migrations")
                migration_count = cursor.fetchone()[0]

                db_metrics = {
                    "version": db_version,
                    "migrations_applied": migration_count,
                    "vendor": connection.vendor,
                    "queries_count": len(connection.queries)
                    if settings.DEBUG
                    else "disabled",
                }
        except Exception as e:
            db_metrics = {"error": str(e)}

        # Métricas do cache
        cache_metrics = {}
        try:
            # Teste simples do cache
            test_key = f"metrics_test_{int(time.time())}"
            cache.set(test_key, "test", 1)
            cache.get(test_key)
            cache.delete(test_key)

            cache_metrics = {
                "backend": cache.__class__.__name__,
                "status": "ok",
                "location": getattr(cache, "_cache", {}).get("_server", "unknown"),
            }
        except Exception as e:
            cache_metrics = {"error": str(e)}

        # Métricas da aplicação
        app_metrics = {
            "django_version": __import__("django").get_version(),
            "python_version": __import__("sys").version,
            "debug_mode": settings.DEBUG,
            "timezone": str(settings.TIME_ZONE),
            "language": settings.LANGUAGE_CODE,
            "installed_apps_count": len(settings.INSTALLED_APPS),
            "middleware_count": len(settings.MIDDLEWARE),
        }

        return Response(
            {
                "system": system_metrics,
                "database": db_metrics,
                "cache": cache_metrics,
                "application": app_metrics,
                "timestamp": timezone.now(),
            }
        )

    except Exception as e:
        logger.error(f"Metrics endpoint failed: {e}")
        return Response(
            {
                "error": str(e),
                "timestamp": timezone.now(),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@extend_schema(
    summary="API Status",
    description="Informações básicas da API",
    responses={
        200: {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"},
                "environment": {"type": "string"},
                "timestamp": {"type": "string", "format": "date-time"},
            },
        }
    },
    tags=["core"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def api_status(request):
    """
    Informações básicas da API
    """
    return Response(
        {
            "name": "wBJJ API",
            "version": "1.0.0",
            "environment": "development" if settings.DEBUG else "production",
            "timestamp": timezone.now(),
            "docs_url": "/api/docs/",
            "redoc_url": "/api/redoc/",
            "schema_url": "/api/schema/",
        }
    )


@extend_schema(
    summary="API Ping",
    description="Endpoint simples para verificar se a API está respondendo",
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "timestamp": {"type": "string", "format": "date-time"},
            },
        }
    },
    tags=["core"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def ping(request):
    """
    Endpoint simples de ping
    """
    return Response(
        {
            "message": "pong",
            "timestamp": timezone.now(),
        }
    )
