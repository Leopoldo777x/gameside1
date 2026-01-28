import uuid
from decimal import Decimal

import pytest

from factories import GameFactory, OrderFactory
from orders.models import Order
from tests import conftest

from .helpers import compare_games, datetime_isoformats_are_close, get_json, post_json

# ==============================================================================
# ADD ORDER
# ==============================================================================


@pytest.mark.django_db
def test_add_order(client, user):
    url = conftest.ORDER_ADD_URL
    status, response = post_json(client, url, bearer_token=user.token.key)
    assert status == 200
    assert response['id'] == 1
    assert Order.objects.get(pk=1, user=user)


@pytest.mark.django_db
def test_add_order_fails_when_token_is_invalid(client):
    url = conftest.ORDER_ADD_URL
    status, response = post_json(client, url, bearer_token='invalid-token')
    assert status == 400
    assert response == {'error': 'Invalid authentication token'}


@pytest.mark.django_db
def test_add_order_fails_when_unregistered_token(client):
    url = conftest.ORDER_ADD_URL
    status, response = post_json(client, url, bearer_token=str(uuid.uuid4()))
    assert status == 401
    assert response == {'error': 'Unregistered authentication token'}


@pytest.mark.django_db
def test_add_order_fails_when_method_is_not_allowed(client):
    url = conftest.ORDER_ADD_URL
    status, _ = get_json(client, url)
    assert status == 405


# ==============================================================================
# ORDER DETAIL
# ==============================================================================


@pytest.mark.django_db
def test_order_detail(client, user, order):
    url = conftest.ORDER_DETAIL_URL.format(order_pk=order.pk)
    status, response = get_json(client, url, bearer_token=user.token.key)
    assert status == 200
    assert response['id'] == order.pk
    assert response['status'] == order.get_status_display()
    for game in response['games']:
        compare_games(game, order.games.get(pk=game['id']))
    assert datetime_isoformats_are_close(response['created_at'], order.created_at.isoformat())
    assert datetime_isoformats_are_close(response['updated_at'], order.updated_at.isoformat())
    assert Decimal(response['price']) == order.price


@pytest.mark.django_db
def test_order_key_is_None_when_order_is_not_paid(client, user):
    order = OrderFactory(user=user, status=Order.Status.CONFIRMED)
    url = conftest.ORDER_DETAIL_URL.format(order_pk=order.pk)
    status, response = get_json(client, url, bearer_token=user.token.key)
    assert status == 200
    assert response['key'] is None


@pytest.mark.django_db
def test_order_key_is_returned_when_order_is_paid(client, user):
    order = OrderFactory(user=user, status=Order.Status.PAID)
    url = conftest.ORDER_DETAIL_URL.format(order_pk=order.pk)
    status, response = get_json(client, url, bearer_token=user.token.key)
    assert status == 200
    assert response['key'] == order.key


@pytest.mark.django_db
def test_order_detail_fails_when_invalid_token(client, order):
    url = conftest.ORDER_DETAIL_URL.format(order_pk=order.pk)
    status, response = get_json(client, url, bearer_token='invalid-token')
    assert status == 400
    assert response == {'error': 'Invalid authentication token'}


@pytest.mark.django_db
def test_order_detail_fails_when_unregistered_token(client, order):
    url = conftest.ORDER_DETAIL_URL.format(order_pk=order.pk)
    status, response = get_json(client, url, bearer_token=str(uuid.uuid4()))
    assert status == 401
    assert response == {'error': 'Unregistered authentication token'}


@pytest.mark.django_db
def test_order_detail_fails_when_user_is_not_the_owner_of_requested_order(client, user):
    order = OrderFactory()
    url = conftest.ORDER_DETAIL_URL.format(order_pk=order.pk)
    status, response = get_json(client, url, bearer_token=user.token.key)
    assert status == 403
    assert response == {'error': 'User is not the owner of requested order'}


@pytest.mark.django_db
def test_order_detail_fails_when_order_does_not_exist(client, user):
    url = conftest.ORDER_DETAIL_URL.format(order_pk=1)
    status, response = get_json(client, url, bearer_token=user.token.key)
    assert status == 404
    assert response == {'error': 'Order not found'}


