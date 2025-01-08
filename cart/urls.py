from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_view, name='cart'),
    path('test/', views.test_view, name='test'),
    path('upload/', views.upload_view, name='upload'),
    path('delete/', views.delete_view, name='delete'),
]