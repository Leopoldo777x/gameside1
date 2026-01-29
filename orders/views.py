import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from shared.decorators import require_http_methods
from users.decorators import auth_required
from .models import Order
from games.models import Game
from .serializers import OrderSerializer
from games.serializers import GameSerializer

@csrf_exempt
@require_http_methods('POST')
@auth_required
def add_order(request):
    order = Order.objects.create(
        user=request.user
    )
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
        return JsonResponse({'error': 'User is not the owner of the requested order'}, status=404)

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
        return JsonResponse({'error': 'User is not the owner of the requested order'}, status=404)
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
        return JsonResponse({'error': 'Missing required fields',}, status=400)
    try:
        order = Order.objects.get(pk=order_pk)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    try:
        game = Game.object.get(slug=payload['game-slug'])
    except Game.DoesNotExist:
        return JsonResponse({'error': 'Game not found'}, status=404)
    if request.user != order.user:
        return JsonResponse({'error': 'User is not the owner of the requested order'}, status=404)
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
        return JsonResponse({'error': 'Missing required fields',}, status=400)
    try:
        order = Order.objects.get(pk=order_pk)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    if request.user != order.user:
        return JsonResponse({'error': 'User is not the owner of the requested order'}, status=404)
    elif payload['status']not in Order.Status.values:
        return JsonResponse({'error': 'Invalid status'}, status=400)