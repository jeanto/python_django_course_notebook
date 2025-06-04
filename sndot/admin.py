from django.contrib import admin

# Register your models here.
from .models import Doador, IntencaoDeDoar, Orgao

class IntencaoDeDoarInline(admin.StackedInline):
    model = IntencaoDeDoar
    extra = 0
    show_change_link = True
    filter_horizontal = ('orgaos',)  # Se quiser facilitar a seleção de órgãos


@admin.register(Doador)
class DoadorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'idade', 'tipo_sanguineo', 'tem_intencao_doar', 'orgaos_desejados')
    list_display_links = ('nome',)
    search_fields = ('nome', 'cpf')
    list_filter = ('tipo_sanguineo',)
    list_per_page = 10
    ordering = ('nome',)
    inlines = [IntencaoDeDoarInline]

    def tem_intencao_doar(self, obj):
        return hasattr(obj, 'intencao_doar') and obj.intencao_doar is not None
    tem_intencao_doar.short_description = 'Intenção de Doar?'
    tem_intencao_doar.boolean = True

    def orgaos_desejados(self, obj):
        if hasattr(obj, 'intencao_doar') and obj.intencao_doar is not None:
            return ", ".join([str(orgao) for orgao in obj.intencao_doar.orgaos.all()])
        return "-"
    orgaos_desejados.short_description = 'Órgãos Desejados'