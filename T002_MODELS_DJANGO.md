# T002 - Models Django e Migrations

## 🎯 Objetivo
Implementar T002 conforme especificação atualizada:
- Criar models Django para entidades principais
- Definir relacionamentos e constraints  
- Gerar migrations Django automaticamente
- Implementar Abstract Base Models para auditoria
- Configurar Django Admin básico

## 📁 Estrutura de Apps Django

```bash
apps/
├── core/           # Abstract models, utilities
├── tenants/        # Tenant model (futuro multitenancy)  
├── authentication/ # User personalizado
├── students/       # Student, Graduation models
├── payments/       # Payment, Invoice models
```

---

## 🏗️ IMPLEMENTAÇÃO DOS MODELS

### 1. Core - Abstract Base Models

```bash
# Dentro de backend/ com ambiente ativado
cd backend
source .venv/bin/activate

# Criar models core
cat > apps/core/models.py << 'EOF'
import uuid
from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
    """
    Abstract base model para auditoria temporal
    Adiciona created_at, updated_at automaticamente
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Abstract base model para soft delete
    Adiciona is_active field
    """
    is_active = models.BooleanField(default=True, help_text="Indica se o registro está ativo")
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False):
        """Soft delete - marca como inativo ao invés de deletar"""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(using=using)
    
    def hard_delete(self, using=None, keep_parents=False):
        """Delete real do banco de dados"""
        super().delete(using=using, keep_parents=keep_parents)


class BaseModel(TimestampedModel, SoftDeleteModel):
    """
    Model base completo com timestamp + soft delete
    Herdar de BaseModel em todos os models principais
    """
    
    class Meta:
        abstract = True


class ActiveManager(models.Manager):
    """Manager que retorna apenas registros ativos"""
    
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
EOF
```

### 2. Tenants - Model de Academia (preparação multitenancy)

```bash
cat > apps/tenants/models.py << 'EOF'
from django.db import models
from django.core.validators import RegexValidator
from apps.core.models import BaseModel


class Tenant(BaseModel):
    """
    Model principal para multitenancy
    Representa uma academia/franquia
    """
    
    # Identificação
    name = models.CharField(max_length=255, help_text="Nome da academia")
    slug = models.SlugField(
        max_length=100, 
        unique=True, 
        help_text="Slug único para subdomínio (ex: gracie-barra)"
    )
    
    # Contato
    email = models.EmailField(help_text="Email principal da academia")
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        help_text="Telefone da academia"
    )
    
    # Endereço
    address = models.TextField(help_text="Endereço completo")
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50, default='Brasil')
    
    # Configurações visuais
    logo = models.ImageField(upload_to='tenant_logos/', blank=True, null=True)
    primary_color = models.CharField(
        max_length=7, 
        default='#3B82F6',
        validators=[RegexValidator(r'^#[0-9A-Fa-f]{6}$')],
        help_text="Cor primária em hex (ex: #3B82F6)"
    )
    secondary_color = models.CharField(
        max_length=7, 
        default='#1E40AF',
        validators=[RegexValidator(r'^#[0-9A-Fa-f]{6}$')],
        help_text="Cor secundária em hex"
    )
    
    # Configurações de negócio
    monthly_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Mensalidade padrão"
    )
    timezone = models.CharField(
        max_length=50, 
        default='America/Sao_Paulo',
        help_text="Timezone da academia"
    )
    
    # Metadata
    founded_date = models.DateField(blank=True, null=True)
    website = models.URLField(blank=True)
    
    class Meta:
        db_table = 'tenants'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def subdomain_url(self):
        """Retorna URL do subdomínio"""
        return f"https://{self.slug}.wbjj.com"
EOF
```

### 3. Authentication - User Personalizado

```bash
cat > apps/authentication/models.py << 'EOF'
from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.core.models import TimestampedModel
# from apps.tenants.models import Tenant  # Uncomment quando implementar multitenancy


class User(AbstractUser, TimestampedModel):
    """
    User personalizado baseado em AbstractUser
    Adiciona campos específicos do wBJJ
    """
    
    # Remove username, usar email como identificador
    username = None
    email = models.EmailField(unique=True, help_text="Email do usuário")
    
    # Campos pessoais
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    
    # Campos profissionais
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('instructor', 'Instrutor'),
        ('manager', 'Gerente'),
        ('student', 'Aluno'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    
    # Relacionamento com tenant (preparação multitenancy)
    # tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True)
    
    # Configurações
    is_verified = models.BooleanField(default=False)
    language = models.CharField(max_length=10, default='pt-br')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        ordering = ['first_name', 'last_name']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def is_instructor(self):
        return self.role in ['instructor', 'admin']
    
    def is_student_user(self):
        return self.role == 'student'
EOF
```

