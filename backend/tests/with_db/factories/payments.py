"""
Factories para modelos de Payment
Dados brasileiros realistas para academias de jiu-jitsu
"""

from datetime import date, timedelta
from decimal import Decimal

import factory

from apps.payments.models import Invoice, PaymentMethod


class PaymentMethodFactory(factory.django.DjangoModelFactory):
    """Factory para PaymentMethod - métodos de pagamento brasileiros"""

    class Meta:
        model = PaymentMethod

    name = factory.Iterator(
        [
            "PIX",
            "Cartão de Crédito",
            "Boleto Bancário",
            "Débito",
            "Dinheiro",
            "Transferência",
        ]
    )

    code = factory.LazyAttribute(lambda obj: obj.name.lower().replace(" ", "_"))

    is_online = factory.LazyAttribute(
        lambda obj: obj.code in ["pix", "cartao_de_credito", "transferencia"]
    )

    processing_fee = factory.LazyAttribute(
        lambda obj: {
            "pix": Decimal("0.0000"),  # PIX gratuito
            "cartao_de_credito": Decimal("0.0290"),  # 2.90%
            "boleto_bancario": Decimal("0.0150"),  # R$1.50 fixo convertido para %
            "debito": Decimal("0.0199"),  # 1.99%
            "dinheiro": Decimal("0.0000"),  # Sem taxa
            "transferencia": Decimal("0.0000"),  # Sem taxa
        }.get(obj.code, Decimal("0.0000"))
    )


class InvoiceFactory(factory.django.DjangoModelFactory):
    """Factory para Invoice - faturas de mensalidade"""

    class Meta:
        model = Invoice

    # Relacionamento com student será definido no teste
    student = factory.SubFactory("tests.with_db.factories.students.StudentFactory")

    # Datas - gerar reference_month variável para evitar duplicates
    due_date = factory.LazyFunction(lambda: date.today() + timedelta(days=10))
    reference_month = factory.Sequence(
        lambda n: (date.today().replace(day=1) - timedelta(days=30 * n))
    )

    # Valores típicos brasileiros
    amount = factory.Iterator(
        [
            Decimal("120.00"),  # Básico
            Decimal("150.00"),  # Intermediário
            Decimal("200.00"),  # Premium
            Decimal("250.00"),  # VIP
            Decimal("300.00"),  # Master
            Decimal("350.00"),  # Black Belt
        ]
    )

    discount = Decimal("0.00")
    late_fee = Decimal("0.00")

    status = "pending"
    description = "Mensalidade"
    notes = ""


# Métodos de conveniência para criar dados específicos
def create_pix_payment_method():
    """Cria método PIX (gratuito)"""
    return PaymentMethodFactory(
        name="PIX", code="pix", is_online=True, processing_fee=Decimal("0.0000")
    )


def create_credit_card_method():
    """Cria método cartão de crédito (2.90%)"""
    return PaymentMethodFactory(
        name="Cartão de Crédito",
        code="cartao_de_credito",
        is_online=True,
        processing_fee=Decimal("0.0290"),
    )


def create_boleto_method():
    """Cria método boleto bancário (1.50%)"""
    return PaymentMethodFactory(
        name="Boleto Bancário",
        code="boleto_bancario",
        is_online=True,
        processing_fee=Decimal("0.0150"),
    )


def create_cash_method():
    """Cria método dinheiro (sem taxa)"""
    return PaymentMethodFactory(
        name="Dinheiro",
        code="dinheiro",
        is_online=False,
        processing_fee=Decimal("0.0000"),
    )
