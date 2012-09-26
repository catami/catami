# Create your views here.
from django.template import Context, loader,RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    context = {}

    rc = RequestContext(request)

    return render_to_response('catamiPortal/index.html', context, rc)
