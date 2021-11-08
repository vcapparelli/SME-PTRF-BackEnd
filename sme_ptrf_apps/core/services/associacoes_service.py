from .periodo_services import status_prestacao_conta_associacao
from django.db.models import Q
from django.core.exceptions import ValidationError


def retorna_status_prestacoes(periodos=None, status_pc=None, uuid=None):
    lista_de_periodos = []
    if periodos:
        for periodo in periodos:
            prestacao_conta_status = status_prestacao_conta_associacao(periodo_uuid=periodo.uuid, associacao_uuid=uuid)

            obj_periodo = {
                'referencia': periodo.referencia,
                'data_inicio_realizacao_despesas': periodo.data_inicio_realizacao_despesas,
                'data_fim_realizacao_despesas': periodo.data_fim_realizacao_despesas,
                'status_pc': prestacao_conta_status['status_prestacao'],
                'texto_status': prestacao_conta_status['texto_status'],
                'legenda_cor': prestacao_conta_status['legenda_cor'],
                'prestacao_de_contas_uuid': prestacao_conta_status['prestacao_de_contas_uuid'],
            }

            lista_de_periodos.append(obj_periodo)

        if status_pc:
            lista_de_periodos = list(filter(lambda d: d['status_pc'] == status_pc, lista_de_periodos))

        return lista_de_periodos


def get_status_presidente(associacao):
    result = {
                 'status_presidente': associacao.status_presidente,
                 'cargo_substituto_presidente_ausente': associacao.cargo_substituto_presidente_ausente,
             }

    return result


def update_status_presidente(associacao, status_presidente, cargo_substituto_presidente_ausente):

    if not status_presidente or status_presidente not in ['PRESENTE', 'AUSENTE']:
        result_error = {
            'erro': 'campo_requerido',
            'mensagem': 'É necessário enviar no payload um staus_presidente válido [PRESENTE|AUSENTE]. '
        }
        raise ValidationError(result_error)

    if status_presidente == 'AUSENTE' and not cargo_diretoria_executiva_valido(cargo_substituto_presidente_ausente):
        result_error = {
            'erro': 'campo_requerido',
            'mensagem': 'É necessário enviar no payload um cargo_substituto_presidente_ausente válido.'
        }
        raise ValidationError(result_error)

    associacao.status_presidente = status_presidente
    associacao.cargo_substituto_presidente_ausente = cargo_substituto_presidente_ausente
    associacao.save()

    result = {
                 'status_presidente': associacao.status_presidente,
                 'cargo_substituto_presidente_ausente': associacao.cargo_substituto_presidente_ausente,
             }

    return result


def cargo_diretoria_executiva_valido(cargo):
    from sme_ptrf_apps.core.choices.membro_associacao import MembroEnum
    cargos_diretoria_executiva = [key[0] for key in MembroEnum.diretoria_executiva_choices()]
    return cargo in cargos_diretoria_executiva


def associacao_pode_implantar_saldo(associacao):
    result = None

    periodo_primeira_pc = associacao.periodo_inicial.proximo_periodo if associacao.periodo_inicial else None

    if not associacao.periodo_inicial:
        result = {
            'permite_implantacao': False,
            'erro': 'periodo_inicial_nao_definido',
            'mensagem': 'Período inicial não foi definido para essa associação. Verifique com o administrador.'
        }

    if associacao.prestacoes_de_conta_da_associacao.exclude(
        Q(periodo=periodo_primeira_pc) & Q(status='DEVOLVIDA')
    ).exists():
        result = {
            'permite_implantacao': False,
            'erro': 'prestacao_de_contas_existente',
            'mensagem': 'Os saldos não podem ser implantados, já existe uma prestação de contas da associação.'
        }

    if not result:
        result = {
            'permite_implantacao': True,
            'erro': '',
            'mensagem': 'Os saldos podem ser implantados normalmente.'
        }

    return result


def get_implantacao_de_saldos_da_associacao(associacao):
    from rest_framework import status
    from .implantacao_saldos_services import implantacoes_de_saldo_da_associacao
    from ..api.serializers import (AcaoAssociacaoLookUpSerializer,
                                   ContaAssociacaoLookUpSerializer,
                                   PeriodoLookUpSerializer)

    periodo_primeira_pc = associacao.periodo_inicial.proximo_periodo if associacao.periodo_inicial else None

    if not associacao.periodo_inicial:
        erro = {
            'erro': 'periodo_inicial_nao_definido',
            'mensagem': 'Período inicial não foi definido para essa associação. Verifique com o administrador.'
        }
        return {
            'conteudo': erro,
            'status_code': status.HTTP_400_BAD_REQUEST
        }

    if associacao.prestacoes_de_conta_da_associacao.exclude(
        Q(periodo=periodo_primeira_pc) & Q(status='DEVOLVIDA')
    ).exists():
        erro = {
            'erro': 'prestacao_de_contas_existente',
            'mensagem': 'Os saldos não podem ser implantados, já existe uma prestação de contas da associação.'
        }
        return {
            'conteudo': erro,
            'status_code': status.HTTP_400_BAD_REQUEST
        }

    saldos = []
    implantacoes = implantacoes_de_saldo_da_associacao(associacao=associacao)
    for implantacao in implantacoes:
        saldo = {
            'acao_associacao': AcaoAssociacaoLookUpSerializer(implantacao['acao_associacao']).data,
            'conta_associacao': ContaAssociacaoLookUpSerializer(implantacao['conta_associacao']).data,
            'aplicacao': implantacao['aplicacao'],
            'saldo': implantacao['saldo']
        }
        saldos.append(saldo)

    result = {
        'associacao': f'{associacao.uuid}',
        'periodo': PeriodoLookUpSerializer(associacao.periodo_inicial).data,
        'saldos': saldos,
    }

    return {
        'conteudo': result,
        'status_code': status.HTTP_200_OK
    }
