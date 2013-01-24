# Create your views here.

from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError
from django import forms
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from collection.api import CollectionResource
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

#@login_required
def index(request):
    return render_to_response('webinterface/index.html', {}, RequestContext(request))

# Explore pages
def explore(request):
    return render_to_response('webinterface/explore.html', {}, RequestContext(request))

# Collection pages

def collections(request):
    return render_to_response('webinterface/collections.html', {}, RequestContext(request))

def viewcollection(request,collection_id):
    return render_to_response('webinterface/viewcollection.html', {}, RequestContext(request))

def allcollections(request):
    return render_to_response('webinterface/allcollections.html', {"public_collections": cl}, RequestContext(request))

def mycollections(request):
    return render_to_response('webinterface/mycollections.html', {}, RequestContext(request))

def publiccollections(request):
    return render_to_response('webinterface/publiccollections.html', {}, RequestContext(request))

# view collection table views
def publiccollections_all(request):
    collection_list = CollectionResource()
    cl_all = collection_list.obj_get_list()
    return render_to_response('webinterface/publiccollections_all.html', {"public_collections": cl_all}, RequestContext(request))

def publiccollections_recent(request):
    collection_list = CollectionResource()
    cl_all = collection_list.obj_get_list()
    return render_to_response('webinterface/publiccollections_recent.html', {"public_collections": cl_all}, RequestContext(request))

def mycollections_all(request):
    collection_list = CollectionResource()
    cl = collection_list.obj_get_list(request,owner=request.user.id)
    return render_to_response('webinterface/mycollections_all.html', {"my_collections": cl}, RequestContext(request))

def mycollections_recent(request):
    collection_list = CollectionResource()
    cl = collection_list.obj_get_list(request,owner=request.user.id)
    return render_to_response('webinterface/mycollections_recent.html', {"my_collections": cl}, RequestContext(request))

# collection object tasks
def delete_collection(request):
    return nil

def flip_public_collection(request):
    return nil

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
