"""@brief Django views generation (html) for Catami (top level).

Created Mark Gray 10/09/2012
markg@ivec.org

Edits :: Name : Date : description

"""
# Create your views here.
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

#@login_required
def index(request):
    """@brief returns root catami html

    """
    context = {}

    return render_to_response('catamiPortal/index.html', 
        context, 
        RequestContext(request))


def faq(request):
    """@brief returns catami faq html
    
    """
    context = {}

    return render_to_response('catamiPortal/faq.html', 
        context, 
        RequestContext(request))


def contact(request):
    """@brief returns catami contact html
    
    """
    context = {}

    return render_to_response('catamiPortal/contact.html', 
        context, 
        RequestContext(request))


def logout_view(request):
    """@brief returns user to html calling the logout action
    
    """
    logout(request)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


    
