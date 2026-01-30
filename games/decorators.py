from django.http import JsonResponse

from .models import Game


def game_exists(func):
    def wrapper(request, *args, **kwargs):
        game_slug = kwargs.get('game_slug')
        try:
            request.game = Game.objects.get(slug=game_slug)
        except Game.DoesNotExist:
            return JsonResponse({'error': 'Game not found'}, status=404)
        return func(request, *args, **kwargs)

    return wrapper
