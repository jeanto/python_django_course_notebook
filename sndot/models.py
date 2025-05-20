from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, ValidationError
from .validador import ValidadorNome, ValidadorIdade, ValidadorSexo, ValidadorEstadoCivil, ValidadorTipoSanguineo # Importe os validadores do arquivo validators.py


def validar_cpf(value):
    """Função para validar o CPF."""
    # Remove caracteres não numéricos
    cpf = ''.join(filter(str.isdigit, value))
    if len(cpf) != 11:
        raise ValidationError("CPF deve ter 11 dígitos.")
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
    return value

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
    estado_natal = models.CharField(max_length=50)
    cpf = models.CharField(max_length=14, unique=True, validators=[validar_cpf])
    profissao = models.CharField(max_length=100, blank=True, null=True)
    cidade_residencia = models.CharField(max_length=100)
    estado_residencia = models.CharField(max_length=50)
    estado_civil = models.CharField(max_length=50, blank=True, null=True)

    # O método clean() no Django é usado para validação personalizada de modelos. 
    # Ele permite que você defina regras de validação além das validações 
    # padrão dos campos. O Django chama esse método quando você usa full_clean() 
    # em uma instância do modelo, geralmente antes de salvar no banco de dados.
    def clean(self):
        super().clean()
        validador_nome = ValidadorNome()
        validador_idade = ValidadorIdade(validador_nome)
        validador_sexo = ValidadorSexo(validador_idade)

        validador_nome.validar(self.nome, 'Nome')
        validador_idade.validar(self.idade, 'Idade')
        validador_sexo.validar(self.sexo, 'Sexo')

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

class Doador(Pessoa):
    contato_emergencia = models.CharField(max_length=255)
    tipo_sanguineo = models.CharField(max_length=5, choices=[
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O-'), ('O-', 'O-')
    ])
    # cpf = models.CharField(max_length=14, unique=True, validators=[validar_cpf]) # Usa o validador customizado

    def clean(self):
        super().clean()
        validador_estado_civil = ValidadorEstadoCivil()
        validador_tipo_sanguineo = ValidadorTipoSanguineo(validador_estado_civil)
        validador_estado_civil.validar(self.estado_civil, 'Estado Civil')
        validador_tipo_sanguineo.validar(self.tipo_sanguineo, 'Tipo Sanguíneo')

    @classmethod
    def cadastrar(cls, nome, idade, sexo, data_nascimento, cidade_natal, estado_natal, cpf, profissao, cidade_residencia, estado_residencia, estado_civil, contato_emergencia, tipo_sanguineo):
        """
        Método de classe para cadastrar um doador.
        """
        doador = cls(
            nome=nome,
            idade=idade,
            sexo=sexo,
            data_nascimento=data_nascimento,
            cidade_natal=cidade_natal,
            estado_natal=estado_natal,
            cpf=cpf,
            profissao=profissao,
            cidade_residencia=cidade_residencia,
            estado_residencia=estado_residencia,
            estado_civil=estado_civil,
            contato_emergencia=contato_emergencia,
            tipo_sanguineo=tipo_sanguineo,
        )
        doador.full_clean()  # Valida o model
        doador.save()  # Salva o doador no banco de dados
        return doador