import pytest

from ...models import Despesa

pytestmark = pytest.mark.django_db


def test_get_tags_informacoes_list():
    tags = Despesa.get_tags_informacoes_list()
    assert tags == [
        {"id": "1", "nome": "Antecipado", "descricao": "Data do pagamento anterior à data do documento."},
        {"id": "2", "nome": "Estornado", "descricao": "Despesa estornada."},
        {"id": "3", "nome": "Parcial", "descricao": "Parte da despesa paga com recursos próprios ou de mais de uma conta."},
        {"id": "4", "nome": "Imposto", "descricao": "Despesa com recolhimento de imposto."},
        {"id": "5", "nome": "Imposto Pago", "descricao": "Imposto recolhido relativo a uma despesa de serviço."},
        {"id": "6", "nome": "Excluído", "descricao": "Lançamento excluído."},
        {"id": "7", "nome": "Não Reconhecida", "descricao": "Despesa não reconhecida pela associação."},
        {"id": "8", "nome": "Sem comprovação fiscal", "descricao": "Despesa sem comprovação fiscal."},
        {"id": "9", "nome": "Conciliada", "descricao": "Despesa com conciliação bancária realizada."},
        {"id": "10", "nome": "Não conciliada", "descricao": "Despesa sem conciliação bancária realizada."},
    ]
