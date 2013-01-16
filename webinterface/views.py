# Create your views here.

from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError
from django import forms
from django.contrib.auth.decorators import login_required
from django.core.cache import cache

import logging

logger = logging.getLogger(__name__)

#@login_required
def index(request):
    return render_to_response('webinterface/index.html', {}, RequestContext(request))

# Explore pages
def explore(request):
    return render_to_response('webinterface/explore.html', {}, RequestContext(request))

# Collection pages
def viewcollection(request):
    return render_to_response('webinterface/viewcollection.html', {}, RequestContext(request))

def allcollections(request):
    return render_to_response('webinterface/allcollections.html', {}, RequestContext(request))

def mycollections(request):
    return render_to_response('webinterface/mycollections.html', {}, RequestContext(request))

def publiccollections(request):
    return render_to_response('webinterface/publiccollections.html', {}, RequestContext(request))

# Subset pages
def viewsubset(request):
    return render_to_response('webinterface/viewsubset.html', {}, RequestContext(request))

def allsubsets(request):
    return render_to_response('webinterface/allsubsets.html', {}, RequestContext(request))

def mysubsets(request):
    return render_to_response('webinterface/mysubsets.html', {}, RequestContext(request))

def publicsubsets(request):
    return render_to_response('webinterface/publicsubsets.html', {}, RequestContext(request))
    
# Single image pages
def imageview(request):
    return render_to_response('webinterface/imageview.html', {}, RequestContext(request))

def imageannotate(request):
    return render_to_response('webinterface/imageannotate.html', {}, RequestContext(request))

def imageedit(request):
    return render_to_response('webinterface/imageedit.html', {}, RequestContext(request))



