from django.db.models import Sum, Q, Count, Max

from sme_ptrf_apps.core.models import Associacao, FechamentoPeriodo, PrestacaoConta
from sme_ptrf_apps.despesas.models import RateioDespesa, Despesa
from sme_ptrf_apps.receitas.models import Receita

from sme_ptrf_apps.despesas.status_cadastro_completo import STATUS_COMPLETO, STATUS_INATIVO


def receitas_conciliadas_por_conta_e_acao_na_conciliacao(conta_associacao, acao_associacao, periodo):
    dataset = periodo.receitas_conciliadas_no_periodo.filter(conta_associacao=conta_associacao)

    if acao_associacao:
        dataset = dataset.filter(acao_associacao=acao_associacao)

    return dataset.all()


def info_conciliacao_pendente(periodo, conta_associacao):
    acoes_associacao = Associacao.acoes_da_associacao(associacao_uuid=conta_associacao.associacao.uuid)
    result = []
    for acao_associacao in acoes_associacao:
        info_acao = info_conciliacao_acao_associacao_no_periodo(acao_associacao=acao_associacao,
                                                                periodo=periodo,
                                                                conta_associacao=conta_associacao)

        info = {
            'acao_associacao_uuid': f'{acao_associacao.uuid}',
            'acao_associacao_nome': acao_associacao.acao.nome,

            'receitas_no_periodo': info_acao['receitas_no_periodo'],

            'despesas_no_periodo': info_acao['despesas_no_periodo'],

            'despesas_nao_conciliadas': info_acao['despesas_nao_conciliadas'],

            'receitas_nao_conciliadas': info_acao['receitas_nao_conciliadas'],

        }
        result.append(info)

    return result


def info_conciliacao_acao_associacao_no_periodo(acao_associacao, periodo, conta_associacao):
    def resultado_vazio():
        return {
            'receitas_no_periodo': 0,
            'despesas_no_periodo': 0,
            'receitas_nao_conciliadas': 0,
            'despesas_nao_conciliadas': 0,
        }

    def sumariza_conciliacao_receitas_do_periodo_e_acao(periodo, conta_associacao, acao_associacao, info):

        receitas_conciliadas = receitas_conciliadas_por_conta_e_acao_na_conciliacao(
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            periodo=periodo)

        for receita_conciliada in receitas_conciliadas:
            info['receitas_no_periodo'] += receita_conciliada.valor

        receitas_nao_conciliadas = receitas_nao_conciliadas_por_conta_e_acao_no_periodo(
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            periodo=periodo)

        for receita_nao_conciliada in receitas_nao_conciliadas:
            info['receitas_no_periodo'] += receita_nao_conciliada.valor
            info['receitas_nao_conciliadas'] += receita_nao_conciliada.valor

        return info

    def sumariza_conciliacao_despesas_do_periodo_e_acao(periodo, conta_associacao, acao_associacao, info, ):
        rateios_conciliados = despesas_conciliadas_por_conta_e_acao_na_conciliacao(
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            periodo=periodo)

        for rateio_conciliado in rateios_conciliados:
            info['despesas_no_periodo'] += rateio_conciliado.valor_rateio

        rateios_nao_conciliados = despesas_nao_conciliadas_por_conta_e_acao_no_periodo(
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            periodo=periodo)

        for rateio_nao_conciliado in rateios_nao_conciliados:
            info['despesas_no_periodo'] += rateio_nao_conciliado.valor_rateio
            info['despesas_nao_conciliadas'] += rateio_nao_conciliado.valor_rateio

        return info

    info = resultado_vazio()

    info = sumariza_conciliacao_receitas_do_periodo_e_acao(periodo=periodo,
                                                           conta_associacao=conta_associacao,
                                                           acao_associacao=acao_associacao,
                                                           info=info)

    info = sumariza_conciliacao_despesas_do_periodo_e_acao(periodo=periodo,
                                                           conta_associacao=conta_associacao,
                                                           acao_associacao=acao_associacao, info=info)

    return info


