from django.urls import path
from . import views


app_name = 'order'

urlpatterns = [
    path('', views.checkout_view, name='checkout'),
    path('submit/', views.submit_view, name='submit_order'),
    path('complete/', views.complete_order_view, name='complete_order'),
]