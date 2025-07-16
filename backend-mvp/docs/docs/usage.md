# wBJJ API - Exemplos Práticos de Uso

Este documento contém exemplos práticos de como usar a wBJJ API em diferentes cenários reais.

## 🎯 Cenários de Uso

### 1. Fluxo Completo de Aluno Novo

Este exemplo mostra o fluxo completo desde o cadastro de um aluno até seu primeiro pagamento.

```python
import requests
import json
from datetime import datetime, timedelta

class WBJJApiClient:
    def __init__(self, base_url, tenant_id):
        self.base_url = base_url
        self.tenant_id = tenant_id
        self.session = requests.Session()
        self.session.headers.update({
            'X-Tenant-ID': tenant_id,
            'Content-Type': 'application/json'
        })

    def login(self, email, password):
        """Fazer login e configurar token"""
        response = self.session.post(f'{self.base_url}/auth/login/', {
            'email': email,
            'password': password
        })

        if response.ok:
            data = response.json()
            self.session.headers['Authorization'] = f"Bearer {data['access']}"
            return data

        raise Exception(f"Login failed: {response.status_code}")

# Configuração
api = WBJJApiClient(
    base_url='http://localhost:8000/api/v1',
    tenant_id='123e4567-e89b-12d3-a456-426614174000'
)

# 1. Login como admin
admin_data = api.login('admin@academia.com', 'senha123')
print(f"Logado como: {admin_data['user']['firstName']}")

# 2. Criar usuário para o aluno
user_data = {
    'email': 'joao.silva@email.com',
    'password': 'senha123',
    'first_name': 'João',
    'last_name': 'Silva'
}

user_response = api.session.post(f'{api.base_url}/auth/users/', user_data)
new_user = user_response.json()
print(f"Usuário criado: {new_user['id']}")

# 3. Criar aluno
student_data = {
    'user': new_user['id'],
    'phone': '(11) 99999-9999',
    'belt_color': 'white',
    'status': 'active',
    'birth_date': '1990-01-15',
    'address': 'Rua das Flores, 123',
    'emergency_contact': 'Maria Silva - (11) 88888-8888',
    'notes': 'Aluno iniciante, muito motivado'
}

student_response = api.session.post(f'{api.base_url}/students/', student_data)
new_student = student_response.json()
print(f"Aluno criado: {new_student['id']}")

# 4. Criar método de pagamento
payment_method_data = {
    'name': 'PIX',
    'type': 'pix',
    'is_active': True
}

payment_method_response = api.session.post(f'{api.base_url}/payment-methods/', payment_method_data)
payment_method = payment_method_response.json()

# 5. Criar fatura para primeira mensalidade
invoice_data = {
    'student': new_student['id'],
    'amount': '150.00',
    'due_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
    'description': 'Mensalidade Janeiro 2024',
    'status': 'pending'
}

invoice_response = api.session.post(f'{api.base_url}/invoices/', invoice_data)
new_invoice = invoice_response.json()
print(f"Fatura criada: {new_invoice['id']} - R$ {new_invoice['amount']}")

# 6. Registrar pagamento
payment_data = {
    'invoice': new_invoice['id'],
    'payment_method': payment_method['id'],
    'amount': '150.00',
    'payment_date': datetime.now().strftime('%Y-%m-%d'),
    'notes': 'Primeiro pagamento - PIX'
}

payment_response = api.session.post(f'{api.base_url}/payments/', payment_data)
new_payment = payment_response.json()

# 7. Confirmar pagamento
confirm_response = api.session.post(
    f'{api.base_url}/payments/{new_payment["id"]}/confirm/',
    {'confirmed': True, 'confirmation_notes': 'Pagamento confirmado via banco'}
)

print("Fluxo completo concluído com sucesso!")
```

### 2. Sistema de Graduação Automática

Exemplo de como implementar um sistema que verifica alunos elegíveis para graduação.

```python
from datetime import datetime, timedelta

def check_graduation_eligibility(api):
    """Verifica alunos elegíveis para graduação baseado em critérios"""

    # Buscar todos os alunos ativos
    students_response = api.session.get(f'{api.base_url}/students/?status=active')
    students = students_response.json()['results']

    eligible_students = []

    for student in students:
        # Buscar graduações do aluno
        graduations_response = api.session.get(
            f'{api.base_url}/students/{student["id"]}/graduations/'
        )
        graduations = graduations_response.json()

        # Buscar presenças dos últimos 6 meses
        six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        attendances_response = api.session.get(
            f'{api.base_url}/students/{student["id"]}/attendances/',
            params={'checkin_time__gte': six_months_ago}
        )
        attendances = attendances_response.json()['results']

        # Critérios para graduação
        criteria = {
            'minimum_time_in_belt': 6,  # meses
            'minimum_attendances': 50,  # presenças
            'current_belt': student['belt_color']
        }

        # Verificar se atende aos critérios
        if len(attendances) >= criteria['minimum_attendances']:
            # Verificar tempo na faixa atual
            last_graduation = graduations[-1] if graduations else None
            time_in_belt = calculate_time_in_belt(last_graduation)

            if time_in_belt >= criteria['minimum_time_in_belt']:
                next_belt = get_next_belt(criteria['current_belt'])
                if next_belt:
                    eligible_students.append({
                        'student': student,
                        'current_belt': criteria['current_belt'],
                        'next_belt': next_belt,
                        'attendances': len(attendances),
                        'time_in_belt_months': time_in_belt
                    })

    return eligible_students

def calculate_time_in_belt(last_graduation):
    """Calcula tempo na faixa atual em meses"""
    if last_graduation:
        graduation_date = datetime.strptime(last_graduation['graduation_date'], '%Y-%m-%d')
    else:
        # Se não tem graduação, considera que começou há muito tempo
        graduation_date = datetime.now() - timedelta(days=365)

    return (datetime.now() - graduation_date).days / 30

def get_next_belt(current_belt):
    """Retorna próxima faixa"""
    belt_progression = {
        'white': 'blue',
        'blue': 'purple',
        'purple': 'brown',
        'brown': 'black'
    }
    return belt_progression.get(current_belt)

# Executar verificação
eligible = check_graduation_eligibility(api)

print(f"Encontrados {len(eligible)} alunos elegíveis para graduação:")
for student_info in eligible:
    print(f"- {student_info['student']['firstName']} {student_info['student']['lastName']}")
    print(f"  {student_info['current_belt']} → {student_info['next_belt']}")
    print(f"  {student_info['attendances']} presenças nos últimos 6 meses")
    print(f"  {student_info['time_in_belt_months']:.1f} meses na faixa atual")
    print()
```

### 3. Relatório Financeiro Mensal

Exemplo de como gerar relatórios financeiros detalhados.

```python
from datetime import datetime, timedelta
import pandas as pd

def generate_monthly_report(api, year, month):
    """Gera relatório financeiro mensal"""

    # Definir período
    start_date = f"{year}-{month:02d}-01"
    if month == 12:
        end_date = f"{year + 1}-01-01"
    else:
        end_date = f"{year}-{month + 1:02d}-01"

    # Buscar faturas do período
    invoices_response = api.session.get(f'{api.base_url}/invoices/', params={
        'due_date__gte': start_date,
        'due_date__lt': end_date
    })
    invoices = invoices_response.json()['results']

    # Buscar pagamentos do período
    payments_response = api.session.get(f'{api.base_url}/payments/', params={
        'payment_date__gte': start_date,
        'payment_date__lt': end_date
    })
    payments = payments_response.json()['results']

    # Calcular métricas
    total_invoiced = sum(float(inv['amount']) for inv in invoices)
    total_received = sum(float(pay['amount']) for pay in payments if pay['confirmed'])
    pending_amount = total_invoiced - total_received

    # Agrupar por status
    invoices_by_status = {}
    for invoice in invoices:
        status = invoice['status']
        if status not in invoices_by_status:
            invoices_by_status[status] = {'count': 0, 'amount': 0}
        invoices_by_status[status]['count'] += 1
        invoices_by_status[status]['amount'] += float(invoice['amount'])

    # Agrupar pagamentos por método
    payments_by_method = {}
    for payment in payments:
        if payment['confirmed']:
            method = payment['payment_method']['name']
            if method not in payments_by_method:
                payments_by_method[method] = {'count': 0, 'amount': 0}
            payments_by_method[method]['count'] += 1
            payments_by_method[method]['amount'] += float(payment['amount'])

    # Gerar relatório
    report = {
        'period': f"{month:02d}/{year}",
        'summary': {
            'total_invoiced': total_invoiced,
            'total_received': total_received,
            'pending_amount': pending_amount,
            'collection_rate': (total_received / total_invoiced * 100) if total_invoiced > 0 else 0
        },
        'invoices_by_status': invoices_by_status,
        'payments_by_method': payments_by_method,
        'top_debtors': get_top_debtors(api, invoices)
    }

    return report

def get_top_debtors(api, invoices):
    """Identifica maiores devedores"""
    pending_by_student = {}

    for invoice in invoices:
        if invoice['status'] == 'pending':
            student_id = invoice['student']['id']
            student_name = f"{invoice['student']['firstName']} {invoice['student']['lastName']}"

            if student_id not in pending_by_student:
                pending_by_student[student_id] = {
                    'name': student_name,
                    'amount': 0,
                    'invoices': 0
                }

            pending_by_student[student_id]['amount'] += float(invoice['amount'])
            pending_by_student[student_id]['invoices'] += 1

    # Ordenar por valor pendente
    return sorted(
        pending_by_student.values(),
        key=lambda x: x['amount'],
        reverse=True
    )[:10]  # Top 10

# Gerar relatório para janeiro de 2024
report = generate_monthly_report(api, 2024, 1)

print(f"=== RELATÓRIO FINANCEIRO - {report['period']} ===")
print(f"Total Faturado: R$ {report['summary']['total_invoiced']:.2f}")
print(f"Total Recebido: R$ {report['summary']['total_received']:.2f}")
print(f"Pendente: R$ {report['summary']['pending_amount']:.2f}")
print(f"Taxa de Cobrança: {report['summary']['collection_rate']:.1f}%")
print()

print("=== FATURAS POR STATUS ===")
for status, data in report['invoices_by_status'].items():
    print(f"{status}: {data['count']} faturas - R$ {data['amount']:.2f}")
print()

print("=== PAGAMENTOS POR MÉTODO ===")
for method, data in report['payments_by_method'].items():
    print(f"{method}: {data['count']} pagamentos - R$ {data['amount']:.2f}")
print()

print("=== MAIORES DEVEDORES ===")
for debtor in report['top_debtors'][:5]:
    print(f"{debtor['name']}: R$ {debtor['amount']:.2f} ({debtor['invoices']} faturas)")
```

