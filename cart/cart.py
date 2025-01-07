from .models import Documents
from django.core.handlers.wsgi import WSGIRequest


class Cart:
    class Options:
        SIZES = ('A3', 'A4', 'A5')
        COLORS = ('W&B', 'C50', 'C100')
        TYPE = ('ONE_SIDE', 'BOTH_SIDES')
        EXTRA_OPTIONS = ('COVERED_NO_PUNCH', 'COVERED_PUNCHED', 'NO_BINDING')

        def validate_options(self, page_size: str, print_color: str, print_type: str, extra_options: str) -> bool | str:
            if page_size not in self.SIZES:
                return 'اندازه صفحه اشتباه است.'
            if print_color not in self.COLORS:
                return 'رنگ چاپ اشتباه است.'
            if print_type not in self.TYPE:
                return 'نوع چاپ اشتباه است.'
            if extra_options not in self.EXTRA_OPTIONS:
                return 'گزینه ها به درستی انتخاب نشده اند'
            return True

    def __init__(self, request: WSGIRequest):
        self.session = request.session
        cart = self.session.get('cart', None)

        if not cart:
            cart = self.session['cart'] = {}

        self.cart = cart

    def save(self):
        self.session.modified = True

    def clear(self):
        del self.cart

    def add(self, document_id, quantity: int, page_size: str, print_color: str, print_type: str,
            extra_options: str):
        result = self.Options.validate_options(page_size, print_color, print_type, extra_options)
        if isinstance(result, str):
            return result
        self.cart[f'{document_id}'] = {
            'quantity': quantity,
            'page_size': page_size,
            'print_color': print_color,
            'print_type': print_type,
            'extra_options': extra_options
        }
        self.save()
        return True

    def remove(self, document_id):
        if self.cart.get(f'{document_id}'):
            del self.cart[f'{document_id}']
            return True
        return False

    def __len__(self):
        return len([document for document in self.cart.keys()])

    def __iter__(self):
        try:
            for product_id, options in self.cart.values():
                yield {
                    'document': Documents.objects.get(id=product_id),
                    'options': options,
                }
        except Documents.DoesNotExist:
            print('Product Does Not Exist')
            return None