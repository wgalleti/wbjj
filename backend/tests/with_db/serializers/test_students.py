"""
Testes para serializers de Students
Foco: Validações básicas sem dependência de DB
Objetivo: Cobertura simples dos serializers
"""

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.students.models import Attendance, Graduation, Student
from apps.students.serializers import (
    AttendanceCreateSerializer,
    GraduateStudentSerializer,
    GraduationCreateSerializer,
    StudentCreateSerializer,
    StudentSerializer,
    StudentUpdateSerializer,
)
from tests.base import BaseModelTestCase
from tests.with_db.factories.authentication import UserFactory
from tests.with_db.factories.students import (
    StudentFactory,
)

User = get_user_model()


@pytest.mark.usefixtures("tenant_models_context")
class TestStudentSerializer(BaseModelTestCase):
    """Testes para StudentSerializer - campos computados"""

    model_class = Student

    def test_serialize_computed_fields(self):
        """Teste serialização de campos computados"""
        user = UserFactory(
            first_name="João", last_name="Silva", email="joao@example.com"
        )
        student = StudentFactory(
            user=user, belt_color="blue", belt_stripes=2, status="active"
        )

        serializer = StudentSerializer(student)
        data = serializer.data

        # Verificar campos computados
        self.assertIn("full_name", data)
        self.assertIn("email", data)
        self.assertIn("belt_display", data)
        self.assertIn("status_display", data)
        self.assertIn("days_since_enrollment", data)
        self.assertIn("total_attendances", data)

        # Verificar valores
        self.assertEqual(data["full_name"], "João Silva")
        self.assertEqual(data["email"], "joao@example.com")
        self.assertIn("listra", data["belt_display"])
        self.assertEqual(data["status_display"], "Ativo")


@pytest.mark.usefixtures("tenant_models_context")
class TestStudentCreateSerializer(BaseModelTestCase):
    """Testes para StudentCreateSerializer - validações de criação"""

    model_class = Student

    def test_create_student_success(self):
        """Teste criação de aluno com sucesso"""
        user = UserFactory()

        valid_data = {
            "user_id": str(user.id),
            "registration_number": "EST001",
            "enrollment_date": "2024-01-01",
            "emergency_contact_name": "Maria Silva",
            "emergency_contact_phone": "11999999999",
            "emergency_contact_relationship": "mãe",
            "belt_color": "white",
            "belt_stripes": 0,
            "status": "active",
        }

        serializer = StudentCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_validate_registration_number_already_exists(self):
        """Teste erro com número de matrícula já existente"""
        # Criar aluno existente
        StudentFactory(registration_number="EST001")

        user = UserFactory()
        invalid_data = {
            "user_id": str(user.id),
            "registration_number": "EST001",  # Já existe
        }

        serializer = StudentCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("registration_number", serializer.errors)

    def test_validate_registration_number_unique(self):
        """Teste sucesso com número de matrícula único"""
        user = UserFactory()

        valid_data = {
            "user_id": str(user.id),
            "registration_number": "EST002",  # Único
            "enrollment_date": "2024-01-01",
            "emergency_contact_name": "João Silva",
            "emergency_contact_phone": "11999999999",
            "emergency_contact_relationship": "pai",
        }

        serializer = StudentCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_validate_enrollment_date_future(self):
        """Teste erro com data de matrícula no futuro"""
        user = UserFactory()

        future_date = (timezone.now() + timedelta(days=1)).date()
        invalid_data = {
            "user_id": str(user.id),
            "registration_number": "EST003",
            "enrollment_date": future_date.isoformat(),  # Futuro - inválido
        }

        serializer = StudentCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("enrollment_date", serializer.errors)

    def test_validate_enrollment_date_valid(self):
        """Teste sucesso com data de matrícula válida"""
        user = UserFactory()

        past_date = (timezone.now() - timedelta(days=30)).date()
        valid_data = {
            "user_id": str(user.id),
            "registration_number": "EST004",
            "enrollment_date": past_date.isoformat(),  # Passado - válido
            "emergency_contact_name": "João Silva",
            "emergency_contact_phone": "11999999999",
            "emergency_contact_relationship": "pai",
        }

        serializer = StudentCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)


@pytest.mark.usefixtures("tenant_models_context")
class TestStudentUpdateSerializer(BaseModelTestCase):
    """Testes para StudentUpdateSerializer - validações de atualização"""

    model_class = Student

    def test_update_student_success(self):
        """Teste atualização de aluno com sucesso"""
        student = StudentFactory()

        update_data = {
            "emergency_contact_name": "João Silva Atualizado",
            "emergency_contact_phone": "11888888888",
            "emergency_contact_relationship": "pai",
            "medical_conditions": "Nenhuma",
            "medications": "Nenhum",
            "status": "inactive",
            "notes": "Notas atualizadas",
        }

        serializer = StudentUpdateSerializer(student, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)


