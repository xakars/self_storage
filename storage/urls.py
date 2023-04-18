from django.urls import path
from django.shortcuts import redirect
from . import views


app_name = "storage"


urlpatterns = [
    path('', lambda request: redirect('storage:start_page')),
    path('index/', views.view_index, name='start_page'),
    path('boxes/', views.view_boxes, name='view_boxes'),
    path('faq/', views.view_faq, name='view_faq'),
    path('my_rent/', views.view_my_rent, name='view_my_rent'),
    path('my_rent_empty/', views.view_my_rent_empty, name='view_my_rent_empty'),
]
