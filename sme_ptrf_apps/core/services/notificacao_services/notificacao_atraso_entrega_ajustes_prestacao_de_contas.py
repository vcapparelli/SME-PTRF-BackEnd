import logging
from datetime import date
from sme_ptrf_apps.core.models import DevolucaoPrestacaoConta, Notificacao
from sme_ptrf_apps.users.services.permissions_service import get_users_by_permission
from .formata_data_dd_mm_yyyy import formata_data_dd_mm_yyyy

from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger(__name__)


def notificar_atraso_entrega_ajustes_prestacao_de_contas():
    logger.info(f'Iniciando a geração de notificação sobre atraso na entrega de ajustes de prestações de contas service')
    data_de_hoje = date.today()

    users = get_users_by_permission('recebe_notificacao_atraso_entrega_ajustes_prestacao_de_contas')
    users = users.filter(visoes__nome="UE")

    devolucoes = DevolucaoPrestacaoConta.objects.filter(prestacao_conta__status="DEVOLVIDA", data_limite_ue__lt=data_de_hoje).order_by('data_limite_ue')

    if devolucoes:
        for devolucao in devolucoes:
            prestacao_de_contas = devolucao.prestacao_conta
            associacao = prestacao_de_contas.associacao
            usuarios = users.filter(unidades__codigo_eol=associacao.unidade.codigo_eol)

            if usuarios:
                for usuario in usuarios:
                    logger.info(f"Gerando notificação de atraso na entrega de ajustes de PC para o usuario: {usuario}")

                    # Gerando uma notificação por período e por cada dia de data limite.
                    Notificacao.notificar(
                        tipo=Notificacao.TIPO_NOTIFICACAO_ALERTA,
                        categoria=Notificacao.CATEGORIA_NOTIFICACAO_ANALISE_PC,
                        remetente=Notificacao.REMETENTE_NOTIFICACAO_SISTEMA,
                        titulo=f"Devolução de ajustes na PC atrasada {prestacao_de_contas.periodo.referencia}",
                        descricao=f"Sua unidade ainda não enviou os ajustes "
                                  f"solicitados pela DRE em sua prestação de contas do período "
                                  f"{prestacao_de_contas.periodo.referencia}. "
                                  f"O seu prazo era {formata_data_dd_mm_yyyy(devolucao.data_limite_ue)}",
                        usuario=usuario,
                        renotificar=False,
                    )
    else:
        logger.info(f"Não foram encontrados prestações de contas a serem notificadas.")


