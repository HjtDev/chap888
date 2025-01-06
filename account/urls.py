from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('login/<phone>/', views.login_view, name='login_action'),
    path('verify/', views.verify_view, name='verify'),
    path('logout/', views.logout_view, name='logout'),
    path('reset/', views.reset_password_view, name='reset'),
    path('reset/<phone>/', views.reset_password_complete_view, name='reset_complete'),
]
