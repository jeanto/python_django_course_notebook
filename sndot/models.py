from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, ValidationError
from .validador import ValidadorNome, ValidadorScriptInjection, ValidadorXSS, ValidadorSQLInjection # Importe os validadores do arquivo validators.py
import re

def validar_cpf(value):
    """Função para validar o CPF."""
    # Remove caracteres não numéricos
    cpf = ''.join(filter(str.isdigit, value))

    # Lógica de validação do CPF (adaptada de https://www.pythonbrasil.org.br/wiki/VerificadorDeCPF)
    try:
        int(cpf)  # Verifica se todos os caracteres são números
    except ValueError:
        raise ValidationError("CPF deve conter apenas números.")

    # Cálculo do primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    if digito1 != int(cpf[9]):
        raise ValidationError("CPF inválido.")

    # Cálculo do segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    if digito2 != int(cpf[10]):
        raise ValidationError("CPF inválido.")
    
    # Se o CPF for válido, retorna o valor original
    return cpf

class Pessoa(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    idade = models.IntegerField(
        validators=[
            MinValueValidator(0, message="A idade deve ser maior ou igual a 0."),
            MaxValueValidator(125, message="A idade deve ser menor ou igual a 125."),
        ]
    )
    sexo = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Feminino')])
    data_nascimento = models.DateField()
    cidade_natal = models.CharField(max_length=100)
    estado_natal = models.CharField(max_length=2)
    cpf = models.CharField(max_length=14, unique=True, validators=[validar_cpf])
    profissao = models.CharField(max_length=100, blank=True, null=True)
    cidade_residencia = models.CharField(max_length=100)
    estado_residencia = models.CharField(max_length=2)
    estado_civil = models.CharField(max_length=50, choices=[
         ('Solteiro', 'Solteiro'), ('Casado', 'Casado'), 
         ('Divorciado', 'Divorciado'), ('Viuvo', 'Viuvo'), 
         ('Uniao Estavel', 'Uniao Estavel')], null=True, blank=True)


    # O método clean() no Django é usado para validação personalizada de modelos. 
    # Ele permite que você defina regras de validação além das validações 
    # padrão dos campos. O Django chama esse método quando você usa full_clean() 
    # em uma instância do modelo, geralmente antes de salvar no banco de dados.
    def clean(self):
        super().clean()
        validador_nome = ValidadorNome()

        # Validar o nome
        validador_nome.validar(self.nome, 'Nome')

    class Meta:
        abstract = True  # Classe base abstrata, não será criada tabela no banco

    def __str__(self):
        return f"{self.nome} ({self.cpf})"

    @classmethod
    def cadastrar(cls, **kwargs):
        """
        Método de classe para cadastrar uma pessoa.
        Deve ser implementado nas subclasses.
        """
        raise NotImplementedError("O método cadastrar deve ser implementado na subclasse.")
    
    def editar(cls, **kwargs):
        """
        Método de classe para editar uma pessoa.
        Deve ser implementado nas subclasses.
        """
        raise NotImplementedError("O método editar deve ser implementado na subclasse.")

class Doador(Pessoa):
    contato_emergencia = models.CharField(max_length=255)
    tipo_sanguineo = models.CharField(max_length=5, choices=[
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')
    ])

    def clean(self):
        super().clean()
        # Validaçoes de segurança
        validador_xss       = ValidadorXSS()
        validador_script    = ValidadorScriptInjection(validador_xss)
        validador_sql       = ValidadorSQLInjection(validador_script)

        # Valida todos os campos
        for field in self._meta.fields:
            if field.name != 'id':
                value = getattr(self, field.name)
                if value:
                    # Valida o valor do campo usando o validador apropriado
                    validador_sql.validar(str(value), field.name)

    @classmethod
    def cadastrar(cls, dados_doador, dados_intencao=None):
        """
        Método de classe para cadastrar um doador.
        """
        try:
            doador = cls(**dados_doador)

            doador.full_clean()  # Valida o model
            doador, criado_doador = Doador.objects.update_or_create(
                cpf=dados_doador['cpf'], # Campo chave para identificar o doador
                defaults={k: v for k, v in dados_doador.items() if k != 'cpf'}
            )

            if dados_intencao:
                # Cria a intenção de doar associada ao doador

                orgaos = dados_intencao.pop('orgaos', None)  # Remove orgaos do dict para não passar no update_or_create
                
                intencao, _ = IntencaoDeDoar.objects.update_or_create(
                    doador=doador,
                    defaults=dados_intencao
                )
                if orgaos:
                    intencao.orgaos.set(orgaos)

            return doador, criado_doador, None  # Retorna o objeto, se foi criado e nenhum erro
        except ValidationError as e:
            return None, False, e.message_dict # Retorna None, False e os erros de validação
    
    def editar(doador, dados_intencao=None):
        """
        Método de classe para editar um doador.
        """
        try:
            doador.full_clean()  # Valida o model
            doador.save()  # Salva as alterações

            if dados_intencao:
                # Cria a intenção de doar associada ao doador

                orgaos = dados_intencao.pop('orgaos', None)  # Remove orgaos do dict para não passar no update_or_create
                
                intencao, _ = IntencaoDeDoar.objects.update_or_create(
                    doador=doador,
                    defaults=dados_intencao
                )
                if orgaos:
                    intencao.orgaos.set(orgaos)

            return doador, True, None  # Retorna o objeto e nenhum erro
        except ValidationError as e:
            return None, False, e.message_dict


class Orgao(models.Model):
    """
    Modelo para representar os tipos de órgãos que podem ser doados.
    """
    nome = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Órgão"
        verbose_name_plural = "Órgãos"

    def __str__(self):
        return self.nome
    

class IntencaoDeDoar(models.Model):

    doador = models.OneToOneField(
        Doador, 
        on_delete=models.CASCADE, 
        related_name='intencao_doar'
    ) 
    # OneToOneField para garantir 1 intenção por doador
    # models.CASCADE: se o objeto referenciado for deletado, 
    # todos os objetos que têm essa referência também serão 
    # deletados automaticamente.

    data_intencao = models.DateField(auto_now_add=True) # Data da criação da intenção
    
    status = models.CharField(max_length=10, choices=[('Ativa', 'Ativa'), ('Inativa', 'Inativa'), ('Concluída', 'Concluída')], default='Ativa')

    # Novo campo para indicar se o doador tem intenção de doar agora
    doar_agora = models.BooleanField(default=False)
    
    # Novo campo para armazenar os órgãos que o doador deseja doar
    orgaos = models.ManyToManyField(Orgao, blank=True, null=True) # blank=True permite que não haja órgãos selecionados

    class Meta:
        verbose_name = "Intenção de Doar"
        verbose_name_plural = "Intenções de Doar"

    def __str__(self):
        return f"Intenção de {self.doador.nome} - Status: {self.status}"
    