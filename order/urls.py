from django.urls import path
from . import views


app_name = 'order'

urlpatterns = [
    path('', views.checkout_view, name='checkout'),
]