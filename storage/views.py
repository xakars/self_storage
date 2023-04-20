from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .models import CustomUser, Storage


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
        username = request.POST['EMAIL_CREATE']
        password = request.POST['PASSWORD_CREATE']
        password1 = request.POST['PASSWORD_CONFIRM']
        if password != password1:
            error_msg = "Пароли не совпадают"
            return render(request, 'signup.html', {'error_msg': error_msg})
        user = CustomUser.objects.create_user(username=username, email=username, password=password)
        user.save()
        return redirect('storage:login')
    else:
        error_msg = None
    return render(request, 'signup.html', {'error_message': error_msg})



def view_boxes(request):
    storages = Storage.objects.all()
    return render(request, template_name="boxes.html",
        context={'storages': storages})


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
