from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    #path('doadores/importar/', views.importar_doadores, name='importar_doadores'),
    path('doadores/importar/', views.importar_doadores_view, name='importar_doadores'),
    path('doadores/cadastrar/', views.cadastrar_doador, name='cadastrar_doador'),
    path('doadores/atualizar/', views.atualizar_dados_doador, name='atualizar_dados_doador'),
    path('doadores/intencao/', views.registrar_intencao, name='intencao_doador'),
    path('doadores/listar/', views.listar_doadores, name='listar_doadores'),
    path('receptores/cadastrar/', views.cadastrar_receptor, name='cadastrar_receptor'),
    path('receptores/atualizar/', views.atualizar_dados_receptor, name='atualizar_dados_receptor'),
    path('receptores/situacao/', views.visualizar_situacao_receptor, name='visualizar_situacao_receptor'),
    path('doacoes/registrar/', views.registrar_doacao_view, name='registrar_doacao'),
    path('doacoes/historico/', views.visualizar_historico_doacoes, name='visualizar_historico_doacoes'),
    path('acesso_restrito/', views.acesso_restrito, name='acesso_restrito'), # Adicione esta linha
]