from ..models import Mandato
from datetime import date
from django.db.models import Q

class ServicoMandatoVigente:
    def get_mandato_vigente(self):
        data_atual = date.today()

        # Filtrar os mandatos com data_inicial anterior ou igual à data atual
        qs = Mandato.objects.filter(data_inicial__lte=data_atual)

        # Filtrar os mandatos com data_final posterior ou igual à data atual OU sem data_final definida
        qs = qs.filter(Q(data_final__gte=data_atual) | Q(data_final__isnull=True))

        # Verificar se há mais de um mandato vigente, e caso haja, retornar o último (o mais recente)
        mandato_vigente = qs.last()

        return mandato_vigente
