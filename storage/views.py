import stripe
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.conf import settings
from .models import CustomUser, Storage, Box
from django.views.generic.base import View
from django.utils.decorators import method_decorator


from django.http import JsonResponse

stripe.api_key = settings.STRIPE_SECRET_KEY


def view_index(request):
    return render(request, template_name="index.html", context={})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['EMAIL']
        password = request.POST['PASSWORD']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('storage:start_page')
        else:
            error_msg ='Неправильный логин или пароль. Попробуйте снова.'
            return render(request, 'login.html', {'error_msg': error_msg})
    else:
        error_message = None
    return render(request, 'login.html', {'error_msg': error_message})


def forgot_view(request):
    return render(request, 'forgot.html')


def logout_view(request):
    logout(request)
    return redirect(reverse_lazy('storage:start_page'))


def signup_view(request):
    if request.method == 'POST':
        first_name = request.POST['FIRST_NAME']
        email = request.POST['EMAIL_CREATE']
        password = request.POST['PASSWORD_CREATE']
        password1 = request.POST['PASSWORD_CONFIRM']
        if password != password1:
            error_msg = "Пароли не совпадают"
            return render(request, 'signup.html', {'error_msg': error_msg})
        user = CustomUser.objects.create_user(username=email, email=email, password=password, first_name=first_name)
        user.save()
        return redirect('storage:login')
    else:
        error_msg = None
    return render(request, 'signup.html', {'error_message': error_msg})


def view_boxes(request):
    user = request.user
    storages = Storage.objects.all()
    boxes = Box.objects.order_by('monthly_price')
    return render(request, template_name="boxes.html",
                  context={
                      'storages': storages,
                      'boxes': boxes,
                      'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
                      'user': user
                  })


@method_decorator(login_required(login_url='login'), name='dispatch')
class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        box_id = self.kwargs["pk"]
        box = Box.objects.get(id=box_id)
        YOUR_DOMAIN = "http://127.0.0.1:8000"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'rub',
                        'unit_amount': int(box.monthly_price)*100,
                        'product_data': {
                            'name': box.storage.name,
                            # 'images': ['https://i.imgur.com/EHyR2nP.png'],
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                "product_id": box.id
            },
            mode='payment',
            success_url=YOUR_DOMAIN + '/success/',
            cancel_url=YOUR_DOMAIN + '/cancel/',
        )
        return JsonResponse({
            'id': checkout_session.id
        })


def view_faq(request):
    return render(request, template_name="faq.html", context={})


@login_required
def view_my_rent(request):
    user = request.user
    if request.method == 'POST':
        if request.POST['NAME_EDIT']:
            user.first_name = request.POST['NAME_EDIT']
        if request.POST['PHONE_EDIT']:
            user.phone_number = request.POST['PHONE_EDIT']
        if request.POST['EMAIL_EDIT']:
            user.email = request.POST['EMAIL_EDIT']
        if request.POST['PASSWORD_EDIT'] != "********":
            user.set_password(request.POST['PASSWORD_EDIT'])
        if request.FILES['AVATAR_EDIT']:
            avatar = request.FILES['AVATAR_EDIT']
            fss = FileSystemStorage()
            file = fss.save(f'avatar/{avatar.name}', avatar)
            user.avatar = fss.url(file)
        user.save()
    return render(request, template_name="my-rent.html", context={'user': user})


def view_my_rent_empty(request):
    return render(request, template_name="my-rent-empty.html", context={})
