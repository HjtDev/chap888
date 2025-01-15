from .models import Documents
from django.core.handlers.wsgi import WSGIRequest


class Cart:
    class Options:
        SIZES = ('A3', 'A4', 'A5')
        COLORS = ('W&B', 'C50', 'C100')
        TYPE = ('ONE_SIDE', 'BOTH_SIDES', 'TWO_PAGES_PER_SIDE')
        EXTRA_OPTIONS = ('COVERED_NO_PUNCH', 'COVERED_PUNCHED', 'NO_BINDING')
        FRONTEND = {
            'A3': 'A3',
            'A4': 'A4',
            'A5': 'A5',
            'W&B': 'سیاه سفید',
            'C50': 'رنگی 50 درصد',
            'C100': 'رنگی 100 درصد',
            'ONE_SIDE': 'یک رو',
            'BOTH_SIDES': 'دو رو',
            'TWO_PAGES_PER_SIDE': 'هر دو صفحه یک رو',
            'COVERED_NO_PUNCH': 'کاور شده بدون پانچ',
            'COVERED_PUNCHED': 'کاور شده با پانچ',
            'NO_BINDING': 'بدون صحافی'
        }

        @staticmethod
        def validate_options(page_size: str, print_color: str, print_type: str, extra_options: str) -> bool | str:
            if page_size not in Cart.Options.SIZES:
                return 'اندازه صفحه اشتباه است.'
            if print_color not in Cart.Options.COLORS:
                return 'رنگ چاپ اشتباه است.'
            if print_type not in Cart.Options.TYPE:
                return 'نوع چاپ اشتباه است.'
            if extra_options not in Cart.Options.EXTRA_OPTIONS:
                return 'گزینه ها به درستی انتخاب نشده اند'
            return True

        @staticmethod
        def convert(options):
            return {key: Cart.Options.FRONTEND[value] for key, value in options.items() if key != 'quantity'}

    def __init__(self, request: WSGIRequest, converted=True):
        self.session = request.session
        cart = self.session.get('cart', None)

        if not cart:
            cart = self.session['cart'] = {}

        self.cart = cart

        self.converted = converted

    def save(self):
        self.session.modified = True

    def clear(self):
        self.session.pop('cart')
        self.save()

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
            self.save()
            return True
        self.save()
        return False

    def __len__(self):
        return len([document for document in self.cart.keys()])

    def __iter__(self):
        document_ids = list(self.cart.keys())
        documents = Documents.objects.filter(id__in=document_ids)

        document_dict = {document.id: document for document in documents}

        for product_id, options in self.cart.items():
            document = document_dict.get(int(product_id))
            if document:
                yield {
                    'document': document,
                    'quantity': options['quantity'],
                    'options': self.Options.convert(options) if self.converted else options,
                }
            else:
                print(f'Product with ID {product_id} does not exist')
