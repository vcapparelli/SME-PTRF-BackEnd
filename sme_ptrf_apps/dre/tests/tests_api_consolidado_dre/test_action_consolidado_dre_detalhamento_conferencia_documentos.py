import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_get_consolidado_dre_detalhamento_conferencia_documentos(
    jwt_authenticated_client_dre,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    consolidado_dre_teste_api_consolidado_dre,
):
    consolidado_dre_uuid = consolidado_dre_teste_api_consolidado_dre.uuid

    response = jwt_authenticated_client_dre.get(
        f'/api/consolidados-dre/detalhamento-conferencia-documentos/?uuid={consolidado_dre_uuid}',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