def despesas_nao_conciliadas_por_conta_e_acao_no_periodo(conta_associacao, acao_associacao, periodo):
    dataset = RateioDespesa.completos.filter(conta_associacao=conta_associacao)

    if acao_associacao:
        dataset = dataset.filter(acao_associacao=acao_associacao)

    # No caso de despesas não conciliadas todas devem ser exibidas até a data limite do período
    if periodo.data_fim_realizacao_despesas:
        dataset = dataset.filter(despesa__data_transacao__lte=periodo.data_fim_realizacao_despesas)

    dataset = dataset.exclude(Q(conferido=True) & Q(periodo_conciliacao__referencia__lte=periodo.referencia))

    return dataset.all()


def despesas_conciliadas_por_conta_e_acao_na_conciliacao(conta_associacao, acao_associacao, periodo):
    dataset = periodo.despesas_conciliadas_no_periodo.filter(despesa__status=STATUS_COMPLETO).filter(
        conta_associacao=conta_associacao)

    if acao_associacao:
        dataset = dataset.filter(acao_associacao=acao_associacao)

    return dataset.all()


def receitas_nao_conciliadas_por_conta_e_acao_no_periodo(conta_associacao, acao_associacao, periodo):
    dataset = Receita.objects.filter(conta_associacao=conta_associacao)

    if acao_associacao:
        dataset = dataset.filter(acao_associacao=acao_associacao)

    dataset = dataset.filter(conferido=False)

    # No caso de despesas não conciliadas todas devem ser exibidas até a data limite do período
    if periodo.data_fim_realizacao_despesas:
        dataset = dataset.filter(data__lte=periodo.data_fim_realizacao_despesas)

    return dataset.all()


def receitas_conciliadas_por_conta_e_acao_no_periodo(conta_associacao, acao_associacao, periodo):
    dataset = Receita.objects.filter(conta_associacao=conta_associacao)

    if acao_associacao:
        dataset = dataset.filter(acao_associacao=acao_associacao)

    dataset = dataset.filter(conferido=True)

    if periodo.data_fim_realizacao_despesas:
        dataset = dataset.filter(
            data__range=(periodo.data_inicio_realizacao_despesas, periodo.data_fim_realizacao_despesas))
    else:
        dataset = dataset.filter(data__gte=periodo.data_inicio_realizacao_despesas)

    return dataset.all()


def info_resumo_conciliacao(periodo, conta_associacao):
    info_conta = info_conciliacao_conta_associacao_no_periodo(periodo=periodo,
                                                              conta_associacao=conta_associacao)

    saldo_anterior = saldo_anterior_total_conta_associacao_no_periodo(conta_associacao=conta_associacao,
                                                                      periodo=periodo)

    saldo_posterior_total = (
        saldo_anterior +
        info_conta['receitas_no_periodo'] -
        info_conta['despesas_no_periodo']
    )

    saldo_posterior_conciliado = (
        saldo_anterior + info_conta['despesas_outros_periodos'] - info_conta['despesas_outros_periodos_conciliadas'] +
        info_conta['receitas_conciliadas'] -
        info_conta['despesas_no_periodo_conciliadas']
    )

    info = {
        'saldo_anterior': saldo_anterior,
        'saldo_anterior_conciliado': saldo_anterior + info_conta['despesas_outros_periodos'] - info_conta[
            'despesas_outros_periodos_conciliadas'],
        'saldo_anterior_nao_conciliado': info_conta['despesas_outros_periodos_conciliadas'] - info_conta[
            'despesas_outros_periodos'],

        'receitas_total': info_conta['receitas_no_periodo'],
        'receitas_conciliadas': info_conta['receitas_conciliadas'],
        'receitas_nao_conciliadas': info_conta['receitas_nao_conciliadas'],

        'despesas_total': info_conta['despesas_no_periodo'],
        'despesas_conciliadas': info_conta['despesas_no_periodo_conciliadas'],
        'despesas_nao_conciliadas': info_conta['despesas_no_periodo_nao_conciliadas'],

        'despesas_outros_periodos': info_conta['despesas_outros_periodos'],
        'despesas_outros_periodos_conciliadas': info_conta['despesas_outros_periodos_conciliadas'],
        'despesas_outros_periodos_nao_conciliadas': info_conta['despesas_outros_periodos_nao_conciliadas'],

        'saldo_posterior_total': saldo_posterior_total,
        'saldo_posterior_conciliado': saldo_posterior_conciliado,
        'saldo_posterior_nao_conciliado': saldo_posterior_total - saldo_posterior_conciliado,
    }

    return info


