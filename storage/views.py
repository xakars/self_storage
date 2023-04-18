from django.shortcuts import render


def view_index(request):
    return render(request, template_name="index.html", context={})


def view_boxes(request):
    return render(request, template_name="boxes.html", context={})


def view_faq(request):
    return render(request, template_name="faq.html", context={})


def view_my_rent(request):
    return render(request, template_name="my-rent.html", context={})


def view_my_rent_empty(request):
    return render(request, template_name="my-rent-empty.html", context={})