### 4. Students - Gestão de Alunos

```bash
cat > apps/students/models.py << 'EOF'
from django.db import models
from django.core.validators import RegexValidator
from apps.core.models import BaseModel, ActiveManager
from apps.authentication.models import User


class Student(BaseModel):
    """
    Model principal para alunos da academia
    """
    
    # Relacionamento com usuário
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    
    # Informações de matrícula
    registration_number = models.CharField(
        max_length=50, 
        unique=True,
        help_text="Número de matrícula único"
    )
    enrollment_date = models.DateField(help_text="Data de matrícula")
    
    # Informações de emergência
    emergency_contact_name = models.CharField(max_length=255)
    emergency_contact_phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')]
    )
    emergency_contact_relationship = models.CharField(max_length=100)
    
    # Informações médicas
    medical_conditions = models.TextField(
        blank=True,
        help_text="Condições médicas relevantes"
    )
    medications = models.TextField(
        blank=True,
        help_text="Medicamentos em uso"
    )
    
    # Graduação atual
    BELT_CHOICES = [
        ('white', 'Branca'),
        ('blue', 'Azul'),
        ('purple', 'Roxa'),
        ('brown', 'Marrom'),
        ('black', 'Preta'),
        ('coral', 'Coral'),
        ('red', 'Vermelha'),
    ]
    belt_color = models.CharField(
        max_length=10, 
        choices=BELT_CHOICES, 
        default='white'
    )
    belt_stripes = models.PositiveSmallIntegerField(default=0)
    last_graduation_date = models.DateField(blank=True, null=True)
    
    # Status do aluno
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('inactive', 'Inativo'),
        ('suspended', 'Suspenso'),
        ('graduated', 'Formado'),
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active'
    )
    
    # Observações
    notes = models.TextField(
        blank=True,
        help_text="Observações do instrutor"
    )
    
    # Managers
    objects = models.Manager()
    active_objects = ActiveManager()
    
    class Meta:
        db_table = 'students'
        ordering = ['user__first_name', 'user__last_name']
        indexes = [
            models.Index(fields=['registration_number']),
            models.Index(fields=['belt_color']),
            models.Index(fields=['status']),
            models.Index(fields=['enrollment_date']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} - {self.get_belt_color_display()}"
    
    @property
    def full_name(self):
        return self.user.full_name
    
    @property
    def email(self):
        return self.user.email
    
    def graduate(self, new_belt, graduation_date=None):
        """Promove aluno para nova faixa"""
        from django.utils import timezone
        
        # Criar registro de graduação
        Graduation.objects.create(
            student=self,
            from_belt=self.belt_color,
            to_belt=new_belt,
            graduation_date=graduation_date or timezone.now().date(),
            instructor=None  # TODO: adicionar instrutor
        )
        
        # Atualizar faixa atual
        self.belt_color = new_belt
        self.belt_stripes = 0
        self.last_graduation_date = graduation_date or timezone.now().date()
        self.save()


class Graduation(BaseModel):
    """
    Histórico de graduações dos alunos
    """
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE,
        related_name='graduations'
    )
    
    from_belt = models.CharField(max_length=10, choices=Student.BELT_CHOICES)
    to_belt = models.CharField(max_length=10, choices=Student.BELT_CHOICES)
    
    graduation_date = models.DateField()
    instructor = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        limit_choices_to={'role__in': ['instructor', 'admin']}
    )
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'graduations'
        ordering = ['-graduation_date']
        indexes = [
            models.Index(fields=['student', 'graduation_date']),
            models.Index(fields=['graduation_date']),
        ]
    
    def __str__(self):
        return f"{self.student.full_name}: {self.from_belt} → {self.to_belt}"


class Attendance(BaseModel):
    """
    Registro de presenças dos alunos
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    
    class_date = models.DateField()
    check_in_time = models.TimeField()
    check_out_time = models.TimeField(blank=True, null=True)
    
    class_type = models.CharField(
        max_length=50,
        default='regular',
        help_text="Tipo de aula (gi, no-gi, competition, etc.)"
    )
    
    instructor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role__in': ['instructor', 'admin']}
    )
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'attendances'
        ordering = ['-class_date', '-check_in_time']
        unique_together = ['student', 'class_date', 'check_in_time']
        indexes = [
            models.Index(fields=['student', 'class_date']),
            models.Index(fields=['class_date']),
        ]
    
    def __str__(self):
        return f"{self.student.full_name} - {self.class_date}"
EOF
```