def info_conciliacao_conta_associacao_no_periodo(periodo, conta_associacao):
    def resultado_vazio():
        return {
            'despesas_no_periodo': 0,
            'despesas_no_periodo_conciliadas': 0,
            'despesas_no_periodo_nao_conciliadas': 0,
            'despesas_outros_periodos': 0,
            'despesas_outros_periodos_nao_conciliadas': 0,
            'despesas_outros_periodos_conciliadas': 0,
            'receitas_no_periodo': 0,
            'receitas_nao_conciliadas': 0,
            'receitas_conciliadas': 0,
        }

    def sumariza_conciliacao_receitas_do_periodo_e_conta(periodo, conta_associacao, info):

        receitas_conciliadas = receitas_conciliadas_por_conta_na_conciliacao(
            conta_associacao=conta_associacao,
            periodo=periodo)

        for receita_conciliada in receitas_conciliadas:
            info['receitas_no_periodo'] += receita_conciliada.valor
            info['receitas_conciliadas'] += receita_conciliada.valor

        receitas_nao_conciliadas = receitas_nao_conciliadas_por_conta_no_periodo(
            conta_associacao=conta_associacao,
            periodo=periodo)

        for receita_nao_conciliada in receitas_nao_conciliadas:
            info['receitas_no_periodo'] += receita_nao_conciliada.valor
            info['receitas_nao_conciliadas'] += receita_nao_conciliada.valor

        return info

    def sumariza_conciliacao_despesas_do_periodo_e_conta(periodo, conta_associacao, info, ):
        # Conciliadas
        rateios_conciliados = despesas_conciliadas_por_conta_na_conciliacao(
            conta_associacao=conta_associacao,
            periodo=periodo)

        for rateio_conciliado in rateios_conciliados:
            if periodo.data_pertence_ao_periodo(rateio_conciliado.despesa.data_transacao):
                info['despesas_no_periodo'] += rateio_conciliado.valor_rateio
                info['despesas_no_periodo_conciliadas'] += rateio_conciliado.valor_rateio
            else:
                info['despesas_outros_periodos'] += rateio_conciliado.valor_rateio
                info['despesas_outros_periodos_conciliadas'] += rateio_conciliado.valor_rateio

        rateios_nao_conciliados = despesas_nao_conciliadas_por_conta_e_acao_no_periodo(
            conta_associacao=conta_associacao,
            periodo=periodo,
            acao_associacao=None
        )

        # Não conciliadas
        for rateio_nao_conciliado in rateios_nao_conciliados:
            if periodo.data_pertence_ao_periodo(rateio_nao_conciliado.despesa.data_transacao):
                info['despesas_no_periodo'] += rateio_nao_conciliado.valor_rateio
                info['despesas_no_periodo_nao_conciliadas'] += rateio_nao_conciliado.valor_rateio
            else:
                info['despesas_outros_periodos'] += rateio_nao_conciliado.valor_rateio
                info['despesas_outros_periodos_nao_conciliadas'] += rateio_nao_conciliado.valor_rateio

        return info

    info = resultado_vazio()

    info = sumariza_conciliacao_receitas_do_periodo_e_conta(periodo=periodo,
                                                            conta_associacao=conta_associacao,
                                                            info=info)

    info = sumariza_conciliacao_despesas_do_periodo_e_conta(periodo=periodo,
                                                            conta_associacao=conta_associacao,
                                                            info=info)

    return info


