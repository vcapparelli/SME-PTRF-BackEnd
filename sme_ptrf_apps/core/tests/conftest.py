import pytest

from django.contrib.auth.models import Permission
from sme_ptrf_apps.users.models import Grupo
from django.contrib.contenttypes.models import ContentType


@pytest.fixture
def permissoes_associacao():
    permissoes = [
        Permission.objects.filter(codename='add_associacao').first(),
        Permission.objects.filter(codename='view_associacao').first(),
        Permission.objects.filter(codename='change_associacao').first(),
        Permission.objects.filter(codename='delete_associacao').first()
    ]

    return permissoes


@pytest.fixture
def permissoes_ata():
    permissoes = [
        Permission.objects.filter(codename='add_ata').first(),
        Permission.objects.filter(codename='view_ata').first(),
        Permission.objects.filter(codename='change_ata').first(),
        Permission.objects.filter(codename='delete_ata').first()
    ]

    return permissoes


@pytest.fixture
def permissoes_cobrancas_prestacoes():
    permissoes = [
        Permission.objects.filter(codename='add_cobrancaprestacaoconta').first(),
        Permission.objects.filter(codename='view_cobrancaprestacaoconta').first(),
        Permission.objects.filter(codename='change_cobrancaprestacaoconta').first(),
        Permission.objects.filter(codename='delete_cobrancaprestacaoconta').first()
    ]

    return permissoes


@pytest.fixture
def permissoes_observacoes_conciliacao():
    permissoes = [
        Permission.objects.filter(codename='add_observacaoconciliacao').first(),
        Permission.objects.filter(codename='view_observacaoconciliacao').first(),
        Permission.objects.filter(codename='change_observacaoconciliacao').first(),
        Permission.objects.filter(codename='delete_observacaoconciliacao').first()
    ]

    return permissoes


@pytest.fixture
def permissoes_demonstrativo_finaceiro():
    permissoes = [
        Permission.objects.filter(codename='add_demonstrativofinanceiro').first(),
        Permission.objects.filter(codename='view_demonstrativofinanceiro').first(),
        Permission.objects.filter(codename='change_demonstrativofinanceiro').first(),
        Permission.objects.filter(codename='delete_demonstrativofinanceiro').first()
    ]

    return permissoes


@pytest.fixture
def permissoes_membro_associacao():
    permissoes = [
        Permission.objects.filter(codename='add_membroassociacao').first(),
        Permission.objects.filter(codename='view_membroassociacao').first(),
        Permission.objects.filter(codename='change_membroassociacao').first(),
        Permission.objects.filter(codename='delete_membroassociacao').first()
    ]

    return permissoes


@pytest.fixture
def permissoes_notificacao():
    permissoes = [
        Permission.objects.filter(codename='add_notificacao').first(),
        Permission.objects.filter(codename='view_notificacao').first(),
        Permission.objects.filter(codename='change_notificacao').first(),
        Permission.objects.filter(codename='delete_notificacao').first()
    ]

    return permissoes


@pytest.fixture
def permissoes_prestacoes_conta():
    permissoes = [
        Permission.objects.filter(codename='add_prestacaoconta').first(),
        Permission.objects.filter(codename='view_prestacaoconta').first(),
        Permission.objects.filter(codename='change_prestacaoconta').first(),
        Permission.objects.filter(codename='delete_prestacaoconta').first()
    ]

    return permissoes


@pytest.fixture
def permissoes_processo_associacao():
    permissoes = [
        Permission.objects.filter(codename='add_processoassociacao').first(),
        Permission.objects.filter(codename='view_processoassociacao').first(),
        Permission.objects.filter(codename='change_processoassociacao').first(),
        Permission.objects.filter(codename='delete_processoassociacao').first()
    ]

    return permissoes


@pytest.fixture
def permissoes_relacoes_bens():
    permissoes = [
        Permission.objects.filter(codename='add_relacaobens').first(),
        Permission.objects.filter(codename='view_relacaobens').first(),
        Permission.objects.filter(codename='change_relacaobens').first(),
        Permission.objects.filter(codename='delete_relacaobens').first()
    ]

    return permissoes


@pytest.fixture
def permissoes_tipo_devolucao():
    permissoes = [
        Permission.objects.filter(codename='add_tipodevolucaoaotesouro').first(),
        Permission.objects.filter(codename='view_tipodevolucaoaotesouro').first(),
        Permission.objects.filter(codename='change_tipodevolucaoaotesouro').first(),
        Permission.objects.filter(codename='delete_tipodevolucaoaotesouro').first()
    ]

    return permissoes
    

