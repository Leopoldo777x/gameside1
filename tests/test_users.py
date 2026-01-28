import pytest

from tests import conftest
from users.models import Token

from .helpers import get_json, post_json


@pytest.mark.django_db
def test_auth(client, user):
    data = {'username': user.username, 'password': '1234'}
    url = conftest.AUTH_URL
    status, response = post_json(client, url, data)
    assert status == 200
    assert Token.objects.get(user=user, key=response['token'])


@pytest.mark.django_db
def test_auth_fails_when_invalid_json_body(client):
    url = conftest.AUTH_URL
    status, response = post_json(client, url, '{')
    assert status == 400
    assert response == {'error': 'Invalid JSON body'}


@pytest.mark.django_db
def test_auth_fails_when_missing_required_fields(client):
    url = conftest.AUTH_URL
    status, response = post_json(client, url)
    assert status == 400
    assert response == {'error': 'Missing required fields'}


@pytest.mark.django_db
def test_auth_fails_when_invalid_credentials(client, user):
    data = {'username': user.username, 'password': 'invalid'}
    url = conftest.AUTH_URL
    status, response = post_json(client, url, data)
    assert status == 401
    assert response == {'error': 'Invalid credentials'}


@pytest.mark.django_db
def test_auth_fails_when_method_is_not_allowed(client):
    url = conftest.AUTH_URL
    status, response = get_json(client, url)
    assert status == 405
    assert response == {'error': 'Method not allowed'}
