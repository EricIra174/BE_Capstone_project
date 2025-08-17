from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    """Home page view."""
    return HttpResponse("Welcome to Advanced API Project!")

def about(request):
    """About page view."""
    return HttpResponse("This is an Advanced API Project for learning Django REST framework.")
