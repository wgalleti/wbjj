import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = 'Aguarda o banco de dados ficar disponível'

    def handle(self, *args, **options):
        self.stdout.write('Aguardando banco de dados...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
                db_conn.cursor()
            except OperationalError:
                self.stdout.write('Banco não disponível, aguardando 1 segundo...')
                time.sleep(1)

        self.stdout.write(
            self.style.SUCCESS('Banco de dados disponível!')
        ) 