def receitas_conciliadas_por_conta_na_conciliacao(conta_associacao, periodo):
    dataset = periodo.receitas_conciliadas_no_periodo.filter(conta_associacao=conta_associacao)
    return dataset.exclude(status=STATUS_INATIVO).all()


def receitas_nao_conciliadas_por_conta_no_periodo(conta_associacao, periodo):
    dataset = Receita.objects.filter(conta_associacao=conta_associacao).filter(
        conferido=False)

    # No caso de despesas não conciliadas todas devem ser exibidas até a data limite do período
    if periodo.data_fim_realizacao_despesas:
        dataset = dataset.filter(data__lte=periodo.data_fim_realizacao_despesas)

    return dataset.all()


def despesas_conciliadas_por_conta_na_conciliacao(conta_associacao, periodo):
    dataset = periodo.despesas_conciliadas_no_periodo.filter(despesa__status=STATUS_COMPLETO)
    dataset = dataset.filter(conta_associacao=conta_associacao)

    return dataset.all()


def despesas_nao_conciliadas_por_conta_no_periodo(conta_associacao, periodo):
    dataset = RateioDespesa.completos.filter(conta_associacao=conta_associacao).filter(conferido=False)

    # No caso de despesas não conciliadas todas devem ser exibidas até a data limite do período
    if periodo.data_fim_realizacao_despesas:
        dataset = dataset.filter(despesa__data_transacao__lte=periodo.data_fim_realizacao_despesas)

    return dataset.all()


def saldo_anterior_total_conta_associacao_no_periodo(conta_associacao, periodo):
    def saldo_anterior_periodo_fechado_sumarizado(fechamentos_periodo):
        saldo_anterior_total = 0

        for fechamento_periodo in fechamentos_periodo:
            saldo_anterior_total += fechamento_periodo.saldo_anterior
        return saldo_anterior_total

    def saldo_posterior_periodo_fechado_sumarizado(fechamentos_periodo):
        saldo_posterior_total = 0
        for fechamento_periodo in fechamentos_periodo:
            saldo_posterior_total += fechamento_periodo.saldo_reprogramado
        return saldo_posterior_total

    def saldo_periodo_aberto_sumarizado(periodo, conta_associacao):

        if not periodo or not periodo.periodo_anterior:
            return 0.00

        fechamentos_periodo_anterior = FechamentoPeriodo.fechamentos_da_conta_no_periodo(
            conta_associacao=conta_associacao,
            periodo=periodo.periodo_anterior)

        saldo = saldo_posterior_periodo_fechado_sumarizado(fechamentos_periodo_anterior)

        return saldo

    fechamentos_periodo = FechamentoPeriodo.fechamentos_da_conta_no_periodo(conta_associacao=conta_associacao,
                                                                            periodo=periodo)
    if fechamentos_periodo:
        return saldo_anterior_periodo_fechado_sumarizado(fechamentos_periodo)
    else:
        return saldo_periodo_aberto_sumarizado(periodo, conta_associacao)


def documentos_de_despesa_nao_conciliados_por_conta_e_acao_no_periodo(conta_associacao, acao_associacao, periodo):
    rateios = despesas_nao_conciliadas_por_conta_e_acao_no_periodo(conta_associacao=conta_associacao,
                                                                   acao_associacao=acao_associacao, periodo=periodo)
    despesas_com_rateios = rateios.values_list('despesa__id', flat=True).distinct()

    dataset = Despesa.completas.filter(id__in=despesas_com_rateios)

    return dataset.all()


