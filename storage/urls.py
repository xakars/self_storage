from django.urls import path
from django.shortcuts import redirect
from . import views


app_name = "storage"


urlpatterns = [
    path('', lambda request: redirect('storage:start_page')),
    path('index/', views.view_index, name='start_page')

]