@pytest.mark.django_db
def test_order_detail_fails_when_method_is_not_allowed(client, order):
    url = conftest.ORDER_DETAIL_URL.format(order_pk=order.pk)
    status, _ = post_json(client, url)
    assert status == 405


# ==============================================================================
# ORDER GAME LIST
# ==============================================================================


@pytest.mark.django_db
def test_order_game_list(client, user, order):
    url = conftest.ORDER_GAME_LIST_URL.format(order_pk=order.pk)
    status, response = get_json(client, url, bearer_token=user.token.key)
    assert status == 200
    for game in response:
        compare_games(game, order.games.get(pk=game['id']))


@pytest.mark.django_db
def test_order_game_list_fails_when_invalid_token(client, order):
    url = conftest.ORDER_GAME_LIST_URL.format(order_pk=order.pk)
    status, response = get_json(client, url, bearer_token='invalid-token')
    assert status == 400
    assert response == {'error': 'Invalid authentication token'}


@pytest.mark.django_db
def test_order_game_list_when_unregistered_token(client, order):
    url = conftest.ORDER_GAME_LIST_URL.format(order_pk=order.pk)
    status, response = get_json(client, url, bearer_token=str(uuid.uuid4()))
    assert status == 401
    assert response == {'error': 'Unregistered authentication token'}


@pytest.mark.django_db
def test_order_game_list_fails_when_user_is_not_the_owner_of_requested_order(client, user):
    order = OrderFactory()
    url = conftest.ORDER_GAME_LIST_URL.format(order_pk=order.pk)
    status, response = get_json(client, url, bearer_token=user.token.key)
    assert status == 403
    assert response == {'error': 'User is not the owner of requested order'}


@pytest.mark.django_db
def test_order_game_list_fails_when_order_does_not_exist(client, user):
    url = conftest.ORDER_GAME_LIST_URL.format(order_pk=1)
    status, response = get_json(client, url, bearer_token=user.token.key)
    assert status == 404
    assert response == {'error': 'Order not found'}


@pytest.mark.django_db
def test_order_game_list_fails_when_method_is_not_allowed(client, order):
    url = conftest.ORDER_GAME_LIST_URL.format(order_pk=order.pk)
    status, _ = post_json(client, url)
    assert status == 405


# ==============================================================================
# ADD GAME TO ORDER
# ==============================================================================


@pytest.mark.django_db
def test_add_game_to_order(client, user, order, game):
    url = conftest.ORDER_ADD_GAME_URL.format(order_pk=order.pk)
    data = {'game-slug': game.slug}
    status, response = post_json(client, url, data, user.token.key)
    assert status == 200
    assert response['num-games-in-order'] == 1
    assert order.games.get(pk=game.pk)


@pytest.mark.django_db
def test_add_game_to_order_fails_when_method_is_not_allowed(client, order):
    url = conftest.ORDER_ADD_GAME_URL.format(order_pk=order.pk)
    status, _ = get_json(client, url)
    assert status == 405


@pytest.mark.django_db
def test_add_game_to_order_fails_when_invalid_json_body(client, order):
    url = conftest.ORDER_ADD_GAME_URL.format(order_pk=order.pk)
    status, response = post_json(client, url, '{')
    assert status == 400
    assert response == {'error': 'Invalid JSON body'}


@pytest.mark.django_db
def test_add_game_to_order_fails_when_missing_required_fields(client, order):
    url = conftest.ORDER_ADD_GAME_URL.format(order_pk=order.pk)
    status, response = post_json(client, url)
    assert status == 400
    assert response == {'error': 'Missing required fields'}


@pytest.mark.django_db
def add_game_to_order_fails_when_invalid_token(client):
    url = conftest.ORDER_ADD_GAME_URL.format(order_pk=1)
    data = {'game-slug': 'game'}
    status, response = post_json(client, url, data, 'invalid-token')
    assert status == 400
    assert response == {'error': 'Invalid authentication token'}


@pytest.mark.django_db
def add_game_to_order_fails_when_unregistered_token(client):
    url = conftest.ORDER_ADD_GAME_URL.format(order_pk=1)
    data = {'game-slug': 'game'}
    status, response = post_json(client, url, data, str(uuid.uuid4()))
    assert status == 401
    assert response == {'error': 'Unregistered authentication token'}


