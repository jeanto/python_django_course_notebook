from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.

def painel_admin(request):
    """
    View para a página administrativa.
    Aqui você pode adicionar lógica para exibir dados administrativos,
    como estatísticas, gráficos, etc.
    """
    # Exemplo de lógica para exibir dados administrativos
    # Você pode substituir isso por qualquer lógica que desejar
    context = {
        'titulo': 'Painel Administrativo',
        'mensagem': 'Bem-vindo ao painel administrativo!'
    }
    return render(request, 'admin.html', context)

def logar(request):
    """
    View para a tela de login administrativo.
    Lida com a exibição do formulário de login (GET)
    e com a autenticação do usuário (POST).
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Tenta autenticar o usuário
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Se o usuário for autenticado, faça o login
            login(request, user)
            messages.success(request, f'Bem-vindo, {user.username}!')
            return redirect('sndot_admin:painel_admin')
        else:
            # Se a autenticação falhar
            messages.error(request, 'Nome de usuário ou senha inválidos.')
    
    # Renderiza a página de login para requisições GET ou falha de POST
    return render(request, 'login.html')

def logout(request):
    """
    View para realizar o logout do usuário administrativo.
    """
    logout(request)
    messages.info(request, 'Você foi desconectado.')
    return redirect('sndot_admin:login') # Redireciona de volta para a tela de login