@pytest.mark.usefixtures("tenant_models_context")
class TestGraduationCreateSerializer(BaseModelTestCase):
    """Testes para GraduationCreateSerializer - validações de criação"""

    model_class = Graduation

    def test_create_graduation_success(self):
        """Teste criação de graduação com sucesso"""
        student = StudentFactory()
        instructor = UserFactory(role="instructor")

        valid_data = {
            "student_id": str(student.id),
            "instructor_id": str(instructor.id),
            "to_belt": "blue",
            "graduation_date": "2024-01-01",
            "notes": "Graduação merecida",
        }

        serializer = GraduationCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_create_graduation_without_instructor(self):
        """Teste criação de graduação sem instrutor"""
        student = StudentFactory()

        valid_data = {
            "student_id": str(student.id),
            "to_belt": "blue",
            "graduation_date": "2024-01-01",
        }

        serializer = GraduationCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_validate_graduation_date_future(self):
        """Teste erro com data de graduação no futuro"""
        student = StudentFactory()

        future_date = (timezone.now() + timedelta(days=1)).date()
        invalid_data = {
            "student_id": str(student.id),
            "to_belt": "blue",
            "graduation_date": future_date.isoformat(),  # Futuro - inválido
        }

        serializer = GraduationCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("graduation_date", serializer.errors)

    def test_validate_graduation_date_valid(self):
        """Teste sucesso com data de graduação válida"""
        student = StudentFactory()

        today = timezone.now().date()
        valid_data = {
            "student_id": str(student.id),
            "to_belt": "blue",
            "graduation_date": today.isoformat(),  # Hoje - válido
        }

        serializer = GraduationCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)


@pytest.mark.usefixtures("tenant_models_context")
class TestAttendanceCreateSerializer(BaseModelTestCase):
    """Testes para AttendanceCreateSerializer - validações de criação"""

    model_class = Attendance

    def test_create_attendance_success(self):
        """Teste criação de presença com sucesso"""
        student = StudentFactory()
        instructor = UserFactory(role="instructor")

        valid_data = {
            "student_id": str(student.id),
            "instructor_id": str(instructor.id),
            "class_date": "2024-01-01",
            "check_in_time": "18:00:00",
            "check_out_time": "19:30:00",
            "class_type": "regular",
            "notes": "Aula normal",
        }

        serializer = AttendanceCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_create_attendance_without_instructor(self):
        """Teste criação de presença sem instrutor"""
        student = StudentFactory()

        valid_data = {
            "student_id": str(student.id),
            "class_date": "2024-01-01",
            "check_in_time": "18:00:00",
            "class_type": "regular",
        }

        serializer = AttendanceCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_validate_check_out_before_check_in(self):
        """Teste erro com check-out antes do check-in"""
        student = StudentFactory()

        invalid_data = {
            "student_id": str(student.id),
            "class_date": "2024-01-01",
            "check_in_time": "19:00:00",
            "check_out_time": "18:30:00",  # Antes do check-in - inválido
            "class_type": "regular",
        }

        serializer = AttendanceCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("check_out_time", serializer.errors)

    def test_validate_check_out_after_check_in(self):
        """Teste sucesso com check-out após check-in"""
        student = StudentFactory()

        valid_data = {
            "student_id": str(student.id),
            "class_date": "2024-01-01",
            "check_in_time": "18:00:00",
            "check_out_time": "19:30:00",  # Após check-in - válido
            "class_type": "regular",
        }

        serializer = AttendanceCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_validate_class_date_future(self):
        """Teste erro com data da aula no futuro"""
        student = StudentFactory()

        future_date = (timezone.now() + timedelta(days=1)).date()
        invalid_data = {
            "student_id": str(student.id),
            "class_date": future_date.isoformat(),  # Futuro - inválido
            "check_in_time": "18:00:00",
            "class_type": "regular",
        }

        serializer = AttendanceCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("class_date", serializer.errors)

    def test_validate_class_date_valid(self):
        """Teste sucesso com data da aula válida"""
        student = StudentFactory()

        today = timezone.now().date()
        valid_data = {
            "student_id": str(student.id),
            "class_date": today.isoformat(),  # Hoje - válido
            "check_in_time": "18:00:00",
            "class_type": "regular",
        }

        serializer = AttendanceCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class TestGraduateStudentSerializer(BaseModelTestCase):
    """Testes para GraduateStudentSerializer - validações de graduação"""

    model_class = Student

    def test_graduate_student_valid_data(self):
        """Teste graduação de aluno com dados válidos"""
        valid_data = {
            "new_belt": "blue",
            "graduation_date": "2024-01-01",
            "notes": "Graduação merecida",
        }

        serializer = GraduateStudentSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_graduate_student_default_date(self):
        """Teste graduação sem data (deve usar hoje)"""
        valid_data = {
            "new_belt": "blue"
            # Sem graduation_date - deve usar default
        }

        serializer = GraduateStudentSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_graduate_student_future_date(self):
        """Teste erro com data de graduação no futuro"""
        future_date = (timezone.now() + timedelta(days=1)).date()
        invalid_data = {
            "new_belt": "blue",
            "graduation_date": future_date.isoformat(),  # Futuro - inválido
        }

        serializer = GraduateStudentSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("graduation_date", serializer.errors)

    def test_graduate_student_invalid_belt(self):
        """Teste erro com faixa inválida"""
        invalid_data = {"new_belt": "INVALID_BELT"}  # Faixa inválida

        serializer = GraduateStudentSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("new_belt", serializer.errors)

    def test_graduate_student_valid_belt_choices(self):
        """Teste sucesso com faixas válidas"""
        for belt_choice, _ in Student.BELT_CHOICES:
            valid_data = {"new_belt": belt_choice}

            serializer = GraduateStudentSerializer(data=valid_data)
            self.assertTrue(
                serializer.is_valid(), f"Faixa {belt_choice} deveria ser válida"
            )

    def test_graduate_student_with_notes(self):
        """Teste graduação com observações"""
        valid_data = {
            "new_belt": "purple",
            "notes": "Aluno demonstrou excelente técnica e dedicação",
        }

        serializer = GraduateStudentSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
