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
def viewcollection(request):
    return render_to_response('webinterface/viewcollection.html', {}, RequestContext(request))

def allcollections(request):
    return render_to_response('webinterface/allcollections.html', {"public_collections": cl}, RequestContext(request))

def mycollections(request):
    collection_list = CollectionResource()
    cl = collection_list.obj_get_list(user=request.user)
    return render_to_response('webinterface/mycollections.html', {"my_collections": cl}, RequestContext(request))

def publiccollections(request):
    collection_list = CollectionResource()
    cl_all = collection_list.obj_get_list()
    cl_public = list()

    # cannot filter on 'is_public'
    for collection_object in cl_all:
        if collection_object.is_public==True:
            cl_public.append(collection_object)
    return render_to_response('webinterface/publiccollections.html', {"public_collections": cl_public}, RequestContext(request))

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

def collections(request):
    collection_list = CollectionResource()
    cl = collection_list.obj_get_list(user=request.user)
    cl_all = collection_list.obj_get_list()
    cl_public = list()

    # cannot filter on 'is_public'
    for collection_object in cl_all:
        if collection_object.is_public==True:
            cl_public.append(collection_object)

    # cl_bundles = [collection_list.build_bundle(obj=q, request=request) for q in cl]
    # data = [collection_list.full_dehydrate(cl_bundle) for cl_bundle in cl_bundles]

    #decoded_json = json.loads(data)

    #return HttpResponse(collection_list.serialize(None,data,'application/json'), mimetype='application/json')
    #return render_to_response('webinterface/collections.html', {"collections_json": decoded_json['objects']}, RequestContext(request))
    return render_to_response('webinterface/collections.html', {"my_collections": cl, "public_collections":cl_public}, RequestContext(request))

