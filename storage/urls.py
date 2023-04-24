from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required


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
    path('my_rent/', views.view_my_rent, name='view_my_rent'),
    path('my_rent_empty/', views.view_my_rent_empty, name='view_my_rent_empty'),
    path('create-checkout-session/<pk>/', login_required(views.CreateCheckoutSessionView.as_view()), name='create-checkout-session'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
