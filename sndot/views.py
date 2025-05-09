import json
from django.shortcuts import render, redirect
from django.core.management import call_command
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from .forms import ImportarDoadoresForm
from .models import Doador  # Importe o model Doador
import os

def index(request):
    return render(request, 'index.html')

def importar_doadores_view(request):
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
    return render(request, 'cadastrar_doador.html')

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
        doadores_lista = Doador.objects.all()  # Recupera todos os doadores

    # Cria um objeto Paginator com a lista de doadores filtrada
    paginator = Paginator(doadores_lista, 5)  # doadores por página

    # Obtém o número da página da requisição
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page) # Alterado para page_obj
    except PageNotAnInteger:
        # Se a página não for um inteiro, exibe a primeira página.
        page_obj = paginator.page(1)
    except EmptyPage:
        # Se a página estiver fora do intervalo, exibe a última página de resultados.
        page_obj = paginator.page(paginator.num_pages)

    # Renderiza o template com os dados dos doadores e o valor do filtro de CPF
    return render(request, 'listar_doadores.html', {'page_obj': page_obj, 'cpf': cpf}) # Alterado para page_obj

def cadastrar_receptor(request):
    return render(request, 'cadastrar_receptor.html')

def atualizar_dados_receptor(request):
    return render(request, 'atualizar_dados_receptor.html')

def visualizar_situacao_receptor(request):
    return render(request, 'visualizar_situacao_receptor.html')

def registrar_doacao_view(request):
    return render(request, 'registrar_doacao.html')

def visualizar_historico_doacoes(request):
    return render(request, 'visualizar_historico_doacoes.html')

def acesso_restrito(request): # Crie esta view
    return render(request, 'acesso_restrito.html')