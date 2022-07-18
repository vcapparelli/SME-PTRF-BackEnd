import pytest

from datetime import datetime
from freezegun import freeze_time

from sme_ptrf_apps.core.services.painel_resumo_recursos_service import (
    PainelResumoRecursosService,
    PainelResumoRecursos,
    PainelResumoRecursosCardConta,
    PainelResumoRecursosCardAcao
)

pytestmark = pytest.mark.django_db


@freeze_time('2020-01-01 10:20:00')
def test_obtem_painel_resumo_recursos_por_associacao_periodo_conta(
    prr_associacao,
    prr_periodo_2020_1,
    prr_conta_associacao_cheque,
    prr_acao_associacao_ptrf,
):
    # result = {
    #     'associacao': f'{associacao_uuid}',
    #     'periodo_referencia': periodo.referencia,
    #     'prestacao_contas_status': prestacao_contas_status,
    #     'data_inicio_realizacao_despesas': f'{periodo.data_inicio_realizacao_despesas if periodo else ""}',
    #     'data_fim_realizacao_despesas': f'{periodo.data_fim_realizacao_despesas if periodo else ""}',
    #     'data_prevista_repasse': f'{periodo.data_prevista_repasse if periodo else ""}',
    #     'ultima_atualizacao': f'{ultima_atualizacao}',
    #     'info_acoes': info_acoes,
    #     'info_conta': info_conta
    # }

    painel = PainelResumoRecursosService.painel_resumo_recursos(
        prr_associacao,
        prr_periodo_2020_1,
        prr_conta_associacao_cheque
    )

    status_pc_esperado = {
        'documentos_gerados': None,
        'legenda_cor': 1,
        'periodo_bloqueado': False,
        'periodo_encerrado': False,
        'prestacao_de_contas_uuid': None,
        'status_prestacao': 'NAO_APRESENTADA',
        'texto_status': 'Período em andamento. '
    }

    assert isinstance(painel, PainelResumoRecursos)
    assert painel.associacao == prr_associacao
    assert painel.periodo_referencia == prr_periodo_2020_1
    assert painel.prestacao_contas_status == status_pc_esperado
    assert painel.data_inicio_realizacao_despesas == prr_periodo_2020_1.data_inicio_realizacao_despesas
    assert painel.data_fim_realizacao_despesas == prr_periodo_2020_1.data_fim_realizacao_despesas
    assert painel.data_prevista_repasse == prr_periodo_2020_1.data_prevista_repasse
    assert painel.ultima_atualizacao == datetime(2020, 1, 1, 10, 20, 0)
    assert isinstance(painel.info_conta, PainelResumoRecursosCardConta)
    assert painel.info_acoes is not None
    assert isinstance(painel.info_acoes[0], PainelResumoRecursosCardAcao)