@pytest.fixture
def permissoes_unidades():
    permissoes = [
        Permission.objects.filter(codename='add_unidade').first(),
        Permission.objects.filter(codename='view_unidade').first(),
        Permission.objects.filter(codename='change_unidade').first(),
        Permission.objects.filter(codename='delete_unidade').first()
    ]

    return permissoes


@pytest.fixture
def grupo_associacao(permissoes_associacao):
    g = Grupo.objects.create(name="associacao")
    g.permissions.add(*permissoes_associacao)
    return g


@pytest.fixture
def grupo_ata(permissoes_ata):
    g = Grupo.objects.create(name="ata")
    g.permissions.add(*permissoes_ata)
    return g


@pytest.fixture
def grupo_cobrancas_prestacoes(permissoes_cobrancas_prestacoes):
    g = Grupo.objects.create(name="cobrancas_prestacoes")
    g.permissions.add(*permissoes_cobrancas_prestacoes)
    return g


@pytest.fixture
def grupo_observacoes_conciliacao(permissoes_observacoes_conciliacao):
    g = Grupo.objects.create(name="observacoes_conciliacao")
    g.permissions.add(*permissoes_observacoes_conciliacao)
    return g


@pytest.fixture
def grupo_demonstrativo_finaceiro(permissoes_demonstrativo_finaceiro):
    g = Grupo.objects.create(name="demonstrativo_finaceiro")
    g.permissions.add(*permissoes_demonstrativo_finaceiro)
    return g


@pytest.fixture
def grupo_membros_associacao(permissoes_membro_associacao):
    g = Grupo.objects.create(name="membro_associacao")
    g.permissions.add(*permissoes_membro_associacao)
    return g


@pytest.fixture
def grupo_notificacao(permissoes_notificacao):
    g = Grupo.objects.create(name="notificacao")
    g.permissions.add(*permissoes_notificacao)
    return g


@pytest.fixture
def grupo_prestacoes_conta(permissoes_prestacoes_conta):
    g = Grupo.objects.create(name="prestacoes_conta")
    g.permissions.add(*permissoes_prestacoes_conta)
    return g


@pytest.fixture
def grupo_processo_associacao(permissoes_processo_associacao):
    g = Grupo.objects.create(name="processo_associacao")
    g.permissions.add(*permissoes_processo_associacao)
    return g


@pytest.fixture
def grupo_relacoes_bens(permissoes_relacoes_bens):
    g = Grupo.objects.create(name="relacoes_bens")
    g.permissions.add(*permissoes_relacoes_bens)
    return g


@pytest.fixture
def grupo_tipo_devolucao(permissoes_tipo_devolucao):
    g = Grupo.objects.create(name="tipo_devolucao")
    g.permissions.add(*permissoes_tipo_devolucao)
    return g


@pytest.fixture
def grupo_unidades(permissoes_unidades):
    g = Grupo.objects.create(name="unidades")
    g.permissions.add(*permissoes_unidades)
    return g


@pytest.fixture
def usuario_permissao_associacao(
        unidade,
        grupo_associacao,
        grupo_ata,
        grupo_cobrancas_prestacoes,
        grupo_observacoes_conciliacao,
        grupo_demonstrativo_finaceiro,
        grupo_membros_associacao,
        grupo_notificacao,
        grupo_prestacoes_conta,
        grupo_processo_associacao,
        grupo_relacoes_bens,
        grupo_tipo_devolucao,
        grupo_unidades):

    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.groups.add(
        grupo_associacao,
        grupo_ata,
        grupo_cobrancas_prestacoes,
        grupo_observacoes_conciliacao,
        grupo_demonstrativo_finaceiro,
        grupo_membros_associacao,
        grupo_notificacao,
        grupo_prestacoes_conta,
        grupo_processo_associacao,
        grupo_relacoes_bens,
        grupo_tipo_devolucao,
        grupo_unidades)
    user.save()
    return user


@pytest.fixture
def jwt_authenticated_client_a(client, usuario_permissao_associacao):
    from unittest.mock import patch

    from rest_framework.test import APIClient
    api_client = APIClient()
    with patch('sme_ptrf_apps.users.api.views.login.AutenticacaoService.autentica') as mock_post:
        data = {
            "nome": "LUCIA HELENA",
            "cpf": "62085077072",
            "email": "luh@gmail.com",
            "login": "7210418"
        }
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = data
        resp = api_client.post('/api/login', {'login': usuario_permissao_associacao.username,
                                              'senha': usuario_permissao_associacao.password}, format='json')
        resp_data = resp.json()
        api_client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(resp_data['token']))
    return api_client
