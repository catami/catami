from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from dajaxice.utils import deserialize_form
from dajax.core import Dajax
import guardian
from webinterface.forms import CreateCollectionForm, CreateWorksetForm, CreateWorksetAndAnnotationForm
from collection.models import Collection, CollectionManager
from annotations.api import PointAnnotationSetResource
from annotations.models import PointAnnotationSet
import sys,traceback
from tastypie.exceptions import ApiFieldError
from django.db import IntegrityError

@dajaxice_register
def send_workset_form(request, form, form_id):
    dajax = Dajax()
    form = CreateWorksetForm(deserialize_form(form))

    user = request.user
    if request.user.is_anonymous():
        user = guardian.utils.get_anonymous_user()

    if form.is_valid():  # All validation rules pass
        dajax.remove_css_class(form_id+' input', 'error')
        dajax.script('form_errors(false,"{0}");'.format(form_id))

        wsid, msg = CollectionManager().workset_from_collection(
            user,
            form.cleaned_data.get('name'),
            form.cleaned_data.get('description'),
            form.cleaned_data.get('ispublic') == "true",
            int(form.cleaned_data.get('c_id')),
            int(form.cleaned_data.get('n')),
            form.cleaned_data.get('method')
        )

        if wsid is None: wsid = "null"
        dajax.script('refresh_worksets({0},"{1}");'.format(wsid,msg))

    else:
        dajax.remove_css_class(form_id+' input', 'error')
        dajax.script('form_errors(true,"{0}");'.format(form_id))
        for error in form.errors:
            dajax.add_css_class(form_id+' #id_%s' % error, 'error')

    return dajax.json()

@dajaxice_register
def send_workset_and_annotation_form(request, form, form_id):
    dajax = Dajax()
    form = CreateWorksetAndAnnotationForm(deserialize_form(form))

    print "form is send_workset_and_annotation_form"    

    user = request.user
    if request.user.is_anonymous():
        user = guardian.utils.get_anonymous_user()

    if form.is_valid():  # All validation rules pass
        print "form is valid"    
        dajax.remove_css_class(form_id+' input', 'error')
        dajax.script('form_errors(false,"{0}");'.format(form_id))

        # make collection for workset
        print form.cleaned_data.get('randomize_workset')

        if form.cleaned_data.get('randomize_workset'):
            wsid, msg = CollectionManager().workset_from_collection(
                user,
                form.cleaned_data.get('name'),
                form.cleaned_data.get('description'),
                form.cleaned_data.get('ispublic') == "true",
                int(form.cleaned_data.get('collection_id')),
                int(form.cleaned_data.get('image_count')),
                "random"
            )

            print wsid
        else:
            wsid, msg = CollectionManager().workset_from_collection(
                user,
                form.cleaned_data.get('name'),
                form.cleaned_data.get('description'),
                form.cleaned_data.get('ispublic') == "true",
                int(form.cleaned_data.get('collection_id')),
                int(form.cleaned_data.get('image_count')),
                "stratified"
            )            
        # make annotation set for workset

        temp = Collection.objects.get(id=wsid)

        if wsid is not None:
            
            annotation_resource = PointAnnotationSetResource()

            datastuff = {'collection':Collection.objects.get(id=wsid),
                         'owner':user,
                         'name':form.cleaned_data.get('name')+'_annotationset',
                         'methodology':int(form.cleaned_data.get('point_sampling_methodology')),
                         'count': int(form.cleaned_data.get('annotation_point_count'))
                        }

            try:
                annotation_bundle = annotation_resource.build_bundle(data = datastuff, request = request)
            except:
                print 'annotation_bundle create failed unexpectedly: ', sys.exc_info()[0]

            try:
                annotation_object = annotation_resource.obj_create(bundle = annotation_bundle)
            except ApiFieldError, e:
                msg = 'Sorry, annotation set creation failed with an ApiFieldError: ', e.args[0]
            except IntegrityError, e:
                msg = 'Sorry, annotation set creation failed with an IntegrityError: ', e.message
            except:
                msg = 'Sorry, annotation set creation failed unexpectedly. Message is: ', sys.exc_info()[0]
        else: 
            wsid = "null"
            msg = 'Sorry, annotation set creation failed unexpectedly because something bad happened during the workset creation'

        dajax.script('refresh_worksets({0},"{1}");'.format(wsid,msg))

    else:
        dajax.remove_css_class(form_id+' input', 'error')
        dajax.script('form_errors(true,"{0}");'.format(form_id))
        for error in form.errors:
            dajax.add_css_class(form_id+' #id_%s' % error, 'error')

    return dajax.json()