### 4. Sistema de Check-in Automático

Exemplo de integração com sistema de catracas ou RFID para check-in automático.

```python
import threading
import time
from datetime import datetime

class AutoCheckInSystem:
    def __init__(self, api_client):
        self.api = api_client
        self.active_students = {}
        self.running = True

    def load_active_students(self):
        """Carrega lista de alunos ativos com suas informações"""
        response = self.api.session.get(f'{self.api.base_url}/students/?status=active')
        students = response.json()['results']

        self.active_students = {
            student['rfid_tag']: student for student in students
            if student.get('rfid_tag')
        }

        print(f"Carregados {len(self.active_students)} alunos com RFID")

    def process_rfid_scan(self, rfid_tag):
        """Processa leitura de tag RFID"""
        if rfid_tag not in self.active_students:
            print(f"Tag RFID {rfid_tag} não encontrada")
            return False

        student = self.active_students[rfid_tag]

        # Verificar se já fez check-in hoje
        today = datetime.now().strftime('%Y-%m-%d')
        existing_attendance = self.check_existing_attendance(student['id'], today)

        if existing_attendance and not existing_attendance.get('checkout_time'):
            # Fazer checkout
            checkout_data = {
                'checkout_time': datetime.now().isoformat()
            }

            response = self.api.session.patch(
                f'{self.api.base_url}/attendances/{existing_attendance["id"]}/',
                checkout_data
            )

            if response.ok:
                print(f"✅ CHECKOUT: {student['firstName']} {student['lastName']}")
                return True
        else:
            # Fazer checkin
            checkin_data = {
                'student': student['id'],
                'checkin_time': datetime.now().isoformat(),
                'class_type': self.get_current_class_type(),
                'notes': 'Check-in automático via RFID'
            }

            response = self.api.session.post(f'{self.api.base_url}/attendances/', checkin_data)

            if response.ok:
                print(f"🟢 CHECKIN: {student['firstName']} {student['lastName']}")
                return True

        return False

    def check_existing_attendance(self, student_id, date):
        """Verifica se aluno já tem presença registrada hoje"""
        response = self.api.session.get(
            f'{self.api.base_url}/students/{student_id}/attendances/',
            params={'checkin_time__date': date}
        )

        attendances = response.json()['results']
        return attendances[0] if attendances else None

    def get_current_class_type(self):
        """Determina tipo de aula baseado no horário"""
        hour = datetime.now().hour

        if 6 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 18:
            return 'afternoon'
        else:
            return 'evening'

    def simulate_rfid_reader(self):
        """Simula leituras de RFID para teste"""
        test_tags = list(self.active_students.keys())[:3]  # Pegar 3 tags para teste

        while self.running:
            for tag in test_tags:
                if not self.running:
                    break

                print(f"Simulando leitura RFID: {tag}")
                self.process_rfid_scan(tag)
                time.sleep(10)  # Aguardar 10 segundos entre leituras

            time.sleep(30)  # Pausa maior entre ciclos

# Inicializar sistema
checkin_system = AutoCheckInSystem(api)
checkin_system.load_active_students()

# Simular funcionamento (em produção, seria integrado com hardware RFID)
print("Iniciando sistema de check-in automático...")
try:
    checkin_system.simulate_rfid_reader()
except KeyboardInterrupt:
    checkin_system.running = False
    print("Sistema de check-in finalizado")
```

