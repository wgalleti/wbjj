from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display
from django.utils.html import format_html
from .models import Tenant


@admin.register(Tenant)
class TenantAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'email', 'city', 'get_fee_display', 'is_active', 'created_at']
    list_filter = ['is_active', 'city', 'state']
    search_fields = ['name', 'email', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['id', 'created_at', 'updated_at']
    list_per_page = 25
    
    @display(description="Mensalidade", ordering="monthly_fee")
    def get_fee_display(self, obj):
        if obj.monthly_fee:
            return f"R$ {obj.monthly_fee:,.2f}"
        return "—"
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'slug', 'email', 'phone')
        }),
        ('Endereço', {
            'fields': ('address', 'city', 'state', 'zip_code', 'country')
        }),
        ('Configurações Visuais', {
            'fields': ('logo', 'primary_color', 'secondary_color')
        }),
        ('Configurações de Negócio', {
            'fields': ('monthly_fee', 'timezone', 'founded_date', 'website')
        }),
        ('Sistema', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
