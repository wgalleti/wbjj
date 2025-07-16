from datetime import date, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.payments.models import Invoice, Payment, PaymentMethod
from apps.students.models import Attendance, Graduation, Student
from apps.tenants.models import Tenant

User = get_user_model()


class Command(BaseCommand):
    help = "Popula o banco de dados com dados de desenvolvimento"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Limpa dados existentes antes de criar novos",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write(self.style.WARNING("Limpando dados existentes..."))
            self.clear_data()

        self.stdout.write(self.style.SUCCESS("Criando dados de desenvolvimento..."))

        # Criar o tenant primeiro
        tenant = self.create_tenant()

        # Criar dados específicos do tenant
        payment_methods = self.create_payment_methods(tenant)
        users = self.create_users(tenant)
        students = self.create_students(users, tenant)
        self.create_graduations(students, tenant)
        self.create_attendances(students, tenant)
        invoices = self.create_invoices(students, tenant)
        self.create_payments(invoices, payment_methods, tenant)

        self.stdout.write(
            self.style.SUCCESS("✅ Dados de desenvolvimento criados com sucesso!")
        )

    def clear_data(self):
        """Remove todos os dados de desenvolvimento"""
        # Limpar dados do tenant específico
        tenant = Tenant.objects.filter(slug="zenith-jj").first()
        if tenant:
            Payment.objects.filter(tenant=tenant).delete()
            Invoice.objects.filter(tenant=tenant).delete()
            # Attendance e Graduation não têm tenant direto, filtrar por student
            Attendance.objects.filter(student__tenant=tenant).delete()
            Graduation.objects.filter(student__tenant=tenant).delete()
            Student.objects.filter(tenant=tenant).delete()
            User.objects.filter(tenant=tenant, is_superuser=False).delete()
            PaymentMethod.objects.filter(tenant=tenant).delete()

        # Limpar o tenant
        Tenant.objects.filter(slug="zenith-jj").delete()

    def create_tenant(self):
        """Cria academia de exemplo"""
        tenant, created = Tenant.objects.get_or_create(
            slug="zenith-jj",
            defaults={
                "subdomain": "zenith-jj",
                "name": "Zenith Jiu Jitsu",
                "email": "contato@zenith-jj.com.br",
                "phone": "+5511999887766",
                "address": "Rua das Academias, 123",
                "city": "São Paulo",
                "state": "SP",
                "zip_code": "01234-567",
                "monthly_fee": Decimal("250.00"),
                "website": "https://zenith-jj.com.br",
                "founded_date": date(2015, 8, 10),
                "is_active": True,
            },
        )
        if created:
            self.stdout.write(f"  ✓ Academia criada: {tenant.name}")
        return tenant

    def create_payment_methods(self, tenant):
        """Cria métodos de pagamento"""
        methods_data = [
            {
                "name": "PIX",
                "code": "pix",
                "is_online": True,
                "processing_fee": Decimal("0.0000"),
            },
            {
                "name": "Cartão de Crédito",
                "code": "credit_card",
                "is_online": True,
                "processing_fee": Decimal("0.0349"),
            },
            {
                "name": "Boleto",
                "code": "boleto",
                "is_online": True,
                "processing_fee": Decimal("0.0199"),
            },
            {
                "name": "Dinheiro",
                "code": "cash",
                "is_online": False,
                "processing_fee": Decimal("0.0000"),
            },
        ]

        methods = []
        for method_data in methods_data:
            method, created = PaymentMethod.objects.get_or_create(
                tenant=tenant,
                code=method_data["code"],
                defaults={**method_data, "tenant": tenant},
            )
            methods.append(method)
            if created:
                self.stdout.write(f"  ✓ Método de pagamento: {method.name}")

        return methods

    def create_users(self, tenant):
        """Cria usuários de exemplo"""
        users_data = [
            {
                "email": "admin@wbjj.com",
                "first_name": "Admin",
                "last_name": "Sistema",
                "role": "admin",
                "is_staff": True,
                "is_superuser": True,
            },
            {
                "email": "professor@zenith-jj.com.br",
                "first_name": "Rafael",
                "last_name": "Santos",
                "role": "instructor",
                "phone": "+5511987654321",
                "birth_date": date(1985, 8, 20),
            },
            {
                "email": "joao.silva@email.com",
                "first_name": "João",
                "last_name": "Silva",
                "role": "student",
                "phone": "+5511912345678",
                "birth_date": date(1990, 5, 15),
            },
            {
                "email": "maria.santos@email.com",
                "first_name": "Maria",
                "last_name": "Santos",
                "role": "student",
                "phone": "+5511923456789",
                "birth_date": date(1995, 12, 3),
            },
            {
                "email": "pedro.oliveira@email.com",
                "first_name": "Pedro",
                "last_name": "Oliveira",
                "role": "student",
                "phone": "+5511934567890",
                "birth_date": date(1988, 7, 22),
            },
        ]

        users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                tenant=tenant,
                email=user_data["email"],
                defaults={
                    **user_data,
                    "tenant": tenant,
                    "password": "pbkdf2_sha256$600000$dummy$hash",
                },
            )
            if created:
                user.set_password("123456")  # Senha padrão para desenvolvimento
                user.save()
                self.stdout.write(f"  ✓ Usuário criado: {user.full_name} ({user.role})")
            users.append(user)

        return users

    def create_students(self, users, tenant):
        """Cria perfis de estudantes"""
        student_users = [u for u in users if u.role == "student"]
        students = []

        students_data = [
            {
                "registration_number": "ZJ-001",
                "belt_color": "blue",
                "belt_stripes": 2,
                "emergency_contact_name": "Ana Silva",
                "emergency_contact_phone": "+5511988776655",
                "emergency_contact_relationship": "Esposa",
                "enrollment_date": date(2023, 1, 15),
            },
            {
                "registration_number": "ZJ-002",
                "belt_color": "white",
                "belt_stripes": 3,
                "emergency_contact_name": "José Santos",
                "emergency_contact_phone": "+5511977665544",
                "emergency_contact_relationship": "Pai",
                "enrollment_date": date(2023, 6, 10),
            },
            {
                "registration_number": "ZJ-003",
                "belt_color": "purple",
                "belt_stripes": 0,
                "emergency_contact_name": "Carla Oliveira",
                "emergency_contact_phone": "+5511966554433",
                "emergency_contact_relationship": "Mãe",
                "enrollment_date": date(2022, 3, 5),
            },
        ]

        for i, student_data in enumerate(students_data):
            if i < len(student_users):
                student, created = Student.objects.get_or_create(
                    tenant=tenant,
                    user=student_users[i],
                    defaults={**student_data, "tenant": tenant},
                )
                students.append(student)
                if created:
                    self.stdout.write(
                        f"  ✓ Aluno criado: {student.full_name} - {student.get_belt_color_display()}"
                    )

        return students

    def create_graduations(self, students, tenant):
        """Cria histórico de graduações"""
        # Graduação do Pedro (purple belt)
        if len(students) >= 3:
            pedro = students[2]  # Purple belt
            graduations = [
                {
                    "student": pedro,
                    "from_belt": "white",
                    "to_belt": "blue",
                    "graduation_date": date(2021, 3, 20),
                    "notes": "Primeira graduação - demonstrou técnicas básicas",
                },
                {
                    "student": pedro,
                    "from_belt": "blue",
                    "to_belt": "purple",
                    "graduation_date": date(2022, 9, 15),
                    "notes": "Evolução excelente - leadership qualities",
                },
            ]

            for grad_data in graduations:
                grad, created = Graduation.objects.get_or_create(
                    student=grad_data["student"],
                    graduation_date=grad_data["graduation_date"],
                    defaults=grad_data,
                )
                if created:
                    self.stdout.write(
                        f"  ✓ Graduação: {grad.student.full_name} {grad.from_belt} → {grad.to_belt}"
                    )

    def create_attendances(self, students, tenant):
        """Cria registros de presença"""
        # Últimas 2 semanas de aulas
        today = timezone.now().date()
        class_days = []

        # Gerar dias de aula (Segunda, Quarta, Sexta)
        for i in range(14):
            day = today - timedelta(days=i)
            if day.weekday() in [0, 2, 4]:  # Segunda, Quarta, Sexta
                class_days.append(day)

        for student in students[:2]:  # Primeiros 2 alunos
            for class_day in class_days[:10]:  # 10 presenças
                attendance, created = Attendance.objects.get_or_create(
                    student=student,
                    class_date=class_day,
                    check_in_time=time(19, 0),
                    defaults={
                        "check_out_time": time(20, 30),
                        "class_type": "gi",
                    },
                )
                if created:
                    self.stdout.write(
                        f"  ✓ Presença: {student.full_name} - {class_day}"
                    )

    def create_invoices(self, students, tenant):
        """Cria faturas mensais"""
        invoices = []
        today = timezone.now().date()

        # Criar faturas dos últimos 3 meses
        for i in range(3):
            month_date = date(today.year, today.month - i, 1)
            if month_date.month <= 0:
                month_date = month_date.replace(
                    year=month_date.year - 1, month=12 + month_date.month
                )

            due_date = month_date.replace(day=10)

            for student in students:
                invoice, created = Invoice.objects.get_or_create(
                    tenant=tenant,
                    student=student,
                    reference_month=month_date,
                    defaults={
                        "tenant": tenant,
                        "due_date": due_date,
                        "amount": Decimal("250.00"),
                        "status": "paid" if i > 0 else "pending",  # Mês atual pendente
                    },
                )
                invoices.append(invoice)
                if created:
                    self.stdout.write(
                        f"  ✓ Fatura: {student.full_name} - {month_date.strftime('%m/%Y')}"
                    )

        return invoices

    def create_payments(self, invoices, payment_methods, tenant):
        """Cria pagamentos para faturas pagas"""
        pix_method = next(
            (pm for pm in payment_methods if pm.code == "pix"), payment_methods[0]
        )

        paid_invoices = [inv for inv in invoices if inv.status == "paid"]

        for invoice in paid_invoices:
            payment, created = Payment.objects.get_or_create(
                tenant=tenant,
                invoice=invoice,
                defaults={
                    "tenant": tenant,
                    "payment_method": pix_method,
                    "amount": invoice.amount,
                    "payment_date": timezone.now() - timedelta(days=5),
                    "status": "confirmed",
                    "confirmed_date": timezone.now() - timedelta(days=4),
                },
            )
            if created:
                self.stdout.write(
                    f"  ✓ Pagamento: {invoice.student.full_name} - R$ {payment.amount}"
                )

        self.stdout.write(self.style.SUCCESS("\n📊 Resumo dos dados criados:"))
        self.stdout.write(f"   - Academias: {Tenant.objects.count()}")
        self.stdout.write(
            f"   - Usuários: {User.objects.filter(tenant=tenant).count()}"
        )
        self.stdout.write(
            f"   - Alunos: {Student.objects.filter(tenant=tenant).count()}"
        )
        self.stdout.write(
            f"   - Graduações: {Graduation.objects.filter(student__tenant=tenant).count()}"
        )
        self.stdout.write(
            f"   - Presenças: {Attendance.objects.filter(student__tenant=tenant).count()}"
        )
        self.stdout.write(
            f"   - Faturas: {Invoice.objects.filter(tenant=tenant).count()}"
        )
        self.stdout.write(
            f"   - Pagamentos: {Payment.objects.filter(tenant=tenant).count()}"
        )
        self.stdout.write(
            f"   - Métodos Pagamento: {PaymentMethod.objects.filter(tenant=tenant).count()}"
        )
