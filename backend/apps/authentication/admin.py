from typing import ClassVar

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    list_display: ClassVar = [
        "email",
        "first_name",
        "last_name",
        "get_role_display",
        "is_active",
        "date_joined",
    ]
    list_filter: ClassVar = ["role", "is_active", "is_staff", "is_verified"]
    search_fields: ClassVar = ["email", "first_name", "last_name"]
    readonly_fields: ClassVar = [
        "id",
        "created_at",
        "updated_at",
        "date_joined",
        "last_login",
    ]
    ordering: ClassVar = ["email"]
    list_per_page = 25

    @display(description="Role", ordering="role")
    def get_role_display(self, obj):
        return obj.get_role_display()

    fieldsets: ClassVar = (
        ("Informações de Login", {"fields": ("email", "password")}),
        (
            "Informações Pessoais",
            {"fields": ("first_name", "last_name", "phone", "birth_date")},
        ),
        (
            "Permissões",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_verified",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Configurações", {"fields": ("language",)}),
        (
            "Datas Importantes",
            {
                "fields": ("last_login", "date_joined", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    add_fieldsets: ClassVar = (
        (
            "Criar Usuário",
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "role",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    filter_horizontal: ClassVar = ("groups", "user_permissions")
