from django.urls import path

from . import views 

urlpatterns = [
    path("", views.index, name="index"),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('apply/', views.apply, name='apply'),
    path('product_registration/', views.product_registration, name='product_registration'), #다나와 크롤링 스크립트
    path('mypg/', views.mypg, name='mypg'),
    path('increment_count/<int:product_id>/', views.increment_count, name='increment_count'),
    path('scrape_product_info/', views.scrape_product_info, name='scrape_product_info'),
    path('setting/', views.setting, name='setting'), 
  
]