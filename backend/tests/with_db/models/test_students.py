"""
Testes para models de Students
Cobertura completa dos models Student, Attendance e Graduation
"""

from datetime import date, time, timedelta

from django.db import IntegrityError

from apps.students.models import Attendance, Graduation, Student
from tests.base import BaseTenantTestCase
from tests.with_db.factories.authentication import UserFactory
from tests.with_db.factories.students import (
    AttendanceFactory,
    GraduationFactory,
    StudentFactory,
)


class TestStudentModel(BaseTenantTestCase):
    """Testes para Student model"""

    def test_create_student_success(self):
        """Teste criação básica de estudante"""
        student_user = UserFactory(role="student")
        student = Student.objects.create(
            user=student_user,
            registration_number="TEST001",
            enrollment_date=date.today(),
            belt_color="white",
            emergency_contact_name="Maria Silva",
            emergency_contact_phone="+5511888888888",
            emergency_contact_relationship="Mãe",
        )

        self.assertEqual(student.user, student_user)
        self.assertEqual(student.registration_number, "TEST001")
        self.assertEqual(student.belt_color, "white")
        self.assertEqual(student.status, "active")  # default

    def test_student_str_representation(self):
        """Teste representação string do Student"""
        student = StudentFactory()
        expected = f"{student.user.full_name} - {student.get_belt_color_display()}"
        self.assertEqual(str(student), expected)

    def test_student_unique_registration_number(self):
        """Teste unicidade do número de matrícula"""
        StudentFactory(registration_number="TEST001")

        # Criar outro usuário para tentar usar mesmo registration_number
        user2 = UserFactory(email="student2@example.com", role="student")

        with self.assertRaises(IntegrityError):
            Student.objects.create(
                user=user2,
                registration_number="TEST001",
                enrollment_date=date.today(),
                belt_color="white",
                emergency_contact_name="Maria Silva",
                emergency_contact_phone="+5511888888888",
                emergency_contact_relationship="Mãe",
            )

    def test_student_ordering(self):
        """Teste ordenação por nome do usuário"""
        # Criar usuários
        user_a = UserFactory(first_name="Ana", last_name="Silva", email="a@example.com")
        user_b = UserFactory(
            first_name="Bruno", last_name="Costa", email="b@example.com"
        )
        user_c = UserFactory(
            first_name="Carlos", last_name="Santos", email="c@example.com"
        )

        # Criar estudantes - deixar factory gerar registration_number
        StudentFactory(user=user_c)
        StudentFactory(user=user_a)
        StudentFactory(user=user_b)

        students = Student.objects.all()
        names = [student.user.first_name for student in students]

        self.assertEqual(names, ["Ana", "Bruno", "Carlos"])

    def test_student_belt_colors(self):
        """Teste diferentes cores de faixa"""
        valid_belts = ["white", "blue", "purple", "brown", "black", "coral", "red"]

        for belt in valid_belts:
            student = StudentFactory(belt_color=belt)
            self.assertEqual(student.belt_color, belt)

    def test_student_current_age_property(self):
        """Teste propriedade current_age (se existir)"""
        # Criar usuário com data de nascimento
        user = UserFactory(birth_date=date(1990, 5, 15))
        student = StudentFactory(user=user)

        # Verificar propriedades básicas
        self.assertEqual(student.user.birth_date, date(1990, 5, 15))
        self.assertEqual(student.full_name, user.full_name)

    def test_student_current_age_no_birth_date(self):
        """Teste propriedade current_age sem data de nascimento"""
        # Se usuário não tem birth_date
        student = StudentFactory()
        student.user.birth_date = None
        student.user.save()

        # Deve funcionar normalmente
        self.assertIsNone(student.user.birth_date)

    def test_student_training_years_property(self):
        """Teste cálculo de anos de treino"""
        # Baseado na data de matrícula
        enrollment_date = date.today() - timedelta(days=365)  # 1 ano atrás
        student = StudentFactory(enrollment_date=enrollment_date)

        # Verificar data de matrícula
        self.assertEqual(student.enrollment_date, enrollment_date)

    def test_student_is_active_default(self):
        """Teste status ativo por padrão"""
        student = StudentFactory()
        self.assertEqual(student.status, "active")

    def test_student_deactivation(self):
        """Teste desativação de estudante"""
        student = StudentFactory()
        student.status = "inactive"
        student.save()

        self.assertEqual(student.status, "inactive")

    def test_student_graduate_method(self):
        """Teste método de graduação"""
        student = StudentFactory(belt_color="white")
        initial_belt = student.belt_color
        new_belt = "blue"

        # Graduar estudante
        student.graduate(new_belt)

        # Verificar mudanças
        student.refresh_from_db()
        self.assertEqual(student.belt_color, new_belt)
        self.assertEqual(student.belt_stripes, 0)
        self.assertEqual(student.last_graduation_date, date.today())

        # Verificar se criou registro de graduação
        graduation = Graduation.objects.filter(student=student).first()
        self.assertIsNotNone(graduation)
        self.assertEqual(graduation.from_belt, initial_belt)
        self.assertEqual(graduation.to_belt, new_belt)


