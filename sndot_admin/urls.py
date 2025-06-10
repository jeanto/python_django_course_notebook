from django.urls import path
from . import views

app_name = 'sndot_admin' # Define o namespace do app

urlpatterns = [
    path('login/', views.logar, name='login'),
    path('logout/', views.logout, name='logout'),
    path('painel-admin/', views.painel_admin, name='painel_admin'),
]