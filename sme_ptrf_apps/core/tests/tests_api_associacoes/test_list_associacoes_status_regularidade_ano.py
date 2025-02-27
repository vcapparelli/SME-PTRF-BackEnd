import json

import pytest
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def dre_1():
    return baker.make('Unidade', codigo_eol='00001', tipo_unidade='DRE', nome='DRE 1')


@pytest.fixture
def dre_2():
    return baker.make('Unidade', codigo_eol='00002', tipo_unidade='DRE', nome='DRE 2')


@pytest.fixture
def ceu_vassouras_dre_1(dre_1):
    return baker.make('Unidade', codigo_eol='00011', dre=dre_1, tipo_unidade='CEU', nome='Escola Vassouras')


@pytest.fixture
def emef_mendes_dre_1(dre_1):
    return baker.make('Unidade', codigo_eol='00022', dre=dre_1, tipo_unidade='EMEF', nome='Escola Mendes')


@pytest.fixture
def ceu_vassouras_dre_1(dre_1):
    return baker.make('Unidade', codigo_eol='00011', dre=dre_1, tipo_unidade='CEU', nome='Escola Vassouras')


@pytest.fixture
def emef_pirai_dre_2(dre_2):
    return baker.make('Unidade', codigo_eol='00033', dre=dre_2, tipo_unidade='EMEF', nome='Escola Piraí')



@pytest.fixture
def associacao_valenca_ceu_vassouras_dre_1(ceu_vassouras_dre_1, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Associacao Valença',
        cnpj='52.302.275/0001-83',
        unidade=ceu_vassouras_dre_1,
    )


@pytest.fixture
def associacao_pinheiros_emef_mendes_dre_1(emef_mendes_dre_1, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Associação Pinheiros',
        cnpj='05.861.145/0001-09',
        unidade=emef_mendes_dre_1,
    )


@pytest.fixture
def associacao_barra_emef_pirai_dre_2(emef_pirai_dre_2, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Associação Barra',
        cnpj='42.837.274/0001-80',
        unidade=emef_pirai_dre_2,
    )


@pytest.fixture
def ano_analise_regularidade_2021():
    return baker.make('AnoAnaliseRegularidade', ano=2021)


@pytest.fixture
def analise_regularidade_associacao_vassouras(
    associacao_valenca_ceu_vassouras_dre_1,
    ano_analise_regularidade_2021
):
    return baker.make(
        'AnaliseRegularidadeAssociacao',
        associacao=associacao_valenca_ceu_vassouras_dre_1,
        ano_analise=ano_analise_regularidade_2021,
        status_regularidade='REGULAR'
    )


