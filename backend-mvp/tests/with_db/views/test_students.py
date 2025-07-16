"""
Testes para Views de Estudantes
Foco: StudentViewSet, GraduationViewSet, AttendanceViewSet, ações customizadas
Objetivo: 100% de cobertura para students/views.py
"""

from datetime import date, time
from unittest.mock import Mock, patch

from rest_framework import status

from apps.students.views import AttendanceViewSet, GraduationViewSet, StudentViewSet
from tests.base import BaseModelTestCase
from tests.with_db.factories import UserFactory


class TestStudentViewSet(BaseModelTestCase):
    """Testes para StudentViewSet - gestão completa de alunos"""

    model_class = UserFactory._meta.model

    def setUp(self):
        super().setUp()
        self.viewset = StudentViewSet()
        self.viewset.action = "list"

    def test_get_serializer_class_create(self):
        """Teste get_serializer_class para ação create"""
        from apps.students.serializers import StudentCreateSerializer

        self.viewset.action = "create"
        serializer_class = self.viewset.get_serializer_class()
        self.assertEqual(serializer_class, StudentCreateSerializer)

    def test_get_serializer_class_update(self):
        """Teste get_serializer_class para ações update/partial_update"""
        from apps.students.serializers import StudentUpdateSerializer

        # Teste update
        self.viewset.action = "update"
        serializer_class = self.viewset.get_serializer_class()
        self.assertEqual(serializer_class, StudentUpdateSerializer)

        # Teste partial_update
        self.viewset.action = "partial_update"
        serializer_class = self.viewset.get_serializer_class()
        self.assertEqual(serializer_class, StudentUpdateSerializer)

    def test_get_serializer_class_default(self):
        """Teste get_serializer_class para outras ações"""
        from apps.students.serializers import StudentSerializer

        self.viewset.action = "list"
        serializer_class = self.viewset.get_serializer_class()
        self.assertEqual(serializer_class, StudentSerializer)

    def test_get_permissions_list_retrieve(self):
        """Teste get_permissions para ações list/retrieve"""
        from rest_framework import permissions

        for action in ["list", "retrieve"]:
            self.viewset.action = action
            permission_instances = self.viewset.get_permissions()

            # Verifica que tem 2 permissões (IsAuthenticated + IsStudentOwner|CanManageStudents)
            self.assertEqual(len(permission_instances), 2)
            self.assertIsInstance(permission_instances[0], permissions.IsAuthenticated)

    def test_get_permissions_modification(self):
        """Teste get_permissions para ações de modificação"""
        from rest_framework import permissions

        from apps.core.permissions import CanManageStudents

        for action in ["create", "update", "destroy"]:
            self.viewset.action = action
            permission_instances = self.viewset.get_permissions()

            # Verifica que tem 2 permissões (IsAuthenticated + CanManageStudents)
            self.assertEqual(len(permission_instances), 2)
            self.assertIsInstance(permission_instances[0], permissions.IsAuthenticated)
            self.assertIsInstance(permission_instances[1], CanManageStudents)

    def test_perform_create(self):
        """Teste perform_create - busca usuário e cria aluno"""
        # Mock user
        mock_user = Mock()
        mock_user.id = "user-123"

        # Mock serializer
        mock_serializer = Mock()
        mock_serializer.validated_data = {
            "user_id": str(mock_user.id),
            "belt_color": "white",
        }
        mock_serializer.save = Mock()

        # Mock User.objects.get
        with patch("apps.students.views.User.objects.get", return_value=mock_user):
            self.viewset.perform_create(mock_serializer)

            # Verifica que removeu user_id e salvou com user
            self.assertNotIn("user_id", mock_serializer.validated_data)
            mock_serializer.save.assert_called_once_with(user=mock_user)

    def test_graduate_action_success(self):
        """Teste action graduate com sucesso"""
        # Mock request
        mock_request = Mock()
        mock_request.user = Mock()
        mock_request.data = {
            "new_belt": "blue",
            "graduation_date": "2024-01-15",
            "notes": "Test notes",
        }

        # Mock get_object
        mock_student = Mock()
        mock_student.belt_color = "white"
        mock_student.graduate = Mock()
        self.viewset.get_object = Mock(return_value=mock_student)

        # Mock serializers
        mock_grad_serializer = Mock()
        mock_grad_serializer.is_valid.return_value = None
        mock_grad_serializer.validated_data = {
            "new_belt": "blue",
            "graduation_date": date(2024, 1, 15),
            "notes": "Test notes",
        }

        mock_response_serializer = Mock()
        mock_response_serializer.data = {"id": "test", "belt_color": "blue"}

        with patch(
            "apps.students.views.GraduateStudentSerializer",
            return_value=mock_grad_serializer,
        ), patch(
            "apps.students.views.StudentSerializer",
            return_value=mock_response_serializer,
        ), patch("apps.students.views.Graduation.objects.create") as mock_create:
            response = self.viewset.graduate(mock_request, pk=1)

            # Verifica que graduou o aluno
            mock_student.graduate.assert_called_once_with("blue", date(2024, 1, 15))

            # Verifica que criou registro de graduação
            mock_create.assert_called_once()
            create_call_kwargs = mock_create.call_args[1]
            self.assertEqual(create_call_kwargs["to_belt"], "blue")
            self.assertEqual(create_call_kwargs["graduation_date"], date(2024, 1, 15))
            self.assertEqual(create_call_kwargs["notes"], "Test notes")
            self.assertEqual(create_call_kwargs["instructor"], mock_request.user)

            # Verifica resposta
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_graduations_action(self):
        """Teste action graduations - lista graduações do aluno"""
        # Mock request
        mock_request = Mock()

        # Mock get_object e graduations
        mock_student = Mock()
        mock_graduations = Mock()
        mock_student.graduations.all.return_value = mock_graduations
        self.viewset.get_object = Mock(return_value=mock_student)

        # Mock serializer
        mock_serializer = Mock()
        mock_serializer.data = [{"id": "grad1"}, {"id": "grad2"}]

        with patch(
            "apps.students.views.GraduationSerializer", return_value=mock_serializer
        ):
            response = self.viewset.graduations(mock_request, pk=1)

            # Verifica resposta
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            mock_student.graduations.all.assert_called_once()

    def test_attendances_action(self):
        """Teste action attendances - lista presenças do aluno"""
        # Mock request
        mock_request = Mock()

        # Mock get_object e attendances
        mock_student = Mock()
        mock_attendances = Mock()
        mock_student.attendances.all.return_value = mock_attendances
        self.viewset.get_object = Mock(return_value=mock_student)

        # Mock serializer
        mock_serializer = Mock()
        mock_serializer.data = [{"id": "att1"}, {"id": "att2"}]

        with patch(
            "apps.students.views.AttendanceSerializer", return_value=mock_serializer
        ):
            response = self.viewset.attendances(mock_request, pk=1)

            # Verifica resposta
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            mock_student.attendances.all.assert_called_once()

    def test_stats_action(self):
        """Teste action stats - estatísticas do aluno"""
        # Mock request
        mock_request = Mock()

        # Mock get_object
        mock_student = Mock()
        mock_student.attendances.count.return_value = 25
        mock_student.attendances.filter.return_value.count.return_value = 8
        mock_student.graduations.count.return_value = 3
        mock_student.enrollment_date = date(2023, 1, 1)
        mock_student.get_belt_color_display.return_value = "Branca"
        mock_student.belt_stripes = 2
        mock_student.get_status_display.return_value = "Ativo"

        self.viewset.get_object = Mock(return_value=mock_student)

        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value.date.return_value = date(2024, 1, 1)

            response = self.viewset.stats(mock_request, pk=1)

            # Verifica resposta
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            expected_stats = {
                "total_attendances": 25,
                "attendances_this_month": 8,
                "total_graduations": 3,
                "days_since_enrollment": 365,  # 2024-01-01 - 2023-01-01
                "belt_color": "Branca",
                "belt_stripes": 2,
                "status": "Ativo",
            }
            self.assertEqual(response.data, expected_stats)

    def test_stats_action_no_enrollment_date(self):
        """Teste action stats sem data de matrícula"""
        # Mock request
        mock_request = Mock()

        # Mock get_object sem enrollment_date
        mock_student = Mock()
        mock_student.attendances.count.return_value = 10
        mock_student.attendances.filter.return_value.count.return_value = 3
        mock_student.graduations.count.return_value = 1
        mock_student.enrollment_date = None  # Sem data
        mock_student.get_belt_color_display.return_value = "Branca"
        mock_student.belt_stripes = 0
        mock_student.get_status_display.return_value = "Ativo"

        self.viewset.get_object = Mock(return_value=mock_student)

        response = self.viewset.stats(mock_request, pk=1)

        # Verifica que days_since_enrollment é None
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["days_since_enrollment"])


