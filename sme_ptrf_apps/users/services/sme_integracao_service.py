import json
import logging

import requests
from django.conf import settings
from rest_framework import status

logger = logging.getLogger(__name__)


class SmeIntegracaoException(Exception):
    pass


class SmeIntegracaoService:
    headers = {
        'accept': 'application/json',
        'x-api-eol-key': f'{settings.SME_INTEGRACAO_TOKEN}'
    }
    timeout = 20

    @classmethod
    def redefine_senha(cls, registro_funcional, senha):
        """Se a nova senha for uma das senhas padões, a API do SME INTEGRAÇÃO
        não deixa fazer a atualização.
        Para resetar para a senha padrão é preciso usar o endpoint ReiniciarSenha da API SME INTEGRAÇÃO"""
        logger.info('Alterando senha.')
        try:
            data = {
                'Usuario': registro_funcional,
                'Senha': senha
            }
            response = requests.post(f'{settings.SME_INTEGRACAO_URL}/api/AutenticacaoSgp/AlterarSenha', data=data, headers=cls.headers)
            if response.status_code == status.HTTP_200_OK:
                result = "OK"
                return result
            else:
                logger.info("Erro ao redefinir senha: %s", response.content.decode('utf-8'))
                raise SmeIntegracaoException(f"Erro ao redefinir senha: {response.content.decode('utf-8')}")
        except Exception as err:
            raise SmeIntegracaoException(str(err))

    @classmethod
    def redefine_email(cls, registro_funcional, email):
        logger.info('Alterando email.')
        try:
            data = {
                'Usuario': registro_funcional,
                'Email': email
            }
            response = requests.post(f'{settings.SME_INTEGRACAO_URL}/api/AutenticacaoSgp/AlterarEmail', data=data, headers=cls.headers)
            if response.status_code == status.HTTP_200_OK:
                result = "OK"
                return result
            else:
                logger.info("Erro ao redefinir email: %s", response.json())
                raise SmeIntegracaoException('Erro ao redefinir email')
        except Exception as err:
            raise SmeIntegracaoException(str(err))


    @classmethod
    def informacao_usuario_sgp(cls, login):
        logger.info('Consultando informação de %s.', login)
        try:
            response = requests.get(f'{settings.SME_INTEGRACAO_URL}/api/AutenticacaoSgp/{login}/dados', headers=cls.headers)
            if response.status_code == status.HTTP_200_OK:
                return response.json()
            else:
                logger.info("Dados não encontrados: %s", response)
                raise SmeIntegracaoException('Dados não encontrados.')
        except Exception as err:
            logger.info("Erro ao consultar informação: %s", str(err))
            raise SmeIntegracaoException(str(err))


    @classmethod
    def atribuir_perfil_coresso(cls, login, visao):
        """ Atribuição de Perfil:

        /api/perfis/servidores/{codigoRF}/perfil/{perfil}/atribuirPerfil - GET
        CodigoRf - RF ou CPF do usuário
        Perfil - Guid do perfil a ser atribuído

        :param login:
        :param visao:
        :return:
        """
        logger.info(f'Atribuindo visão {visao} ao usuário {login}.')
        sys_grupo_ids = {
            "UE": settings.SYS_GRUPO_ID_UE,
            "DRE": settings.SYS_GRUPO_ID_DRE,
            "SME": settings.SYS_GRUPO_ID_SME,
            "PTRF": settings.SYS_GRUPO_ID_PTRF
        }
        try:
            grupo_id = sys_grupo_ids[visao]
            url = f'{settings.SME_INTEGRACAO_URL}/api/perfis/servidores/{login}/perfil/{grupo_id}/atribuirPerfil'
            response = requests.get(url, headers=cls.headers)
            if response.status_code == status.HTTP_200_OK:
                return ""
            else:
                logger.info("Falha ao tentar fazer atribuição de perfil: %s", response)
                raise SmeIntegracaoException('Falha ao fazer atribuição de perfil.')
        except Exception as err:
            logger.info("Erro ao tentar fazer atribuição de perfil: %s", str(err))
            raise SmeIntegracaoException(str(err))