def documentos_de_despesa_conciliados_por_conta_e_acao_na_conciliacao(conta_associacao, acao_associacao, periodo):
    rateios = despesas_conciliadas_por_conta_e_acao_na_conciliacao(conta_associacao=conta_associacao,
                                                                   acao_associacao=acao_associacao, periodo=periodo)
    despesas_com_rateios = rateios.values_list('despesa__id', flat=True).distinct()

    dataset = Despesa.completas.filter(id__in=despesas_com_rateios)

    return dataset.all()


def monta_item_de_despesa_imposto_para_lista_de_transacoes(periodo, conta_associacao, despesa_imposto,
                                                           max_notificar_dias_nao_conferido,
                                                           DespesaConciliacaoSerializer,
                                                           RateioDespesaConciliacaoSerializer, DespesaImpostoSerializer,
                                                           despesa_geradora_do_imposto):
    transacao = {
        'periodo': f'{periodo.uuid}',
        'conta': f'{conta_associacao.uuid}',
        'data': despesa_imposto.data_transacao,
        'tipo_transacao': 'Gasto',
        'numero_documento': despesa_imposto.numero_documento,
        'descricao': despesa_imposto.nome_fornecedor,
        'valor_transacao_total': despesa_imposto.valor_total,
        'valor_transacao_na_conta':
            despesa_imposto.rateios.filter(status=STATUS_COMPLETO).filter(
                conta_associacao=conta_associacao).aggregate(Sum('valor_rateio'))[
                'valor_rateio__sum'],
        'valores_por_conta': despesa_imposto.rateios.filter(status=STATUS_COMPLETO).values(
            'conta_associacao__tipo_conta__nome').annotate(
            Sum('valor_rateio')),
        'conferido': despesa_imposto.conferido,
        'documento_mestre': DespesaConciliacaoSerializer(despesa_imposto, many=False).data,
        'rateios': RateioDespesaConciliacaoSerializer(
            despesa_imposto.rateios.filter(status=STATUS_COMPLETO).filter(
                conta_associacao=conta_associacao).order_by('id'),
            many=True).data,
        'notificar_dias_nao_conferido': max_notificar_dias_nao_conferido,
        'despesa_geradora_do_imposto': DespesaImpostoSerializer(despesa_geradora_do_imposto,
                                                                many=False).data if despesa_geradora_do_imposto else None,
        'despesas_impostos': None,
        'uuid': str(despesa_imposto.uuid)
    }

    return transacao


