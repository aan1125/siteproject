from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('apply/', views.apply, name='apply'),
    path('product_registration/', views.product_registration, name='product_registration'),
]