### 5. Dashboard em Tempo Real com WebSockets

Exemplo de como implementar um dashboard que atualiza em tempo real.

```python
import asyncio
import websockets
import json
from datetime import datetime

class RealTimeDashboard:
    def __init__(self, api_client):
        self.api = api_client
        self.connected_clients = set()
        self.last_stats = {}

    async def register_client(self, websocket, path):
        """Registra novo cliente WebSocket"""
        self.connected_clients.add(websocket)
        print(f"Cliente conectado. Total: {len(self.connected_clients)}")

        # Enviar dados iniciais
        await self.send_initial_data(websocket)

        try:
            await websocket.wait_closed()
        finally:
            self.connected_clients.remove(websocket)
            print(f"Cliente desconectado. Total: {len(self.connected_clients)}")

    async def send_initial_data(self, websocket):
        """Envia dados iniciais para cliente"""
        stats = await self.get_current_stats()
        await websocket.send(json.dumps({
            'type': 'initial_data',
            'data': stats
        }))

    async def get_current_stats(self):
        """Busca estatísticas atuais"""
        try:
            # Estatísticas de alunos
            students_response = self.api.session.get(f'{self.api.base_url}/students/stats/')
            students_stats = students_response.json()

            # Presenças de hoje
            today = datetime.now().strftime('%Y-%m-%d')
            attendances_response = self.api.session.get(
                f'{self.api.base_url}/attendances/',
                params={'checkin_time__date': today}
            )
            todays_attendances = attendances_response.json()['count']

            # Pagamentos do mês
            month_start = datetime.now().strftime('%Y-%m-01')
            payments_response = self.api.session.get(
                f'{self.api.base_url}/payments/',
                params={'payment_date__gte': month_start, 'confirmed': True}
            )
            monthly_payments = sum(
                float(p['amount']) for p in payments_response.json()['results']
            )

            # Health check
            health_response = self.api.session.get(f'{self.api.base_url}/health/quick/')
            health_status = health_response.json()['status']

            return {
                'timestamp': datetime.now().isoformat(),
                'students': students_stats,
                'todays_attendances': todays_attendances,
                'monthly_revenue': monthly_payments,
                'system_health': health_status
            }

        except Exception as e:
            print(f"Erro ao buscar stats: {e}")
            return self.last_stats

    async def broadcast_updates(self):
        """Envia atualizações para todos os clientes conectados"""
        while True:
            if self.connected_clients:
                current_stats = await self.get_current_stats()

                # Verificar se houve mudanças significativas
                if self.stats_changed(current_stats):
                    message = json.dumps({
                        'type': 'stats_update',
                        'data': current_stats
                    })

                    # Enviar para todos os clientes
                    disconnected = set()
                    for client in self.connected_clients:
                        try:
                            await client.send(message)
                        except websockets.exceptions.ConnectionClosed:
                            disconnected.add(client)

                    # Remover clientes desconectados
                    self.connected_clients -= disconnected

                    self.last_stats = current_stats

            await asyncio.sleep(5)  # Atualizar a cada 5 segundos

    def stats_changed(self, new_stats):
        """Verifica se estatísticas mudaram significativamente"""
        if not self.last_stats:
            return True

        # Verificar campos que devem gerar update
        important_fields = [
            'todays_attendances',
            'monthly_revenue',
            'system_health'
        ]

        for field in important_fields:
            if self.last_stats.get(field) != new_stats.get(field):
                return True

        return False

# Exemplo de cliente JavaScript para receber atualizações
js_client_example = """
// Frontend JavaScript
const ws = new WebSocket('ws://localhost:8001/dashboard');

ws.onmessage = function(event) {
    const message = JSON.parse(event.data);

    if (message.type === 'initial_data' || message.type === 'stats_update') {
        updateDashboard(message.data);
    }
};

function updateDashboard(stats) {
    document.getElementById('total-students').textContent = stats.students.total;
    document.getElementById('todays-attendances').textContent = stats.todays_attendances;
    document.getElementById('monthly-revenue').textContent =
        'R$ ' + stats.monthly_revenue.toFixed(2);

    const healthIndicator = document.getElementById('health-status');
    healthIndicator.className = stats.system_health === 'ok' ? 'healthy' : 'unhealthy';
}
"""

print("Exemplo de cliente JavaScript:")
print(js_client_example)

# Inicializar dashboard (exemplo de uso)
# dashboard = RealTimeDashboard(api)
#
# # Iniciar servidor WebSocket
# start_server = websockets.serve(dashboard.register_client, "localhost", 8001)
#
# # Executar loop de atualizações
# asyncio.get_event_loop().run_until_complete(asyncio.gather(
#     start_server,
#     dashboard.broadcast_updates()
# ))
```

