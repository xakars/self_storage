from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User


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
    return redirect('login')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['EMAIL_CREATE']
        password = request.POST['PASSWORD_CREATE']
        password1 = request.POST['PASSWORD_CONFIRM']
        if password != password1:
            error_msg = "Пароли не совпадают"
            return render(request, 'signup.html', {'error_msg': error_msg})
        user = User.objects.create_user(username=username, email=username, password=password)
        user.save()
        return redirect('storage:login')
    else:
        error_msg = None
    return render(request, 'signup.html', {'error_message': error_msg})



def view_boxes(request):
    return render(request, template_name="boxes.html", context={})


def view_faq(request):
    return render(request, template_name="faq.html", context={})


def view_my_rent(request):
    return render(request, template_name="my-rent.html", context={})


def view_my_rent_empty(request):
    return render(request, template_name="my-rent-empty.html", context={})
