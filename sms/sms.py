from .melipayamak import Api
from django.conf import settings
from django.core.cache import cache
import os

class SMS:
    def __init__(self, api_key, username, password, admin, sender, method='rest'):
        self.admin = admin
        self.sender = sender
        self.api_key = api_key
        self.api = Api(username, password)
        self.sms = self.api.sms(method)
        
        self.check_credit()
        
    def check_credit(self):
        credit = self.sms.get_credit()
        if isinstance(credit, dict) and credit.get('Value'):
            if float(credit.get('Value')) <= 10.0 and not cache.get('low_charge_sms_warning'):
                self.sms.send(self.admin, self.sender, 'موجودی پنل ملی پیامک شما کمتر از ۱۰ پیامک است لطفا قبل از ایجاد اخلال در سایت حساب خود را شارژ کنید.')
                cache.set('low_charge_sms_warning', True)
            elif float(credit.get('Value')) > 10.0 and cache.get('low_charge_sms_warning'):
                cache.set('low_charge_sms_warning', False)
    
    
    def send(self, to, message):
        self.sms.send(to, self.sender, message)
        
    def send_by_base(self, to, bodyID, *args):
        for arg in args:
            if not isinstance(arg, str):
                raise ValueError('All arguments must be strings.')
        response = self.sms.send_by_base_number(';'.join(arg for arg in args), to, bodyID)
        return True if len(response.get('Value')) >= 15 else False
    
    def notify_admin(self, name, order_id, phone):
        return self.send_by_base(self.admin, 373556, name, order_id, phone)
    
    def send_authentication(self, to, token):
        return self.send_by_base(to, 373342, token)
        
    def order_confirmed(self, to, name, order_id):
        return self.send_by_base(to, 373347, name, order_id)
        
    def order_ready(self, to, name, order_id):
        return self.send_by_base(to, 373360, name, order_id)
    
    def order_shipped(self, to, name, order_id):
        return self.send_by_base(to, 373362, name, order_id)
        
    def order_completed(self, to, name, order_id):
        return self.send_by_base(to, 373364, name, order_id)
    
    def order_canceled(self, to, name, order_id):
        return self.send_by_base(to, 373366, name, order_id)
    
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Chap.settings')
sms = SMS(settings.SMS_API, settings.SMS_USERNAME, settings.SMS_PASSWORD, settings.SMS_ADMIN, settings.SMD_SENDER)
# sms.send('09381432078', 'تست ارسال اعتبار سنجی')
# # sms.send_by_base('09385965775', 373342, '1234')
# sms.send_authentication('09381432078', '349138')
# sms.order_confirmed('09381432078', 'محمد حجت', 'order_test-1234')
# sms.order_ready('09381432078', 'محمد حجت', 'order_test-1234')
# sms.order_shipped('09381432078', 'محمد حجت', 'order_test-1234')
# sms.order_completed('09381432078', 'محمد حجت', 'order_test-1234')
# sms.order_canceled('09381432078', 'محمد حجت', 'order_test-1234')
