"""
Factories para testes seguindo padrões brasileiros de academias de jiu-jitsu
"""

# Tenants
# Authentication
from .authentication import (
    AdminUserFactory,
    InstructorUserFactory,
    StaffUserFactory,
    StudentUserFactory,
    UserFactory,
    UserFactoryData,
)

# Payments
from .payments import (
    InvoiceFactory,
    PaymentMethodFactory,
    create_boleto_method,
    create_cash_method,
    create_credit_card_method,
    create_pix_payment_method,
)

# Students
from .students import AttendanceFactory, GraduationFactory, StudentFactory
from .tenants import TenantFactory

__all__ = [
    # Tenants
    "TenantFactory",
    # Authentication
    "UserFactory",
    "StudentUserFactory",
    "InstructorUserFactory",
    "AdminUserFactory",
    "StaffUserFactory",
    "UserFactoryData",
    # Students
    "StudentFactory",
    "AttendanceFactory",
    "GraduationFactory",
    # Payments
    "PaymentMethodFactory",
    "InvoiceFactory",
    "create_pix_payment_method",
    "create_credit_card_method",
    "create_boleto_method",
    "create_cash_method",
]
