import logging

from celery import shared_task

from sme_ptrf_apps.core.models import (
    Periodo,
    Unidade,
    TipoConta
)

from sme_ptrf_apps.dre.models import (
    AtaParecerTecnico
)


logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=333333,
    soft_time_limit=333333
)
def gerar_relatorio_consolidado_dre_async(periodo_uuid, dre_uuid, tipo_conta_uuid, parcial):
    logger.info(f'Iniciando Relatório DRE. DRE:{dre_uuid} Período:{periodo_uuid} Tipo Conta:{tipo_conta_uuid}.')

    from sme_ptrf_apps.dre.services import gera_relatorio_dre

    try:
        periodo = Periodo.objects.get(uuid=periodo_uuid)
    except Periodo.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        dre = Unidade.dres.get(uuid=dre_uuid)
    except Unidade.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        tipo_conta = TipoConta.objects.get(uuid=tipo_conta_uuid)
    except TipoConta.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto tipo de conta para o uuid {tipo_conta_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        gera_relatorio_dre(dre, periodo, tipo_conta, parcial)
        AtaParecerTecnico.iniciar(
            dre=dre,
            periodo=periodo
        )
    except Exception as err:
        erro = {
            'erro': 'problema_geracao_relatorio',
            'mensagem': 'Erro ao gerar relatório.'
        }
        logger.error("Erro ao gerar relatório consolidado: %s", str(err))
        raise Exception(erro)

    logger.info(f'Finalizado Relatório DRE. DRE:{dre_uuid} Período:{periodo_uuid} Tipo Conta:{tipo_conta_uuid}.')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=333333,
    soft_time_limit=333333
)
def gerar_previa_relatorio_consolidado_dre_async(dre_uuid, tipo_conta_uuid, periodo_uuid, parcial):
    logger.info(f'Iniciando Prévia Relatório DRE. DRE:{dre_uuid} Período:{periodo_uuid} Tipo Conta:{tipo_conta_uuid}.')
    from sme_ptrf_apps.dre.services import gera_previa_relatorio_dre

    try:
        periodo = Periodo.objects.get(uuid=periodo_uuid)
    except Periodo.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        dre = Unidade.dres.get(uuid=dre_uuid)
    except Unidade.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        tipo_conta = TipoConta.objects.get(uuid=tipo_conta_uuid)
    except TipoConta.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto tipo de conta para o uuid {tipo_conta_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        gera_previa_relatorio_dre(dre, periodo, tipo_conta, parcial)
    except Exception as err:
        erro = {
            'erro': 'problema_geracao_relatorio',
            'mensagem': 'Erro ao gerar relatório.'
        }
        logger.error("Erro ao gerar relatório consolidado: %s", str(err))
        raise Exception(erro)

    logger.info(f'Finalizado Prévia Relatório DRE. DRE:{dre_uuid} Período:{periodo_uuid} Tipo Conta:{tipo_conta_uuid}.')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_lauda_csv_async(dre_uuid, tipo_conta_uuid, periodo_uuid, parcial, username):
    logger.info(f'Iniciando a geração do arquivo csv da lauda async. DRE:{dre_uuid} Período:{periodo_uuid} Tipo Conta:{tipo_conta_uuid}.')
    from sme_ptrf_apps.dre.services import gerar_csv
    from sme_ptrf_apps.core.services.arquivo_download_service import gerar_arquivo_download, atualiza_arquivo_download, atualiza_arquivo_download_erro

    try:
        periodo = Periodo.objects.get(uuid=periodo_uuid)
    except Periodo.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        dre = Unidade.dres.get(uuid=dre_uuid)
    except Unidade.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        tipo_conta = TipoConta.objects.get(uuid=tipo_conta_uuid)
    except TipoConta.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto tipo de conta para o uuid {tipo_conta_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        nome_dre = dre.nome.upper()
        if "DIRETORIA REGIONAL DE EDUCACAO" in nome_dre:
            nome_dre = nome_dre.replace("DIRETORIA REGIONAL DE EDUCACAO", "")
            nome_dre = nome_dre.strip()

        nome_dre = nome_dre.lower()
        nome_conta = tipo_conta.nome.lower()
        obj_arquivo_download = gerar_arquivo_download(username, f"Lauda_{nome_dre}_{nome_conta}.csv")
        gerar_csv(dre, periodo, tipo_conta, obj_arquivo_download, parcial)
    except Exception as err:
        erro = {
            'erro': 'problema_geracao_csv',
            'mensagem': 'Erro ao gerar csv.'
        }
        logger.error("Erro ao gerar lauda: %s", str(err))
        raise Exception(erro)

    logger.info(f'Finalizado geração arquivo csv da lauda async. DRE:{dre_uuid} Período:{periodo_uuid} Tipo Conta:{tipo_conta_uuid}.')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_lauda_txt_async(dre_uuid, tipo_conta_uuid, periodo_uuid, parcial, username):
    logger.info(f'Iniciando a geração do arquivo txt da lauda async. DRE:{dre_uuid} Período:{periodo_uuid} Tipo Conta:{tipo_conta_uuid}.')
    from sme_ptrf_apps.dre.services import gerar_txt
    from sme_ptrf_apps.core.services.arquivo_download_service import gerar_arquivo_download, atualiza_arquivo_download, atualiza_arquivo_download_erro

    try:
        periodo = Periodo.objects.get(uuid=periodo_uuid)
    except Periodo.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        dre = Unidade.dres.get(uuid=dre_uuid)
    except Unidade.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        tipo_conta = TipoConta.objects.get(uuid=tipo_conta_uuid)
    except TipoConta.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto tipo de conta para o uuid {tipo_conta_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    ata = AtaParecerTecnico.objects.filter(dre=dre).filter(periodo=periodo).last()

    if not ata:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto ata parecer tecnico para a dre {dre_uuid} e periodo {periodo_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        nome_dre = dre.nome.upper()
        if "DIRETORIA REGIONAL DE EDUCACAO" in nome_dre:
            nome_dre = nome_dre.replace("DIRETORIA REGIONAL DE EDUCACAO", "")
            nome_dre = nome_dre.strip()

        nome_dre = nome_dre.lower()
        nome_conta = tipo_conta.nome.lower()
        obj_arquivo_download = gerar_arquivo_download(username, f"Lauda_{nome_dre}_{nome_conta}.docx.txt")
        gerar_txt(dre, periodo, tipo_conta, obj_arquivo_download, ata, parcial)
    except Exception as err:
        erro = {
            'erro': 'problema_geracao_txt',
            'mensagem': 'Erro ao gerar txt.'
        }
        logger.error("Erro ao gerar lauda: %s", str(err))
        raise Exception(erro)

    logger.info(f'Finalizado geração arquivo txt da lauda async. DRE:{dre_uuid} Período:{periodo_uuid} Tipo Conta:{tipo_conta_uuid}.')
