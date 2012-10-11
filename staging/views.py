"""Views for the staging app.
"""

from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django import forms
from django.contrib.auth.decorators import login_required
from django.core.cache import cache

from .forms import AUVImportForm, FileImportForm, MetadataStagingForm
from .extras import UploadProgressCachedHandler
from . import tasks
from .models import MetadataFile

from django.views.decorators.csrf import csrf_exempt, csrf_protect

import logging

logger = logging.getLogger(__name__)

@login_required
def index(request):
    """The home/index view for staging."""
    context = {}

    rcon = RequestContext(request)

    return render_to_response('staging/index.html', context, rcon)

@login_required
def auvprogress(request):
    """Used to return progress of an operation."""
    context = {}

    rcon = RequestContext(request)

    uuid = request.GET.get('uuid', None)

    track_key = uuid + "_track_key"
    netcdf_key = uuid + "_netcdf_key"

    context['track_percent'] = cache.get(track_key)
    context['netcdf_percent'] = cache.get(netcdf_key)

    if not uuid:
        return Error

    # contains three elements that are needed to render

    return render_to_response('staging/auvprogress.html', context, rcon)

@login_required
def fileprogress(request):
    """Used to return progress of an operation."""
    context = {}

    rcon = RequestContext(request)

    uuid = request.GET.get('uuid', None)

    file_key = uuid + "_file_key"

    context['file_percent'] = cache.get(file_key)

    if not uuid:
        raise Exception("Coult not find uuid in cache.")

    # contains three elements that are needed to render

    return render_to_response('staging/fileprogress.html', context, rcon)

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

                # get the uuid - not part of POST
                # but appears in the GET maybe?
                uuid = request.REQUEST.get('uuid')

                track_key = uuid + "_track_key"
                netcdf_key = uuid + "_netcdf_key"

                cache.add(track_key, 0, 300) # last for 5 minutes
                cache.add(netcdf_key, 0, 300) # last for 5 minutes

                input_params = (data['base_url'], str(data['campaign_name'].date_start), data['campaign_name'].short_name, data['mission_name'])

                logger.debug("auvimport: determining remote files to fetch.")
                (track_url, netcdf_urlpattern, start_time) = tasks.auvfetch(*input_params)

                logger.debug("auvimport: fetching remote track file.")
                track_file = tasks.get_known_file(track_key, track_url)

                logger.debug("auvimport: fetching remote netcdf file.")
                netcdf_file = tasks.get_netcdf_file(netcdf_key, netcdf_urlpattern, start_time)

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

@login_required
def metadatastage(request):
    """
    Form to upload a generic file that needs more complex parsing.
    """
    context = {}
    rcon = RequestContext(request)

    if request.method == 'POST':
        form = MetadataStagingForm(request.POST, request.FILES)

        if form.is_valid():
            # this is where the import is performed...
            # and the file is read in
            logger.debug("metadatastage: validated, now saving.")
            metadata_file = form.save(commit=False)
            metadata_file.owner_id = request.user.pk
            metadata_file.save()
            logger.debug("metadatastage: saved, now redirecting.")

            return redirect('staging.views.metadatalist')
    else:
        mfile = MetadataFile(owner_id=request.user.pk)
        form = MetadataStagingForm(instance=mfile)

    context['form'] = form

    return render_to_response('staging/metadatastage.html', context, rcon)

@login_required
def metadatalist(request):
    """
    Page with lists of all metadata the user can access.

    Currently shows only files they own.
    """
    owned_files = MetadataFile.objects.filter(owner=request.user)
    public_files = MetadataFile.objects.filter(is_public=True)
    public_files = public_files.exclude(owner=request.user)

    rcon = RequestContext(request)
    context = {}
    context['owned_files'] = owned_files
    context['public_files'] = public_files
    context['user'] = request.user
    return render_to_response('staging/metadatalist.html', context, rcon)

@login_required
def metadatabook(request, file_id):
    """
    Page with info about all the sheets in the file.
    """

    file_entry = MetadataFile.objects.get(pk=file_id)
    # get the on disk location of the file
    file_name = file_entry.metadata_file.name

    workbook_descriptor = tasks.metadata_outline(file_name)
    context = {}
    context['book_id'] = file_entry.pk
    context['book_name'] = file_entry.description
    context['book'] = workbook_descriptor

    rcon = RequestContext(request)

    return render_to_response('staging/metadatabook.html', context, rcon)

@login_required
def metadatasheet(request, file_id, page_name):
    """
    Setup the sheet for importing.
    """
    # need to get the workbook first, then the sheet
    file_entry = MetadataFile.objects.get(pk=file_id)
    if file_entry.owner.username == request.user.username:
        # get the sheet
        filename = file_entry.metadata_file.name
        sheet_name = tasks.metadata_sheet_name_deslug(filename, page_name)
        structure = tasks.metadata_transform(filename, sheet_name)
    else:
        # permission denied
        return HttpResponseForbidden("You do not have permission to view this metadata file.")

    # process the structure to get what we need
    # it is a set of dictionaries
    headings = structure[0].keys()

    data_rows = []
    for row in structure:
        new_row = []
        for key in headings:
            new_row.append(row[key])
        data_rows.append(new_row)

    # now setup the data to be displayed in a table
    # so need the headings, and then lists of data in order
    context = {}
    rcon = RequestContext(request)

    context['book_name'] = file_entry.description
    context['sheet_name'] = sheet_name
    context['headings'] = headings
    context['data_rows'] = data_rows

    return render_to_response('staging/metadatasheet.html', context, rcon)

@login_required
@login_required
def metadatadelete(request, file_id):
    """Command to delete metadata file.

    Restricted to owner.
    """
    file_entry = MetadataFile.objects.get(pk=file_id)

    if file_entry.owner.username == request.user.username:
        # delete the file, this is the owner
        file_entry.delete()
    else:
        # don't delete it, the owner is not here
        return HttpResponseForbidden("You do not have permission to delete this metadata file.")

    return redirect('staging.views.metadatalist')

