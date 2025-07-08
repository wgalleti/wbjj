from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from .models import Invoice, Payment, PaymentMethod


class PaymentInline(TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ["created_at", "confirmed_date"]
    fields = [
        "payment_method",
        "amount",
        "processing_fee",
        "payment_date",
        "status",
        "external_id",
    ]


@admin.register(PaymentMethod)
class PaymentMethodAdmin(ModelAdmin):
    list_display = ["name", "code", "get_type_display", "processing_fee", "is_active"]
    list_filter = ["is_online", "is_active"]
    search_fields = ["name", "code"]
    readonly_fields = ["id", "created_at", "updated_at"]
    list_per_page = 25

    @display(description="Tipo", ordering="is_online")
    def get_type_display(self, obj):
        return "💻 Online" if obj.is_online else "🏪 Presencial"

    fieldsets = (
        ("Informações Básicas", {"fields": ("name", "code", "is_online")}),
        ("Configurações", {"fields": ("processing_fee",)}),
        (
            "Sistema",
            {
                "fields": ("is_active", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Invoice)
class InvoiceAdmin(ModelAdmin):
    list_display = [
        "student",
        "reference_month",
        "due_date",
        "get_amount_display",
        "get_status_display",
        "get_overdue_display",
    ]
    list_filter = ["status", "due_date", "reference_month"]
    search_fields = ["student__user__first_name", "student__user__last_name"]
    readonly_fields = ["id", "created_at", "updated_at", "total_amount", "is_overdue"]
    inlines = [PaymentInline]
    date_hierarchy = "due_date"
    list_per_page = 25

    @display(description="Valor", ordering="amount")
    def get_amount_display(self, obj):
        return f"R$ {obj.amount:,.2f}"

    @display(description="Status", ordering="status")
    def get_status_display(self, obj):
        colors = {
            "pending": "#f59e0b",
            "paid": "#10b981",
            "overdue": "#ef4444",
            "cancelled": "#6b7280",
        }
        color = colors.get(obj.status, "#6b7280")
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            color,
            obj.get_status_display(),
        )

    @display(description="Vencida", boolean=True, ordering="due_date")
    def get_overdue_display(self, obj):
        return obj.is_overdue

    fieldsets = (
        ("Fatura", {"fields": ("student", "reference_month", "due_date", "status")}),
        ("Valores", {"fields": ("amount", "discount", "late_fee", "total_amount")}),
        ("Descrição", {"fields": ("description", "notes")}),
        (
            "Sistema",
            {
                "fields": ("is_active", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = [
        "invoice",
        "payment_method",
        "get_amount_display",
        "payment_date",
        "get_status_display",
    ]
    list_filter = ["status", "payment_method", "payment_date"]
    search_fields = [
        "invoice__student__user__first_name",
        "invoice__student__user__last_name",
        "external_id",
    ]
    readonly_fields = ["id", "created_at", "updated_at", "confirmed_date"]
    date_hierarchy = "payment_date"
    list_per_page = 25

    @display(description="Valor", ordering="amount")
    def get_amount_display(self, obj):
        return f"R$ {obj.amount:,.2f}"

    @display(description="Status", ordering="status")
    def get_status_display(self, obj):
        colors = {
            "pending": "#f59e0b",
            "confirmed": "#10b981",
            "failed": "#ef4444",
            "cancelled": "#6b7280",
        }
        color = colors.get(obj.status, "#6b7280")
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            color,
            obj.get_status_display(),
        )

    fieldsets = (
        (
            "Pagamento",
            {"fields": ("invoice", "payment_method", "amount", "processing_fee")},
        ),
        ("Datas", {"fields": ("payment_date", "confirmed_date")}),
        ("Status", {"fields": ("status", "external_id")}),
        ("Observações", {"fields": ("notes",)}),
        (
            "Sistema",
            {
                "fields": ("is_active", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
