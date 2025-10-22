from django.core.management.base import BaseCommand
from django.db import connection
import os

class Command(BaseCommand):
    help = "Executa o script SQL para popular a tabela Residuo."

    def handle(self, *args, **options):
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sql_file_path = os.path.join(app_dir, 'queries', 'insert_residuos.sql')
        
        if not os.path.exists(sql_file_path):
            self.stdout.write(self.style.ERROR(f"Arquivo SQL não encontrado em: {sql_file_path}"))
            return

        self.stdout.write(self.style.NOTICE("Executando script SQL para popular Resíduos..."))

        try:
            with open(sql_file_path, 'r') as f:
                sql_statements = f.read()

            with connection.cursor() as cursor:
                cursor.execute(sql_statements)
            
            self.stdout.write(self.style.SUCCESS("Dados de Resíduos inseridos/atualizados com sucesso!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro ao executar o script SQL: {e}"))