@pytest.mark.django_db
def test_add_game_to_order_fails_when_order_does_not_exist(client, user):
    url = conftest.ORDER_ADD_GAME_URL.format(order_pk=1)
    data = {'game-slug': 'game'}
    status, response = post_json(client, url, data, user.token.key)
    assert status == 404
    assert response == {'error': 'Order not found'}


@pytest.mark.django_db
def test_add_game_to_order_fails_when_game_does_not_exist(client, user, order):
    url = conftest.ORDER_ADD_GAME_URL.format(order_pk=order.pk)
    data = {'game-slug': 'game'}
    status, response = post_json(client, url, data, user.token.key)
    assert status == 404
    assert response == {'error': 'Game not found'}


@pytest.mark.django_db
def test_add_game_to_order_fails_when_user_is_not_the_owner_of_requested_order(client, user, game):
    order = OrderFactory(games=[game])
    url = conftest.ORDER_ADD_GAME_URL.format(order_pk=order.pk)
    data = {'game-slug': game.slug}
    status, response = post_json(client, url, data, user.token.key)
    assert status == 403
    assert response == {'error': 'User is not the owner of requested order'}


@pytest.mark.django_db
def add_game_to_order_fails_when_game_is_out_of_stock(client, user):
    game = GameFactory(stock=0)
    url = conftest.ORDER_ADD_GAME_URL.format(order_pk=1)
    data = {'game-slug': game.slug}
    status, response = post_json(client, url, data, user.token.key)
    assert status == 400
    assert response == {'error': 'Game is out of stock'}


# ==============================================================================
# CHANGE ORDER STATUS
# ==============================================================================


@pytest.mark.django_db
def test_change_order_status_to_confirmed(client, user):
    order = OrderFactory(user=user, status=Order.Status.INITIATED)
    data = {'status': Order.Status.CONFIRMED}
    url = conftest.ORDER_STATUS_URL.format(order_pk=order.pk)
    status, response = post_json(client, url, data, user.token.key)
    assert status == 200
    assert response['status'] == 'Confirmed'
    assert Order.objects.get(pk=order.pk, status=Order.Status.CONFIRMED)


@pytest.mark.django_db
def test_change_order_status_to_cancelled(client, user):
    order = OrderFactory(user=user, status=Order.Status.INITIATED)
    data = {'status': Order.Status.CANCELLED}
    url = conftest.ORDER_STATUS_URL.format(order_pk=order.pk)
    status, response = post_json(client, url, data, user.token.key)
    assert status == 200
    assert response['status'] == 'Cancelled'
    assert Order.objects.get(pk=order.pk, status=Order.Status.CANCELLED)


@pytest.mark.django_db
def test_change_order_status_fails_when_method_is_not_allowed(client, order):
    url = conftest.ORDER_STATUS_URL.format(order_pk=order.pk)
    status, response = get_json(client, url)
    assert status == 405


@pytest.mark.django_db
def test_change_order_status_fails_when_missing_required_fields(client, order):
    url = conftest.ORDER_STATUS_URL.format(order_pk=order.pk)
    status, response = post_json(client, url)
    assert status == 400
    assert response == {'error': 'Missing required fields'}


@pytest.mark.django_db
def test_change_order_status_fails_when_invalid_token(client, order):
    data = {'status': Order.Status.CONFIRMED}
    url = conftest.ORDER_STATUS_URL.format(order_pk=order.pk)
    status, response = post_json(client, url, data, 'invalid-token')
    assert status == 400
    assert response == {'error': 'Invalid authentication token'}


@pytest.mark.django_db
def test_change_order_status_fails_when_unregistered_token(client, order):
    data = {'status': Order.Status.CONFIRMED}
    url = conftest.ORDER_STATUS_URL.format(order_pk=order.pk)
    status, response = post_json(client, url, data, str(uuid.uuid4()))
    assert status == 401
    assert response == {'error': 'Unregistered authentication token'}


@pytest.mark.django_db
def test_change_order_status_fails_when_order_does_not_exist(client, user):
    data = {'status': Order.Status.CONFIRMED}
    url = conftest.ORDER_STATUS_URL.format(order_pk=1)
    status, response = post_json(client, url, data, user.token.key)
    assert status == 404
    assert response == {'error': 'Order not found'}