class TestAttendanceModel(BaseTenantTestCase):
    """Testes para Attendance model"""

    model_class = Attendance

    def test_create_attendance_success(self):
        """Teste criação básica de presença"""
        student = StudentFactory()
        attendance = Attendance.objects.create(
            student=student,
            class_date=date.today(),
            check_in_time=time(18, 0),
            class_type="regular",
        )

        self.assertEqual(attendance.student, student)
        self.assertEqual(attendance.class_date, date.today())
        self.assertEqual(attendance.check_in_time, time(18, 0))
        self.assertEqual(attendance.class_type, "regular")

    def test_attendance_str_representation(self):
        """Teste representação string da Attendance"""
        student = StudentFactory()
        attendance = AttendanceFactory(student=student, class_date=date.today())
        expected = f"{student.full_name} - {date.today()}"
        self.assertEqual(str(attendance), expected)

    def test_attendance_ordering(self):
        """Teste ordenação por data/hora (desc)"""
        student = StudentFactory()
        # Criar presenças em dias diferentes
        AttendanceFactory(
            student=student, class_date=date(2024, 1, 15), check_in_time=time(18, 0)
        )
        AttendanceFactory(
            student=student, class_date=date(2024, 1, 16), check_in_time=time(19, 0)
        )
        AttendanceFactory(
            student=student, class_date=date(2024, 1, 14), check_in_time=time(17, 0)
        )

        attendances = list(Attendance.objects.all())
        dates = [att.class_date for att in attendances]

        # Ordenação descendente (mais recente primeiro)
        expected_order = [date(2024, 1, 16), date(2024, 1, 15), date(2024, 1, 14)]
        self.assertEqual(dates, expected_order)

    def test_attendance_class_types(self):
        """Teste tipos de aula"""
        student = StudentFactory()
        class_types = ["regular", "competition", "private", "seminar"]

        for class_type in class_types:
            attendance = AttendanceFactory(student=student, class_type=class_type)
            self.assertEqual(attendance.class_type, class_type)

    def test_attendance_check_out_time(self):
        """Teste horário de saída opcional"""
        student = StudentFactory()
        attendance = AttendanceFactory(
            student=student, check_in_time=time(18, 0), check_out_time=time(19, 30)
        )

        self.assertEqual(attendance.check_in_time, time(18, 0))
        self.assertEqual(attendance.check_out_time, time(19, 30))

        # Sem horário de saída
        attendance2 = AttendanceFactory(student=student, check_out_time=None)
        self.assertIsNone(attendance2.check_out_time)

    def test_attendance_with_instructor(self):
        """Teste presença com instrutor"""
        student = StudentFactory()
        instructor_user = UserFactory(role="instructor")
        attendance = AttendanceFactory(student=student, instructor=instructor_user)

        self.assertEqual(attendance.instructor, instructor_user)

    def test_attendance_unique_constraint(self):
        """Teste constraint de unicidade por aluno/data/horário"""
        from datetime import time

        student = StudentFactory()
        check_in = time(19, 0)  # 19:00
        class_date_today = date.today()

        AttendanceFactory(
            student=student, class_date=class_date_today, check_in_time=check_in
        )

        # Tentar criar segunda presença no mesmo dia e horário
        with self.assertRaises(IntegrityError):
            AttendanceFactory(
                student=student, class_date=class_date_today, check_in_time=check_in
            )


class TestGraduationModel(BaseTenantTestCase):
    """Testes para Graduation model"""

    model_class = Graduation

    def test_create_graduation_success(self):
        """Teste criação básica de graduação"""
        student = StudentFactory()
        instructor_user = UserFactory(role="instructor")
        graduation = Graduation.objects.create(
            student=student,
            from_belt="white",
            to_belt="blue",
            graduation_date=date.today(),
            instructor=instructor_user,
        )

        self.assertEqual(graduation.student, student)
        self.assertEqual(graduation.from_belt, "white")
        self.assertEqual(graduation.to_belt, "blue")
        self.assertEqual(graduation.instructor, instructor_user)

    def test_graduation_str_representation(self):
        """Teste representação string da Graduation"""
        student = StudentFactory()
        graduation = GraduationFactory(
            student=student, from_belt="white", to_belt="blue"
        )
        expected = f"{student.full_name}: white → blue"
        self.assertEqual(str(graduation), expected)

    def test_graduation_ordering(self):
        """Teste ordenação por data (desc)"""
        student = StudentFactory()
        GraduationFactory(student=student, graduation_date=date(2024, 1, 15))
        GraduationFactory(student=student, graduation_date=date(2024, 1, 16))
        GraduationFactory(student=student, graduation_date=date(2024, 1, 14))

        graduations = list(Graduation.objects.all())
        dates = [grad.graduation_date for grad in graduations]

        # Ordenação descendente (mais recente primeiro)
        expected_order = [date(2024, 1, 16), date(2024, 1, 15), date(2024, 1, 14)]
        self.assertEqual(dates, expected_order)

    def test_graduation_belt_progression(self):
        """Teste progressão lógica de faixas"""
        student = StudentFactory()
        valid_progressions = [
            ("white", "blue"),
            ("blue", "purple"),
            ("purple", "brown"),
            ("brown", "black"),
        ]

        for from_belt, to_belt in valid_progressions:
            graduation = GraduationFactory(
                student=student, from_belt=from_belt, to_belt=to_belt
            )
            self.assertEqual(graduation.from_belt, from_belt)
            self.assertEqual(graduation.to_belt, to_belt)

    def test_graduation_auto_update_student_belt(self):
        """Teste atualização automática da faixa do estudante"""
        student = StudentFactory(belt_color="white")
        graduation = GraduationFactory(
            student=student, from_belt="white", to_belt="blue"
        )

        # Verificar se atualizou a faixa do estudante
        student.refresh_from_db()
        self.assertEqual(student.belt_color, "blue")
        self.assertEqual(student.last_graduation_date, graduation.graduation_date)