def transacoes_para_conciliacao_agrupado_por_impostos(despesas, periodo, conta_associacao, acao_associacao,
                                                      conferido=False):
    from sme_ptrf_apps.despesas.api.serializers.despesa_serializer import DespesaConciliacaoSerializer, \
        DespesaImpostoSerializer
    from sme_ptrf_apps.despesas.api.serializers.rateio_despesa_serializer import RateioDespesaConciliacaoSerializer

    # Iniciar a lista de transacoes com a lista de despesas ordenada
    transacoes = []
    for despesa in despesas:

        max_notificar_dias_nao_conferido = 0
        for rateio in despesa.rateios.filter(status=STATUS_COMPLETO, conta_associacao=conta_associacao):
            if rateio.notificar_dias_nao_conferido > max_notificar_dias_nao_conferido:
                max_notificar_dias_nao_conferido = rateio.notificar_dias_nao_conferido

        despesa_geradora_do_imposto = despesa.despesa_geradora_do_imposto.first()
        despesas_impostos = despesa.despesas_impostos.all()

        # Retorna a lista de uuid das despesas contidas na lista de transações
        # Utilizada para verificar se a despesa já está contida nessa lista para evitar repetição
        existe_em_transacoes = [d['uuid'] for d in transacoes]

        # Se despesa_geradora_do_imposto não estiver atribuido,
        # ou seja for None então ela é a despesa geradora do imposto
        if (not despesa_geradora_do_imposto) or (str(despesa.uuid) not in existe_em_transacoes and despesa.conferido == conferido and despesa.cadastro_completo()):
            transacao = {
                'periodo': f'{periodo.uuid}',
                'conta': f'{conta_associacao.uuid}',
                'data': despesa.data_transacao,
                'tipo_transacao': 'Gasto',
                'numero_documento': despesa.numero_documento,
                'descricao': despesa.nome_fornecedor,
                'valor_transacao_total': despesa.valor_total,
                'valor_transacao_na_conta':
                    despesa.rateios.filter(status=STATUS_COMPLETO).filter(conta_associacao=conta_associacao).aggregate(
                        Sum('valor_rateio'))[
                        'valor_rateio__sum'],
                'valores_por_conta': despesa.rateios.filter(status=STATUS_COMPLETO).values(
                    'conta_associacao__tipo_conta__nome').annotate(
                    Sum('valor_rateio')),
                'conferido': despesa.conferido,
                'documento_mestre': DespesaConciliacaoSerializer(despesa, many=False).data,
                'rateios': RateioDespesaConciliacaoSerializer(
                    despesa.rateios.filter(status=STATUS_COMPLETO).filter(conta_associacao=conta_associacao).order_by(
                        'id'),
                    many=True).data,
                'notificar_dias_nao_conferido': max_notificar_dias_nao_conferido,
                'despesa_geradora_do_imposto': DespesaImpostoSerializer(despesa_geradora_do_imposto,
                                                                        many=False).data if despesa_geradora_do_imposto else None,
                'despesas_impostos': DespesaImpostoSerializer(despesas_impostos, many=True,
                                                              required=False).data if despesas_impostos else None,
                'uuid': str(despesa.uuid)
            }
            transacoes.append(transacao)

        if despesas_impostos:
            for despesa_imposto in despesas_impostos:
                despesa_geradora_do_imposto = despesa_imposto.despesa_geradora_do_imposto.first()

                # Se o filtro de ação nao foi passado, simplesmente retorna as despesas
                if not acao_associacao:
                    if despesa_imposto.conferido == despesa_geradora_do_imposto.conferido and str(despesa_imposto.uuid) not in existe_em_transacoes and despesa_imposto.cadastro_completo():
                        transacao = monta_item_de_despesa_imposto_para_lista_de_transacoes(periodo,
                                                                                           conta_associacao,
                                                                                           despesa_imposto,
                                                                                           max_notificar_dias_nao_conferido,
                                                                                           DespesaConciliacaoSerializer,
                                                                                           RateioDespesaConciliacaoSerializer,
                                                                                           DespesaImpostoSerializer,
                                                                                           despesa_geradora_do_imposto)
                        transacoes.append(transacao)
                else:
                    # Se o filtro de ação foi passado, percorre os rateios
                    # e verifica se o rateio atual tem a mesma ação passada no filtro
                    rateios = despesa_imposto.rateios.all()
                    for rateio in rateios:
                        if despesa_imposto.conferido == despesa_geradora_do_imposto.conferido and rateio.acao_associacao == acao_associacao and (str(despesa_imposto.uuid) not in existe_em_transacoes) and despesa_imposto.cadastro_completo():

                            transacao = monta_item_de_despesa_imposto_para_lista_de_transacoes(periodo,
                                                                                               conta_associacao,
                                                                                               despesa_imposto,
                                                                                               max_notificar_dias_nao_conferido,
                                                                                               DespesaConciliacaoSerializer,
                                                                                               RateioDespesaConciliacaoSerializer,
                                                                                               DespesaImpostoSerializer,
                                                                                               despesa_geradora_do_imposto)
                            transacoes.append(transacao)

    return transacoes


