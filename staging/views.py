"""Views for the staging app.
"""

from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django import forms
from django.contrib.auth.decorators import login_required
from django.core.cache import cache

from .forms import AUVImportForm, FileImportForm
from .models import Progress
from .extras import UploadProgressCachedHandler
from . import tasks

from django.views.decorators.csrf import csrf_exempt, csrf_protect

import logging

logger = logging.getLogger(__name__)

@login_required
def index(request):
    """The home/index view for staging."""
    context = {}
    context['sections'] = ['auv', 'bruv']

    rcon = RequestContext(request)

    return render_to_response('staging/index.html', context, rcon)

@login_required
def progress(request, key):
    """Used to return progress of an operation."""
    context = {}
    rcon = RequestContext(request)

    try:
        prog = Progress.objects.get(pk=key)
    except Progress.DoesNotExist:
        context['percent'] = 40
    else:
        context['percent'] = prog.progress

    return render_to_response('staging/progress.json', context, rcon)
    

@login_required
def auvimport(request):
    """The auvimport view. Handles GET and POST for the form."""
    errors = ""
    context = {}
    if request.method == 'POST':
        form = AUVImportForm(request.POST)
        if form.is_valid():
            # try and get the files and import
            try:
                data = form.cleaned_data

                input_params = (data['base_url'], str(data['campaign_name'].date_start), data['campaign_name'].short_name, data['mission_name'])

                logger.debug("auvimport: determining remote files to fetch.")
                (track_url, netcdf_urlpattern, start_time) = tasks.auvfetch(*input_params)

                logger.debug("auvimport: fetching remote track file.")
                track_file = tasks.get_known_file(1, track_url)

                logger.debug("auvimport: fetching remote netcdf file.")
                netcdf_file = tasks.get_netcdf_file(1, netcdf_urlpattern, start_time)

                logger.debug("auvimport: processing remote files to create json string.")
                json_string = tasks.auvprocess(track_file, netcdf_file, *input_params)

                logger.debug("auvimport: importing json string into database.")
                tasks.json_sload(json_string)

            except Exception as exc:
                errors = form._errors.setdefault(forms.forms.NON_FIELD_ERRORS, forms.util.ErrorList())
                errors.append("{0}: {1}".format(exc.__class__.__name__, exc))
                logger.debug('auvimport: failed to import auv mission: ({0}): {1}'.format(exc.__class__.__name__, exc))

            else:
                logger.debug("auvimport: import successful, redirecting to auvimported.")
                return redirect('staging.views.auvimported')

    else:
        form = AUVImportForm()

    rcon = RequestContext(request)
    context['form'] = form

    return render_to_response('staging/auvimport.html', context, rcon)

@login_required
def auvimported(request):
    """Displays the thankyou message on auvimport success."""
    context = {}
    rcon = RequestContext(request)

    return render_to_response('staging/auvimported.html', context, rcon)

# to enable the handler to exist...
@login_required
@csrf_exempt
def fileupload(request):
    """Handles setting up progress handler and uploading json files."""
    # get a new progress
    #key = Progress.objects.get_new()


    # this is done here due to issues with csrf and touching of the POST
    # data
    request.upload_handlers.insert(0, UploadProgressCachedHandler(request))
    return _fileupload(request)

@csrf_protect
def _fileupload(request):
    """Deals with the actual uploading of files."""
    context = {}
    rcon = RequestContext(request)

    if request.method == 'POST':
        form = FileImportForm(request.POST, request.FILES)

        if form.is_valid():
            # this is where the import is performed...
            # and the file is read in
            logger.debug("_fileupload: getting uploaded file.")
            upload = request.FILES['upload_file']

            # if it is large, read from the file
            # else read the entirety into a string
            try:
                if hasattr(upload, 'temporary_file_path'):
                    logger.debug("_fileupload: large file so pass filename to json_fload.")
                    tasks.json_fload(upload.temporary_file_path())
                else:
                    logger.debug("_fileupload: small file so pass string to json_sload.")
                    tasks.json_sload(upload.read())
                
            except Exception as e:
                errors = form._errors.setdefault(forms.forms.NON_FIELD_ERRORS, forms.util.ErrorList())
                errors.append("{0}: {1}".format(e.__class__.__name__, e))
                logger.debug('_fileupload: failed to import json contents: ({0}): {1}'.format(e.__class__.__name__, e))
            else:
                logger.debug("_fileupload: import successful, redirecting to fileuploaded.")
                return redirect('staging.views.fileuploaded')
    else:
        form = FileImportForm()

    context['form'] = form

    return render_to_response('staging/fileupload.html', context, rcon)

@login_required
def fileuploaded(request):
    """Thankyou message after uploaded file imported successfully."""
    context = {}
    rcon = RequestContext(request)

    return render_to_response('staging/fileuploaded.html', context, rcon)

@login_required
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

