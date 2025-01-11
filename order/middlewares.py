from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import reverse
from django.contrib import messages
from order.models import Order


class FalseOrderRemovalMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path != reverse('account:verify') and not request.user.is_authenticated and 'order' in request.session:
            order_pk = request.session['order']
            try:
                Order.objects.get(pk=order_pk).delete()
            except Order.DoesNotExist:
                pass
            finally:
                del request.session['order']
            messages.warning(request, 'شما سفارش خود را لغو کردید.')


