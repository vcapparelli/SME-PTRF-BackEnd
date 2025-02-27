import pytest
from datetime import date
from freezegun import freeze_time

from sme_ptrf_apps.core.services import lancamentos_da_prestacao

pytestmark = pytest.mark.django_db


def test_get_lancamentos_da_analise_da_prestacao_com_tag_de_informacao_antecipado(
    jwt_authenticated_client_a,
    despesa_2020_1_fornecedor_antonio_jose,
    rateio_despesa_2020_antonio_jose,
    periodo_2020_1,
    conta_associacao_cartao,
    acao_associacao_ptrf,
    prestacao_conta_2020_1_em_analise,
    analise_prestacao_conta_2020_1_em_analise,
    analise_lancamento_receita_prestacao_conta_2020_1_em_analise,
    analise_lancamento_despesa_prestacao_conta_2020_1_em_analise,
    tipo_transacao_pix
):
    despesa_2020_1_fornecedor_antonio_jose.data_transacao = date(2020, 3, 9)
    despesa_2020_1_fornecedor_antonio_jose.save()

    lancamentos = lancamentos_da_prestacao(
        analise_prestacao_conta=analise_prestacao_conta_2020_1_em_analise,
        conta_associacao=conta_associacao_cartao,
        tipo_transacao='GASTOS',
        tipo_de_pagamento=tipo_transacao_pix,
    )

    assert len(lancamentos) == 1

    lancamento = lancamentos[0]
    assert lancamento['documento_mestre']['uuid'] == f'{despesa_2020_1_fornecedor_antonio_jose.uuid}'
    assert lancamento['informacoes'] == [{
        'tag_id': '1',
        'tag_nome': 'Antecipado',
        'tag_hint': 'Data do pagamento (09/03/2020) anterior à data do documento (10/03/2020).'
    },
        {'tag_hint': 'Essa despesa já possui conciliação bancária.',
         'tag_id': '9',
         'tag_nome': 'Conciliada'}
    ]


def test_get_lancamentos_da_analise_da_prestacao_com_tag_de_informacao_estornado(
    jwt_authenticated_client_a,
    despesa_2020_1_fornecedor_antonio_jose,
    rateio_despesa_2020_antonio_jose,
    periodo_2020_1,
    conta_associacao_cartao,
    acao_associacao_ptrf,
    prestacao_conta_2020_1_em_analise,
    analise_prestacao_conta_2020_1_em_analise,
    analise_lancamento_receita_prestacao_conta_2020_1_em_analise,
    analise_lancamento_despesa_prestacao_conta_2020_1_em_analise,
    tipo_transacao_pix,
    receita_estorno_do_rateio_despesa_2020_antonio_jose
):
    lancamentos = lancamentos_da_prestacao(
        analise_prestacao_conta=analise_prestacao_conta_2020_1_em_analise,
        conta_associacao=conta_associacao_cartao,
        tipo_transacao='GASTOS',
        tipo_de_pagamento=tipo_transacao_pix,
    )

    assert len(lancamentos) == 1

    lancamento = lancamentos[0]
    assert lancamento['documento_mestre']['uuid'] == f'{despesa_2020_1_fornecedor_antonio_jose.uuid}'
    assert lancamento['informacoes'] == [{
        'tag_id': '2',
        'tag_nome': 'Estornado',
        'tag_hint': 'Esse gasto possui estornos.'
    },
        {'tag_hint': 'Essa despesa já possui conciliação bancária.',
         'tag_id': '9',
         'tag_nome': 'Conciliada'}
    ]


def test_get_lancamentos_da_analise_da_prestacao_com_tag_de_informacao_imposto_apenas_um_imposto_retido(
    jwt_authenticated_client_a,
    despesa_com_retencao_imposto,
    rateio_despesa_com_retencao_imposto,
    despesa_imposto_retido,
    rateio_despesa_imposto_retido,
    periodo_2020_1,
    conta_associacao_cartao,
    acao_associacao_ptrf,
    prestacao_conta_2020_1_em_analise,
    analise_prestacao_conta_2020_1_em_analise,
    analise_lancamento_receita_prestacao_conta_2020_1_em_analise,
    analise_lancamento_despesa_prestacao_conta_2020_1_em_analise,
    tipo_transacao_pix,
):
    lancamentos = lancamentos_da_prestacao(
        analise_prestacao_conta=analise_prestacao_conta_2020_1_em_analise,
        conta_associacao=conta_associacao_cartao,
        tipo_transacao='GASTOS',
        filtrar_por_nome_fornecedor="Antônio José"
    )

    assert len(lancamentos) == 1

    lancamento = lancamentos[0]
    assert lancamento['documento_mestre']['uuid'] == f'{despesa_com_retencao_imposto.uuid}'

    informacoes = lancamento['informacoes']
    informacoes_filtradas_tag_imposto = [info for info in informacoes if info['tag_id'] == '4']

    assert informacoes_filtradas_tag_imposto == [{
        'tag_id': '4',
        'tag_nome': 'Imposto',
        'tag_hint': ['Essa despesa teve retenção de imposto:', 'R$ 10,00, pago em 10/03/2020.']
    }]