class TestGraduationViewSet(BaseModelTestCase):
    """Testes para GraduationViewSet - histórico de graduações"""

    model_class = UserFactory._meta.model

    def setUp(self):
        super().setUp()
        self.viewset = GraduationViewSet()
        self.viewset.action = "list"

    def test_get_serializer_class_create(self):
        """Teste get_serializer_class para ação create"""
        from apps.students.serializers import GraduationCreateSerializer

        self.viewset.action = "create"
        serializer_class = self.viewset.get_serializer_class()
        self.assertEqual(serializer_class, GraduationCreateSerializer)

    def test_get_serializer_class_default(self):
        """Teste get_serializer_class para outras ações"""
        from apps.students.serializers import GraduationSerializer

        self.viewset.action = "list"
        serializer_class = self.viewset.get_serializer_class()
        self.assertEqual(serializer_class, GraduationSerializer)

    def test_perform_create_with_instructor_id(self):
        """Teste perform_create com instructor_id"""
        # Mock serializer
        mock_serializer = Mock()
        mock_serializer.validated_data = {
            "student_id": "student-123",
            "instructor_id": "instructor-456",
            "to_belt": "blue",
        }
        mock_serializer.save = Mock()

        # Mock request
        self.viewset.request = Mock()
        self.viewset.request.user = Mock()

        # Mock student e instructor
        mock_student = Mock()
        mock_student.belt_color = "white"
        mock_instructor = Mock()

        with patch(
            "apps.students.views.Student.objects.get", return_value=mock_student
        ), patch("apps.students.views.User.objects.get", return_value=mock_instructor):
            self.viewset.perform_create(mock_serializer)

            # Verifica que removeu os IDs e salvou com objetos
            self.assertNotIn("student_id", mock_serializer.validated_data)
            self.assertNotIn("instructor_id", mock_serializer.validated_data)
            mock_serializer.save.assert_called_once_with(
                student=mock_student, instructor=mock_instructor, from_belt="white"
            )

    def test_perform_create_without_instructor_id(self):
        """Teste perform_create sem instructor_id (usa request.user)"""
        # Mock serializer
        mock_serializer = Mock()
        mock_serializer.validated_data = {
            "student_id": "student-123",
            "to_belt": "blue",
        }
        mock_serializer.save = Mock()

        # Mock request
        mock_instructor = Mock()
        self.viewset.request = Mock()
        self.viewset.request.user = mock_instructor

        # Mock student
        mock_student = Mock()
        mock_student.belt_color = "white"

        with patch(
            "apps.students.views.Student.objects.get", return_value=mock_student
        ):
            self.viewset.perform_create(mock_serializer)

            # Verifica que usou request.user como instructor
            mock_serializer.save.assert_called_once_with(
                student=mock_student, instructor=mock_instructor, from_belt="white"
            )


