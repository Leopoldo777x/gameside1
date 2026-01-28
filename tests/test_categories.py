import pytest

from categories.models import Category
from factories import CategoryFactory
from tests import conftest

from .helpers import compare_categories, get_json, post_json


@pytest.mark.django_db
def test_category_list(client):
    CategoryFactory.create_batch(10)
    categories = Category.objects.all()
    status, response = get_json(client, conftest.CATEGORY_LIST_URL)
    assert status == 200
    for category in response:
        compare_categories(category, categories.get(pk=category['id']))


@pytest.mark.django_db
def test_category_list_fails_when_method_is_not_allowed(client):
    status, response = post_json(client, conftest.CATEGORY_LIST_URL)
    assert status == 405
    assert response == {'error': 'Method not allowed'}


@pytest.mark.django_db
def test_category_detail(client, category):
    url = conftest.CATEGORY_DETAIL_URL.format(category_slug=category.slug)
    status, response = get_json(client, url)
    assert status == 200
    compare_categories(response, category)


@pytest.mark.django_db
def test_category_detail_fails_when_method_is_not_allowed(client, category):
    url = conftest.CATEGORY_DETAIL_URL.format(category_slug=category.slug)
    status, _ = post_json(client, url)
    assert status == 405


@pytest.mark.django_db
def test_category_detail_fails_when_category_does_not_exist(client):
    url = conftest.CATEGORY_DETAIL_URL.format(category_slug='test')
    status, response = get_json(client, url)
    assert status == 404
    assert response == {'error': 'Category not found'}
