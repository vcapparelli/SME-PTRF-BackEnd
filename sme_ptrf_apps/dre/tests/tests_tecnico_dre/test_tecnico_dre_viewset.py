import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.tecnicos_dre_viewset import TecnicosDreViewSet

pytestmark = pytest.mark.django_db


def test_view_set(tecnico_dre, fake_user):
    request = APIRequestFactory().get("")
    detalhe = TecnicosDreViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=fake_user)
    response = detalhe(request, uuid=tecnico_dre.uuid)

    assert response.status_code == status.HTTP_200_OK
