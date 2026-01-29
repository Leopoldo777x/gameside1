import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from shared.decorators import require_http_methods
from users.decorators import auth_required
from .models import Game, Review
from .serializers import GameSerializer, ReviewSerializer


@csrf_exempt
@require_http_methods('GET')
def game_list(request):
    games = Game.objects.all()

    category_slug = request.GET.get('category')
    platform_slug = request.GET.get('platforms')

    if category_slug:
        games = games.filter(category__slug=category_slug)

    if platform_slug:
        games = games.filter(platforms__slug=platform_slug).distinct()
    serializer = GameSerializer(games, request=request)
    return serializer.json_response()


@csrf_exempt
@require_http_methods('GET')
def game_detail(request, game_slug):
    try:
        game = Game.objects.get(slug=game_slug)
    except Game.DoesNotExist:
        return JsonResponse({'error': 'Game not found'}, status=404)
    serializer = GameSerializer(game, request=request)
    return serializer.json_response()


@csrf_exempt
@require_http_methods('GET')
def review_list(request, game_slug):
    try:
        game = Game.objects.get(slug=game_slug)
    except Game.DoesNotExist:
        return JsonResponse({'error': 'Game not found'}, status=404)
    reviews = game.reviews.all()
    serializer = ReviewSerializer(reviews, request=request)
    return serializer.json_response()


@csrf_exempt
@require_http_methods('GET')
def review_detail(request, review_pk):
    try:
        review = Review.objects.get(pk=review_pk)
    except Review.DoesNotExist:
        return JsonResponse({'error': 'Review not found'}, status=404)
    serializer = ReviewSerializer(review, request=request)
    return serializer.json_response()

@csrf_exempt
@require_http_methods('POST')
@auth_required
def add_review(request, game_slug):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)
    required = {'rating', 'comment'}
    
    if required - payload.keys():
        return JsonResponse({'error': 'Missing required fields',}, status=400)
    try:
        game = Game.objects.get(slug=game_slug)
    except Game.DoesNotExist:
        return JsonResponse({'error': 'Game not found'}, status=404)
    if not (1 <= payload['rating'] <= 5):
        return JsonResponse({'error': 'Rating is out of range'}, status=400)
    review = Review.objects.create(
        rating = payload['rating'],
        comment = payload['comment'],
        author = request.user,
        game = game
    )
    return JsonResponse({'id': review.pk})
