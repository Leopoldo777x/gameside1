import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from shared.decorators import require_http_methods
from .models import Category
from .serializers import CategorySerializer

@csrf_exempt
@require_http_methods('GET')
def category_list(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories)
    return serializer.json_response()


@csrf_exempt
@require_http_methods('GET')
def category_detail(request, category_slug):
    try:
        category = Category.objects.get(slug=category_slug)
    except Category.DoesNotExist:
        return JsonResponse({'error': 'Category not found'}, status=404)
    serializer = CategorySerializer(category)
    return serializer.json_response()