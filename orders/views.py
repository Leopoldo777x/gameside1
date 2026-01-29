import json
import re
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from games.models import Game
from games.serializers import GameSerializer
from shared.decorators import require_http_methods
from users.decorators import auth_required

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
def order_detail(request, order_pk):
    try:
        order = Order.objects.get(pk=order_pk)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    if request.user != order.user:
        return JsonResponse({'error': 'User is not the owner of requested order'}, status=403)

    serializer = OrderSerializer(order, request=request)
    return serializer.json_response()


@csrf_exempt
@require_http_methods('GET')
@auth_required
def order_game_list(request, order_pk):
    try:
        order = Order.objects.get(pk=order_pk)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    if request.user != order.user:
        return JsonResponse({'error': 'User is not the owner of requested order'}, status=403)
    games = order.games.all()
    serializer = GameSerializer(games, request=request)
    return serializer.json_response()


@csrf_exempt
@require_http_methods('POST')
@auth_required
def add_game_to_order(request, order_pk):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)
    required = {'game-slug'}

    if required - payload.keys():
        return JsonResponse(
            {
                'error': 'Missing required fields',
            },
            status=400,
        )
    try:
        order = Order.objects.get(pk=order_pk)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    try:
        game = Game.objects.get(slug=payload['game-slug'])
    except Game.DoesNotExist:
        return JsonResponse({'error': 'Game not found'}, status=404)
    if request.user != order.user:
        return JsonResponse({'error': 'User is not the owner of requested order'}, status=403)
    elif not game.stock:
        return JsonResponse({'error': 'Game out of stock'}, status=400)
    order.games.add(game)
    game.stock -= 1
    game.save()
    return JsonResponse({'num-games-in-order': order.games.count()})


@csrf_exempt
@require_http_methods('POST')
@auth_required
def change_order_status(request, order_pk):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)
    required = {'status'}

    if required - payload.keys():
        return JsonResponse(
            {
                'error': 'Missing required fields',
            },
            status=400,
        )
    try:
        order = Order.objects.get(pk=order_pk)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    if request.user != order.user:
        return JsonResponse({'error': 'User is not the owner of requested order'}, status=403)
    elif payload['status'] not in Order.Status.values:
        return JsonResponse({'error': 'Invalid status'}, status=400)
    elif not order.get_status_display() == Order.Status.INITIATED:
        return JsonResponse(
            {'error': 'Orders can only be confirmed/cancelled when initiated'}, status=400
        )
    if order.get_status_display() == Order.Status.CONFIRMED:
        order.status == Order.Status.CANCELLED
        for game in order.games.all():
            game.stock += 1
            game.save()
    else:
        order.status == Order.Status.CONFIRMED
    order.save()
    return JsonResponse({'status': order.get_status_display()}, status=200)


@csrf_exempt
@require_http_methods('POST')
@auth_required
def pay_order(request, order_pk):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)
    required = {'card-number', 'exp-date', 'cvc'}
    if required - payload.keys():
        return JsonResponse(
            {
                'error': 'Missing required fields',
            },
            status=400,
        )
    try:
        order = Order.objects.get(pk=order_pk)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    if request.user != order.user:
        return JsonResponse({'error': 'User is not the owner of requested order'}, status=403)
    elif not order.status == Order.Status.CONFIRMED:
        return JsonResponse({'error': 'Orders can only be paid when confirmed'}, status=400)
    elif not re.match(r'^\d{4}-\d{4}-\d{4}-\d{4}$', payload['card-number']):
        return JsonResponse({'error': 'Invalid card number'}, status=400)
    elif not re.match(r'^(0[1-2]|1[0-2])/\d{4}$', payload['exp-date']):
        return JsonResponse({'error': 'Invalid expiration date'}, status=400)
    elif not re.match(r'^\d{3}$', payload['cvc']):
        return JsonResponse({'error': 'Invalid CVC'}, status=400)

    elif datetime.now().strftime('%m/%Y') > payload['exp-date']:
        return JsonResponse({'error': 'Card expired'}, status=400)
    order.status = Order.Status.PAID
    order.save()
    return JsonResponse({'status': order.get_status_display(), 'key': order.key}, status=200)
