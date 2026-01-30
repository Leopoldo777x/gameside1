from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from shared.decorators import require_http_methods

from .models import Platform
from .serializers import PlatformSerializer


@csrf_exempt
@require_http_methods('GET')
def platform_list(request):
    categories = Platform.objects.all()
    serializer = PlatformSerializer(categories, request=request)
    return serializer.json_response()


@csrf_exempt
@require_http_methods('GET')
def platform_detail(request, platform_slug):
    try:
        platform = Platform.objects.get(slug=platform_slug)
    except Platform.DoesNotExist:
        return JsonResponse({'error': 'Platform not found'}, status=404)
    serializer = PlatformSerializer(platform, request=request)
    return serializer.json_response()