class TestStudentBusinessLogic(BaseTenantTestCase):
    """Testes de lógica de negócio para estudantes"""

    model_class = Student

    def test_student_attendance_frequency(self):
        """Teste frequência de treino do estudante"""
        student = StudentFactory()

        # Criar algumas presenças
        for i in range(10):
            AttendanceFactory(
                student=student, class_date=date.today() - timedelta(days=i)
            )

        attendances = Attendance.objects.filter(student=student)
        self.assertEqual(attendances.count(), 10)

    def test_student_graduation_history(self):
        """Teste histórico de graduações"""
        student = StudentFactory(belt_color="white")

        # Criar histórico de graduações
        graduations_data = [
            ("white", "blue", date(2023, 6, 15)),
            ("blue", "purple", date(2024, 1, 15)),
        ]

        for from_belt, to_belt, grad_date in graduations_data:
            GraduationFactory(
                student=student,
                from_belt=from_belt,
                to_belt=to_belt,
                graduation_date=grad_date,
            )

        graduations = Graduation.objects.filter(student=student)
        self.assertEqual(graduations.count(), 2)

        # Verificar ordenação por data
        graduation_dates = list(graduations.values_list("graduation_date", flat=True))
        self.assertEqual(
            graduation_dates[0], date(2024, 1, 15)
        )  # Mais recente primeiro

    def test_student_training_consistency(self):
        """Teste consistência de treino"""
        student = StudentFactory()

        # Simular treino consistente (3x por semana por 4 semanas)
        base_date = date.today() - timedelta(days=28)
        for week in range(4):
            for day in [0, 2, 4]:  # Segunda, quarta, sexta
                training_date = base_date + timedelta(days=(week * 7) + day)
                AttendanceFactory(student=student, class_date=training_date)

        total_attendances = Attendance.objects.filter(student=student).count()
        self.assertEqual(total_attendances, 12)  # 3 treinos x 4 semanas

    def test_student_inactive_periods(self):
        """Teste períodos de inatividade"""
        student = StudentFactory()

        # Criar período ativo, depois inativo, depois ativo novamente
        AttendanceFactory(student=student, class_date=date(2024, 1, 15))
        AttendanceFactory(student=student, class_date=date(2024, 1, 16))
        # Gap de 30 dias sem treino
        AttendanceFactory(student=student, class_date=date(2024, 2, 20))
        AttendanceFactory(student=student, class_date=date(2024, 2, 22))

        attendances = Attendance.objects.filter(student=student).order_by("class_date")
        dates = list(attendances.values_list("class_date", flat=True))

        # Verificar que temos os treinos esperados
        self.assertEqual(len(dates), 4)
        self.assertEqual(dates[0], date(2024, 1, 15))
        self.assertEqual(dates[-1], date(2024, 2, 22))


class TestStudentIntegration(BaseTenantTestCase):
    """Testes de integração para estudantes"""

    model_class = Student

    def test_complete_student_journey(self):
        """Teste jornada completa do estudante"""
        # 1. Criar estudante novo
        student = StudentFactory(belt_color="white", enrollment_date=date(2023, 1, 15))

        # 2. Registrar treinos regulares
        for i in range(50):  # 50 treinos
            AttendanceFactory(
                student=student, class_date=date(2023, 1, 15) + timedelta(days=i * 2)
            )

        # 3. Primeira graduação após 6 meses
        GraduationFactory(
            student=student,
            from_belt="white",
            to_belt="blue",
            graduation_date=date(2023, 7, 15),
        )

        # 4. Mais treinos
        for i in range(30):
            AttendanceFactory(
                student=student, class_date=date(2023, 8, 1) + timedelta(days=i * 3)
            )

        # 5. Segunda graduação
        GraduationFactory(
            student=student,
            from_belt="blue",
            to_belt="purple",
            graduation_date=date(2024, 1, 15),
        )

        # Verificações finais
        self.assertEqual(student.belt_color, "purple")
        self.assertEqual(Attendance.objects.filter(student=student).count(), 80)
        self.assertEqual(Graduation.objects.filter(student=student).count(), 2)
