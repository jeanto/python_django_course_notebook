import json
from django.core.management.base import BaseCommand, CommandError
from sndot.models import Doador
from datetime import datetime
import os

class Command(BaseCommand):
    help = 'Importa doadores do arquivo JSON para o banco de dados'

    def add_arguments(self, parser):
        parser.add_argument('json_file_name', type=str, help='Nome do arquivo JSON')  # Altera para receber o nome do arquivo

    def handle(self, *args, **options):
        json_file_name = options['json_file_name']
        print(f"json_file_name: {json_file_name}") # apenas para debug

        try:
            with open(json_file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"carregado: {json_file_name}") # apenas para debug
        except FileNotFoundError:
            print(f"carregado1: {json_file_name}: Diretório atual: {os.getcwd()}") # apenas para debug
            raise CommandError(f'Arquivo JSON não encontrado: {json_file_name}')
        except json.JSONDecodeError:
            print(f"carregado2: {json_file_name}") # apenas para debug
            raise CommandError(f'Erro ao decodificar o arquivo JSON: {json_file_name}')

        for doador_data in data:
            dados_doador = doador_data['dados']
            #intencao_doador = doador_data['intencao'] # Não estamos usando intencao aqui, mas pode ser útil no futuro

            # Converta a data de string para objeto date
            try:
                data_nascimento = datetime.strptime(dados_doador['data_nascimento'], '%d/%m/%Y').date()
            except ValueError:
                self.stdout.write(self.style.ERROR(f"Erro ao converter data de nascimento para o doador: {dados_doador['nome']}. Data: {dados_doador['data_nascimento']}"))
                continue  # Pula para o próximo doador

            try:
                # Crie ou atualize o doador usando update_or_create
                doador, created = Doador.objects.update_or_create(
                    cpf=dados_doador['cpf'],  # Use CPF como identificador único
                    defaults={
                        'nome': dados_doador['nome'],
                        'idade': dados_doador['idade'],
                        'sexo': dados_doador['sexo'],
                        'data_nascimento': data_nascimento,
                        'cidade_natal': dados_doador['cidade_natal'],
                        'estado_natal': dados_doador['estado_natal'],
                        'profissao': dados_doador['profissao'],
                        'cidade_residencia': dados_doador['cidade_residencia'],
                        'estado_residencia': dados_doador['estado_residencia'],
                        'estado_civil': dados_doador['estado_civil'],
                        'contato_emergencia': dados_doador['contato_emergencia'],
                        'tipo_sanguineo': dados_doador['tipo_sanguineo'],
                    }
                )

                print(f"criado: {json_file_name}") # apenas para debug

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Doador '{doador.nome}' criado com sucesso."))
                else:
                    self.stdout.write(self.style.SUCCESS(f"Doador '{doador.nome}' atualizado com sucesso."))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro ao processar doador '{dados_doador['nome']}': {e}"))

        self.stdout.write(self.style.SUCCESS('Importação de doadores concluída com sucesso.'))
