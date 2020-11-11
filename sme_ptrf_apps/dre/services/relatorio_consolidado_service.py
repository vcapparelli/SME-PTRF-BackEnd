import logging

from django.db.models import Count, Sum, F

from sme_ptrf_apps.core.models import PrestacaoConta, FechamentoPeriodo, PrevisaoRepasseSme, DevolucaoAoTesouro
from sme_ptrf_apps.dre.models import RelatorioConsolidadoDRE
from sme_ptrf_apps.receitas.models import Receita

logger = logging.getLogger(__name__)


def status_de_geracao_do_relatorio(dre, periodo, tipo_conta):
    '''
    Calcula o status de geração do relatório da DRE em determinado período e tipo de conta conforme tabela:

    PCs em análise?	Relatório gerado?	Texto status	                                                                            Cor
    Sim	            Não	                Ainda constam prestações de contas das associações em análise. Relatório não gerado.	    0
    Sim	            Sim (parcial)	    Ainda constam prestações de contas das associações em análise. Relatório parcial gerado.	1
    Não	            Não	                Análise de prestações de contas das associações completa. Relatório não gerado.	            2
    Não	            Sim (parcial)	    Análise de prestações de contas das associações completa. Relatório parcial gerado.	        2
    Não	            Sim (final)	        Análise de prestações de contas das associações completa. Relatório final gerado.	        3
    '''
    LEGENDA_COR = {
        'NAO_GERADO': {'com_pcs_em_analise': 0, 'sem_pcs_em_analise': 2},
        'GERADO_PARCIAL': {'com_pcs_em_analise': 1, 'sem_pcs_em_analise': 2},
        'GERADO_TOTAL': {'com_pcs_em_analise': 0, 'sem_pcs_em_analise': 3},
    }

    pcs_em_analise = PrestacaoConta.objects.filter(periodo=periodo,
                                                   status__in=['EM_ANALISE', 'RECEBIDA', 'NAO_RECEBIDA', 'DEVOLVIDA'],
                                                   associacao__unidade__dre=dre).exists()

    relatorio = RelatorioConsolidadoDRE.objects.filter(dre=dre, periodo=periodo, tipo_conta=tipo_conta).first()

    status_relatorio = relatorio.status if relatorio else 'NAO_GERADO'

    status_txt_relatorio = f'{RelatorioConsolidadoDRE.STATUS_NOMES[status_relatorio]}.'

    if pcs_em_analise:
        status_txt_analise = 'Ainda constam prestações de contas das associações em análise.'
    else:
        status_txt_analise = 'Análise de prestações de contas das associações completa.'

    status_txt_geracao = f'{status_txt_analise} {status_txt_relatorio}'

    cor_idx = LEGENDA_COR[status_relatorio]['com_pcs_em_analise' if pcs_em_analise else 'sem_pcs_em_analise']

    status = {
        'pcs_em_analise': pcs_em_analise,
        'status_geracao': status_relatorio,
        'status_txt': status_txt_geracao,
        'cor_idx': cor_idx,
    }
    return status


