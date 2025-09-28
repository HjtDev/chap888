from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('faq/', views.faq_view, name='faq'),
    path('terms/', views.terms_of_use_view, name='terms'),
    path('control_panel/', views.control_panel_view, name='control_panel'),
    path('price_list/', views.price_list, name='price_list'),
]
