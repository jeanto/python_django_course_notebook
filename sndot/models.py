from django.db import models

class Pessoa(models.Model):
    nome = models.CharField(max_length=255)
    idade = models.IntegerField()
    sexo = models.CharField(max_length=1)  # Use CharField para sexo
    data_nascimento = models.DateField()
    cidade_natal = models.CharField(max_length=100)
    estado_natal = models.CharField(max_length=50)
    cpf = models.CharField(max_length=14, unique=True)
    profissao = models.CharField(max_length=100, blank=True, null=True)
    cidade_residencia = models.CharField(max_length=100)
    estado_residencia = models.CharField(max_length=50)
    estado_civil = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        abstract = True  # Classe abstrata, não cria tabela no banco

    def __str__(self):
        return self.nome  # Retorna o nome para representação amigável

class Doador(Pessoa):
    contato_emergencia = models.CharField(max_length=255)
    tipo_sanguineo = models.CharField(max_length=5)

    # Removido: doadores e contador_id (gerenciados pelo Django)

    def __str__(self):
        return f"{self.nome} (Doador)" #Método para retornar o nome e a classe do objeto

    # Removido: cadastrar_doador, atualizar_dados_doador, listar_doadores (lógica será movida para views e services)