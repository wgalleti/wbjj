from typing import ClassVar

from django.core.validators import RegexValidator
from django.db import models

from apps.authentication.models import User
from apps.core.models import ActiveManager, BaseModel, TenantMixin


class Student(BaseModel, TenantMixin):
    """
    Model principal para alunos da academia
    """

    # Relacionamento com usuário
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="student_profile"
    )

    # Informações de matrícula
    registration_number = models.CharField(
        max_length=50, unique=True, help_text="Número de matrícula único"
    )
    enrollment_date = models.DateField(help_text="Data de matrícula")

    # Informações de emergência
    emergency_contact_name = models.CharField(max_length=255)
    emergency_contact_phone = models.CharField(
        max_length=20, validators=[RegexValidator(r"^\+?1?\d{9,15}$")]
    )
    emergency_contact_relationship = models.CharField(max_length=100)

    # Informações médicas
    medical_conditions = models.TextField(
        blank=True, help_text="Condições médicas relevantes"
    )
    medications = models.TextField(blank=True, help_text="Medicamentos em uso")

    # Graduação atual
    BELT_CHOICES: ClassVar = [
        ("white", "Branca"),
        ("blue", "Azul"),
        ("purple", "Roxa"),
        ("brown", "Marrom"),
        ("black", "Preta"),
        ("coral", "Coral"),
        ("red", "Vermelha"),
    ]
    belt_color = models.CharField(max_length=10, choices=BELT_CHOICES, default="white")
    belt_stripes = models.PositiveSmallIntegerField(default=0)
    last_graduation_date = models.DateField(blank=True, null=True)

    # Status do aluno
    STATUS_CHOICES: ClassVar = [
        ("active", "Ativo"),
        ("inactive", "Inativo"),
        ("suspended", "Suspenso"),
        ("graduated", "Formado"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    # Observações
    notes = models.TextField(blank=True, help_text="Observações do instrutor")

    # Managers
    objects = models.Manager()
    active_objects = ActiveManager()

    class Meta:
        db_table = "students"
        ordering: ClassVar = ["user__first_name", "user__last_name"]
        indexes: ClassVar = [
            models.Index(fields=["registration_number"]),
            models.Index(fields=["belt_color"]),
            models.Index(fields=["status"]),
            models.Index(fields=["enrollment_date"]),
        ]

    def __str__(self):
        return f"{self.user.full_name} - {self.get_belt_color_display()}"

    @property
    def full_name(self):
        return self.user.full_name

    @property
    def email(self):
        return self.user.email

    def graduate(self, new_belt, graduation_date=None):
        """Promove aluno para nova faixa"""
        from django.utils import timezone

        # Criar registro de graduação
        Graduation.objects.create(
            student=self,
            from_belt=self.belt_color,
            to_belt=new_belt,
            graduation_date=graduation_date or timezone.now().date(),
            instructor=None,  # TODO: adicionar instrutor
        )

        # Atualizar faixa atual
        self.belt_color = new_belt
        self.belt_stripes = 0
        self.last_graduation_date = graduation_date or timezone.now().date()
        self.save()


class Graduation(BaseModel):
    """
    Histórico de graduações dos alunos
    """

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="graduations"
    )

    from_belt = models.CharField(max_length=10, choices=Student.BELT_CHOICES)
    to_belt = models.CharField(max_length=10, choices=Student.BELT_CHOICES)

    graduation_date = models.DateField()
    instructor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={"role__in": ["instructor", "admin"]},
    )

    notes = models.TextField(blank=True)

    class Meta:
        db_table = "graduations"
        ordering: ClassVar = ["-graduation_date"]
        indexes: ClassVar = [
            models.Index(fields=["student", "graduation_date"]),
            models.Index(fields=["graduation_date"]),
        ]

    def __str__(self):
        return f"{self.student.full_name}: {self.from_belt} → {self.to_belt}"


class Attendance(BaseModel):
    """
    Registro de presenças dos alunos
    """

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="attendances"
    )

    class_date = models.DateField()
    check_in_time = models.TimeField()
    check_out_time = models.TimeField(blank=True, null=True)

    CLASS_TYPE_CHOICES: ClassVar = [
        ("gi", "Gi (Kimono)"),
        ("no_gi", "No-Gi"),
        ("competition", "Competição"),
        ("kids", "Infantil"),
        ("fundamentals", "Fundamentos"),
        ("advanced", "Avançado"),
        ("open_mat", "Treino Livre"),
        ("seminar", "Seminário"),
        ("regular", "Regular"),
    ]

    class_type = models.CharField(
        max_length=50,
        choices=CLASS_TYPE_CHOICES,
        default="regular",
        help_text="Tipo de aula",
    )

    instructor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={"role__in": ["instructor", "admin"]},
    )

    notes = models.TextField(blank=True)

    class Meta:
        db_table = "attendances"
        ordering: ClassVar = ["-class_date", "-check_in_time"]
        unique_together: ClassVar = ["student", "class_date", "check_in_time"]
        indexes: ClassVar = [
            models.Index(fields=["student", "class_date"]),
            models.Index(fields=["class_date"]),
        ]

    def __str__(self):
        return f"{self.student.full_name} - {self.class_date}"
