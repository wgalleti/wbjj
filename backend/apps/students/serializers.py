"""
Serializers para gestão de alunos

Seguindo padrões estabelecidos no CONTEXT.md:
- SEMPRE documentar campos computados
- Validações rigorosas de negócio
- Campos de auditoria padronizados
"""
from typing import ClassVar

from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.authentication.serializers import UserSerializer
from apps.core.serializers import BaseModelSerializer

from .models import Attendance, Graduation, Student


class StudentSerializer(BaseModelSerializer):
    """
    Serializer para alunos
    """

    user = UserSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    belt_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    days_since_enrollment = serializers.SerializerMethodField()
    total_attendances = serializers.SerializerMethodField()

    @extend_schema_field(serializers.CharField())
    def get_full_name(self, obj):
        """Nome completo do aluno"""
        return obj.full_name

    @extend_schema_field(serializers.EmailField())
    def get_email(self, obj):
        """Email do aluno"""
        return obj.email

    @extend_schema_field(serializers.CharField())
    def get_belt_display(self, obj):
        """Faixa atual formatada"""
        belt_name = obj.get_belt_color_display()
        if obj.belt_stripes > 0:
            return f"{belt_name} - {obj.belt_stripes} listra(s)"
        return belt_name

    @extend_schema_field(serializers.CharField())
    def get_status_display(self, obj):
        """Status do aluno formatado"""
        return obj.get_status_display()

    @extend_schema_field(serializers.IntegerField())
    def get_days_since_enrollment(self, obj):
        """Dias desde a matrícula"""
        if obj.enrollment_date:
            today = timezone.now().date()
            return (today - obj.enrollment_date).days
        return None

    @extend_schema_field(serializers.IntegerField())
    def get_total_attendances(self, obj):
        """Total de presenças"""
        return obj.attendances.count()

    class Meta:
        model = Student
        fields: ClassVar = [
            "id",
            "user",
            "registration_number",
            "enrollment_date",
            "emergency_contact_name",
            "emergency_contact_phone",
            "emergency_contact_relationship",
            "medical_conditions",
            "medications",
            "belt_color",
            "belt_stripes",
            "last_graduation_date",
            "status",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
            # Campos computados
            "full_name",
            "email",
            "belt_display",
            "status_display",
            "days_since_enrollment",
            "total_attendances",
        ]
        read_only_fields: ClassVar = [
            "id",
            "created_at",
            "updated_at",
            "full_name",
            "email",
            "belt_display",
            "status_display",
            "days_since_enrollment",
            "total_attendances",
        ]
        extra_kwargs: ClassVar = {
            "registration_number": {"help_text": "Número de matrícula único"},
            "enrollment_date": {"help_text": "Data de matrícula"},
            "emergency_contact_name": {"help_text": "Nome do contato de emergência"},
            "emergency_contact_phone": {
                "help_text": "Telefone do contato de emergência"
            },
            "emergency_contact_relationship": {
                "help_text": "Relacionamento com o contato"
            },
            "medical_conditions": {"help_text": "Condições médicas relevantes"},
            "medications": {"help_text": "Medicamentos em uso"},
            "belt_color": {"help_text": "Cor da faixa atual"},
            "belt_stripes": {"help_text": "Número de listras na faixa"},
            "last_graduation_date": {"help_text": "Data da última graduação"},
            "status": {"help_text": "Status do aluno"},
            "notes": {"help_text": "Observações do instrutor"},
        }


class StudentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de alunos
    """

    user_id = serializers.UUIDField(write_only=True, help_text="ID do usuário")

    class Meta:
        model = Student
        fields: ClassVar = [
            "user_id",
            "registration_number",
            "enrollment_date",
            "emergency_contact_name",
            "emergency_contact_phone",
            "emergency_contact_relationship",
            "medical_conditions",
            "medications",
            "belt_color",
            "belt_stripes",
            "status",
            "notes",
        ]
        extra_kwargs: ClassVar = {
            "registration_number": {"help_text": "Número de matrícula único"},
            "enrollment_date": {"help_text": "Data de matrícula"},
            "emergency_contact_name": {"help_text": "Nome do contato de emergência"},
            "emergency_contact_phone": {
                "help_text": "Telefone do contato de emergência"
            },
            "emergency_contact_relationship": {
                "help_text": "Relacionamento com o contato"
            },
            "medical_conditions": {"help_text": "Condições médicas relevantes"},
            "medications": {"help_text": "Medicamentos em uso"},
            "belt_color": {"help_text": "Cor da faixa atual"},
            "belt_stripes": {"help_text": "Número de listras na faixa"},
            "status": {"help_text": "Status do aluno"},
            "notes": {"help_text": "Observações do instrutor"},
        }

    def validate_registration_number(self, value):
        """Validar número de matrícula único"""
        if Student.objects.filter(registration_number=value).exists():
            raise serializers.ValidationError("Este número de matrícula já está em uso")
        return value

    def validate_enrollment_date(self, value):
        """Validar data de matrícula"""
        if value > timezone.now().date():
            raise serializers.ValidationError(
                "Data de matrícula não pode ser no futuro"
            )
        return value


class StudentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para atualização de alunos
    """

    class Meta:
        model = Student
        fields: ClassVar = [
            "emergency_contact_name",
            "emergency_contact_phone",
            "emergency_contact_relationship",
            "medical_conditions",
            "medications",
            "status",
            "notes",
        ]
        extra_kwargs: ClassVar = {
            "emergency_contact_name": {"help_text": "Nome do contato de emergência"},
            "emergency_contact_phone": {
                "help_text": "Telefone do contato de emergência"
            },
            "emergency_contact_relationship": {
                "help_text": "Relacionamento com o contato"
            },
            "medical_conditions": {"help_text": "Condições médicas relevantes"},
            "medications": {"help_text": "Medicamentos em uso"},
            "status": {"help_text": "Status do aluno"},
            "notes": {"help_text": "Observações do instrutor"},
        }


class GraduationSerializer(BaseModelSerializer):
    """
    Serializer para graduações
    """

    student = StudentSerializer(read_only=True)
    instructor = UserSerializer(read_only=True)
    from_belt_display = serializers.SerializerMethodField()
    to_belt_display = serializers.SerializerMethodField()

    @extend_schema_field(serializers.CharField())
    def get_from_belt_display(self, obj):
        """Faixa anterior formatada"""
        return dict(Student.BELT_CHOICES).get(obj.from_belt, obj.from_belt)

    @extend_schema_field(serializers.CharField())
    def get_to_belt_display(self, obj):
        """Nova faixa formatada"""
        return dict(Student.BELT_CHOICES).get(obj.to_belt, obj.to_belt)

    class Meta:
        model = Graduation
        fields: ClassVar = [
            "id",
            "student",
            "instructor",
            "from_belt",
            "to_belt",
            "graduation_date",
            "notes",
            "created_at",
            "updated_at",
            # Campos computados
            "from_belt_display",
            "to_belt_display",
        ]
        read_only_fields: ClassVar = [
            "id",
            "created_at",
            "updated_at",
            "from_belt_display",
            "to_belt_display",
        ]
        extra_kwargs: ClassVar = {
            "from_belt": {"help_text": "Faixa anterior"},
            "to_belt": {"help_text": "Nova faixa"},
            "graduation_date": {"help_text": "Data da graduação"},
            "notes": {"help_text": "Observações sobre a graduação"},
        }


class GraduationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de graduações
    """

    student_id = serializers.UUIDField(write_only=True, help_text="ID do aluno")
    instructor_id = serializers.UUIDField(
        write_only=True, help_text="ID do instrutor", required=False
    )

    class Meta:
        model = Graduation
        fields: ClassVar = [
            "student_id",
            "instructor_id",
            "to_belt",
            "graduation_date",
            "notes",
        ]
        extra_kwargs: ClassVar = {
            "to_belt": {"help_text": "Nova faixa"},
            "graduation_date": {"help_text": "Data da graduação"},
            "notes": {"help_text": "Observações sobre a graduação"},
        }

    def validate_graduation_date(self, value):
        """Validar data de graduação"""
        if value > timezone.now().date():
            raise serializers.ValidationError(
                "Data de graduação não pode ser no futuro"
            )
        return value


class AttendanceSerializer(BaseModelSerializer):
    """
    Serializer para presenças
    """

    student = StudentSerializer(read_only=True)
    instructor = UserSerializer(read_only=True)
    class_type_display = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()

    @extend_schema_field(serializers.CharField())
    def get_class_type_display(self, obj):
        """Tipo de aula formatado"""
        return obj.get_class_type_display()

    @extend_schema_field(serializers.CharField())
    def get_duration(self, obj):
        """Duração da aula"""
        if obj.check_in_time and obj.check_out_time:
            from datetime import datetime

            checkin = datetime.combine(obj.class_date, obj.check_in_time)
            checkout = datetime.combine(obj.class_date, obj.check_out_time)
            duration = checkout - checkin
            return str(duration)
        return None

    class Meta:
        model = Attendance
        fields: ClassVar = [
            "id",
            "student",
            "instructor",
            "class_date",
            "check_in_time",
            "check_out_time",
            "class_type",
            "notes",
            "created_at",
            "updated_at",
            # Campos computados
            "class_type_display",
            "duration",
        ]
        read_only_fields: ClassVar = [
            "id",
            "created_at",
            "updated_at",
            "class_type_display",
            "duration",
        ]
        extra_kwargs: ClassVar = {
            "class_date": {"help_text": "Data da aula"},
            "check_in_time": {"help_text": "Horário de entrada"},
            "check_out_time": {"help_text": "Horário de saída"},
            "class_type": {"help_text": "Tipo de aula"},
            "notes": {"help_text": "Observações sobre a aula"},
        }


class AttendanceCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de presenças
    """

    student_id = serializers.UUIDField(write_only=True, help_text="ID do aluno")
    instructor_id = serializers.UUIDField(
        write_only=True, help_text="ID do instrutor", required=False
    )

    class Meta:
        model = Attendance
        fields: ClassVar = [
            "student_id",
            "instructor_id",
            "class_date",
            "check_in_time",
            "check_out_time",
            "class_type",
            "notes",
        ]
        extra_kwargs: ClassVar = {
            "class_date": {"help_text": "Data da aula"},
            "check_in_time": {"help_text": "Horário de entrada"},
            "check_out_time": {"help_text": "Horário de saída"},
            "class_type": {"help_text": "Tipo de aula"},
            "notes": {"help_text": "Observações sobre a aula"},
        }

    def validate(self, attrs):
        """Validação customizada"""
        # Validar se check_out é após check_in
        if attrs.get("check_out_time") and attrs.get("check_in_time"):
            if attrs["check_out_time"] <= attrs["check_in_time"]:
                raise serializers.ValidationError(
                    {
                        "check_out_time": "Horário de saída deve ser após horário de entrada"
                    }
                )

        # Validar data da aula
        if attrs.get("class_date") and attrs["class_date"] > timezone.now().date():
            raise serializers.ValidationError(
                {"class_date": "Data da aula não pode ser no futuro"}
            )

        return attrs


class GraduateStudentSerializer(serializers.Serializer):
    """
    Serializer para graduação de aluno
    """

    new_belt = serializers.ChoiceField(
        choices=Student.BELT_CHOICES, help_text="Nova faixa do aluno"
    )
    graduation_date = serializers.DateField(
        required=False, help_text="Data da graduação (padrão: hoje)"
    )
    notes = serializers.CharField(
        required=False, help_text="Observações sobre a graduação"
    )

    def validate_graduation_date(self, value):
        """Validar data de graduação"""
        if value and value > timezone.now().date():
            raise serializers.ValidationError(
                "Data de graduação não pode ser no futuro"
            )
        return value
