from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.db import transaction
from django.core import serializers
from django import forms

from staging.forms import AUVImportForm, FileImportForm
from staging.auvimport import create_structure, structure_string
from staging.models import Progress
from staging.extras import UploadProgressCachedHandler
from staging import tasks

from django.views.decorators.csrf import csrf_exempt, csrf_protect

def index(request):
    context = {}
    context['sections'] = ['auv', 'bruv']

    rc = RequestContext(request)

    return render_to_response('staging/index.html', context, rc)

def progress(request, key):
    """Used to return progress of an operation."""
    context = {}
    rc = RequestContext(request)

    try:
        prog = Progress.objects.get(pk=key)
    except Progress.DoesNotExist:
        context['percent'] = 40
    else:
        context['percent'] = prog.progress

    return render_to_response('staging/progress.json', context, rc)
    

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

# to enable the handler to exist...
@csrf_exempt
def fileupload(request):
    # get a new progress
    key = Progress.objects.get_new()

    request.upload_handlers.insert(0, UploadProgressCachedHandler(request))
    return _fileupload(request)

@csrf_protect
def _fileupload(request):
    context = {}
    rc = RequestContext(request)

    if request.method == 'POST':
        form = FileImportForm(request.POST, request.FILES)

        if form.is_valid():
            # this is where the import is performed...
            # and the file is read in
            upload = request.FILES['upload_file']

            # if it is large, read from the file
            # else read the entirety into a string
            try:
                if hasattr(upload, 'temporary_file_path'):
                    tasks.json_fload(upload.temporary_file_path())
                else:
                    tasks.json_sload(upload.read())
                
            except Exception as e:
                errors = form._errors.setdefault(forms.forms.NON_FIELD_ERRORS, forms.util.ErrorList())
                errors.append("{0}: {1}".format(e.__class__.__name__, e))
            else:
                return redirect('staging.views.fileuploaded')
    else:
        form = FileImportForm()

    context['form'] = form

    return render_to_response('staging/fileupload.html', context, rc)

def fileuploaded(request):
    context = {}
    rc = RequestContext(request)

    return render_to_response('staging/fileuploaded.html', context, rc)

def upload_progress(request):
    """
    Return JSON object with information about the progress of an upload.
    """
    progress_id = ''
    if 'X-Progress-ID' in request.GET:
        progress_id = request.GET['X-Progress-ID']
    elif 'X-Progress-ID' in request.META:
        progress_id = request.META['X-Progress-ID']
    if progress_id:
        from django.utils import simplejson
        cache_key = "%s_%s" % (request.META['REMOTE_ADDR'], progress_id)
        data = cache.get(cache_key)
        return HttpResponse(simplejson.dumps(data))
    else:
        return HttpResponseServerError('Server Error: You must provide X-Progress-ID header or query param.')

