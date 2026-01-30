import json
from http import HTTPStatus

from django.http import JsonResponse


def require_http_methods(*methods):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if request.method not in methods:
                return JsonResponse(
                    {'error': 'Method not allowed'},
                    status=HTTPStatus.METHOD_NOT_ALLOWED,
                )
            return func(request, *args, **kwargs)

        return wrapper

    return decorator


def validate_json(func):
    def wrapper(request, *args, **kwargs):
        try:
            request.payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON body'}, status=400)
        return func(request, *args, **kwargs)

    return wrapper


def required_fields(required):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if set(required) - request.payload.keys():
                return JsonResponse(
                    {
                        'error': 'Missing required fields',
                    },
                    status=400,
                )
            return func(request, *args, **kwargs)

        return wrapper

    return decorator