@pytest.mark.django_db
def test_change_order_status_fails_when_user_is_not_the_owner_of_requested_order(client, user):
    order = OrderFactory()
    data = {'status': Order.Status.CONFIRMED}
    url = conftest.ORDER_STATUS_URL.format(order_pk=order.pk)
    status, response = post_json(client, url, data, user.token.key)
    assert status == 403
    assert response == {'error': 'User is not the owner of requested order'}


@pytest.mark.parametrize('status', [Order.Status.INITIATED, Order.Status.PAID])
@pytest.mark.django_db
def test_change_order_status_fails_when_invalid_status(client, user, order, status):
    """
    Desde una llamada a la API no es posible cambiar el estado de un pedido
    a INITIATED o PAID. Si ello se intentara habría que devolver 'Invalid status'
    ya que estos estados sólo se pueden cambiar desde el propio backend en función
    de cierta lógica de negocio.
    """
    data = {'status': status}
    url = conftest.ORDER_STATUS_URL.format(order_pk=order.pk)
    status, response = post_json(client, url, data, user.token.key)
    assert status == 400
    assert response == {'error': 'Invalid status'}


@pytest.mark.django_db
@pytest.mark.parametrize(
    'status', [Order.Status.CANCELLED, Order.Status.CONFIRMED, Order.Status.PAID]
)
def test_change_order_status_to_confirmed_fails_when_order_is_not_initiated(client, user, status):
    order = OrderFactory(user=user, status=status)
    data = {'status': Order.Status.CONFIRMED}
    url = conftest.ORDER_STATUS_URL.format(order_pk=order.pk)
    status, response = post_json(client, url, data, user.token.key)
    assert status == 400
    assert response == {'error': 'Orders can only be confirmed/cancelled when initiated'}


@pytest.mark.django_db
@pytest.mark.parametrize(
    'status', [Order.Status.CANCELLED, Order.Status.CONFIRMED, Order.Status.PAID]
)
def test_change_order_status_to_cancelled_fails_when_order_is_not_initiated(client, user, status):
    order = OrderFactory(user=user, status=status)
    data = {'status': Order.Status.CANCELLED}
    url = conftest.ORDER_STATUS_URL.format(order_pk=order.pk)
    status, response = post_json(client, url, data, user.token.key)
    assert status == 400
    assert response == {'error': 'Orders can only be confirmed/cancelled when initiated'}


# ==============================================================================
# PAY ORDER
# ==============================================================================


@pytest.mark.django_db
def test_pay_order(client, user):
    order = OrderFactory(user=user, status=Order.Status.CONFIRMED)
    data = {
        'card-number': '1234-1234-1234-1234',
        'exp-date': '01/2099',
        'cvc': '123',
    }
    url = conftest.ORDER_PAY_URL.format(order_pk=order.pk)
    status, response = post_json(client, url, data, user.token.key)
    assert status == 200
    assert response['status'] == 'Paid'
    assert Order.objects.get(pk=order.pk, status=Order.Status.PAID)


@pytest.mark.django_db
def test_pay_order_fails_when_invalid_json_body(client, order):
    url = conftest.ORDER_PAY_URL.format(order_pk=order.pk)
    status, response = post_json(client, url, '{')
    assert status == 400
    assert response == {'error': 'Invalid JSON body'}


@pytest.mark.django_db
def test_pay_order_fails_when_invalid_token(client, order):
    data = {
        'card-number': '1234-1234-1234-1234',
        'exp-date': '01/2099',
        'cvc': '123',
    }
    url = conftest.ORDER_PAY_URL.format(order_pk=order.pk)
    status, response = post_json(client, url, data, 'invalid-token')
    assert status == 400
    assert response == {'error': 'Invalid authentication token'}


@pytest.mark.django_db
def test_pay_order_fails_when_missing_required_fields(client, order):
    url = conftest.ORDER_PAY_URL.format(order_pk=order.pk)
    status, response = post_json(client, url)
    assert status == 400
    assert response == {'error': 'Missing required fields'}


