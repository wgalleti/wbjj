"""
Testes para models de Payments
Cobertura completa dos models PaymentMethod e Invoice
"""

from datetime import date, timedelta
from decimal import Decimal

from django.db import IntegrityError
from django.utils import timezone

from apps.payments.models import Invoice, PaymentMethod
from tests.base import BaseTenantTestCase
from tests.with_db.factories.payments import (
    InvoiceFactory,
    PaymentMethodFactory,
    create_credit_card_method,
    create_pix_payment_method,
)
from tests.with_db.factories.students import StudentFactory


class TestPaymentMethodModel(BaseTenantTestCase):
    """Testes para PaymentMethod model"""

    def test_create_payment_method_success(self):
        """Teste criação básica de método de pagamento"""
        payment_method = PaymentMethod.objects.create(
            name="PIX", code="pix", is_online=True, processing_fee=Decimal("0.00")
        )

        self.assertEqual(payment_method.name, "PIX")
        self.assertEqual(payment_method.code, "pix")
        self.assertTrue(payment_method.is_online)
        self.assertEqual(payment_method.processing_fee, Decimal("0.00"))
        self.assertTrue(payment_method.is_active)  # default

    def test_payment_method_str_representation(self):
        """Teste representação string do PaymentMethod"""
        payment_method = PaymentMethodFactory(name="PIX")
        self.assertEqual(str(payment_method), "PIX")

    def test_payment_method_unique_code(self):
        """Teste unicidade do código"""
        PaymentMethodFactory(code="pix")

        with self.assertRaises(IntegrityError):
            PaymentMethodFactory(code="pix")

    def test_payment_method_ordering(self):
        """Teste ordenação por nome"""
        PaymentMethodFactory(name="Cartão", code="card")
        PaymentMethodFactory(name="Boleto", code="boleto")
        PaymentMethodFactory(name="PIX", code="pix")

        methods = PaymentMethod.objects.all()
        names = [method.name for method in methods]

        self.assertEqual(names, ["Boleto", "Cartão", "PIX"])

    def test_payment_method_is_active_default(self):
        """Teste valor padrão de is_active"""
        payment_method = PaymentMethodFactory()
        self.assertTrue(payment_method.is_active)

    def test_payment_method_processing_fee_precision(self):
        """Teste precisão do campo processing_fee"""
        payment_method = PaymentMethodFactory(processing_fee=Decimal("0.0349"))  # 3.49%

        self.assertEqual(payment_method.processing_fee, Decimal("0.0349"))

    def test_payment_method_deactivation(self):
        """Teste desativação de método de pagamento"""
        payment_method = PaymentMethodFactory()

        payment_method.is_active = False
        payment_method.save()

        self.assertFalse(payment_method.is_active)

    def test_brazilian_payment_methods(self):
        """Teste métodos de pagamento brasileiros específicos"""
        # PIX
        pix = create_pix_payment_method()
        self.assertEqual(pix.name, "PIX")
        self.assertEqual(pix.code, "pix")
        self.assertTrue(pix.is_online)
        self.assertEqual(pix.processing_fee, Decimal("0.0000"))

        # Cartão de crédito
        card = create_credit_card_method()
        self.assertEqual(card.name, "Cartão de Crédito")
        self.assertEqual(card.code, "cartao_de_credito")
        self.assertTrue(card.is_online)
        self.assertEqual(card.processing_fee, Decimal("0.0290"))