def test_get_lancamentos_da_analise_da_prestacao_com_tag_de_informacao_imposto_apenas_dois_impostos_retidos(
    jwt_authenticated_client_a,
    despesa_com_retencao_imposto_2,
    rateio_despesa_com_retencao_imposto_2,
    despesa_imposto_retido,
    rateio_despesa_imposto_retido,
    despesa_imposto_retido_2,
    rateio_despesa_imposto_retido_2,
    periodo_2020_1,
    conta_associacao_cartao,
    acao_associacao_ptrf,
    prestacao_conta_2020_1_em_analise,
    analise_prestacao_conta_2020_1_em_analise,
    analise_lancamento_receita_prestacao_conta_2020_1_em_analise,
    analise_lancamento_despesa_prestacao_conta_2020_1_em_analise,
    tipo_transacao_pix,
):
    lancamentos = lancamentos_da_prestacao(
        analise_prestacao_conta=analise_prestacao_conta_2020_1_em_analise,
        conta_associacao=conta_associacao_cartao,
        tipo_transacao='GASTOS',
        filtrar_por_nome_fornecedor="Antônio José"
    )

    assert len(lancamentos) == 1

    lancamento = lancamentos[0]
    assert lancamento['documento_mestre']['uuid'] == f'{despesa_com_retencao_imposto_2.uuid}'

    assert lancamento['informacoes'][0]["tag_id"] == '4'
    assert lancamento['informacoes'][0]["tag_nome"] == "Imposto"
    assert "Essa despesa teve retenções de impostos:" in lancamento['informacoes'][0]["tag_hint"]
    assert "R$ 10,00, pagamento ainda não realizado." in lancamento['informacoes'][0]["tag_hint"]
    assert "R$ 10,00, pago em 10/03/2020." in lancamento['informacoes'][0]["tag_hint"]


def test_get_lancamentos_da_analise_da_prestacao_com_tag_de_informacao_imposto_pago(
    jwt_authenticated_client_a,
    despesa_com_retencao_imposto,
    rateio_despesa_com_retencao_imposto,
    despesa_imposto_retido,
    rateio_despesa_imposto_retido,
    periodo_2020_1,
    conta_associacao_cartao,
    acao_associacao_ptrf,
    prestacao_conta_2020_1_em_analise,
    analise_prestacao_conta_2020_1_em_analise,
    analise_lancamento_receita_prestacao_conta_2020_1_em_analise,
    analise_lancamento_despesa_prestacao_conta_2020_1_em_analise,
    tipo_transacao_pix,
):
    lancamentos = lancamentos_da_prestacao(
        analise_prestacao_conta=analise_prestacao_conta_2020_1_em_analise,
        conta_associacao=conta_associacao_cartao,
        tipo_transacao='GASTOS',
        filtrar_por_nome_fornecedor="Prefeitura"
    )

    assert len(lancamentos) == 1

    lancamento = lancamentos[0]
    assert lancamento['documento_mestre']['uuid'] == f'{despesa_imposto_retido.uuid}'

    informacoes = lancamento['informacoes']
    informacoes_filtradas_tag_imposto_pago = [info for info in informacoes if info['tag_id'] == '5']

    assert informacoes_filtradas_tag_imposto_pago == [{
        'tag_id': '5',
        'tag_nome': 'Imposto Pago',
        'tag_hint': 'Esse imposto está relacionado à despesa 123315 / Antônio José SA.',
    }]

@freeze_time("2023-06-22")
def test_get_lancamentos_da_analise_da_prestacao_com_tag_de_informacao_nao_conciliada(
    jwt_authenticated_client_a,
    despesa_com_retencao_imposto,
    rateio_despesa_com_retencao_imposto,
    despesa_imposto_retido,
    rateio_despesa_imposto_retido,
    periodo_2020_1,
    conta_associacao_cartao,
    acao_associacao_ptrf,
    prestacao_conta_2020_1_em_analise,
    analise_prestacao_conta_2020_1_em_analise,
    analise_lancamento_receita_prestacao_conta_2020_1_em_analise,
    analise_lancamento_despesa_prestacao_conta_2020_1_em_analise,
    tipo_transacao_pix,
):
    lancamentos = lancamentos_da_prestacao(
        analise_prestacao_conta=analise_prestacao_conta_2020_1_em_analise,
        conta_associacao=conta_associacao_cartao,
        tipo_transacao='GASTOS',
        filtrar_por_nome_fornecedor="Prefeitura"
    )

    assert len(lancamentos) == 1

    lancamento = lancamentos[0]
    assert lancamento['documento_mestre']['uuid'] == f'{despesa_imposto_retido.uuid}'

    informacoes = lancamento['informacoes']
    informacoes_filtradas_tag_nao_conciliada = [info for info in informacoes if info['tag_id'] == '10']

    assert informacoes_filtradas_tag_nao_conciliada == [
        {'tag_hint': ['Essa despesa não possui conciliação bancária.', 'Não demonstrado por 39 meses.'],
         'tag_id': '10',
         'tag_nome': 'Não conciliada'}
    ]