def transacoes_para_conciliacao(periodo, conta_associacao, conferido=False, acao_associacao=None,
                                ordenar_por_numero_do_documento=False, ordenar_por_data_especificacao=False,
                                ordenar_por_valor=False, ordenar_por_imposto=False):

    from sme_ptrf_apps.despesas.api.serializers.despesa_serializer import DespesaConciliacaoSerializer, \
        DespesaImpostoSerializer
    from sme_ptrf_apps.despesas.api.serializers.rateio_despesa_serializer import RateioDespesaConciliacaoSerializer
    from sme_ptrf_apps.despesas.services.despesa_service import ordena_despesas_por_imposto

    lista_argumentos_ordenacao = []

    if conferido:
        despesas = documentos_de_despesa_conciliados_por_conta_e_acao_na_conciliacao(
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            periodo=periodo)
    else:
        despesas = documentos_de_despesa_nao_conciliados_por_conta_e_acao_no_periodo(
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            periodo=periodo)

    # Ordenação
    if ordenar_por_numero_do_documento:
        if ordenar_por_numero_do_documento == 'crescente':
            lista_argumentos_ordenacao.append('numero_documento')
        elif ordenar_por_numero_do_documento == 'decrescente':
            lista_argumentos_ordenacao.append('-numero_documento')

    if ordenar_por_data_especificacao:
        if ordenar_por_data_especificacao == 'crescente':
            lista_argumentos_ordenacao.append('data_documento')
        elif ordenar_por_data_especificacao == 'decrescente':
            lista_argumentos_ordenacao.append('-data_documento')

    if ordenar_por_valor:
        if ordenar_por_valor == 'crescente':
            lista_argumentos_ordenacao.append('valor_total')
        elif ordenar_por_valor == 'decrescente':
            lista_argumentos_ordenacao.append('-valor_total')

    if ordenar_por_imposto:
        # Cria uma lista com os impostos ordenados.
        # Passo os demais argumentos de ordenação e já retorna ordenada por todos
        despesas = ordena_despesas_por_imposto(despesas, lista_argumentos_ordenacao)

        # Cria uma lista com os ids dos importos ordenados na ordem correta
        pk_list = [obj.pk for obj in despesas]

        # Converte a lista de impostos em um queryset respeitando a ordem da lista
        clauses = ' '.join(['WHEN despesas_despesa.id=%s THEN %s' % (pk, i) for i, pk in enumerate(pk_list)])
        ordering = 'CASE %s END' % clauses
        despesas = Despesa.objects.filter(pk__in=pk_list).extra(
            select={'ordering': ordering}, order_by=('ordering',))

        return transacoes_para_conciliacao_agrupado_por_impostos(despesas, periodo, conta_associacao, acao_associacao,
                                                                 conferido)

    # Caso nenhum argumento de ordenação seja passado, ordenamos por -data_transacao
    # Caso tenha sido solicitado ordenar por imposto já é retornada ordenada por todos os argumentos, além do imposto
    if not ordenar_por_imposto:
        if not lista_argumentos_ordenacao:
            despesas = despesas.order_by('-data_transacao')
        else:
            despesas = despesas.order_by(*lista_argumentos_ordenacao)

    # Iniciar a lista de transacoes com a lista de despesas ordenada
    transacoes = []
    for despesa in despesas:

        max_notificar_dias_nao_conferido = 0
        for rateio in despesa.rateios.filter(status=STATUS_COMPLETO, conta_associacao=conta_associacao):
            if rateio.notificar_dias_nao_conferido > max_notificar_dias_nao_conferido:
                max_notificar_dias_nao_conferido = rateio.notificar_dias_nao_conferido

        despesa_geradora_do_imposto = despesa.despesa_geradora_do_imposto.first()
        despesas_impostos = despesa.despesas_impostos.all()

        transacao = {
            'periodo': f'{periodo.uuid}',
            'conta': f'{conta_associacao.uuid}',
            'data': despesa.data_transacao,
            'tipo_transacao': 'Gasto',
            'numero_documento': despesa.numero_documento,
            'descricao': despesa.nome_fornecedor,
            'valor_transacao_total': despesa.valor_total,
            'valor_transacao_na_conta':
                despesa.rateios.filter(status=STATUS_COMPLETO).filter(
                    conta_associacao=conta_associacao).aggregate(
                    Sum('valor_rateio'))[
                    'valor_rateio__sum'],
            'valores_por_conta': despesa.rateios.filter(status=STATUS_COMPLETO).values(
                'conta_associacao__tipo_conta__nome').annotate(
                Sum('valor_rateio')),
            'conferido': despesa.conferido,
            'informacoes': despesa.tags_de_informacao,
            'documento_mestre': DespesaConciliacaoSerializer(despesa, many=False).data,
            'rateios': RateioDespesaConciliacaoSerializer(
                despesa.rateios.filter(status=STATUS_COMPLETO).filter(
                    conta_associacao=conta_associacao).order_by(
                    'id'),
                many=True).data,
            'notificar_dias_nao_conferido': max_notificar_dias_nao_conferido,
            'despesa_geradora_do_imposto': DespesaImpostoSerializer(despesa_geradora_do_imposto,
                                                                    many=False).data if despesa_geradora_do_imposto else None,
            'despesas_impostos': DespesaImpostoSerializer(despesas_impostos, many=True,
                                                          required=False).data if despesas_impostos else None
        }
        transacoes.append(transacao)

    return transacoes