## 🔧 Utilitários Auxiliares

### Cliente Python Simplificado

```python
class SimpleWBJJClient:
    """Cliente Python simplificado para operações comuns"""

    def __init__(self, base_url, tenant_id, email, password):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'X-Tenant-ID': tenant_id,
            'Content-Type': 'application/json'
        })

        # Login automático
        self.login(email, password)

    def login(self, email, password):
        response = self.session.post(f'{self.base_url}/auth/login/', {
            'email': email, 'password': password
        })

        if response.ok:
            token = response.json()['access']
            self.session.headers['Authorization'] = f'Bearer {token}'
        else:
            raise Exception(f"Login failed: {response.status_code}")

    def get_students(self, **filters):
        """Buscar alunos com filtros opcionais"""
        return self.session.get(f'{self.base_url}/students/', params=filters).json()

    def create_student(self, **student_data):
        """Criar novo aluno"""
        return self.session.post(f'{self.base_url}/students/', student_data).json()

    def graduate_student(self, student_id, new_belt, graduation_date=None, notes=None):
        """Graduar aluno"""
        data = {'new_belt': new_belt}
        if graduation_date:
            data['graduation_date'] = graduation_date
        if notes:
            data['notes'] = notes

        return self.session.post(
            f'{self.base_url}/students/{student_id}/graduate/',
            data
        ).json()

    def checkin_student(self, student_id, class_type='gi', notes=None):
        """Registrar presença de aluno"""
        data = {
            'student': student_id,
            'checkin_time': datetime.now().isoformat(),
            'class_type': class_type
        }
        if notes:
            data['notes'] = notes

        return self.session.post(f'{self.base_url}/attendances/', data).json()

    def create_invoice(self, student_id, amount, due_date, description):
        """Criar fatura"""
        data = {
            'student': student_id,
            'amount': amount,
            'due_date': due_date,
            'description': description,
            'status': 'pending'
        }

        return self.session.post(f'{self.base_url}/invoices/', data).json()

    def record_payment(self, invoice_id, payment_method_id, amount, payment_date=None):
        """Registrar pagamento"""
        data = {
            'invoice': invoice_id,
            'payment_method': payment_method_id,
            'amount': amount,
            'payment_date': payment_date or datetime.now().strftime('%Y-%m-%d')
        }

        return self.session.post(f'{self.base_url}/payments/', data).json()

# Uso simplificado
client = SimpleWBJJClient(
    base_url='http://localhost:8000/api/v1',
    tenant_id='123e4567-e89b-12d3-a456-426614174000',
    email='admin@academia.com',
    password='senha123'
)

# Operações simples
students = client.get_students(belt_color='white', status='active')
new_student = client.create_student(
    email='novo@email.com',
    first_name='Novo',
    last_name='Aluno',
    belt_color='white'
)
```

### Script de Backup de Dados

```python
import json
from datetime import datetime

def backup_academy_data(client, backup_file=None):
    """Faz backup completo dos dados da academia"""

    if not backup_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'backup_wbjj_{timestamp}.json'

    backup_data = {
        'timestamp': datetime.now().isoformat(),
        'academy_data': {}
    }

    # Backup de todas as entidades
    entities = [
        'students', 'attendances', 'invoices',
        'payments', 'payment-methods', 'tenants'
    ]

    for entity in entities:
        print(f"Fazendo backup de {entity}...")

        # Buscar todos os registros
        all_records = []
        page = 1

        while True:
            response = client.session.get(
                f'{client.base_url}/{entity}/',
                params={'page': page, 'page_size': 100}
            )

            if not response.ok:
                print(f"Erro ao buscar {entity}: {response.status_code}")
                break

            data = response.json()
            all_records.extend(data['results'])

            if not data['next']:
                break

            page += 1

        backup_data['academy_data'][entity] = all_records
        print(f"✅ {len(all_records)} registros de {entity}")

    # Salvar backup
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)

    print(f"📁 Backup salvo em: {backup_file}")
    return backup_file

# Executar backup
backup_file = backup_academy_data(client)
```

Estes exemplos demonstram como usar a wBJJ API em cenários reais, desde operações básicas até implementações mais complexas com tempo real e automação.
