from decimal import Decimal
from typing import ClassVar

from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import BaseModel
from apps.students.models import Student


class PaymentMethod(BaseModel):
    """
    Métodos de pagamento disponíveis
    """

    name = models.CharField(
        max_length=100, help_text="Nome do método (ex: PIX, Cartão)"
    )
    code = models.CharField(max_length=20, unique=True, help_text="Código único")
    is_online = models.BooleanField(default=False, help_text="É pagamento online?")
    processing_fee = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=0,
        help_text="Taxa de processamento (ex: 0.0349 = 3.49%)",
    )

    class Meta:
        db_table = "payment_methods"
        ordering: ClassVar = ["name"]

    def __str__(self):
        return self.name


class Invoice(BaseModel):
    """
    Faturas mensais dos alunos
    """

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="invoices"
    )

    # Período da fatura
    due_date = models.DateField(help_text="Data de vencimento")
    reference_month = models.DateField(help_text="Mês de referência (YYYY-MM-01)")

    # Valores
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Status
    STATUS_CHOICES: ClassVar = [
        ("pending", "Pendente"),
        ("paid", "Pago"),
        ("overdue", "Vencido"),
        ("cancelled", "Cancelado"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # Observações
    description = models.TextField(
        default="Mensalidade", help_text="Descrição da fatura"
    )
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "invoices"
        ordering: ClassVar = ["-due_date"]
        unique_together: ClassVar = ["student", "reference_month"]
        indexes: ClassVar = [
            models.Index(fields=["student", "status"]),
            models.Index(fields=["due_date", "status"]),
            models.Index(fields=["reference_month"]),
        ]

    def __str__(self):
        return f"{self.student.full_name} - {self.reference_month.strftime('%m/%Y')}"

    @property
    def total_amount(self):
        """Valor total com desconto e multa"""
        return self.amount - self.discount + self.late_fee

    @property
    def is_overdue(self):
        """Verifica se está vencida"""
        from django.utils import timezone

        return self.due_date < timezone.now().date() and self.status == "pending"


class Payment(BaseModel):
    """
    Registros de pagamentos realizados
    """

    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="payments"
    )

    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)

    # Valores
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Datas
    payment_date = models.DateTimeField(help_text="Data/hora do pagamento")
    confirmed_date = models.DateTimeField(
        blank=True, null=True, help_text="Data/hora da confirmação"
    )

    # Status e referências externas
    STATUS_CHOICES: ClassVar = [
        ("pending", "Pendente"),
        ("confirmed", "Confirmado"),
        ("failed", "Falhou"),
        ("refunded", "Estornado"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    external_id = models.CharField(
        max_length=255, blank=True, help_text="ID da transação no gateway de pagamento"
    )

    notes = models.TextField(blank=True)

    class Meta:
        db_table = "payments"
        ordering: ClassVar = ["-payment_date"]
        indexes: ClassVar = [
            models.Index(fields=["invoice", "status"]),
            models.Index(fields=["payment_date"]),
            models.Index(fields=["external_id"]),
        ]

    def __str__(self):
        return f"Pagamento {self.amount} - {self.invoice.student.full_name}"

    def confirm_payment(self):
        """Confirma o pagamento e atualiza a fatura"""
        from django.utils import timezone

        self.status = "confirmed"
        self.confirmed_date = timezone.now()
        self.save()

        # Atualizar status da fatura se valor total foi pago
        total_paid = self.invoice.payments.filter(status="confirmed").aggregate(
            total=models.Sum("amount")
        )["total"] or Decimal("0")

        if total_paid >= self.invoice.total_amount:
            self.invoice.status = "paid"
            self.invoice.save()