class TestInvoiceModel(BaseTenantTestCase):
    """Testes para Invoice model"""

    def test_create_invoice_success(self):
        """Teste criação básica de fatura"""
        student = StudentFactory()
        invoice = Invoice.objects.create(
            student=student,
            due_date=date.today() + timedelta(days=30),
            reference_month=date.today().replace(day=1),
            amount=Decimal("200.00"),
            status="pending",
            description="Mensalidade",
        )

        self.assertEqual(invoice.student, student)
        self.assertEqual(invoice.amount, Decimal("200.00"))
        self.assertEqual(invoice.status, "pending")
        self.assertEqual(invoice.description, "Mensalidade")

    def test_invoice_str_representation(self):
        """Teste representação string da Invoice"""
        student = StudentFactory()
        invoice = InvoiceFactory(student=student, reference_month=date(2024, 1, 1))
        expected = f"{student.user.full_name} - 01/2024"
        self.assertEqual(str(invoice), expected)

    def test_invoice_ordering(self):
        """Teste ordenação por data de vencimento (desc)"""
        student = StudentFactory()
        invoice1 = InvoiceFactory(student=student, due_date=date(2024, 1, 15))
        invoice2 = InvoiceFactory(student=student, due_date=date(2024, 2, 15))

        invoices = list(Invoice.objects.all())
        self.assertEqual(invoices[0], invoice2)  # mais recente primeiro
        self.assertEqual(invoices[1], invoice1)

    def test_invoice_status_choices(self):
        """Teste choices válidos de status"""
        student = StudentFactory()
        valid_statuses = ["pending", "paid", "overdue", "cancelled"]

        for status in valid_statuses:
            invoice = InvoiceFactory(student=student, status=status)
            self.assertEqual(invoice.status, status)

    def test_invoice_amount_precision(self):
        """Teste precisão do campo amount"""
        student = StudentFactory()
        invoice = InvoiceFactory(student=student, amount=Decimal("199.99"))

        self.assertEqual(invoice.amount, Decimal("199.99"))

    def test_invoice_payment_processing(self):
        """Teste processamento de pagamento"""
        student = StudentFactory()
        invoice = InvoiceFactory(
            student=student,
            amount=Decimal("200.00"),
            discount=Decimal("20.00"),
            late_fee=Decimal("10.00"),
        )

        # Testa propriedade total_amount
        self.assertEqual(invoice.total_amount, Decimal("190.00"))  # 200 - 20 + 10

    def test_invoice_overdue_detection(self):
        """Teste detecção de fatura vencida"""
        student = StudentFactory()
        # Fatura vencida
        overdue_invoice = InvoiceFactory(
            student=student, due_date=date.today() - timedelta(days=5), status="pending"
        )

        # Fatura em dia
        current_invoice = InvoiceFactory(
            student=student, due_date=date.today() + timedelta(days=5), status="pending"
        )

        # Verificar propriedades
        self.assertTrue(overdue_invoice.due_date < date.today())
        self.assertTrue(current_invoice.due_date > date.today())

    def test_invoice_future_due_date(self):
        """Teste validação de data de vencimento futura"""
        student = StudentFactory()
        future_date = date.today() + timedelta(days=30)
        invoice = InvoiceFactory(student=student, due_date=future_date)

        self.assertEqual(invoice.due_date, future_date)

    def test_invoice_cancellation(self):
        """Teste cancelamento de fatura"""
        student = StudentFactory()
        invoice = InvoiceFactory(student=student, status="pending")

        invoice.status = "cancelled"
        invoice.save()

        self.assertEqual(invoice.status, "cancelled")

    def test_invoice_with_processing_fee(self):
        """Teste fatura com taxa de processamento via Payment"""
        student = StudentFactory()
        payment_method = PaymentMethodFactory(processing_fee=Decimal("0.0290"))  # 2.90%
        invoice = InvoiceFactory(student=student, amount=Decimal("200.00"))

        # Criar pagamento associado à fatura
        from apps.payments.models import Payment

        payment = Payment.objects.create(
            invoice=invoice,
            payment_method=payment_method,
            amount=Decimal("200.00"),
            processing_fee=Decimal("200.00") * Decimal("0.0290"),
            payment_date=timezone.now(),
        )

        # Verificar taxa de processamento
        self.assertEqual(payment.payment_method.processing_fee, Decimal("0.0290"))
        self.assertEqual(payment.processing_fee, Decimal("5.80"))


