from django.contrib import admin

# Register your models here.
from .models import Doador

@admin.register(Doador)
class DoadorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'idade', 'tipo_sanguineo')
    search_fields = ('nome', 'cpf')