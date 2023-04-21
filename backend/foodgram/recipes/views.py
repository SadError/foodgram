from django.shortcuts import render
from django.http import HttpResponse
from .models import Tag, Ingredient, Recipe

def index(request):
    return HttpResponse(Recipe.objects.all())