def test_get_lancamentos_da_analise_da_prestacao_com_tag_de_informacao_parcial_recurso_proprio(
    jwt_authenticated_client_a,
    despesa_2020_1_recurso_proprio,
    rateio_despesa_2020_recurso_proprio,
    periodo_2020_1,
    conta_associacao_cartao,
    acao_associacao_ptrf,
    prestacao_conta_2020_1_em_analise,
    analise_prestacao_conta_2020_1_em_analise,
    analise_lancamento_receita_prestacao_conta_2020_1_em_analise,
    analise_lancamento_despesa_prestacao_conta_2020_1_em_analise,
    tipo_transacao_pix,
):
    lancamentos = lancamentos_da_prestacao(
        analise_prestacao_conta=analise_prestacao_conta_2020_1_em_analise,
        conta_associacao=conta_associacao_cartao,
        tipo_transacao='GASTOS',
        filtrar_por_nome_fornecedor="Recurso próprio"
    )

    assert len(lancamentos) == 1

    lancamento = lancamentos[0]
    assert lancamento['documento_mestre']['uuid'] == f'{despesa_2020_1_recurso_proprio.uuid}'
    assert lancamento['informacoes'] == [{
        'tag_id': '3',
        'tag_nome': 'Parcial',
        'tag_hint': 'Parte da despesa foi paga com recursos próprios ou por mais de uma conta.',
    },
        {'tag_hint': 'Essa despesa já possui conciliação bancária.',
         'tag_id': '9',
         'tag_nome': 'Conciliada'}
    ]


def test_get_lancamentos_da_analise_da_prestacao_com_tag_de_informacao_parcial_multiplas_contas(
    jwt_authenticated_client_a,
    despesa_2020_1_multiplas_contas,
    rateio_despesa_2020_multiplas_contas_cartao,
    rateio_despesa_2020_multiplas_contas_cheque,
    periodo_2020_1,
    conta_associacao_cartao,
    acao_associacao_ptrf,
    prestacao_conta_2020_1_em_analise,
    analise_prestacao_conta_2020_1_em_analise,
    analise_lancamento_receita_prestacao_conta_2020_1_em_analise,
    analise_lancamento_despesa_prestacao_conta_2020_1_em_analise,
    tipo_transacao_pix,
):
    lancamentos = lancamentos_da_prestacao(
        analise_prestacao_conta=analise_prestacao_conta_2020_1_em_analise,
        conta_associacao=conta_associacao_cartao,
        tipo_transacao='GASTOS',
        filtrar_por_nome_fornecedor="Multiplas"
    )

    assert len(lancamentos) == 1

    lancamento = lancamentos[0]
    assert lancamento['documento_mestre']['uuid'] == f'{despesa_2020_1_multiplas_contas.uuid}'
    assert lancamento['informacoes'] == [{
        'tag_id': '3',
        'tag_nome': 'Parcial',
        'tag_hint': 'Parte da despesa foi paga com recursos próprios ou por mais de uma conta.',
    },
        {'tag_hint': 'Essa despesa já possui conciliação bancária.',
         'tag_id': '9',
         'tag_nome': 'Conciliada'}
    ]


def test_get_lancamentos_da_analise_da_prestacao_com_tag_inativa(
    jwt_authenticated_client_a,
    rateio_despesa_2020_inativa_teste_tag,
    periodo_2020_1,
    conta_associacao_cartao,
    acao_associacao_ptrf,
    prestacao_conta_2020_1_em_analise_despesa_inativa,
    analise_prestacao_conta_2020_1_em_analise_despesa_inativa,
    analise_lancamento_despesa_prestacao_conta_2020_1_despesa_inativa,
    despesa_2020_1_inativa_teste_tag,
    tipo_transacao,
):
    filtro_informacoes_list = ['6']

    lancamentos = lancamentos_da_prestacao(
        analise_prestacao_conta=analise_prestacao_conta_2020_1_em_analise_despesa_inativa,
        conta_associacao=conta_associacao_cartao,
        tipo_transacao='GASTOS',
        filtro_informacoes_list=filtro_informacoes_list
    )

    assert len(lancamentos) == 1

    lancamento = lancamentos[0]
    assert lancamento['documento_mestre']['uuid'] == f'{despesa_2020_1_inativa_teste_tag.uuid}'
    assert lancamento['informacoes'] == [{
        'tag_id': '6',
        'tag_nome': 'Excluído',
        'tag_hint': 'Este gasto foi excluído em 10/05/2020 05:10:10',
    },
        {'tag_hint': 'Essa despesa já possui conciliação bancária.',
         'tag_id': '9',
         'tag_nome': 'Conciliada'}
    ]
