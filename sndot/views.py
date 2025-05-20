import json
from django.shortcuts import render, redirect
from django.core.management import call_command
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from .forms import ImportarDoadoresForm, CadastrarDoadorForm, BRAZILIAN_STATES_AND_CITIES
from .models import Doador  # Importe o model Doador
import os

def index(request):
    return render(request, 'index.html')

def importar_doadores(request):
    if request.method == 'POST':
        form = ImportarDoadoresForm(request.POST, request.FILES)
        if form.is_valid():
            json_file = request.FILES['json_file']
            try:
                # Salva o arquivo JSON no diretório correto
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                json_file_path = os.path.join(base_dir, 'dados_json', json_file.name)

                with open(json_file_path, 'wb') as f:
                    for chunk in json_file.chunks():
                        f.write(chunk)

                # Chama a management command para importar os dados
                call_command('import_doadores', json_file_path)
                messages.success(request, 'Doadores importados com sucesso!')
                return redirect('listar_doadores')  # Redireciona para a página de listagem
            except json.JSONDecodeError:
                messages.error(request, 'Erro ao decodificar o arquivo JSON. Verifique se o arquivo está no formato correto.')
            except Exception as e:
                messages.error(request, f'Ocorreu um erro durante a importação: {e}')
        else:
            messages.error(request, 'Por favor, selecione um arquivo JSON válido.')
    else:
        form = ImportarDoadoresForm()
    return render(request, 'importar_doadores.html', {'form': form})


def cadastrar_doador(request):
    """
    View para cadastrar um novo doador.
    Lida com a exibição do formulário (GET) e o processamento dos dados (POST).
    """
    if request.method == 'POST':
        form = CadastrarDoadorForm(request.POST)
        if form.is_valid():
            # Os dados do formulário estão limpos e validados pelo Django Forms.
            # Agora, vamos lidar com a lógica de 'Outra' profissão e a idade calculada.

            # Lógica para 'Outra' profissão
            profissao_final = form.dados_validados['profissao']
            if profissao_final == 'Outra' and form.dados_validados.get('outra_profissao'):
                profissao_final = form.dados_validados['outra_profissao']

            # A idade é calculada no frontend e passada como um campo oculto.
            # Precisamos pegá-la diretamente do request.POST, pois não é um campo do ModelForm.
            idade_calculada = request.POST.get('idade')
            if idade_calculada:
                try:
                    idade_calculada = int(idade_calculada)
                except ValueError:
                    messages.error(request, 'Erro: Idade calculada inválida. Por favor, verifique a data de nascimento.')
                    return render(request, 'cadastrar_doador.html', {'form': form})
            else:
                messages.error(request, 'Erro: Idade não foi calculada no frontend. Por favor, verifique a data de nascimento.')
                return render(request, 'cadastrar_doador.html', {'form': form})

            try:
                # Chama o método de classe cadastrar do Doador, que usa o Factory Method
                # e a Chain of Responsibility para validação.
                doador = Doador.cadastrar(
                    nome=form.dados_validados['nome'],
                    idade=idade_calculada, # Usar a idade calculada
                    sexo=form.dados_validados['sexo'],
                    data_nascimento=form.dados_validados['data_nascimento'], # data_nascimento já é um objeto date
                    cidade_natal=form.dados_validados['cidade_natal'],
                    estado_natal=form.dados_validados['estado_natal'],
                    cpf=form.dados_validados['cpf'],
                    profissao=profissao_final, # Usar a profissão final
                    cidade_residencia=form.dados_validados['cidade_residencia'],
                    estado_residencia=form.dados_validados['estado_residencia'],
                    estado_civil=form.dados_validados['estado_civil'],
                    contato_emergencia=form.dados_validados['contato_emergencia'],
                    tipo_sanguineo=form.dados_validados['tipo_sanguineo']
                )
                messages.success(request, f'Doador "{doador.nome}" cadastrado com sucesso!')
                return redirect('listar_doadores') # Redireciona para a lista de doadores
            except Exception as e:
                # Captura exceções da validação do Model (Chain of Responsibility) ou outras.
                messages.error(request, f'Erro ao cadastrar doador: {e}')
        else:
            # Se o formulário não for válido, os erros serão exibidos no template
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = CadastrarDoadorForm() # Cria um formulário vazio para requisições GET

    # Este contexto é crucial para que o JavaScript receba os dados de estados/cidades
    contexto = {
        'form': form,
        'estados_cidades_json': json.dumps(BRAZILIAN_STATES_AND_CITIES)
    }

    return render(request, 'cadastrar_doador.html', contexto)


def atualizar_dados_doador(request):
    return render(request, 'atualizar_dados_doador.html')

def registrar_intencao(request):
    return render(request, 'registrar_intencao.html')

def listar_doadores(request):
    """
    View para listar doadores com paginação e filtro por CPF.
    """
    # Recupera o valor do CPF do parâmetro GET da requisição
    cpf = request.GET.get('cpf')

    # Filtra os doadores por CPF, se o parâmetro for fornecido
    if cpf:
        doadores_lista = Doador.objects.filter(cpf=cpf)
    else:
        doadores_lista = Doador.objects.all().order_by('nome')  # Recupera todos os doadores

    # Cria um objeto Paginator com a lista de doadores filtrada
    paginator = Paginator(doadores_lista, 5)  # doadores por página

    # Obtém o número da página da requisição
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        # Se a página não for um inteiro, exibe a primeira página.
        page_obj = paginator.page(1)
    except EmptyPage:
        # Se a página estiver fora do intervalo, exibe a última página de resultados.
        page_obj = paginator.page(paginator.num_pages)

    # Renderiza o template com os dados dos doadores e o valor do filtro de CPF
    return render(request, 'listar_doadores.html', {'page_obj': page_obj, 'cpf': cpf})

def cadastrar_receptor(request):
    return render(request, 'cadastrar_receptor.html')

def atualizar_dados_receptor(request):
    return render(request, 'atualizar_dados_receptor.html')

def visualizar_situacao_receptor(request):
    return render(request, 'visualizar_situacao_receptor.html')

def registrar_doacao(request):
    return render(request, 'registrar_doacao.html')

def visualizar_historico_doacoes(request):
    return render(request, 'visualizar_historico_doacoes.html')

def acesso_restrito(request): # Crie esta view
    return render(request, 'acesso_restrito.html')