### 5. Payments - Sistema Financeiro

```bash
cat > apps/payments/models.py << 'EOF'
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.core.models import BaseModel, ActiveManager
from apps.students.models import Student


class PaymentMethod(BaseModel):
    """
    Métodos de pagamento disponíveis
    """
    name = models.CharField(max_length=100, help_text="Nome do método (ex: PIX, Cartão)")
    code = models.CharField(max_length=20, unique=True, help_text="Código único")
    is_online = models.BooleanField(default=False, help_text="É pagamento online?")
    processing_fee = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0,
        help_text="Taxa de processamento (ex: 0.0349 = 3.49%)"
    )
    
    class Meta:
        db_table = 'payment_methods'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Invoice(BaseModel):
    """
    Faturas mensais dos alunos
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    
    # Período da fatura
    due_date = models.DateField(help_text="Data de vencimento")
    reference_month = models.DateField(help_text="Mês de referência (YYYY-MM-01)")
    
    # Valores
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    discount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    late_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    
    # Status
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('paid', 'Pago'),
        ('overdue', 'Vencido'),
        ('cancelled', 'Cancelado'),
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    
    # Observações
    description = models.TextField(
        default='Mensalidade',
        help_text="Descrição da fatura"
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'invoices'
        ordering = ['-due_date']
        unique_together = ['student', 'reference_month']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['due_date', 'status']),
            models.Index(fields=['reference_month']),
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
        return self.due_date < timezone.now().date() and self.status == 'pending'


class Payment(BaseModel):
    """
    Registros de pagamentos realizados
    """
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.PROTECT
    )
    
    # Valores
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    processing_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    
    # Datas
    payment_date = models.DateTimeField(help_text="Data/hora do pagamento")
    confirmed_date = models.DateTimeField(
        blank=True, 
        null=True,
        help_text="Data/hora da confirmação"
    )
    
    # Status e referências externas
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('confirmed', 'Confirmado'),
        ('failed', 'Falhou'),
        ('refunded', 'Estornado'),
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    
    external_id = models.CharField(
        max_length=255, 
        blank=True,
        help_text="ID da transação no gateway de pagamento"
    )
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['invoice', 'status']),
            models.Index(fields=['payment_date']),
            models.Index(fields=['external_id']),
        ]
    
    def __str__(self):
        return f"Pagamento {self.amount} - {self.invoice.student.full_name}"
    
    def confirm_payment(self):
        """Confirma o pagamento e atualiza a fatura"""
        from django.utils import timezone
        
        self.status = 'confirmed'
        self.confirmed_date = timezone.now()
        self.save()
        
        # Atualizar status da fatura se valor total foi pago
        total_paid = self.invoice.payments.filter(
            status='confirmed'
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0')
        
        if total_paid >= self.invoice.total_amount:
            self.invoice.status = 'paid'
            self.invoice.save()
EOF
```

---

## 🔧 CONFIGURAÇÃO E MIGRATIONS

### 1. Apps Configuration

```bash
# Configurar apps no Django
cat > apps/core/apps.py << 'EOF'
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core'
EOF

cat > apps/tenants/apps.py << 'EOF'
from django.apps import AppConfig


class TenantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tenants'
    verbose_name = 'Academias'
EOF

cat > apps/authentication/apps.py << 'EOF'
from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'
    verbose_name = 'Autenticação'
EOF

cat > apps/students/apps.py << 'EOF'
from django.apps import AppConfig


class StudentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.students'
    verbose_name = 'Alunos'
EOF

cat > apps/payments/apps.py << 'EOF'
from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.payments'
    verbose_name = 'Pagamentos'
EOF
```

### 2. Atualizar Settings Django

```bash
# Adicionar apps ao settings
cat >> config/settings/base.py << 'EOF'

# Django Apps
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Third Party Apps
THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'django_filters',
]

# Local Apps
LOCAL_APPS = [
    'apps.core',
    'apps.tenants', 
    'apps.authentication',
    'apps.students',
    'apps.payments',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# User model personalizado
AUTH_USER_MODEL = 'authentication.User'
EOF
```

