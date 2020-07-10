from sme_ptrf_apps.core.models.arquivo import CARGA_PERIODO_INICIAL, CARGA_REPASSE_REALIZADO
from sme_ptrf_apps.receitas.services.carga_repasses_realizados import carrega_repasses
from sme_ptrf_apps.core.services.periodo_inicial import carrega_periodo_inicial


def processa_cargas(queryset):
    for arquivo in queryset.all():
        if arquivo.tipo_carga == CARGA_REPASSE_REALIZADO:
            carrega_repasses(arquivo)
        elif arquivo.tipo_carga == CARGA_PERIODO_INICIAL:
            carrega_periodo_inicial(arquivo)
