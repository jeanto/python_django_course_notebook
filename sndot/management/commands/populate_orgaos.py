from django.core.management.base import BaseCommand
from sndot.models import Orgao # Importe o seu model Orgao

class Command(BaseCommand):
    help = 'Popula a tabela Orgao com uma lista predefinida de órgãos.'

    def handle(self, *args, **kwargs):
        orgaos_lista = [
            "Coração", "Rins", "Fígado", "Pâncreas", "Pulmões", "Intestino",
            "Córneas", "Pele", "Ossos", "Válvulas cardíacas", "Cartilagem",
            "Medula Óssea", "Tendões", "Vasos Sanguíneos", "Sangue de Cordão Umbilical",
            "Sangue Universal"
        ]

        self.stdout.write(self.style.SUCCESS('Iniciando a população da tabela Orgao...'))

        for nome_orgao in orgaos_lista:
            # get_or_create tenta obter o objeto; se não existe, cria.
            orgao, created = Orgao.objects.get_or_create(nome=nome_orgao)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Órgão '{orgao.nome}' criado com sucesso."))
            else:
                self.stdout.write(self.style.WARNING(f"Órgão '{orgao.nome}' já existe."))

        self.stdout.write(self.style.SUCCESS('População da tabela Orgao concluída.'))
