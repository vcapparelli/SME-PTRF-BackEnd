import pytest
from datetime import date

from model_bakery import baker

from ...api.serializers.prestacao_conta_serializer import (PrestacaoContaLookUpSerializer, PrestacaoContaListSerializer,
                                                           PrestacaoContaRetrieveSerializer)

pytestmark = pytest.mark.django_db


def test_lookup_serializer(prestacao_conta):
    serializer = PrestacaoContaLookUpSerializer(prestacao_conta)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['periodo_uuid']
    assert serializer.data['status']


@pytest.fixture
def tecnico_dre(dre):
    return baker.make(
        'TecnicoDre',
        dre=dre,
        nome='José Testando',
        rf='271170',
    )


@pytest.fixture
def atribuicao(tecnico_dre, unidade, periodo):
    return baker.make(
        'Atribuicao',
        tecnico=tecnico_dre,
        unidade=unidade,
        periodo=periodo,
    )


@pytest.fixture
def processo_associacao_2019(associacao):
    return baker.make(
        'ProcessoAssociacao',
        associacao=associacao,
        numero_processo='123456',
        ano='2019'
    )


def test_list_serializer(prestacao_conta, atribuicao, processo_associacao_2019):
    serializer = PrestacaoContaListSerializer(prestacao_conta)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['unidade_eol']
    assert serializer.data['unidade_nome']
    assert serializer.data['status']
    assert serializer.data['tecnico_responsavel'] == atribuicao.tecnico.nome
    assert serializer.data['processo_sei'] == processo_associacao_2019.numero_processo
    assert serializer.data['data_recebimento']
    assert serializer.data['data_ultima_analise']
    assert serializer.data['devolucao_ao_tesouro']



@pytest.fixture
def devolucao_prestacao_conta_2020_1(prestacao_conta):
    return baker.make(
        'DevolucaoPrestacaoConta',
        prestacao_conta=prestacao_conta,
        data=date(2020, 7, 1),
        data_limite_ue=date(2020, 8, 1),
    )


def test_retrieve_serializer(prestacao_conta, devolucao_prestacao_conta_2020_1, atribuicao):
    serializer = PrestacaoContaRetrieveSerializer(prestacao_conta)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['periodo_uuid']
    assert serializer.data['status']
    assert serializer.data['associacao']
    assert serializer.data['tecnico_responsavel']
    assert serializer.data['data_recebimento']
    assert serializer.data['devolucoes_da_prestacao']
