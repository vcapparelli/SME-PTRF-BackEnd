from datetime import datetime

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.core.models import Periodo
from ...models import Repasse, Receita
from ..serializers import RepasseSerializer


class RepasseViewSet(GenericViewSet):

    @action(detail=False, methods=['GET'])
    def pendentes(self, request, *args, **kwargs):
        acao_associacao_uuid = self.request.query_params.get('acao-associacao')
        receita_uuid = self.request.query_params.get('uuid-receita')
        data_str = self.request.query_params.get('data')
        
        if not acao_associacao_uuid or not data_str:
            return Response("uuid da ação-associação e data são obrigatórios", status=HTTP_400_BAD_REQUEST)
        
        data = datetime.strptime(data_str, '%d/%m/%Y')
        periodo = Periodo.da_data(data)

        if not receita_uuid:
            """Em conversa com o time ficou definido que não deve existir repasse
            pendente para a mesma ação associação no mesmo período.
            Então o trecho abaixo não tem problema."""
            repasse = Repasse.objects\
            .filter(
                acao_associacao__uuid=acao_associacao_uuid, 
                periodo=periodo,
                status='PENDENTE')\
            .order_by('-criado_em').last()
        else:
            try:
                receita = Receita.objects.get(uuid=receita_uuid)
                repasse = receita.repasse

                if repasse.acao_associacao.uuid != acao_associacao_uuid:
                    """Caso o usuário troque para uma ação associação diferente do que está vinculado a receita
                    que está sendo editada."""
                    repasse = Repasse.objects\
                    .filter(
                        acao_associacao__uuid=acao_associacao_uuid, 
                        periodo=periodo,
                        status='PENDENTE')\
                    .order_by('-criado_em').last()

            except Receita.DoesNotExist as e:
                return Response("Repasse não encontrado para receita {receita.uuid}.", status=HTTP_400_BAD_REQUEST)
        
        if not repasse:
            return Response(f"Repasse não encontrado para ação-associação {acao_associacao_uuid} e para o periodo {periodo}.", status=HTTP_404_NOT_FOUND)

        serializer = RepasseSerializer(repasse)
        return Response(serializer.data)
