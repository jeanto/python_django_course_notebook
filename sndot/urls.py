from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('doadores/importar/', views.importar_doadores, name='importar_doadores'),
    path('doadores/cadastrar/', views.cadastrar_doador, name='cadastrar_doador'),
    path('doadores/editar/<int:doador_id>/', views.editar_doador, name='editar_doador'),
    path('doadores/deletar/<int:doador_id>/', views.deletar_doador, name='deletar_doador'),
    path('doadores/listar/', views.listar_doadores, name='listar_doadores'),
    path('receptores/importar/', views.importar_receptores, name='importar_receptores'),
    path('receptores/cadastrar/', views.cadastrar_receptor, name='cadastrar_receptor'),
    path('receptores/listar/', views.listar_receptores, name='listar_receptores'),
    path('doacoes/registrar/', views.registrar_doacao, name='registrar_doacao'),
    path('doacoes/historico/', views.visualizar_historico_doacoes, name='visualizar_historico_doacoes'),
    path('acesso_restrito/', views.acesso_restrito, name='acesso_restrito'), # Adicione esta linha
]