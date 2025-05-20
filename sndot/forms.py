from django import forms
from .models import Doador  # Importe o model Doador

class ImportarDoadoresForm(forms.Form):
    json_file = forms.FileField(
        label='Arquivo JSON',
        widget=forms.FileInput(attrs={'accept': '.json'})
    )

# Define Brazilian states and their cities
# This data will be passed to the frontend via json_script
BRAZILIAN_STATES_AND_CITIES = {
    "AC": ["Rio Branco", "Cruzeiro do Sul"],
    "AL": ["Maceió", "Arapiraca"],
    "AM": ["Manaus", "Parintins"],
    "AP": ["Macapá", "Santana"],
    "BA": ["Salvador", "Feira de Santana"],
    "CE": ["Fortaleza", "Caucaia"],
    "DF": ["Brasília"],
    "ES": ["Vitória", "Vila Velha"],
    "GO": ["Goiânia", "Aparecida de Goiânia"],
    "MA": ["São Luís", "Imperatriz"],
    "MG": ["Belo Horizonte", "Uberlândia", "Contagem"],
    "MS": ["Campo Grande", "Dourados"],
    "MT": ["Cuiabá", "Várzea Grande"],
    "PA": ["Belém", "Ananindeua"],
    "PB": ["João Pessoa", "Campina Grande"],
    "PE": ["Recife", "Jaboatão dos Guararapes"],
    "PI": ["Teresina", "Parnaíba"],
    "PR": ["Curitiba", "Londrina", "Maringá"],
    "RJ": ["Rio de Janeiro", "Niterói", "Duque de Caxias"],
    "RN": ["Natal", "Mossoró"],
    "RO": ["Porto Velho", "Ji-Paraná"],
    "RR": ["Boa Vista"],
    "RS": ["Porto Alegre", "Caxias do Sul", "Canoas"],
    "SC": ["Florianópolis", "Joinville", "Blumenau"],
    "SE": ["Aracaju", "Nossa Senhora do Socorro"],
    "SP": ["São Paulo", "Campinas", "Guarulhos", "São Bernardo do Campo"],
    "TO": ["Palmas", "Araguaína"]
}

# Create choices for states
STATE_CHOICES = [('', 'Selecione o Estado')] + [(uf, uf) for uf in sorted(BRAZILIAN_STATES_AND_CITIES.keys())]

# Choices for Sexo
SEXO_CHOICES = [
    ('', 'Selecione'),
    ('M', 'Masculino'),
    ('F', 'Feminino')
]

# Choices for Tipo Sanguíneo
TIPO_SANGUINEO_CHOICES = [
    ('', 'Selecione'),
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
    ('O+', 'O+'), ('O-', 'O-')
]

# Choices for Profissão
PROFISSAO_CHOICES = [
    ('', 'Selecione'),
    ('Engenheiro', 'Engenheiro'),
    ('Médico', 'Médico'),
    ('Professor', 'Professor'),
    ('Estudante', 'Estudante'),
    ('Aposentado', 'Aposentado'),
    ('Outra', 'Outra')
]

# Choices for Estado Civil
ESTADO_CIVIL_CHOICES = [
    ('', 'Selecione'),
    ('Solteiro', 'Solteiro'),
    ('Casado', 'Casado'),
    ('Divorciado', 'Divorciado'),
    ('Viuvo', 'Viúvo'),
    ('União Estável', 'União Estável')
]


class CadastrarDoadorForm(forms.ModelForm):
    # Campos de estado agora são ChoiceFields com opções predefinidas
    estado_natal = forms.ChoiceField(choices=STATE_CHOICES, label="Estado Natal")
    estado_residencia = forms.ChoiceField(choices=STATE_CHOICES, label="Estado de Residência")

    # Campos de cidade não são obrigatórios no formulário Django, pois serão validados pelo JS
    # e pelo método clean do formulário se o estado for selecionado.
    cidade_natal = forms.CharField(max_length=100, required=False, label="Cidade Natal")
    cidade_residencia = forms.CharField(max_length=100, required=False, label="Cidade de Residência")

    # Campo para "Outra Profissão" que não está no modelo
    outra_profissao = forms.CharField(max_length=100, required=False)

    class Meta:
        model = Doador
        fields = [
            'cpf', 'nome', 'tipo_sanguineo', 'data_nascimento', 'idade', 'sexo',
            'profissao', 'estado_natal', 'cidade_natal', 'estado_residencia',
            'cidade_residencia', 'estado_civil', 'contato_emergencia'
        ]
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'idade': forms.HiddenInput(), # Oculta o campo idade no formulário
        }

    # Sobrescrevendo os campos para usar as CHOICES definidas
    sexo = forms.ChoiceField(choices=SEXO_CHOICES, label="Sexo")
    tipo_sanguineo = forms.ChoiceField(choices=TIPO_SANGUINEO_CHOICES, label="Tipo Sanguíneo")
    profissao = forms.ChoiceField(choices=PROFISSAO_CHOICES, label="Profissão")
    estado_civil = forms.ChoiceField(choices=ESTADO_CIVIL_CHOICES, label="Estado Civil")


    def clean(self):
        dados_validados = super().clean()
        profissao = dados_validados.get('profissao')
        outra_profissao = dados_validados.get('outra_profissao')

        # Lógica para "Outra Profissão"
        if profissao == 'Outra' and not outra_profissao:
            self.add_error('outra_profissao', 'Por favor, especifique a outra profissão.')
        elif profissao == 'Outra' and outra_profissao:
            dados_validados['profissao'] = outra_profissao

        # Validação para cidades se o estado foi selecionado
        estado_natal = dados_validados.get('estado_natal')
        cidade_natal = dados_validados.get('cidade_natal')
        if estado_natal and not cidade_natal:
            self.add_error('cidade_natal', 'Cidade natal é obrigatória quando o estado é selecionado.')

        estado_residencia = dados_validados.get('estado_residencia')
        cidade_residencia = dados_validados.get('cidade_residencia')
        if estado_residencia and not cidade_residencia:
            self.add_error('cidade_residencia', 'Cidade de residência é obrigatória quando o estado é selecionado.')

        return dados_validados