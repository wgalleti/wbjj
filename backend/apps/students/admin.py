from typing import ClassVar

from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from .models import Attendance, Graduation, Student


class GraduationInline(TabularInline):
    model = Graduation
    extra = 0
    readonly_fields = ["created_at"]
    fields: ClassVar = [
        "from_belt",
        "to_belt",
        "graduation_date",
        "instructor",
        "notes",
    ]


class AttendanceInline(TabularInline):
    model = Attendance
    extra = 0
    readonly_fields = ["created_at"]
    fields: ClassVar = [
        "class_date",
        "check_in_time",
        "check_out_time",
        "class_type",
        "instructor",
    ]


@admin.register(Student)
class StudentAdmin(ModelAdmin):
    list_display = [
        "full_name",
        "registration_number",
        "get_belt_display",
        "status",
        "enrollment_date",
    ]
    list_filter = ["belt_color", "status", "enrollment_date"]
    search_fields: ClassVar = [
        "user__first_name",
        "user__last_name",
        "user__email",
        "registration_number",
    ]
    readonly_fields = ["id", "created_at", "updated_at"]
    inlines = [GraduationInline, AttendanceInline]
    list_per_page = 25

    @display(description="Faixa", ordering="belt_color")
    def get_belt_display(self, obj):
        stripes = " ★" * obj.belt_stripes if obj.belt_stripes else ""
        return f"{obj.get_belt_color_display()}{stripes}"

    fieldsets = (
        ("Informações do Usuário", {"fields": ("user",)}),
        ("Matrícula", {"fields": ("registration_number", "enrollment_date", "status")}),
        (
            "Graduação",
            {"fields": ("belt_color", "belt_stripes", "last_graduation_date")},
        ),
        (
            "Contato de Emergência",
            {
                "fields": (
                    "emergency_contact_name",
                    "emergency_contact_phone",
                    "emergency_contact_relationship",
                )
            },
        ),
        (
            "Informações Médicas",
            {"fields": ("medical_conditions", "medications"), "classes": ("collapse",)},
        ),
        ("Observações", {"fields": ("notes",), "classes": ("collapse",)}),
        (
            "Sistema",
            {
                "fields": ("is_active", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Graduation)
class GraduationAdmin(ModelAdmin):
    list_display = [
        "student",
        "get_from_belt",
        "get_to_belt",
        "graduation_date",
        "instructor",
    ]
    list_filter = ["from_belt", "to_belt", "graduation_date"]
    search_fields: ClassVar = ["student__user__first_name", "student__user__last_name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    list_per_page = 25

    @display(description="De", ordering="from_belt")
    def get_from_belt(self, obj):
        return obj.get_from_belt_display()

    @display(description="Para", ordering="to_belt")
    def get_to_belt(self, obj):
        return obj.get_to_belt_display()

    fieldsets = (
        (
            "Graduação",
            {
                "fields": (
                    "student",
                    "from_belt",
                    "to_belt",
                    "graduation_date",
                    "instructor",
                )
            },
        ),
        ("Observações", {"fields": ("notes",)}),
        (
            "Sistema",
            {
                "fields": ("is_active", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Attendance)
class AttendanceAdmin(ModelAdmin):
    list_display = [
        "student",
        "class_date",
        "check_in_time",
        "check_out_time",
        "get_class_type_display",
    ]
    list_filter = ["class_date", "class_type"]
    search_fields: ClassVar = ["student__user__first_name", "student__user__last_name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    date_hierarchy = "class_date"
    list_per_page = 50

    @display(description="Tipo de Aula", ordering="class_type")
    def get_class_type_display(self, obj):
        return obj.get_class_type_display()

    fieldsets = (
        (
            "Presença",
            {"fields": ("student", "class_date", "check_in_time", "check_out_time")},
        ),
        ("Aula", {"fields": ("class_type", "instructor")}),
        ("Observações", {"fields": ("notes",)}),
        (
            "Sistema",
            {
                "fields": ("is_active", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
