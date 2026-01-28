import uuid

import pytest

from factories import GameFactory, ReviewFactory
from games.models import Review
from tests import conftest

from .helpers import compare_games, compare_reviews, get_json, get_obj_by_pk, post_json

# ==============================================================================
# GAMES
# ==============================================================================


@pytest.mark.django_db
def test_game_list(client):
    games = GameFactory.create_batch(10)
    status, response = get_json(client, conftest.GAME_LIST_URL)
    assert status == 200
    for game in response:
        expected_game = get_obj_by_pk(games, game['id'])
        compare_games(game, expected_game)


@pytest.mark.django_db
def test_game_list_fails_when_method_is_not_allowed(client):
    status, response = post_json(client, conftest.GAME_LIST_URL)
    assert status == 405
    assert response == {'error': 'Method not allowed'}


@pytest.mark.django_db
def test_game_list_with_querystring_filter(client, category, platform):
    blacklist_games = GameFactory.create_batch(5)
    games = GameFactory.create_batch(5, category=category, platforms=[platform])
    url = conftest.GAME_FILTER_URL.format(category_slug=category.slug, platform_slug=platform.slug)
    status, response = get_json(client, url)
    assert status == 200
    for game in response:
        expected_game = get_obj_by_pk(games, game['id'])
        compare_games(game, expected_game)
    blacklist_games_pks = [game.pk for game in blacklist_games]
    for game in response:
        assert game['id'] not in blacklist_games_pks


@pytest.mark.django_db
def test_game_list_with_querystring_filter_fails_when_method_is_not_allowed(client):
    url = conftest.GAME_FILTER_URL.format(
        category_slug='category-test', platform_slug='platform-test'
    )
    status, response = post_json(client, url)
    assert status == 405
    assert response == {'error': 'Method not allowed'}


@pytest.mark.django_db
def test_game_detail(client, game):
    url = conftest.GAME_DETAIL_URL.format(game_slug=game.slug)
    status, response = get_json(client, url)
    assert status == 200
    compare_games(response, game)


@pytest.mark.django_db
def test_game_detail_fails_when_method_is_not_allowed(client, game):
    url = conftest.GAME_DETAIL_URL.format(game_slug=game.slug)
    status, response = post_json(client, url)
    assert status == 405
    assert response == {'error': 'Method not allowed'}


@pytest.mark.django_db
def test_game_detail_fails_when_game_does_not_exist(client):
    url = conftest.GAME_DETAIL_URL.format(game_slug='test')
    status, response = get_json(client, url)
    assert status == 404
    assert response == {'error': 'Game not found'}


# ==============================================================================
# REVIEWS
# ==============================================================================


@pytest.mark.django_db
def test_review_list(client, game):
    reviews = ReviewFactory.create_batch(5, game=game)
    url = conftest.REVIEW_LIST_URL.format(game_slug=game.slug)
    status, response = get_json(client, url)
    assert status == 200
    for review in response:
        expected_review = get_obj_by_pk(reviews, review['id'])
        compare_reviews(review, expected_review)


@pytest.mark.django_db
def test_review_list_fails_when_method_is_not_allowed(client, game):
    url = conftest.REVIEW_LIST_URL.format(game_slug=game.slug)
    status, response = post_json(client, url)
    assert status == 405
    assert response == {'error': 'Method not allowed'}


@pytest.mark.django_db
def test_review_list_fails_when_game_does_not_exist(client):
    url = conftest.REVIEW_LIST_URL.format(game_slug='test')
    status, response = get_json(client, url)
    assert status == 404
    assert response == {'error': 'Game not found'}


@pytest.mark.django_db
def test_review_detail(client, review):
    url = conftest.REVIEW_DETAIL_URL.format(review_pk=review.pk)
    status, response = get_json(client, url)
    assert status == 200
    compare_reviews(response, review)


@pytest.mark.django_db
def test_review_detail_fails_when_method_is_not_allowed(client):
    url = conftest.REVIEW_DETAIL_URL.format(review_pk=1)
    status, response = post_json(client, url)


@pytest.mark.django_db
def test_review_detail_fails_when_review_does_not_exist(client):
    url = conftest.REVIEW_DETAIL_URL.format(review_pk=1)
    status, response = get_json(client, url)
    assert status == 404
    assert response == {'error': 'Review not found'}


@pytest.mark.django_db
def test_add_review(client, user, game):
    data = {'rating': 5, 'comment': 'This is a test comment'}
    url = conftest.REVIEW_ADD_URL.format(game_slug=game.slug)
    status, response = post_json(client, url, data, user.token.key)
    assert status == 200
    assert response == {'id': 1}
    review = Review.objects.get(pk=response['id'])
    assert review.rating == data['rating']
    assert review.comment == data['comment']
    assert review.game == game
    assert review.author == user


@pytest.mark.django_db
def test_add_review_fails_when_invalid_json_body(client, game):
    url = conftest.REVIEW_ADD_URL.format(game_slug=game.slug)
    status, response = post_json(client, url, '{')
    assert status == 400
    assert response == {'error': 'Invalid JSON body'}


@pytest.mark.django_db
def test_add_review_fails_when_token_is_invalid(client, game):
    data = {'rating': 1, 'comment': 'This is a test comment'}
    url = conftest.REVIEW_ADD_URL.format(game_slug=game.slug)
    status, response = post_json(client, url, data, 'invalid-token')
    assert status == 400
    assert response == {'error': 'Invalid authentication token'}


@pytest.mark.django_db
def test_add_review_fails_when_missing_required_fields(client, game):
    url = conftest.REVIEW_ADD_URL.format(game_slug=game.slug)
    status, response = post_json(client, url)
    assert status == 400
    assert response == {'error': 'Missing required fields'}


@pytest.mark.django_db
def test_add_review_fails_when_rating_is_out_of_range(client, user, game):
    data = {'rating': 6, 'comment': 'This is a test comment'}
    url = conftest.REVIEW_ADD_URL.format(game_slug=game.slug)
    status, response = post_json(client, url, data, user.token.key)
    assert status == 400
    assert response == {'error': 'Rating is out of range'}


@pytest.mark.django_db
def test_add_review_fails_when_unregistered_token(client, game):
    data = {'rating': 1, 'comment': 'This is a test comment'}
    url = conftest.REVIEW_ADD_URL.format(game_slug=game.slug)
    status, response = post_json(client, url, data, str(uuid.uuid4()))
    assert status == 401
    assert response == {'error': 'Unregistered authentication token'}


@pytest.mark.django_db
def test_add_review_fails_when_game_not_found(client, user):
    data = {'rating': 1, 'comment': 'This is a test comment'}
    url = conftest.REVIEW_ADD_URL.format(game_slug='test')
    status, response = post_json(client, url, data, user.token.key)
    assert status == 404
    assert response == {'error': 'Game not found'}
