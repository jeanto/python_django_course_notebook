import json
from django.shortcuts import render, redirect, get_object_or_404
from django.core.management import call_command
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from .forms import ImportarDoadoresForm, CadastrarDoadorForm, BRAZILIAN_STATES_AND_CITIES
from .models import Doador, IntencaoDeDoar  # Importe o model Doador
import os
from datetime import date

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
        print(request.POST)
        form = CadastrarDoadorForm(request.POST or None)
        if form.is_valid():
            dados = form.cleaned_data

            # Lógica para 'Outra' profissão
            profissao_final = dados['profissao']
            if profissao_final == 'Outra' and dados.get('outra_profissao'):
                profissao_final = dados['outra_profissao']

            # Calcula a idade a partir da data de nascimento
            data_nascimento = dados['data_nascimento']
            idade = dados['idade']

            # Lógica para Intenção de Doar
            doar_agora = dados['doar_agora']
            orgaos_desejados = dados['orgaos_desejados']

            try:
                doador = {
                    "nome":dados['nome'],
                    "cpf":dados['cpf'],
                    "idade":idade,
                    "sexo":dados['sexo'],
                    "data_nascimento":data_nascimento,
                    "cidade_natal":dados['cidade_natal'],
                    "estado_natal":dados['estado_natal'],
                    "profissao":profissao_final,
                    "cidade_residencia":dados['cidade_residencia'],
                    "estado_residencia":dados['estado_residencia'],
                    "estado_civil":dados['estado_civil'],
                    "contato_emergencia":dados['contato_emergencia'],
                    "tipo_sanguineo":dados['tipo_sanguineo'],
                }

                if doar_agora:
                    intencao = {
                        "doar_agora": True,
                        "status": "ativa",  # Status inicial da intenção
                        "orgaos": orgaos_desejados,
                    }
                else:
                    try:
                        intencao = IntencaoDeDoar.objects.get(doador__cpf=dados['cpf'])
                        intencao.doar_agora = False  # Atualiza para não doar agora
                        intencao.status = "inativa"  # Atualiza o status para inativa
                        intencao.save()
                    except IntencaoDeDoar.DoesNotExist:
                        pass # Se não houver intenção, não faz nada

                doador, criado, erros = Doador.cadastrar(dados_doador=doador, dados_intencao=intencao if doar_agora else None)

                if not erros:
                    if criado:
                        messages.success(request, f'Doador "{doador.nome}" cadastrado com sucesso!')
                    else:
                        messages.success(request, f'Doador "{doador.nome}" atualizado com sucesso')
                else:
                    for field, error in erros.items():
                        messages.error(request, f'Erro: {error[0]}')

                return redirect('cadastrar_doador')
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar doador: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = CadastrarDoadorForm()


    contexto = {
        'form': form,
        'estados_cidades': json.dumps(BRAZILIAN_STATES_AND_CITIES)
    }

    return render(request, 'cadastrar_doador.html', contexto)


def editar_doador(request, doador_id):
    """
    Permite editar os dados de um doador existente.
    """
    doador = get_object_or_404(Doador, id=doador_id)

    if request.method == 'POST':
        form = CadastrarDoadorForm(request.POST, instance=doador)
        if form.is_valid():
            # Lógica para 'Outra' profissão (se aplicável)
            profissao_final = form.cleaned_data['profissao']
            if profissao_final == 'Outra' and form.cleaned_data.get('outra_profissao'):
                doador.profissao = form.cleaned_data['outra_profissao']
            else:
                doador.profissao = profissao_final

            # Atualiza os outros campos do doador com os dados do formulário
            doador.nome = form.cleaned_data['nome']
            doador.cpf = form.cleaned_data['cpf']
            doador.tipo_sanguineo = form.cleaned_data['tipo_sanguineo']
            doador.data_nascimento = form.cleaned_data['data_nascimento']
            doador.idade = form.cleaned_data['idade']
            doador.sexo = form.cleaned_data['sexo']
            doador.estado_natal = form.cleaned_data['estado_natal']
            doador.cidade_natal = form.cleaned_data['cidade_natal']
            doador.estado_residencia = form.cleaned_data['estado_residencia']
            doador.cidade_residencia = form.cleaned_data['cidade_residencia']
            doador.estado_civil = form.cleaned_data['estado_civil']
            doador.contato_emergencia = form.cleaned_data['contato_emergencia']

            # Lógica para Intenção de Doar
            doar_agora = form.cleaned_data['doar_agora']
            orgaos_desejados = form.cleaned_data['orgaos_desejados']

            if doar_agora:
                intencao = {
                    "doar_agora": True,
                    "status": "ativa",  # Status inicial da intenção
                    "orgaos": orgaos_desejados,
                }
            else:
                try:
                    intencao = IntencaoDeDoar.objects.get(doador__cpf=doador.cpf)
                    intencao.doar_agora = False  # Atualiza para não doar agora
                    intencao.status = "inativa"  # Atualiza o status para inativa
                    intencao.save()
                except IntencaoDeDoar.DoesNotExist:
                    pass # Se não houver intenção, não faz nada

            doador, criado, erros = Doador.editar(doador=doador, dados_intencao=intencao if doar_agora else None)

            if not erros:
                if criado:
                    messages.success(request, f'Doador "{doador.nome}" atualizado com sucesso!')
            else:
                for field, error in erros.items():
                    messages.error(request, f'Erro: {error[0]}')

            #return redirect('listar_doadores') # Redireciona para a lista após a edição
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        print(repr(doador.data_nascimento))
        form = CadastrarDoadorForm(instance=doador) # Preenche o formulário com os dados do doador

    contexto = {
        'form': form,
        'doador': doador, # Passa o objeto doador para o template
        'estados_cidades': json.dumps(BRAZILIAN_STATES_AND_CITIES)
    }
    return render(request, 'editar_doador.html', contexto)

def deletar_doador(request, doador_id):
    """
    Permite deletar um doador existente.
    """
    doador = get_object_or_404(Doador, id=doador_id)

    if request.method == 'POST':
        doador_nome = doador.nome # Salva o nome antes de deletar para a mensagem
        doador.delete()
        messages.success(request, f'Doador "{doador_nome}" deletado com sucesso!')
        return redirect('listar_doadores')  # Redireciona para a lista após a exclusão

    # Para requisições GET para a URL de delete, redireciona para a lista
    # ou para a página de edição com uma mensagem de erro, se preferir.
    messages.error(request, 'Método não permitido para exclusão direta. Use o formulário de edição.')
    return redirect('listar_doadores')

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
        doadores_lista = Doador.objects.all().order_by('nome')

    doadores_lista = doadores_lista.values(
        'id',
        'nome',
        'cpf',
        'idade',
        'data_nascimento',
        'cidade_residencia',
        'estado_residencia',
        'tipo_sanguineo',
        'contato_emergencia',            
    )

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

def importar_receptores(request):
    return render(request, 'importar_receptores.html')

def cadastrar_receptor(request):
    return render(request, 'cadastrar_receptor.html')

def listar_receptores(request):
    return render(request, 'listar_receptores.html')

def registrar_doacao(request):
    return render(request, 'registrar_doacao.html')

def visualizar_historico_doacoes(request):
    return render(request, 'visualizar_historico_doacoes.html')

def acesso_restrito(request): # Crie esta view
    return render(request, 'acesso_restrito.html')