class TestAttendanceViewSet(BaseModelTestCase):
    """Testes para AttendanceViewSet - registro de presenças"""

    model_class = UserFactory._meta.model

    def setUp(self):
        super().setUp()
        self.viewset = AttendanceViewSet()
        self.viewset.action = "list"

    def test_get_serializer_class_create(self):
        """Teste get_serializer_class para ação create"""
        from apps.students.serializers import AttendanceCreateSerializer

        self.viewset.action = "create"
        serializer_class = self.viewset.get_serializer_class()
        self.assertEqual(serializer_class, AttendanceCreateSerializer)

    def test_get_serializer_class_default(self):
        """Teste get_serializer_class para outras ações"""
        from apps.students.serializers import AttendanceSerializer

        self.viewset.action = "list"
        serializer_class = self.viewset.get_serializer_class()
        self.assertEqual(serializer_class, AttendanceSerializer)

    def test_perform_create_with_instructor_id(self):
        """Teste perform_create com instructor_id"""
        # Mock serializer
        mock_serializer = Mock()
        mock_serializer.validated_data = {
            "student_id": "student-123",
            "instructor_id": "instructor-456",
            "class_type": "regular",
        }
        mock_serializer.save = Mock()

        # Mock request
        self.viewset.request = Mock()
        self.viewset.request.user = Mock()

        # Mock student e instructor
        mock_student = Mock()
        mock_instructor = Mock()

        with patch(
            "apps.students.views.Student.objects.get", return_value=mock_student
        ), patch("apps.students.views.User.objects.get", return_value=mock_instructor):
            self.viewset.perform_create(mock_serializer)

            # Verifica que removeu os IDs e salvou com objetos
            self.assertNotIn("student_id", mock_serializer.validated_data)
            self.assertNotIn("instructor_id", mock_serializer.validated_data)
            mock_serializer.save.assert_called_once_with(
                student=mock_student, instructor=mock_instructor
            )

    def test_perform_create_without_instructor_id(self):
        """Teste perform_create sem instructor_id (usa request.user)"""
        # Mock serializer
        mock_serializer = Mock()
        mock_serializer.validated_data = {
            "student_id": "student-123",
            "class_type": "regular",
        }
        mock_serializer.save = Mock()

        # Mock request
        mock_instructor = Mock()
        self.viewset.request = Mock()
        self.viewset.request.user = mock_instructor

        # Mock student
        mock_student = Mock()

        with patch(
            "apps.students.views.Student.objects.get", return_value=mock_student
        ):
            self.viewset.perform_create(mock_serializer)

            # Verifica que usou request.user como instructor
            mock_serializer.save.assert_called_once_with(
                student=mock_student, instructor=mock_instructor
            )

    def test_checkin_action_success(self):
        """Teste action checkin com sucesso"""
        # Mock request
        mock_request = Mock()
        mock_request.user = Mock()
        mock_request.data = {"student_id": "student-123", "class_type": "regular"}

        # Mock student
        mock_student = Mock()
        mock_student.id = "student-123"

        # Mock timezone.now
        today = date(2024, 1, 15)
        now_time = time(10, 30)

        with patch("django.utils.timezone.now") as mock_now, patch(
            "apps.students.views.Student.objects.get", return_value=mock_student
        ), patch("apps.students.views.Attendance.objects.filter") as mock_filter, patch(
            "apps.students.views.Attendance.objects.create"
        ) as mock_create, patch(
            "apps.students.views.AttendanceSerializer"
        ) as mock_serializer_class:
            mock_now.return_value.date.return_value = today
            mock_now.return_value.time.return_value = now_time
            mock_filter.return_value.first.return_value = None  # Sem check-in existente

            mock_attendance = Mock()
            mock_create.return_value = mock_attendance

            mock_serializer = Mock()
            mock_serializer.data = {"id": "att123", "student": "student-123"}
            mock_serializer_class.return_value = mock_serializer

            response = self.viewset.checkin(mock_request)

            # Verifica que criou attendance
            mock_create.assert_called_once_with(
                student=mock_student,
                class_date=today,
                check_in_time=now_time,
                class_type="regular",
                instructor=mock_request.user,
            )

            # Verifica resposta
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_checkin_action_missing_student_id(self):
        """Teste action checkin sem student_id"""
        # Mock request sem student_id
        mock_request = Mock()
        mock_request.data = {}

        response = self.viewset.checkin(mock_request)

        # Verifica erro
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("student_id é obrigatório", response.data["error"])

    def test_checkin_action_student_not_found(self):
        """Teste action checkin com aluno não encontrado"""
        from apps.students.models import Student

        # Mock request
        mock_request = Mock()
        mock_request.data = {"student_id": "invalid-id"}

        with patch(
            "apps.students.views.Student.objects.get", side_effect=Student.DoesNotExist
        ):
            response = self.viewset.checkin(mock_request)

            # Verifica erro
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn("Aluno não encontrado", response.data["error"])

    def test_checkin_action_already_checked_in(self):
        """Teste action checkin com aluno já com check-in"""
        # Mock request
        mock_request = Mock()
        mock_request.data = {"student_id": "student-123"}

        # Mock student
        mock_student = Mock()

        # Mock attendance existente
        existing_attendance = Mock()

        with patch(
            "apps.students.views.Student.objects.get", return_value=mock_student
        ), patch("apps.students.views.Attendance.objects.filter") as mock_filter:
            mock_filter.return_value.first.return_value = existing_attendance

            response = self.viewset.checkin(mock_request)

            # Verifica erro
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("Aluno já fez check-in hoje", response.data["error"])

    def test_checkout_action_success(self):
        """Teste action checkout com sucesso"""
        # Mock request
        mock_request = Mock()

        # Mock get_object
        mock_attendance = Mock()
        mock_attendance.check_out_time = None  # Sem checkout
        mock_attendance.save = Mock()

        self.viewset.get_object = Mock(return_value=mock_attendance)

        # Mock serializer
        mock_serializer = Mock()
        mock_serializer.data = {"id": "att123", "check_out_time": "15:30:00"}

        with patch("django.utils.timezone.now") as mock_now, patch(
            "apps.students.views.AttendanceSerializer", return_value=mock_serializer
        ):
            checkout_time = time(15, 30)
            mock_now.return_value.time.return_value = checkout_time

            response = self.viewset.checkout(mock_request, pk=1)

            # Verifica que fez checkout
            self.assertEqual(mock_attendance.check_out_time, checkout_time)
            mock_attendance.save.assert_called_once()

            # Verifica resposta
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_checkout_action_already_done(self):
        """Teste action checkout já realizado"""
        # Mock request
        mock_request = Mock()

        # Mock get_object com checkout já feito
        mock_attendance = Mock()
        mock_attendance.check_out_time = time(15, 30)  # Já tem checkout

        self.viewset.get_object = Mock(return_value=mock_attendance)

        response = self.viewset.checkout(mock_request, pk=1)

        # Verifica erro
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Check-out já foi realizado", response.data["error"])