def informacoes_execucao_financeira(dre, periodo, tipo_conta):
    def _totalizador_zerado():
        return {
            'saldo_reprogramado_periodo_anterior_custeio': 0,
            'saldo_reprogramado_periodo_anterior_capital': 0,
            'saldo_reprogramado_periodo_anterior_livre': 0,
            'saldo_reprogramado_periodo_anterior_total': 0,

            'repasses_previstos_sme_custeio': 0,
            'repasses_previstos_sme_capital': 0,
            'repasses_previstos_sme_livre': 0,
            'repasses_previstos_sme_total': 0,

            'repasses_no_periodo_custeio': 0,
            'repasses_no_periodo_capital': 0,
            'repasses_no_periodo_livre': 0,
            'repasses_no_periodo_total': 0,

            'receitas_rendimento_no_periodo_custeio': 0,
            'receitas_rendimento_no_periodo_capital': 0,
            'receitas_rendimento_no_periodo_livre': 0,
            'receitas_rendimento_no_periodo_total': 0,

            'receitas_devolucao_no_periodo_custeio': 0,
            'receitas_devolucao_no_periodo_capital': 0,
            'receitas_devolucao_no_periodo_livre': 0,
            'receitas_devolucao_no_periodo_total': 0,

            'demais_creditos_no_periodo_custeio': 0,
            'demais_creditos_no_periodo_capital': 0,
            'demais_creditos_no_periodo_livre': 0,
            'demais_creditos_no_periodo_total': 0,

            'receitas_totais_no_periodo_custeio': 0,
            'receitas_totais_no_periodo_capital': 0,
            'receitas_totais_no_periodo_livre': 0,
            'receitas_totais_no_periodo_total': 0,

            'despesas_no_periodo_custeio': 0,
            'despesas_no_periodo_capital': 0,
            'despesas_no_periodo_total': 0,

            'saldo_reprogramado_proximo_periodo_custeio': 0,
            'saldo_reprogramado_proximo_periodo_capital': 0,
            'saldo_reprogramado_proximo_periodo_livre': 0,
            'saldo_reprogramado_proximo_periodo_total': 0,

            'devolucoes_ao_tesouro_no_periodo_total': 0,
        }

    def _soma_fechamento(totalizador, fechamento):
        # Saldo Anterior
        totalizador['saldo_reprogramado_periodo_anterior_custeio'] += fechamento.saldo_anterior_custeio
        totalizador['saldo_reprogramado_periodo_anterior_capital'] += fechamento.saldo_anterior_capital
        totalizador['saldo_reprogramado_periodo_anterior_livre'] += fechamento.saldo_anterior_livre
        totalizador['saldo_reprogramado_periodo_anterior_total'] += fechamento.saldo_anterior

        # Repasses no período
        totalizador['repasses_no_periodo_custeio'] += fechamento.total_repasses_custeio
        totalizador['repasses_no_periodo_capital'] += fechamento.total_repasses_capital
        totalizador['repasses_no_periodo_livre'] += fechamento.total_repasses_livre
        totalizador['repasses_no_periodo_total'] += fechamento.total_repasses

        # Receitas Tipo Devolução no período
        totalizador['receitas_devolucao_no_periodo_custeio'] += fechamento.total_receitas_devolucao_custeio
        totalizador['receitas_devolucao_no_periodo_capital'] += fechamento.total_receitas_devolucao_capital
        totalizador['receitas_devolucao_no_periodo_livre'] += fechamento.total_receitas_devolucao_livre
        totalizador['receitas_devolucao_no_periodo_total'] += fechamento.total_receitas_devolucao

        # Receitas Totais no período
        totalizador['receitas_totais_no_periodo_custeio'] += fechamento.total_receitas_custeio
        totalizador['receitas_totais_no_periodo_capital'] += fechamento.total_receitas_capital
        totalizador['receitas_totais_no_periodo_livre'] += fechamento.total_receitas_livre
        totalizador['receitas_totais_no_periodo_total'] += fechamento.total_receitas

        # Despesas Totais no período
        totalizador['despesas_no_periodo_custeio'] += fechamento.total_despesas_custeio
        totalizador['despesas_no_periodo_capital'] += fechamento.total_despesas_capital
        totalizador['despesas_no_periodo_total'] += fechamento.total_despesas

        # Saldos Reprogramados Totais para o próximo período
        totalizador['saldo_reprogramado_proximo_periodo_custeio'] += fechamento.saldo_reprogramado_custeio
        totalizador['saldo_reprogramado_proximo_periodo_capital'] += fechamento.saldo_reprogramado_capital
        totalizador['saldo_reprogramado_proximo_periodo_livre'] += fechamento.saldo_reprogramado_livre
        totalizador['saldo_reprogramado_proximo_periodo_total'] += fechamento.saldo_reprogramado

        return totalizador

    def _soma_receitas_tipo_rendimento(totais, periodo, conta_associacao, acao_associacao):

        receitas = Receita.receitas_da_acao_associacao_no_periodo(acao_associacao=acao_associacao, periodo=periodo,
                                                                  conta_associacao=conta_associacao)
        for receita in receitas:
            if receita.tipo_receita.e_rendimento:
                totais['receitas_rendimento_no_periodo_total'] += receita.valor

                if receita.categoria_receita == 'CAPITAL':
                    totais['receitas_rendimento_no_periodo_capital'] += receita.valor
                elif receita.categoria_receita == 'CUSTEIO':
                    totais['receitas_rendimento_no_periodo_custeio'] += receita.valor
                else:
                    totais['receitas_rendimento_no_periodo_livre'] += receita.valor

        return totais

    def _atualiza_demais_creditos(totais):
        totais['demais_creditos_no_periodo_custeio'] += totais['receitas_totais_no_periodo_custeio'] - \
                                                        totais['repasses_no_periodo_custeio'] - \
                                                        totais['receitas_devolucao_no_periodo_custeio'] - \
                                                        totais['receitas_rendimento_no_periodo_custeio']

        totais['demais_creditos_no_periodo_capital'] += totais['receitas_totais_no_periodo_capital'] - \
                                                        totais['repasses_no_periodo_capital'] - \
                                                        totais['receitas_devolucao_no_periodo_capital'] - \
                                                        totais['receitas_rendimento_no_periodo_capital']

        totais['demais_creditos_no_periodo_livre'] += totais['receitas_totais_no_periodo_livre'] - \
                                                      totais['repasses_no_periodo_livre'] - \
                                                      totais['receitas_devolucao_no_periodo_livre'] - \
                                                      totais['receitas_rendimento_no_periodo_livre']

        totais['demais_creditos_no_periodo_total'] += totais['receitas_totais_no_periodo_total'] - \
                                                      totais['repasses_no_periodo_total'] - \
                                                      totais['receitas_devolucao_no_periodo_total'] - \
                                                      totais['receitas_rendimento_no_periodo_total']

        return totais

    def _totaliza_fechamentos(dre, periodo, tipo_conta, totais):
        # Fechamentos no período da conta de PCs de Associações da DRE, concluídas
        fechamentos = FechamentoPeriodo.objects.filter(
            periodo=periodo,
            conta_associacao__tipo_conta=tipo_conta,
            associacao__unidade__dre=dre,
            prestacao_conta__status__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA']
        )
        for fechamento in fechamentos:
            totais = _soma_fechamento(totais, fechamento)
            totais = _soma_receitas_tipo_rendimento(
                periodo=periodo,
                conta_associacao=fechamento.conta_associacao,
                acao_associacao=fechamento.acao_associacao,
                totais=totais
            )
        return totais

    def _totaliza_previsoes_repasses_sme(dre, periodo, tipo_conta, totais):
        # Previsões para o período e conta com o tipo de conta para Associações da DRE
        previsoes = PrevisaoRepasseSme.objects.filter(
            periodo=periodo,
            conta_associacao__tipo_conta=tipo_conta,
            associacao__unidade__dre=dre
        )
        for previsao in previsoes:
            totais['repasses_previstos_sme_custeio'] += previsao.valor_custeio
            totais['repasses_previstos_sme_capital'] += previsao.valor_capital
            totais['repasses_previstos_sme_livre'] += previsao.valor_livre
            totais['repasses_previstos_sme_total'] += previsao.valor_total

        return totais

    def _totaliza_devolucoes_ao_tesouro(dre, periodo, totais):
        # Devoluções ao tesouro de PCs de Associações da DRE, no período e concluídas
        devolucoes = DevolucaoAoTesouro.objects.filter(
            prestacao_conta__periodo=periodo,
            prestacao_conta__associacao__unidade__dre=dre,
            prestacao_conta__status__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA']
        )
        for devolucao in devolucoes:
            totais['devolucoes_ao_tesouro_no_periodo_total'] += devolucao.valor

        return totais

    totais = _totalizador_zerado()

    totais = _totaliza_fechamentos(dre, periodo, tipo_conta, totais)

    totais = _atualiza_demais_creditos(totais)

    totais = _totaliza_previsoes_repasses_sme(dre, periodo, tipo_conta, totais)

    totais = _totaliza_devolucoes_ao_tesouro(dre, periodo, totais)

    return totais


