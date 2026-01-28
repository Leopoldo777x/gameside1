import pytest

from platforms.models import Platform
from tests import conftest

from .helpers import compare_platforms, get_json, get_obj_by_pk, post_json


@pytest.mark.django_db
def test_platform_list(client, platform):
    platforms = Platform.objects.all()
    url = conftest.PLATFORM_LIST_URL
    status, response = get_json(client, url)
    assert status == 200
    for platform in response:
        expected_platform = get_obj_by_pk(platforms, platform['id'])
        compare_platforms(platform, expected_platform)


@pytest.mark.django_db
def test_platform_list_fails_when_method_is_not_allowed(client):
    url = conftest.PLATFORM_LIST_URL
    status, response = post_json(client, url)
    assert status == 405
    assert response == {'error': 'Method not allowed'}


@pytest.mark.django_db
def test_platform_detail(client, platform):
    url = conftest.PLATFORM_DETAIL_URL.format(platform_slug=platform.slug)
    status, response = get_json(client, url)
    assert status == 200
    compare_platforms(response, platform)


@pytest.mark.django_db
def test_platform_detail_fails_when_method_is_not_allowed(client, platform):
    url = conftest.PLATFORM_DETAIL_URL.format(platform_slug=platform.slug)
    status, response = post_json(client, url)
    assert status == 405
    assert response == {'error': 'Method not allowed'}


@pytest.mark.django_db
def test_platform_detail_fails_when_platform_does_not_exist(client):
    url = conftest.PLATFORM_DETAIL_URL.format(platform_slug='test')
    status, response = get_json(client, url)
    assert status == 404
    assert response == {'error': 'Platform not found'}
