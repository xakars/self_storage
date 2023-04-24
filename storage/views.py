from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta
from .models import CustomUser, Storage, Box, Order

import stripe
import os
from django.conf import settings
from django.shortcuts import render
from django.urls import reverse

from .forms import AddressForm

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
    storages = Storage.objects.all()
    boxes = Box.objects.order_by('monthly_price')
    return render(request, template_name="boxes.html",
        context={'storages': storages, 'boxes': boxes})


def view_faq(request):
    return render(request, template_name="faq.html", context={})


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
def create_order(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            #address = form.cleaned_data['address']
            address = form.cleaned_data['address']
            client = request.user
            box_id = request.POST.get('box')
            #client = request.POST.get('client')
            #address = request.POST.get('address')
            #rental_period = request.POST.get('rental_period')
            #delivery_needed = request.POST.get('delivery_needed')
            #measurement_needed = request.GET.get('measurement_needed')
            pickup_deadline = timezone.now() + timedelta(days=30*3)
            order = Order.objects.create(
                box=Box.objects.get(id=int(box_id)),
                client=client,
                address=address,
                rental_period=3,
                #delivery_needed=delivery_needed,
                #measurement_needed=measurement_needed,
                pickup_deadline=pickup_deadline
            )
            order.calculate_rental_period_price()
            order.generate_qr_code()
            return redirect('/checkout/')
    else:
        box_id = request.GET.get('box')
        rental_period = request.GET.get('rental_period')
        form = AddressForm()
        print(box_id, type(box_id), rental_period, type(rental_period))
        return render(request, 'create_order.html', {'form': form, 'box_id': box_id, 'rental_period': rental_period})

@login_required(login_url='/login/')
def checkout(request):
    order = Order.objects.latest('id')
    stripe.api_key = 'sk_test_51MzdXXF1yAxsYBjXJ0t3xIfgAHTkAfHFstfzqpCiFvpoacqdsjGu39yVX3rJay7T8LPbjFzO83RWQrcIxsVo9aWe00nNNgkwqu'
    user = request.user
    stripe_product = stripe.Product.create(
       name=f"{order.client.phone_number} {order.box.number}",
       description="price/month",)
    stripe_product_price = stripe.Price.create(
       unit_amount=order.rental_period_price*100,
       currency="RUB",
       product=stripe_product['id'],)
    price = stripe_product_price['id']

    checkout_session = stripe.checkout.Session.create(
        #payment_method_types=['card'],
        line_items=[{
            'price': price,
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://self-storage.semellot.one/my-rent',
        #success_url='/my-rent/',
        cancel_url='http://localhost:8000/cancel/',
        customer_email=user.email
    )

    #print(f'Checkout is: {checkout_session}')

    checkout_url = checkout_session.url
    return redirect(checkout_url)


def success(request):
    return render(request, 'success.html')


def cancel(request):
    return render(request, 'cancel.html')
