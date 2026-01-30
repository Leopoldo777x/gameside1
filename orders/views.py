import re
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from games.models import Game
from games.serializers import GameSerializer
from shared.decorators import require_http_methods, required_fields, validate_json
from users.decorators import auth_required

from .decorators import order_exists, user_is_owner_of_requested_order
from .models import Order
from .serializers import OrderSerializer


@csrf_exempt
@require_http_methods('POST')
@auth_required
def add_order(request):
    order = Order.objects.create(user=request.user)
    return JsonResponse({'id': order.pk})


@csrf_exempt
@require_http_methods('GET')
@auth_required
@order_exists
@user_is_owner_of_requested_order
def order_detail(request, order_pk):
    order = request.order
    serializer = OrderSerializer(order, request=request)
    return serializer.json_response()


@csrf_exempt
@require_http_methods('GET')
@auth_required
@order_exists
@user_is_owner_of_requested_order
def order_game_list(request, order_pk):
    order = request.order
    games = order.games.all()
    serializer = GameSerializer(games, request=request)
    return serializer.json_response()


@csrf_exempt
@require_http_methods('POST')
@validate_json
@required_fields({'game-slug'})
@auth_required
@order_exists
@user_is_owner_of_requested_order
def add_game_to_order(request, order_pk):
    payload = request.payload

    try:
        game = Game.objects.get(slug=payload['game-slug'])
    except Game.DoesNotExist:
        return JsonResponse({'error': 'Game not found'}, status=404)
    order = request.order
    if not game.stock:
        return JsonResponse({'error': 'Game out of stock'}, status=400)
    order.games.add(game)
    game.stock -= 1
    game.save()
    return JsonResponse({'num-games-in-order': order.games.count()})


@csrf_exempt
@require_http_methods('POST')
@validate_json
@required_fields({'status'})
@auth_required
@order_exists
@user_is_owner_of_requested_order
def change_order_status(request, order_pk):
    payload = request.payload
    order = request.order
    new_status = payload['status']

    if new_status not in [Order.Status.CANCELLED, Order.Status.CONFIRMED]:
        return JsonResponse({'error': 'Invalid status'}, status=400)
    elif order.status != Order.Status.INITIATED:
        return JsonResponse(
            {'error': 'Orders can only be confirmed/cancelled when initiated'}, status=400
        )
    order.status = new_status
    for game in order.games.all():
        game.stock += 1
        game.save()
    order.save()
    return JsonResponse({'status': order.get_status_display()})


@csrf_exempt
@require_http_methods('POST')
@validate_json
@required_fields({'card-number', 'exp-date', 'cvc'})
@auth_required
@order_exists
@user_is_owner_of_requested_order
def pay_order(request, order_pk):
    CARD_NUM_RE = r'^\d{4}-\d{4}-\d{4}-\d{4}$'
    EXP_DATE_RE = r'^(0[1-2]|1[0-2])/\d{4}$'
    CVC_RE = r'^\d{3}$'

    payload = request.payload
    order = request.order
    card_number = payload['card-number']
    exp_date = payload['exp-date']
    cvc = payload['cvc']

    if not order.status == Order.Status.CONFIRMED:
        return JsonResponse({'error': 'Orders can only be paid when confirmed'}, status=400)
    elif not re.match(CARD_NUM_RE, card_number):
        return JsonResponse({'error': 'Invalid card number'}, status=400)
    elif not re.match(EXP_DATE_RE, exp_date):
        return JsonResponse({'error': 'Invalid expiration date'}, status=400)
    elif not re.match(CVC_RE, cvc):
        return JsonResponse({'error': 'Invalid CVC'}, status=400)
    elif datetime.now().strftime('%m/%Y') > exp_date:
        return JsonResponse({'error': 'Card expired'}, status=400)

    order.status = Order.Status.PAID
    order.save()
    return JsonResponse({'status': order.get_status_display(), 'key': order.key}, status=200)
