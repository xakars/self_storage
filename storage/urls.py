from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static


app_name = "storage"


urlpatterns = [
    # path('', lambda request: redirect('storage:start_page')),
    path('', views.view_index, name='start_page'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(next_page='storage:start_page'), name="logout"),
    path('forgot/', views.forgot_view, name="forgot"),
    path('boxes/', views.view_boxes, name='view_boxes'),
    path('faq/', views.view_faq, name='view_faq'),
    path('my-rent/', views.view_my_rent, name='view_my_rent'),
    path('my-rent-empty/', views.view_my_rent_empty, name='view_my_rent_empty'),
    path('create_order/', views.create_order, name='create_order'),
    path('checkout/', views.checkout, name='checkout'),
    path('cancel/', views.cancel, name='cancel'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
