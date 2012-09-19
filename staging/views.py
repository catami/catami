from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.db import transaction
from django.core import serializers

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
            imported = False

            # try and get the files and import
            try:
                data = form.cleaned_data
                struc = create_structure(data['base_url'], data['campaign_name'], data['mission_name'])
                json_string = structure_string(struc)

                # now deserialize the string into the database
                # check that there are no errors before saving them all
                # if there are any, rollback to the initial state
                with transaction.commit_manually():
                    try:
                        for obj in serializers.deserialize('json', json_string):
                            obj.save()
                    except Exception as e:
                        transaction.rollback()
                        errors = "ImportError: {0}".format(unicode(e))
                        context['debug'] = json_string
                    except:
                        transaction.rollback()
                        errors = "ImportError: Unknown Error"
                    else:
                        transaction.commit()
                        imported = True

            except Exception as e:
                errors = "ImportError: {0}".format(unicode(e))

            # if it worked
            if imported:
                return redirect('staging.views.auvimported')

    else:
        form = AUVImportForm()

    rc = RequestContext(request)
    context['form'] = form
    context['errors'] = errors

    return render_to_response('staging/auvimport.html', context, rc)

def auvimported(request):
    context = {}
    rc = RequestContext(request)

    return render_to_response('staging/auvimported.html', context, rc)