def conciliar_transacao(periodo, conta_associacao, transacao):
    from sme_ptrf_apps.despesas.api.serializers.despesa_serializer import DespesaConciliacaoSerializer

    if isinstance(transacao, Despesa):
        rateios = transacao.rateios.filter(status=STATUS_COMPLETO).filter(conta_associacao=conta_associacao).filter(
            conferido=False)
        for rateio in rateios:
            rateio.marcar_conferido(periodo_conciliacao=periodo)
        despesa_conciliada = Despesa.by_uuid(transacao.uuid)
        return DespesaConciliacaoSerializer(despesa_conciliada, many=False).data


def desconciliar_transacao(conta_associacao, transacao):
    from sme_ptrf_apps.despesas.api.serializers.despesa_serializer import DespesaConciliacaoSerializer

    if isinstance(transacao, Despesa):
        rateios = transacao.rateios.filter(status=STATUS_COMPLETO).filter(conta_associacao=conta_associacao).filter(
            conferido=True)
        for rateio in rateios:
            rateio.desmarcar_conferido()
        despesa_desconciliada = Despesa.by_uuid(transacao.uuid)
        return DespesaConciliacaoSerializer(despesa_desconciliada, many=False).data


def salva_conciliacao_bancaria(justificativa_ou_extrato_bancario, texto_observacao, periodo,
                               conta_associacao, data_extrato, saldo_extrato,
                               comprovante_extrato, data_atualizacao_comprovante_extrato,
                               observacao_conciliacao):
    if justificativa_ou_extrato_bancario == "JUSTIFICATIVA":
        observacao_conciliacao.criar_atualizar_justificativa(
            periodo=periodo,
            conta_associacao=conta_associacao,
            texto_observacao=texto_observacao,
        )
    elif justificativa_ou_extrato_bancario == "EXTRATO_BANCARIO":
        observacao_conciliacao.criar_atualizar_extrato_bancario(
            periodo=periodo,
            conta_associacao=conta_associacao,
            data_extrato=data_extrato,
            saldo_extrato=saldo_extrato,
            comprovante_extrato=comprovante_extrato,
            data_atualizacao_comprovante_extrato=data_atualizacao_comprovante_extrato,
        )


def permite_editar_campos_extrato(associacao, periodo, conta_associacao):
    prestacao_conta = PrestacaoConta.objects.filter(
        associacao=associacao,
        periodo=periodo
    ).first()

    if not prestacao_conta:
        return True

    if prestacao_conta.status != PrestacaoConta.STATUS_DEVOLVIDA:
        return False

    ultima_analise = prestacao_conta.analises_da_prestacao.last()

    tem_acertos_de_extrato = ultima_analise.tem_acertos_extratos_bancarios(conta_associacao) if \
        ultima_analise is not None else False

    return tem_acertos_de_extrato