def test_api_list_status_associacoes_dre_1(
    jwt_authenticated_client_a,
    dre_1,
    associacao_valenca_ceu_vassouras_dre_1,
    associacao_barra_emef_pirai_dre_2,
    ano_analise_regularidade_2021,
    analise_regularidade_associacao_vassouras
):
    url = f'/api/associacoes/lista-regularidade-ano/?dre_uuid={dre_1.uuid}&ano=2021'
    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)

    result_esperado = [
        {
            'associacao': {
                'uuid': f'{associacao_valenca_ceu_vassouras_dre_1.uuid}',
                'nome': associacao_valenca_ceu_vassouras_dre_1.nome,
                'data_de_encerramento': None,
                'tooltip_data_encerramento': None,
                'encerrada': False,
                'informacoes': associacao_valenca_ceu_vassouras_dre_1.tags_de_informacao,
                'status_valores_reprogramados': associacao_valenca_ceu_vassouras_dre_1.status_valores_reprogramados,
                'unidade': {
                    'uuid': f'{associacao_valenca_ceu_vassouras_dre_1.unidade.uuid}',
                    'codigo_eol': associacao_valenca_ceu_vassouras_dre_1.unidade.codigo_eol,
                    'nome_com_tipo': associacao_valenca_ceu_vassouras_dre_1.unidade.nome_com_tipo,
                    'nome_dre': associacao_valenca_ceu_vassouras_dre_1.unidade.nome_dre
                },
                'cnpj': associacao_valenca_ceu_vassouras_dre_1.cnpj,
            },
            'status_regularidade': 'REGULAR',
            'motivo': '',
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado


def test_api_list_status_associacoes_pelo_nome_associacao_ignorando_acentos(
    jwt_authenticated_client_a,
    dre_1,
    associacao_valenca_ceu_vassouras_dre_1,
    associacao_pinheiros_emef_mendes_dre_1,
    associacao_barra_emef_pirai_dre_2,
    ano_analise_regularidade_2021,
    analise_regularidade_associacao_vassouras
):

    url = f'/api/associacoes/lista-regularidade-ano/?dre_uuid={dre_1.uuid}&ano=2021&nome=valenca'
    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)

    result_esperado = [
        {
            'associacao': {
                'uuid': f'{associacao_valenca_ceu_vassouras_dre_1.uuid}',
                'nome': associacao_valenca_ceu_vassouras_dre_1.nome,
                'data_de_encerramento': None,
                'tooltip_data_encerramento': None,
                'encerrada': False,
                'informacoes': associacao_valenca_ceu_vassouras_dre_1.tags_de_informacao,
                'status_valores_reprogramados': associacao_valenca_ceu_vassouras_dre_1.status_valores_reprogramados,
                'unidade': {
                    'uuid': f'{associacao_valenca_ceu_vassouras_dre_1.unidade.uuid}',
                    'codigo_eol': associacao_valenca_ceu_vassouras_dre_1.unidade.codigo_eol,
                    'nome_com_tipo': associacao_valenca_ceu_vassouras_dre_1.unidade.nome_com_tipo,
                    'nome_dre': associacao_valenca_ceu_vassouras_dre_1.unidade.nome_dre
                },
                'cnpj': associacao_valenca_ceu_vassouras_dre_1.cnpj,
            },
            'status_regularidade': 'REGULAR',
            'motivo': ''
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado


def test_api_list_status_associacoes_pelo_nome_escola(
    jwt_authenticated_client_a,
    dre_1,
    associacao_valenca_ceu_vassouras_dre_1,
    associacao_pinheiros_emef_mendes_dre_1,
    associacao_barra_emef_pirai_dre_2,
    ano_analise_regularidade_2021,
    analise_regularidade_associacao_vassouras
):
    url = f'/api/associacoes/lista-regularidade-ano/?dre_uuid={dre_1.uuid}&ano=2021&nome=vassouras'
    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)

    result_esperado = [
        {
            'associacao': {
                'uuid': f'{associacao_valenca_ceu_vassouras_dre_1.uuid}',
                'nome': associacao_valenca_ceu_vassouras_dre_1.nome,
                'data_de_encerramento': None,
                'tooltip_data_encerramento': None,
                'encerrada': False,
                'informacoes': associacao_valenca_ceu_vassouras_dre_1.tags_de_informacao,
                'status_valores_reprogramados': associacao_valenca_ceu_vassouras_dre_1.status_valores_reprogramados,
                'unidade': {
                    'uuid': f'{associacao_valenca_ceu_vassouras_dre_1.unidade.uuid}',
                    'codigo_eol': associacao_valenca_ceu_vassouras_dre_1.unidade.codigo_eol,
                    'nome_com_tipo': associacao_valenca_ceu_vassouras_dre_1.unidade.nome_com_tipo,
                    'nome_dre': associacao_valenca_ceu_vassouras_dre_1.unidade.nome_dre
                },
                'cnpj': associacao_valenca_ceu_vassouras_dre_1.cnpj,
            },
            'status_regularidade': 'REGULAR',
            'motivo': ''
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado


def test_api_list_status_associacoes_pelo_tipo_unidade(
    jwt_authenticated_client_a,
    dre_1,
    associacao_valenca_ceu_vassouras_dre_1,
    associacao_pinheiros_emef_mendes_dre_1,
    associacao_barra_emef_pirai_dre_2,
    ano_analise_regularidade_2021,
    analise_regularidade_associacao_vassouras
):

    url = f'/api/associacoes/lista-regularidade-ano/?dre_uuid={dre_1.uuid}&ano=2021&tipo_unidade=CEU'
    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)


    result_esperado = [
        {
            'associacao': {
                'uuid': f'{associacao_valenca_ceu_vassouras_dre_1.uuid}',
                'nome': associacao_valenca_ceu_vassouras_dre_1.nome,
                'data_de_encerramento': None,
                'tooltip_data_encerramento': None,
                'encerrada': False,
                'informacoes': associacao_valenca_ceu_vassouras_dre_1.tags_de_informacao,
                'status_valores_reprogramados': associacao_valenca_ceu_vassouras_dre_1.status_valores_reprogramados,
                'unidade': {
                    'uuid': f'{associacao_valenca_ceu_vassouras_dre_1.unidade.uuid}',
                    'codigo_eol': associacao_valenca_ceu_vassouras_dre_1.unidade.codigo_eol,
                    'nome_com_tipo': associacao_valenca_ceu_vassouras_dre_1.unidade.nome_com_tipo,
                    'nome_dre': associacao_valenca_ceu_vassouras_dre_1.unidade.nome_dre
                },
                'cnpj': associacao_valenca_ceu_vassouras_dre_1.cnpj,
            },
            'status_regularidade': 'REGULAR',
            'motivo': ''
        },
    ]
    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado


def test_api_list_status_associacoes_pelo_status(
    jwt_authenticated_client_a,
    dre_1,
    associacao_valenca_ceu_vassouras_dre_1,
    associacao_pinheiros_emef_mendes_dre_1,
    associacao_barra_emef_pirai_dre_2,
    ano_analise_regularidade_2021,
    analise_regularidade_associacao_vassouras
):

    url = f'/api/associacoes/lista-regularidade-ano/?dre_uuid={dre_1.uuid}&ano=2021&status_regularidade=REGULAR'
    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)


    result_esperado = [
        {
            'associacao': {
                'uuid': f'{associacao_valenca_ceu_vassouras_dre_1.uuid}',
                'nome': associacao_valenca_ceu_vassouras_dre_1.nome,
                'data_de_encerramento': None,
                'tooltip_data_encerramento': None,
                'encerrada': False,
                'informacoes': associacao_valenca_ceu_vassouras_dre_1.tags_de_informacao,
                'status_valores_reprogramados': associacao_valenca_ceu_vassouras_dre_1.status_valores_reprogramados,
                'unidade': {
                    'uuid': f'{associacao_valenca_ceu_vassouras_dre_1.unidade.uuid}',
                    'codigo_eol': associacao_valenca_ceu_vassouras_dre_1.unidade.codigo_eol,
                    'nome_com_tipo': associacao_valenca_ceu_vassouras_dre_1.unidade.nome_com_tipo,
                    'nome_dre': associacao_valenca_ceu_vassouras_dre_1.unidade.nome_dre
                },
                'cnpj': associacao_valenca_ceu_vassouras_dre_1.cnpj,
            },
            'status_regularidade': 'REGULAR',
            'motivo': ''
        },
    ]
    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado
