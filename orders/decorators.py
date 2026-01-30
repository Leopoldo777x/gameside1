from django.http import JsonResponse

from .models import Order


def order_exists(func):
    def wrapper(request, *args, **kwargs):
        order_pk = kwargs.get('order_pk')
        try:
            request.order = Order.objects.get(pk=order_pk)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
        return func(request, *args, **kwargs)

    return wrapper


def user_is_owner_of_requested_order(func):
    def wrapper(request, *args, **kwargs):
        if request.user != request.order.user:
            return JsonResponse({'error': 'User is not the owner of requested order'}, status=403)
        return func(request, *args, **kwargs)

    return wrapper