### 3. Gerar e Aplicar Migrations

```bash
# Gerar migrations para todos os apps
python manage.py makemigrations core
python manage.py makemigrations tenants
python manage.py makemigrations authentication
python manage.py makemigrations students
python manage.py makemigrations payments

# Verificar migrations
python manage.py showmigrations

# Aplicar migrations (quando tiver banco configurado)
# python manage.py migrate
```

### 4. Django Admin Configuration

```bash
cat > apps/tenants/admin.py << 'EOF'
from django.contrib import admin
from .models import Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'email', 'city', 'is_active', 'created_at']
    list_filter = ['is_active', 'city', 'state']
    search_fields = ['name', 'email', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'slug', 'email', 'phone')
        }),
        ('Endereço', {
            'fields': ('address', 'city', 'state', 'zip_code', 'country')
        }),
        ('Configurações Visuais', {
            'fields': ('logo', 'primary_color', 'secondary_color')
        }),
        ('Configurações de Negócio', {
            'fields': ('monthly_fee', 'timezone', 'founded_date', 'website')
        }),
        ('Sistema', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
EOF

cat > apps/authentication/admin.py << 'EOF'
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'is_verified']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'phone', 'birth_date')}),
        ('Permissões', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_verified')}),
        ('Configurações', {'fields': ('language',)}),
        ('Datas', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'role'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'date_joined', 'last_login']
EOF

cat > apps/students/admin.py << 'EOF'
from django.contrib import admin
from .models import Student, Graduation, Attendance


class GraduationInline(admin.TabularInline):
    model = Graduation
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'registration_number', 'belt_color', 'status', 'enrollment_date']
    list_filter = ['belt_color', 'status', 'enrollment_date']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'registration_number']
    inlines = [GraduationInline]
    
    fieldsets = (
        ('Usuário', {
            'fields': ('user',)
        }),
        ('Matrícula', {
            'fields': ('registration_number', 'enrollment_date', 'status')
        }),
        ('Graduação', {
            'fields': ('belt_color', 'belt_stripes', 'last_graduation_date')
        }),
        ('Contato de Emergência', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship')
        }),
        ('Informações Médicas', {
            'fields': ('medical_conditions', 'medications'),
            'classes': ('collapse',)
        }),
        ('Observações', {
            'fields': ('notes',)
        })
    )


@admin.register(Graduation)
class GraduationAdmin(admin.ModelAdmin):
    list_display = ['student', 'from_belt', 'to_belt', 'graduation_date', 'instructor']
    list_filter = ['from_belt', 'to_belt', 'graduation_date']
    search_fields = ['student__user__first_name', 'student__user__last_name']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'class_date', 'check_in_time', 'check_out_time', 'class_type']
    list_filter = ['class_date', 'class_type']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    date_hierarchy = 'class_date'
EOF

cat > apps/payments/admin.py << 'EOF'
from django.contrib import admin
from .models import PaymentMethod, Invoice, Payment


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_online', 'processing_fee', 'is_active']
    list_filter = ['is_online', 'is_active']


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['created_at', 'confirmed_date']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['student', 'reference_month', 'due_date', 'amount', 'status']
    list_filter = ['status', 'due_date', 'reference_month']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    inlines = [PaymentInline]
    date_hierarchy = 'due_date'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'payment_method', 'amount', 'payment_date', 'status']
    list_filter = ['status', 'payment_method', 'payment_date']
    search_fields = ['invoice__student__user__first_name', 'external_id']
    date_hierarchy = 'payment_date'
EOF
```

### 5. Management Command para Seed Data

