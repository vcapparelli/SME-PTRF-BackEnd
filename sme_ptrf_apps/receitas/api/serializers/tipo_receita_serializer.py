from rest_framework import serializers

from .detalhe_tipo_receita_serializer import DetalheTipoReceitaSerializer
from ...models import TipoReceita


class TipoReceitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoReceita
        fields = ('id', 'nome', 'e_repasse', 'aceita_capital', 'aceita_custeio', 'aceita_livre', 'e_devolucao')


class TipoReceitaEDetalhesSerializer(serializers.ModelSerializer):
    detalhes_tipo_receita = DetalheTipoReceitaSerializer(many=True)
    class Meta:
        model = TipoReceita
        fields = ('id', 'nome', 'e_repasse', 'aceita_capital', 'aceita_custeio', 'aceita_livre', 'detalhes_tipo_receita', 'e_devolucao')
