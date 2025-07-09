"""
Factories para modelos de Students seguindo padrões brasileiros de jiu-jitsu.

Seguindo CONTEXT.md:
- Dados realistas brasileiros
- Naming conventions consistentes
- Factories completas para testes
"""

from datetime import date, timedelta

import factory
from factory import fuzzy
from faker import Faker

from apps.students.models import Attendance, Graduation, Student

from .authentication import StudentUserFactory

fake = Faker("pt_BR")  # Faker brasileiro


class StudentFactory(factory.django.DjangoModelFactory):
    """
    Factory para estudantes de jiu-jitsu brasileiros
    """

    class Meta:
        model = Student

    # Usuário associado
    user = factory.SubFactory(StudentUserFactory)

    # Matrícula sequencial brasileira - garantir unicidade sem get_or_create
    registration_number = factory.Sequence(lambda n: f"BJJ{n:06d}")

    # Data de matrícula (últimos 5 anos)
    enrollment_date = factory.LazyFunction(
        lambda: fake.date_between(start_date="-5y", end_date="today")
    )

    # Graduação inicial
    belt_color = "white"

    # Contato de emergência brasileiro
    emergency_contact_name = factory.LazyFunction(lambda: fake.name())
    emergency_contact_phone = factory.LazyFunction(lambda: fake.phone_number())
    emergency_contact_relationship = fuzzy.FuzzyChoice(
        [
            "Pai",
            "Mãe",
            "Esposa",
            "Esposo",
            "Irmão",
            "Irmã",
            "Filho",
            "Filha",
            "Tio",
            "Tia",
            "Primo",
            "Prima",
        ]
    )

    # Status ativo por padrão
    is_active = True


class AttendanceFactory(factory.django.DjangoModelFactory):
    """
    Factory para presenças em treinos
    """

    class Meta:
        model = Attendance

    # Estudante
    student = factory.SubFactory(StudentFactory)

    # Data do treino (últimos 30 dias) - usando nome correto do campo
    class_date = factory.LazyFunction(
        lambda: fake.date_between(start_date="-30d", end_date="today")
    )

    # Horários de entrada e saída
    check_in_time = factory.LazyFunction(lambda: fake.time_object(end_datetime=None))

    check_out_time = factory.LazyAttribute(
        lambda obj: None
        if fake.boolean(chance_of_getting_true=20)
        else fake.time_object(end_datetime=None)
    )

    # Tipo de aula brasileira
    class_type = fuzzy.FuzzyChoice(
        [
            "regular",  # Aula regular
            "competition",  # Treino de competição
            "fundamentals",  # Fundamentos
            "advanced",  # Avançado
            "open_mat",  # Treino livre
            "seminar",  # Seminário
        ]
    )

    # Observações opcionais
    notes = factory.LazyFunction(
        lambda: fake.sentence() if fake.boolean(chance_of_getting_true=30) else ""
    )


class GraduationFactory(factory.django.DjangoModelFactory):
    """
    Factory para graduações de faixas
    """

    class Meta:
        model = Graduation
        skip_postgeneration_save = True

    # Estudante
    student = factory.SubFactory(StudentFactory)

    # Progressão típica de faixas - usando nomes corretos dos campos
    from_belt = "white"
    to_belt = "blue"

    # Data de graduação (últimos 2 anos)
    graduation_date = factory.LazyFunction(
        lambda: fake.date_between(start_date="-2y", end_date="today")
    )

    # Observações do instrutor
    notes = factory.LazyFunction(lambda: fake.text(max_nb_chars=200))

    @factory.post_generation
    def update_student_belt(self, create, extracted, **kwargs):
        """Atualiza automaticamente a faixa do student após criar graduação"""
        if create:
            # Atualizar faixa do student para refletir a graduação
            self.student.belt_color = self.to_belt
            self.student.last_graduation_date = self.graduation_date
            self.student.save()


class StudentFactoryData:
    """
    Factories com dados específicos para cenários brasileiros
    """

    @classmethod
    def white_belt_beginner(cls):
        """Estudante iniciante faixa branca"""
        return StudentFactory(
            user=StudentUserFactory(
                first_name="João",
                last_name="Iniciante",
                email="joao.iniciante@test.com",
            ),
            enrollment_date=date.today() - timedelta(days=30),
            belt_color="white",
            emergency_contact_name="Maria Iniciante",
            emergency_contact_relationship="Mãe",
        )

    @classmethod
    def blue_belt_intermediate(cls):
        """Estudante intermediário faixa azul"""
        return StudentFactory(
            user=StudentUserFactory(
                first_name="Carlos", last_name="Azul", email="carlos.azul@test.com"
            ),
            enrollment_date=date.today() - timedelta(days=365 * 2),
            belt_color="blue",
            emergency_contact_name="Ana Azul",
            emergency_contact_relationship="Esposa",
        )

    @classmethod
    def purple_belt_advanced(cls):
        """Estudante avançado faixa roxa"""
        return StudentFactory(
            user=StudentUserFactory(
                first_name="Rafael", last_name="Roxo", email="rafael.roxo@test.com"
            ),
            enrollment_date=date.today() - timedelta(days=365 * 4),
            belt_color="purple",
            emergency_contact_name="Pedro Roxo",
            emergency_contact_relationship="Pai",
        )

    @classmethod
    def brown_belt_expert(cls):
        """Estudante especialista faixa marrom"""
        return StudentFactory(
            user=StudentUserFactory(
                first_name="Marcelo",
                last_name="Marrom",
                email="marcelo.marrom@test.com",
            ),
            enrollment_date=date.today() - timedelta(days=365 * 6),
            belt_color="brown",
            emergency_contact_name="Lucia Marrom",
            emergency_contact_relationship="Irmã",
        )

    @classmethod
    def black_belt_master(cls):
        """Mestre faixa preta"""
        return StudentFactory(
            user=StudentUserFactory(
                first_name="Professor",
                last_name="Preto",
                email="professor.preto@test.com",
                role="instructor",
            ),
            enrollment_date=date.today() - timedelta(days=365 * 10),
            belt_color="black",
            emergency_contact_name="Família Preto",
            emergency_contact_relationship="Família",
        )

    @classmethod
    def with_regular_attendance(cls, student=None):
        """Estudante com frequência regular (3x por semana)"""
        if not student:
            student = cls.white_belt_beginner()

        # Criar presenças dos últimos 30 dias (3x por semana)
        attendances = []
        today = date.today()

        for i in range(12):  # 12 treinos em 30 dias (3x semana)
            attendance_date = today - timedelta(days=int(i * 2.5))  # A cada 2.5 dias
            attendance = AttendanceFactory(
                student=student, class_date=attendance_date, class_type="regular"
            )
            attendances.append(attendance)

        return student, attendances

    @classmethod
    def with_graduation_history(cls, student=None):
        """Estudante com histórico de graduações"""
        if not student:
            student = cls.blue_belt_intermediate()

        # Graduação de branca para azul
        graduation = GraduationFactory(
            student=student,
            from_belt="white",
            to_belt="blue",
            graduation_date=date.today() - timedelta(days=365),
            notes="Excelente progresso, técnica sólida",
        )

        return student, graduation