class TestPaymentBusinessLogic(BaseTenantTestCase):
    """Testes para lógica de negócio de pagamentos"""

    def test_monthly_invoice_generation(self):
        """Teste geração mensal de faturas"""
        student = StudentFactory()

        # Simular geração de faturas para 3 meses
        months = [
            date(2024, 1, 1),
            date(2024, 2, 1),
            date(2024, 3, 1),
        ]

        for ref_month in months:
            InvoiceFactory(
                student=student, reference_month=ref_month, amount=Decimal("200.00")
            )

        invoices = Invoice.objects.filter(student=student)
        self.assertEqual(invoices.count(), 3)

        # Verificar valores consistentes
        for invoice in invoices:
            self.assertEqual(invoice.amount, Decimal("200.00"))

    def test_payment_method_usage_statistics(self):
        """Teste estatísticas de uso de métodos de pagamento via Payment"""
        student = StudentFactory()

        # Criar métodos de pagamento
        pix = create_pix_payment_method()
        card = create_credit_card_method()

        # Criar faturas
        invoice1 = InvoiceFactory(student=student, status="paid")
        invoice2 = InvoiceFactory(student=student, status="paid")
        invoice3 = InvoiceFactory(student=student, status="paid")

        # Criar pagamentos com diferentes métodos
        from apps.payments.models import Payment

        Payment.objects.create(
            invoice=invoice1,
            payment_method=pix,
            amount=invoice1.amount,
            payment_date=timezone.now(),
        )
        Payment.objects.create(
            invoice=invoice2,
            payment_method=pix,
            amount=invoice2.amount,
            payment_date=timezone.now(),
        )
        Payment.objects.create(
            invoice=invoice3,
            payment_method=card,
            amount=invoice3.amount,
            payment_date=timezone.now(),
        )

        # Verificar distribuição
        pix_payments = Payment.objects.filter(payment_method=pix).count()
        card_payments = Payment.objects.filter(payment_method=card).count()

        self.assertEqual(pix_payments, 2)
        self.assertEqual(card_payments, 1)

    def test_student_payment_history(self):
        """Teste histórico de pagamentos do estudante"""
        student = StudentFactory()

        # Criar histórico de 6 meses
        for month in range(1, 7):
            InvoiceFactory(
                student=student,
                reference_month=date(2024, month, 1),
                amount=Decimal("200.00"),
                status="paid" if month < 6 else "pending",
            )

        # Verificar histórico
        all_invoices = Invoice.objects.filter(student=student)
        paid_invoices = Invoice.objects.filter(student=student, status="paid")
        pending_invoices = Invoice.objects.filter(student=student, status="pending")

        self.assertEqual(all_invoices.count(), 6)
        self.assertEqual(paid_invoices.count(), 5)
        self.assertEqual(pending_invoices.count(), 1)

    def test_brazilian_payment_preferences(self):
        """Teste preferências de pagamento brasileiras via Payment"""
        student = StudentFactory()

        # Criar métodos típicos brasileiros
        pix = create_pix_payment_method()
        boleto = PaymentMethodFactory(
            name="Boleto", code="boleto", processing_fee=Decimal("0.0150")
        )
        cartao = create_credit_card_method()

        from apps.payments.models import Payment

        # Simular uso típico brasileiro (PIX sendo mais usado)
        for _ in range(5):
            invoice = InvoiceFactory(student=student)
            Payment.objects.create(
                invoice=invoice,
                payment_method=pix,
                amount=invoice.amount,
                payment_date=timezone.now(),
            )

        for _ in range(2):
            invoice = InvoiceFactory(student=student)
            Payment.objects.create(
                invoice=invoice,
                payment_method=boleto,
                amount=invoice.amount,
                payment_date=timezone.now(),
            )

        for _ in range(1):
            invoice = InvoiceFactory(student=student)
            Payment.objects.create(
                invoice=invoice,
                payment_method=cartao,
                amount=invoice.amount,
                payment_date=timezone.now(),
            )

        # Verificar distribuição
        pix_count = Payment.objects.filter(payment_method=pix).count()
        boleto_count = Payment.objects.filter(payment_method=boleto).count()
        cartao_count = Payment.objects.filter(payment_method=cartao).count()

        self.assertEqual(pix_count, 5)
        self.assertEqual(boleto_count, 2)
        self.assertEqual(cartao_count, 1)

    def test_invoice_status_transitions(self):
        """Teste transições de status da fatura"""
        student = StudentFactory()
        invoice = InvoiceFactory(student=student, status="pending")

        # Pendente -> Pago
        invoice.status = "paid"
        invoice.save()
        self.assertEqual(invoice.status, "paid")

        # Criar nova fatura para teste de vencimento
        overdue_invoice = InvoiceFactory(
            student=student, status="pending", due_date=date.today() - timedelta(days=5)
        )

        # Simular processo de vencimento
        overdue_invoice.status = "overdue"
        overdue_invoice.save()
        self.assertEqual(overdue_invoice.status, "overdue")


class TestPaymentIntegration(BaseTenantTestCase):
    """Testes de integração para pagamentos"""

    def test_complete_payment_flow(self):
        """Teste fluxo completo de pagamento"""
        # 1. Criar estudante
        student = StudentFactory()

        # 2. Criar método de pagamento
        pix = create_pix_payment_method()

        # 3. Gerar fatura
        invoice = InvoiceFactory(
            student=student, amount=Decimal("200.00"), status="pending"
        )

        # 4. Criar e processar pagamento
        from apps.payments.models import Payment

        payment = Payment.objects.create(
            invoice=invoice,
            payment_method=pix,
            amount=Decimal("200.00"),
            payment_date=timezone.now(),
        )

        # 5. Confirmar pagamento
        payment.confirm_payment()

        # 6. Verificar resultado final
        payment.refresh_from_db()
        invoice.refresh_from_db()

        self.assertEqual(payment.status, "confirmed")
        self.assertEqual(invoice.status, "paid")
        self.assertEqual(payment.amount, Decimal("200.00"))

    def test_multi_student_payment_scenario(self):
        """Teste cenário com múltiplos estudantes"""
        # Criar múltiplos estudantes
        students = [StudentFactory() for _ in range(3)]

        # Gerar faturas para todos
        for student in students:
            InvoiceFactory(
                student=student,
                amount=Decimal("200.00"),
                reference_month=date(2024, 1, 1),
            )

        # Verificar isolamento
        for student in students:
            student_invoices = Invoice.objects.filter(student=student)
            self.assertEqual(student_invoices.count(), 1)

        # Verificar total
        all_invoices = Invoice.objects.all()
        self.assertEqual(all_invoices.count(), 3)