def informacoes_devolucoes_a_conta_ptrf(dre, periodo, tipo_conta):
    # Devoluções à conta referente ao período e tipo_conta de Associações da DRE concluídas
    associacoes_com_pc_concluidas = PrestacaoConta.objects.filter(
        periodo=periodo,
        associacao__unidade__dre=dre,
        status__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA']
    ).values_list('associacao__uuid')

    if periodo.data_fim_realizacao_despesas:
        receitas_periodo = Receita.objects.filter(
            data__range=(periodo.data_inicio_realizacao_despesas, periodo.data_fim_realizacao_despesas))
    else:
        receitas_periodo = Receita.objects.filter(
            data__gte=periodo.data_inicio_realizacao_despesas)

    devolucoes = receitas_periodo.filter(
        tipo_receita__e_devolucao=True,
        conta_associacao__tipo_conta=tipo_conta,
        associacao__uuid__in=associacoes_com_pc_concluidas,
    ).values('detalhe_tipo_receita__nome').annotate(ocorrencias=Count('uuid'), valor=Sum('valor'))

    return devolucoes


def informacoes_devolucoes_ao_tesouro(dre, periodo):
    # Devoluções ao tesouro de PCs de Associações da DRE, no período da conta e concluídas
    devolucoes = DevolucaoAoTesouro.objects.filter(
        prestacao_conta__periodo=periodo,
        prestacao_conta__associacao__unidade__dre=dre,
        prestacao_conta__status__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA']
    ).values('tipo__nome').annotate(ocorrencias=Count('uuid'), valor=Sum('valor'))

    return devolucoes
