"""
Views para gestão de alunos

Seguindo padrões estabelecidos no CONTEXT.md:
- SEMPRE herdar de TenantViewSet
- SEMPRE documentar com drf-spectacular
- SEMPRE usar permissions granulares
"""
from typing import ClassVar

from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.authentication.models import User
from apps.core.permissions import CanManageStudents, IsStudentOwner
from apps.core.viewsets import TenantViewSet

from .models import Attendance, Graduation, Student
from .serializers import (
    AttendanceCreateSerializer,
    AttendanceSerializer,
    GraduateStudentSerializer,
    GraduationCreateSerializer,
    GraduationSerializer,
    StudentCreateSerializer,
    StudentSerializer,
    StudentUpdateSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="Listar alunos", tags=["students"]),
    create=extend_schema(summary="Criar aluno", tags=["students"]),
    retrieve=extend_schema(summary="Obter aluno", tags=["students"]),
    update=extend_schema(summary="Atualizar aluno", tags=["students"]),
    partial_update=extend_schema(
        summary="Atualizar aluno parcialmente", tags=["students"]
    ),
    destroy=extend_schema(summary="Deletar aluno", tags=["students"]),
)
class StudentViewSet(TenantViewSet):
    """
    ViewSet para gestão completa de alunos
    """

    queryset = Student.objects.select_related("user").prefetch_related(
        "graduations", "attendances"
    )
    serializer_class = StudentSerializer
    permission_classes: ClassVar = [CanManageStudents]
    search_fields: ClassVar = [
        "user__first_name",
        "user__last_name",
        "user__email",
        "registration_number",
    ]
    filterset_fields: ClassVar = ["belt_color", "status", "enrollment_date"]
    ordering_fields: ClassVar = [
        "user__first_name",
        "user__last_name",
        "enrollment_date",
        "created_at",
    ]
    ordering: ClassVar = ["user__first_name", "user__last_name"]

    def get_serializer_class(self):
        """
        Retorna serializer apropriado baseado na ação
        """
        if self.action == "create":
            return StudentCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return StudentUpdateSerializer
        return StudentSerializer

    def get_permissions(self):
        """
        Instancia e retorna a lista de permissões que esta view requer
        """
        if self.action in ["list", "retrieve"]:
            # Instrutores podem ver, alunos só seus próprios dados
            permission_classes: ClassVar = [
                permissions.IsAuthenticated,
                IsStudentOwner | CanManageStudents,
            ]
        else:
            # Apenas instrutores e admins podem modificar
            permission_classes: ClassVar = [
                permissions.IsAuthenticated,
                CanManageStudents,
            ]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Customiza criação de aluno
        """
        # Buscar usuário
        user_id = serializer.validated_data.pop("user_id")
        user = User.objects.get(id=user_id)

        serializer.save(user=user)

    @extend_schema(
        summary="Graduar aluno",
        description="Promove aluno para nova faixa",
        request=GraduateStudentSerializer,
        responses={200: StudentSerializer},
        tags=["students"],
    )
    @action(detail=True, methods=["post"])
    def graduate(self, request, pk=None):
        """
        Gradua aluno para nova faixa
        """
        student = self.get_object()
        serializer = GraduateStudentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Graduar aluno
        new_belt = serializer.validated_data["new_belt"]
        graduation_date = serializer.validated_data.get(
            "graduation_date", timezone.now().date()
        )
        notes = serializer.validated_data.get("notes", "")

        student.graduate(new_belt, graduation_date)

        # Criar registro de graduação
        Graduation.objects.create(
            student=student,
            from_belt=student.belt_color,  # Será a faixa anterior após o graduate()
            to_belt=new_belt,
            graduation_date=graduation_date,
            instructor=request.user,
            notes=notes,
        )

        # Retornar dados atualizados
        response_serializer = StudentSerializer(student, context={"request": request})
        return Response(response_serializer.data)

    @extend_schema(
        summary="Histórico de graduações",
        description="Lista todas as graduações do aluno",
        responses={200: GraduationSerializer(many=True)},
        tags=["students"],
    )
    @action(detail=True, methods=["get"])
    def graduations(self, request, pk=None):
        """
        Lista graduações do aluno
        """
        student = self.get_object()
        graduations = student.graduations.all()
        serializer = GraduationSerializer(
            graduations, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @extend_schema(
        summary="Histórico de presenças",
        description="Lista presenças do aluno",
        responses={200: AttendanceSerializer(many=True)},
        tags=["students"],
    )
    @action(detail=True, methods=["get"])
    def attendances(self, request, pk=None):
        """
        Lista presenças do aluno
        """
        student = self.get_object()
        attendances = student.attendances.all()
        serializer = AttendanceSerializer(
            attendances, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @extend_schema(
        summary="Estatísticas do aluno",
        description="Retorna estatísticas de presenças e graduações",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "total_attendances": {"type": "integer"},
                    "attendances_this_month": {"type": "integer"},
                    "total_graduations": {"type": "integer"},
                    "days_since_enrollment": {"type": "integer"},
                    "belt_color": {"type": "string"},
                    "status": {"type": "string"},
                },
            }
        },
        tags=["students"],
    )
    @action(detail=True, methods=["get"])
    def stats(self, request, pk=None):
        """
        Estatísticas do aluno
        """
        student = self.get_object()
        today = timezone.now().date()

        # Presenças este mês
        attendances_this_month = student.attendances.filter(
            class_date__year=today.year, class_date__month=today.month
        ).count()

        stats = {
            "total_attendances": student.attendances.count(),
            "attendances_this_month": attendances_this_month,
            "total_graduations": student.graduations.count(),
            "days_since_enrollment": (today - student.enrollment_date).days
            if student.enrollment_date
            else None,
            "belt_color": student.get_belt_color_display(),
            "belt_stripes": student.belt_stripes,
            "status": student.get_status_display(),
        }

        return Response(stats)


@extend_schema_view(
    list=extend_schema(summary="Listar graduações", tags=["students"]),
    create=extend_schema(summary="Criar graduação", tags=["students"]),
    retrieve=extend_schema(summary="Obter graduação", tags=["students"]),
    update=extend_schema(summary="Atualizar graduação", tags=["students"]),
    partial_update=extend_schema(
        summary="Atualizar graduação parcialmente", tags=["students"]
    ),
    destroy=extend_schema(summary="Deletar graduação", tags=["students"]),
)
class GraduationViewSet(TenantViewSet):
    """
    ViewSet para histórico de graduações
    """

    queryset = Graduation.objects.select_related("student__user", "instructor").all()
    serializer_class = GraduationSerializer
    permission_classes: ClassVar = [CanManageStudents]
    filterset_fields: ClassVar = ["student", "from_belt", "to_belt", "graduation_date"]
    ordering_fields: ClassVar = ["graduation_date", "created_at"]
    ordering: ClassVar = ["-graduation_date"]

    def get_serializer_class(self):
        """
        Retorna serializer apropriado baseado na ação
        """
        if self.action == "create":
            return GraduationCreateSerializer
        return GraduationSerializer

    def perform_create(self, serializer):
        """
        Customiza criação de graduação
        """
        # Buscar student e instructor
        student_id = serializer.validated_data.pop("student_id")
        instructor_id = serializer.validated_data.pop("instructor_id", None)

        student = Student.objects.get(id=student_id)
        instructor = (
            User.objects.get(id=instructor_id) if instructor_id else self.request.user
        )

        # Salvar faixa anterior
        from_belt = student.belt_color

        serializer.save(student=student, instructor=instructor, from_belt=from_belt)


@extend_schema_view(
    list=extend_schema(summary="Listar presenças", tags=["students"]),
    create=extend_schema(summary="Registrar presença", tags=["students"]),
    retrieve=extend_schema(summary="Obter presença", tags=["students"]),
    update=extend_schema(summary="Atualizar presença", tags=["students"]),
    partial_update=extend_schema(
        summary="Atualizar presença parcialmente", tags=["students"]
    ),
    destroy=extend_schema(summary="Deletar presença", tags=["students"]),
)
class AttendanceViewSet(TenantViewSet):
    """
    ViewSet para registro de presenças
    """

    queryset = Attendance.objects.select_related("student__user", "instructor").all()
    serializer_class = AttendanceSerializer
    permission_classes: ClassVar = [CanManageStudents]
    filterset_fields: ClassVar = ["student", "class_date", "class_type"]
    ordering_fields: ClassVar = ["class_date", "check_in_time", "created_at"]
    ordering: ClassVar = ["-class_date", "-check_in_time"]

    def get_serializer_class(self):
        """
        Retorna serializer apropriado baseado na ação
        """
        if self.action == "create":
            return AttendanceCreateSerializer
        return AttendanceSerializer

    def perform_create(self, serializer):
        """
        Customiza criação de presença
        """
        # Buscar student e instructor
        student_id = serializer.validated_data.pop("student_id")
        instructor_id = serializer.validated_data.pop("instructor_id", None)

        student = Student.objects.get(id=student_id)
        instructor = (
            User.objects.get(id=instructor_id) if instructor_id else self.request.user
        )

        serializer.save(student=student, instructor=instructor)

    @extend_schema(
        summary="Check-in de aluno",
        description="Registra entrada de aluno na aula",
        request={
            "type": "object",
            "properties": {
                "student_id": {"type": "string", "format": "uuid"},
                "class_type": {"type": "string"},
            },
        },
        responses={201: AttendanceSerializer},
        tags=["students"],
    )
    @action(detail=False, methods=["post"])
    def checkin(self, request):
        """
        Registra check-in de aluno
        """
        student_id = request.data.get("student_id")
        class_type = request.data.get("class_type", "regular")

        if not student_id:
            return Response(
                {"error": "student_id é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response(
                {"error": "Aluno não encontrado"}, status=status.HTTP_404_NOT_FOUND
            )

        # Verificar se já existe check-in hoje
        today = timezone.now().date()
        existing_attendance = Attendance.objects.filter(
            student=student, class_date=today, check_out_time__isnull=True
        ).first()

        if existing_attendance:
            return Response(
                {"error": "Aluno já fez check-in hoje"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Criar registro de presença
        attendance = Attendance.objects.create(
            student=student,
            class_date=today,
            check_in_time=timezone.now().time(),
            class_type=class_type,
            instructor=request.user,
        )

        serializer = AttendanceSerializer(attendance, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Check-out de aluno",
        description="Registra saída de aluno da aula",
        responses={200: AttendanceSerializer},
        tags=["students"],
    )
    @action(detail=True, methods=["post"])
    def checkout(self, request, pk=None):
        """
        Registra check-out de aluno
        """
        attendance = self.get_object()

        if attendance.check_out_time:
            return Response(
                {"error": "Check-out já foi realizado"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        attendance.check_out_time = timezone.now().time()
        attendance.save()

        serializer = AttendanceSerializer(attendance, context={"request": request})
        return Response(serializer.data)