@pytest.mark.django_db
def test_pay_order_fails_when_order_is_not_confirmed(client, user):
    order = OrderFactory(user=user, status=Order.Status.INITIATED)
    data = {
        'card-number': '1234-1234-1234-1234',
        'exp-date': '01/2099',
        'cvc': '123',
    }
    url = conftest.ORDER_PAY_URL.format(order_pk=order.pk)
    status, response = post_json(client, url, data, user.token.key)
    assert status == 400
    assert response == {'error': 'Orders can only be paid when confirmed'}


@pytest.mark.django_db
def test_pay_order_fails_when_invalid_card_number(client, user):
    order = OrderFactory(user=user, status=Order.Status.CONFIRMED)
    data = {
        'card-number': '1234-1234-1234-123',
        'exp-date': '01/2099',
        'cvc': '123',
    }
    url = conftest.ORDER_PAY_URL.format(order_pk=order.pk)
    status, response = post_json(client, url, data, user.token.key)
    assert status == 400
    assert response == {'error': 'Invalid card number'}


@pytest.mark.django_db
def test_pay_order_fails_when_invalid_card_expiration_date(client, user):
    order = OrderFactory(user=user, status=Order.Status.CONFIRMED)
    data = {
        'card-number': '1234-1234-1234-1234',
        'exp-date': '01/99',
        'cvc': '123',
    }
    url = conftest.ORDER_PAY_URL.format(order_pk=order.pk)
    status, response = post_json(client, url, data, user.token.key)
    assert status == 400
    assert response == {'error': 'Invalid expiration date'}


@pytest.mark.django_db
def test_pay_order_fails_when_invalid_cvc(client, user):
    order = OrderFactory(user=user, status=Order.Status.CONFIRMED)
    data = {
        'card-number': '1234-1234-1234-1234',
        'exp-date': '01/2099',
        'cvc': '12',
    }
    url = conftest.ORDER_PAY_URL.format(order_pk=order.pk)
    status, response = post_json(client, url, data, user.token.key)
    assert status == 400
    assert response == {'error': 'Invalid CVC'}


@pytest.mark.django_db
def test_pay_order_fails_when_card_has_expired(client, user):
    order = OrderFactory(user=user, status=Order.Status.CONFIRMED)
    data = {
        'card-number': '1234-1234-1234-1234',
        'exp-date': '01/2020',
        'cvc': '123',
    }
    url = conftest.ORDER_PAY_URL.format(order_pk=order.pk)
    status, response = post_json(client, url, data, user.token.key)
    assert status == 400
    assert response == {'error': 'Card expired'}


@pytest.mark.django_db
def test_pay_order_fails_when_unregistered_token(client, order):
    data = {
        'card-number': '1234-1234-1234-1234',
        'exp-date': '01/2099',
        'cvc': '123',
    }
    url = conftest.ORDER_PAY_URL.format(order_pk=order.pk)
    status, response = post_json(client, url, data, str(uuid.uuid4()))
    assert status == 401
    assert response == {'error': 'Unregistered authentication token'}


@pytest.mark.django_db
def test_pay_order_fails_when_user_is_not_the_owner_of_requested_order(client, user):
    data = {
        'card-number': '1234-1234-1234-1234',
        'exp-date': '01/2099',
        'cvc': '123',
    }
    order = OrderFactory(status=Order.Status.CONFIRMED)
    url = conftest.ORDER_PAY_URL.format(order_pk=order.pk)
    status, response = post_json(client, url, data, user.token.key)
    assert status == 403
    assert response == {'error': 'User is not the owner of requested order'}


@pytest.mark.django_db
def test_pay_order_fails_when_order_does_not_exist(client, user):
    data = {
        'card-number': '1234-1234-1234-1234',
        'exp-date': '01/2099',
        'cvc': '123',
    }
    url = conftest.ORDER_PAY_URL.format(order_pk=1)
    status, response = post_json(client, url, data, user.token.key)
    assert status == 404
    assert response == {'error': 'Order not found'}


@pytest.mark.django_db
def test_pay_order_fails_when_method_is_not_allowed(client, order):
    url = conftest.ORDER_PAY_URL.format(order_pk=order.pk)
    status, _ = get_json(client, url)
    assert status == 405
