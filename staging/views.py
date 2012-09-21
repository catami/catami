from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.db import transaction
from django.core import serializers
from django import forms

from staging.forms import AUVImportForm
from staging.auvimport import create_structure, structure_string

def index(request):
    context = {}
    context['sections'] = ['auv', 'bruv']

    rc = RequestContext(request)

    return render_to_response('staging/index.html', context, rc)

def auvimport(request):
    errors = ""
    context = {}
    if request.method == 'POST':
        form = AUVImportForm(request.POST)
        if form.is_valid():
            # try and get the files and import
            try:
                data = form.cleaned_data

                input_params = (data['base_url'], str(data['campaign_name'].date_start), data['campaign_name'].short_name, data['mission_name'])

                print "fetching!!"
                (track_url, netcdf_urlpattern, start_time) = tasks.auvfetch(*input_params)

                print "get track"
                track_file = tasks.get_known_file(1, track_url)

                print "get netcdf"
                netcdf_file = tasks.get_netcdf_file(1, netcdf_urlpattern, start_time)

                print "process '{0}' '{1}'".format(track_file, netcdf_file)
                json_string = tasks.auvprocess(track_file, netcdf_file, *input_params)

                print "loading"
                tasks.json_sload(json_string)

            except Exception as e:
                errors = form._errors.setdefault(forms.forms.NON_FIELD_ERRORS, forms.util.ErrorList())
                errors.append("{0}: {1}".format(e.__class__.__name__, e))

            else:
                return redirect('staging.views.auvimported')

    else:
        form = AUVImportForm()

    rc = RequestContext(request)
    context['form'] = form

    return render_to_response('staging/auvimport.html', context, rc)

def auvimported(request):
    context = {}
    rc = RequestContext(request)

    return render_to_response('staging/auvimported.html', context, rc)

def fileupload(request):
    context = {}
    rc = RequestContext(request)

    return render_to_response('staging/fileupload.html', context, rc)

def fileuploaded(request):
    context = {}
    rc = RequestContext(request)

    return render_to_response('staging/fileuploaded.html', context, rc)
