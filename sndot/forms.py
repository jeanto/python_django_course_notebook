from django import forms
from .models import Doador, Orgao  # Importe o model Doador
from datetime import datetime

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
    ('Viuvo', 'Viuvo'),
    ('Uniao Estavel', 'Uniao Estavel')
]


class CadastrarDoadorForm(forms.ModelForm):
    # 'outra_profissao' é um campo extra do formulário, não diretamente do modelo
    outra_profissao = forms.CharField(label='Outra Profissão', max_length=100, required=False)
    idade = forms.IntegerField(label='Idade', required=False, widget=forms.HiddenInput())

    # Novos campos para Intenção de Doar
    doar_agora = forms.BooleanField(label="Tenho intenção de doar agora", required=False)
    orgaos_desejados = forms.ModelMultipleChoiceField(
        queryset=Orgao.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Quais órgãos deseja doar"
    )

    class Meta:
        model = Doador
        fields = [
            'cpf', 'nome', 'tipo_sanguineo', 'data_nascimento', 'idade', 'sexo',
            'profissao', 'estado_natal', 'cidade_natal', 'estado_residencia',
            'cidade_residencia', 'estado_civil', 'contato_emergencia'
        ]
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'sexo': forms.Select(choices=SEXO_CHOICES),
            'tipo_sanguineo': forms.Select(choices=TIPO_SANGUINEO_CHOICES),
            'profissao': forms.Select(choices=PROFISSAO_CHOICES),
            'estado_civil': forms.Select(choices=ESTADO_CIVIL_CHOICES),
            'estado_natal': forms.Select(choices=STATE_CHOICES),
            'estado_residencia': forms.Select(choices=STATE_CHOICES),
            # As cidades não têm choices fixas aqui, pois são preenchidas dinamicamente no __init__
            # e são CharField no modelo.
        }
        labels = {
            'cpf': 'CPF',
            'nome': 'Nome',
            'sexo': 'Sexo',
            'tipo_sanguineo': 'Tipo Sanguíneo',
            'data_nascimento': 'Data de Nascimento',
            'estado_civil': 'Estado Civil',
            'estado_natal': 'Estado Natal',
            'cidade_natal': 'Cidade Natal',
            'estado_residencia': 'Estado de Residência',
            'cidade_residencia': 'Cidade de Residência',
            'contato_emergencia': 'Contato de Emergência',
            'profissao': 'Profissão',
        }

    def __init__(self, *args, **kwargs):

        # Popula os campos de Intenção de Doar se uma instância de Doador for passada
        # (usado na edição de doador)
        doador_instance = kwargs.get('instance')
        if doador_instance and doador_instance.pk:
            try:
                intencao = doador_instance.intencao_doar
                initial_doar_agora = intencao.doar_agora
                initial_orgaos_desejados = intencao.orgaos.all()
                kwargs['initial'] = kwargs.get('initial', {})
                kwargs['initial']['doar_agora'] = initial_doar_agora
                kwargs['initial']['orgaos_desejados'] = initial_orgaos_desejados
            except doador_instance._meta.model.intencao_doar.RelatedObjectDoesNotExist:
                # Nenhuma intenção de doar existente para este doador
                pass

        super().__init__(*args, **kwargs)

        # Aplica uma classe CSS padrão a todos os inputs, a menos que já tenham uma classe definida
        for field_name, field in self.fields.items():
            # Exclui campos de checkbox de ter a classe padrão aplicada automaticamente
            if not isinstance(field.widget, forms.CheckboxInput) and \
               not isinstance(field.widget, forms.CheckboxSelectMultiple):
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'

        # Lógica para popular dinamicamente os choices de cidade_natal e cidade_residencia
        # Obtém os dados do formulário (POST) ou os dados iniciais (GET, instance)
        data = self.data if self.data else self.initial

        # Para cidade_natal
        estado_natal_value = data.get('estado_natal')
        if estado_natal_value and estado_natal_value in BRAZILIAN_STATES_AND_CITIES:
            cidades = BRAZILIAN_STATES_AND_CITIES[estado_natal_value]
            self.fields['cidade_natal'].choices = [('', 'Selecione a Cidade')] + [(c, c) for c in cidades]
            # Se houver um valor inicial para cidade_natal e ele não estiver nas opções atuais, adicione-o
            if data.get('cidade_natal') and data.get('cidade_natal') not in [c for c, _ in self.fields['cidade_natal'].choices]:
                self.fields['cidade_natal'].choices.append((data.get('cidade_natal'), data.get('cidade_natal')))
        else:
            self.fields['cidade_natal'].choices = [('', 'Selecione a Cidade')]
            self.fields['cidade_natal'].widget.attrs['disabled'] = 'disabled' # Desabilita se não houver estado

        # Para cidade_residencia
        estado_residencia_value = data.get('estado_residencia')
        if estado_residencia_value and estado_residencia_value in BRAZILIAN_STATES_AND_CITIES:
            cidades = BRAZILIAN_STATES_AND_CITIES[estado_residencia_value]
            self.fields['cidade_residencia'].choices = [('', 'Selecione a Cidade')] + [(c, c) for c in cidades]
            # Se houver um valor inicial para cidade_residencia e ele não estiver nas opções atuais, adicione-o
            if data.get('cidade_residencia') and data.get('cidade_residencia') not in [c for c, _ in self.fields['cidade_residencia'].choices]:
                self.fields['cidade_residencia'].choices.append((data.get('cidade_residencia'), data.get('cidade_residencia')))
        else:
            self.fields['cidade_residencia'].choices = [('', 'Selecione a Cidade')]
            self.fields['cidade_residencia'].widget.attrs['disabled'] = 'disabled' # Desabilita se não houver estado


    def clean(self):
        cleaned_data = super().clean()
        profissao = cleaned_data.get('profissao')
        outra_profissao = cleaned_data.get('outra_profissao')

        # Lógica para "Outra Profissão"
        if profissao == 'Outra' and not outra_profissao:
            self.add_error('outra_profissao', 'Por favor, informe a outra profissão.')
        elif profissao == 'Outra' and outra_profissao:
            # Se 'Outra' for selecionada e 'outra_profissao' preenchida,
            # use o valor de 'outra_profissao' para o campo 'profissao' do modelo.
            cleaned_data['profissao'] = outra_profissao

        # Validação para cidades se o estado foi selecionado
        estado_natal = cleaned_data.get('estado_natal')
        cidade_natal = cleaned_data.get('cidade_natal')
        if estado_natal and not cidade_natal:
            self.add_error('cidade_natal', 'Cidade natal é obrigatória quando o estado é selecionado.')

        estado_residencia = cleaned_data.get('estado_residencia')
        cidade_residencia = cleaned_data.get('cidade_residencia')
        if estado_residencia and not cidade_residencia:
            self.add_error('cidade_residencia', 'Cidade de residência é obrigatória quando o estado é selecionado.')

        # Validação para idade
        data_nascimento = cleaned_data.get('data_nascimento')
        if data_nascimento:
            idade = (datetime.now().date() - data_nascimento).days // 365
            cleaned_data['idade'] = idade
        else:
            cleaned_data['idade'] = None

        return cleaned_data