```bash
mkdir -p apps/core/management/commands

cat > apps/core/management/commands/seed_data.py << 'EOF'
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.tenants.models import Tenant
from apps.students.models import Student
from apps.payments.models import PaymentMethod
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with initial data for development'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        
        # Payment Methods
        payment_methods = [
            {'name': 'PIX', 'code': 'pix', 'is_online': True, 'processing_fee': Decimal('0.01')},
            {'name': 'Cartão de Crédito', 'code': 'credit_card', 'is_online': True, 'processing_fee': Decimal('0.0349')},
            {'name': 'Dinheiro', 'code': 'cash', 'is_online': False, 'processing_fee': Decimal('0')},
            {'name': 'Transferência', 'code': 'transfer', 'is_online': False, 'processing_fee': Decimal('0')},
        ]
        
        for pm_data in payment_methods:
            PaymentMethod.objects.get_or_create(
                code=pm_data['code'],
                defaults=pm_data
            )
        
        # Tenant exemplo
        tenant, created = Tenant.objects.get_or_create(
            slug='academia-exemplo',
            defaults={
                'name': 'Academia Exemplo',
                'email': 'contato@academiaexemplo.com',
                'phone': '+5511999999999',
                'address': 'Rua Exemplo, 123',
                'city': 'São Paulo',
                'state': 'SP',
                'zip_code': '01234-567',
                'monthly_fee': Decimal('150.00'),
            }
        )
        
        # Admin user
        admin_user, created = User.objects.get_or_create(
            email='admin@academiaexemplo.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'Sistema',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
        
        # Instructor user
        instructor_user, created = User.objects.get_or_create(
            email='instrutor@academiaexemplo.com',
            defaults={
                'first_name': 'João',
                'last_name': 'Silva',
                'role': 'instructor',
            }
        )
        
        if created:
            instructor_user.set_password('instructor123')
            instructor_user.save()
        
        # Student users
        students_data = [
            {'first_name': 'Maria', 'last_name': 'Santos', 'belt': 'blue'},
            {'first_name': 'Pedro', 'last_name': 'Oliveira', 'belt': 'white'},
            {'first_name': 'Ana', 'last_name': 'Costa', 'belt': 'purple'},
        ]
        
        for student_data in students_data:
            email = f"{student_data['first_name'].lower()}@email.com"
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': student_data['first_name'],
                    'last_name': student_data['last_name'],
                    'role': 'student',
                }
            )
            
            if created:
                user.set_password('student123')
                user.save()
                
                # Create student profile
                Student.objects.get_or_create(
                    user=user,
                    defaults={
                        'registration_number': f'REG{user.id:04d}',
                        'enrollment_date': '2024-01-01',
                        'belt_color': student_data['belt'],
                        'emergency_contact_name': 'Contato Emergência',
                        'emergency_contact_phone': '+5511888888888',
                        'emergency_contact_relationship': 'Familiar',
                    }
                )
        
        self.stdout.write(
            self.style.SUCCESS('Database seeded successfully!')
        )
        self.stdout.write('Users created:')
        self.stdout.write(f'  Admin: admin@academiaexemplo.com / admin123')
        self.stdout.write(f'  Instructor: instrutor@academiaexemplo.com / instructor123')
        self.stdout.write(f'  Students: maria@email.com, pedro@email.com, ana@email.com / student123')
EOF
```

---

## ✅ CHECKLIST DE VALIDAÇÃO T002

### Models Django
- [ ] `apps/core/models.py` criado com BaseModel, TimestampedModel, SoftDeleteModel
- [ ] `apps/tenants/models.py` criado com Tenant model
- [ ] `apps/authentication/models.py` criado com User personalizado
- [ ] `apps/students/models.py` criado com Student, Graduation, Attendance
- [ ] `apps/payments/models.py` criado com PaymentMethod, Invoice, Payment

### Configuração Django
- [ ] Apps configurados em `config/settings/base.py`
- [ ] `AUTH_USER_MODEL` definido como `authentication.User`
- [ ] Apps configs criados para cada app

### Migrations
- [ ] `python manage.py makemigrations` executado para todos os apps
- [ ] `python manage.py showmigrations` mostra migrations criadas
- [ ] Migrations aplicadas com `python manage.py migrate` (quando banco estiver configurado)

### Django Admin
- [ ] Admin classes criadas para todos os models
- [ ] `python manage.py createsuperuser` funcionando
- [ ] Admin interface acessível e funcional

### Dados de Seed
- [ ] Command `seed_data` criado
- [ ] `python manage.py seed_data` executa sem erro
- [ ] Dados básicos criados (users, tenant, payment methods)

### Validação Final
- [ ] `python manage.py check` passa sem erros
- [ ] Models seguem padrões do `CONTEXT.md` (UUID, BaseModel, etc.)
- [ ] Relacionamentos definidos corretamente
- [ ] Documentação dos models atualizada

---

## 📞 Próximos Passos

Após executar T002:

1. **Marcar T002 como completa**
2. **Iniciar T003 - Setup Backend Django**
3. **Configurar PostgreSQL e aplicar migrations**
4. **Testar admin interface e models**

**Total estimado**: 16 horas conforme T002 