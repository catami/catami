# Create your views here.
from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render, redirect
from django.core.urlresolvers import reverse

def index(request):
    return HttpResponse("CATAMI Project Main")
