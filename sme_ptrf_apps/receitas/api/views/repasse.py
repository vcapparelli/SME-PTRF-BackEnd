from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.viewsets import GenericViewSet

from ...models import Repasse
from ..serializers import RepasseSerializer


class RepasseViewSet(GenericViewSet):

    @action(detail=False, methods=['GET'])
    def pendentes(self, request, *args, **kwargs):
        acao_associacao_uuid = self.request.query_params.get('acao-associacao')
        edit = self.request.query_params.get('edit')
        if not acao_associacao_uuid:
            return Response("uuid da ação-associação não foi passado", status=HTTP_400_BAD_REQUEST)
        
        status = ['PENDENTE']
        if edit:
            status.append('REALIZADO')

        repasse = Repasse.objects\
            .filter(acao_associacao__uuid=acao_associacao_uuid, status__in=status)\
            .order_by('-criado_em').last()
        
        if not repasse:
            return Response(f"Repasse não encontrado para ação-associação {acao_associacao_uuid}", status=HTTP_404_NOT_FOUND)

        serializer = RepasseSerializer(repasse)
        return Response(serializer.data)
