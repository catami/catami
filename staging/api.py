from tastypie import fields
from tastypie.resources import ModelResource, Resource, Bundle
from tastypie.exceptions import NotFound, BadRequest
from tastypie.utils import trailing_slash
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import ReadOnlyAuthorization

import staging.settings as staging_settings
import staging.forms as staging_forms
from staging.auvimport import AUVImporter

from catamidb.models import AUVDeployment, Deployment

from django.core.urlresolvers import reverse
from django.conf.urls import url
import logging

logger = logging.getLogger(__name__)

import os
import os.path


class StagingFileObject(object):
    def __init__(self, initial=None):
        self.__dict__['_data'] = {}

        if hasattr(initial, 'items'):
            self.__dict__['_data'] = initial

    def __getattr__(self, name):
        return self._data.get(name, None)

    def __setattr__(self, name, value):
        self.__dict__['_data'][name] = value

    def to_dict(self):
        return self._data


class StagingFilesResource(Resource):
    """Read only resource that allows exploration of the staging area."""
    pk = fields.CharField(attribute='pk')
    path = fields.CharField(attribute='path')
    name = fields.CharField(attribute='name')
    is_dir = fields.BooleanField(attribute='is_dir')

    parent = fields.CharField(attribute='parent')

    class Meta:
        resource_name = 'stagingfiles'
        object_class = StagingFileObject
        auv_create_allowed_methods = ['post']
        authentication = BasicAuthentication()
        authorization = ReadOnlyAuthorization()

    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.path.encode('hex')
        else:
            kwargs['pk'] = bundle_or_obj.path.encode('hex')

        return kwargs

    def get_object_list(self, request):
        pass

    def get_auv_create_uri(self, bundle_or_obj):
        """Get the URI to call auv import on this object."""

        # these are both needed...
        kwargs = {'api_name': self._meta.api_name,
            'resource_name': self._meta.resource_name,
            }

        kwargs = {}

        # get the objects pk/lookup
        if isinstance(bundle_or_obj, Bundle):
            pk = bundle_or_obj.obj.pk
        else:
            pk = bundle_or_obj.pk

        # add it in
        kwargs['pk'] = pk

        # and get the reverse url from django
        #return reverse("api_auv_create", kwargs=kwargs)
        # the url of the form view (it can derive the api creation url)
        return reverse("api_auv_form", kwargs=kwargs)

    def obj_get(self, request=None, **kwargs):
        # get the system dir and list child folders
        base = staging_settings.STAGING_IMPORT_DIR
        path = kwargs['pk'].decode('hex')
        system_dir = os.path.join(base, path)

        parent = {}
        parent_path = os.path.dirname(path)
        if parent_path == "":
            parent_path = "./"
        parent['pk'] = parent_path.encode('hex')

        parent_obj = StagingFileObject(initial=parent)

        data = {}
        data['path'] = path
        data['pk'] = path.encode('hex')
        data['parent'] = parent['pk']  # the straight key is more useful   parent_obj
        data['name'] = os.path.basename(path)
        data['is_dir'] = os.path.isdir(system_dir)
        obj = StagingFileObject(initial=data)

        actions = {}
        if AUVImporter.dependency_check(system_dir):
            actions['auvcreate'] = self.get_auv_create_uri(obj)

        obj.actions = actions

        return obj

    def apply_filters(self, request, applicable_filters):
        parent_path = applicable_filters.get('folder', "").decode('hex')
        base = staging_settings.STAGING_IMPORT_DIR
        system_dir = os.path.join(base, parent_path)

        # create the parent of all of these objects...
        if parent_path == "":
            parent_path = "./"
        parent = {}
        parent['pk'] = parent_path.encode('hex')

        parent_obj = StagingFileObject(initial=parent)

        if os.path.isdir(system_dir):
            children = []
            for name in os.listdir(system_dir):
                system_name = os.path.join(system_dir, name)
                relative_name = os.path.join(parent_path, name)

                if os.path.isdir(system_name):
                    is_dir = True
                elif os.path.isfile(system_name):
                    is_dir = False
                else:
                    # not a file or dir? skip on
                    continue

                # now create the StagingFileObject
                data = {}
                data['parent'] = parent_obj
                data['path'] = relative_name
                data['pk'] = relative_name.encode('hex')
                data['name'] = name
                data['is_dir'] = is_dir
                obj = StagingFileObject(initial=data)

                actions = {}
                if AUVImporter.dependency_check(system_name):
                    actions['auvcreate'] = self.get_auv_create_uri(obj)

                obj.actions = actions
                children.append(obj)
                #children.append(StagingFileObject(initial=data))
        else:
            children = []

        return children

    def obj_get_list(self, bundle, **kwargs):
        # this is where filtering normally happens...
        filters = {}
        if hasattr(bundle.request, 'GET'):
            filters = bundle.request.GET.copy()

        filters.update(kwargs)

        applicable_filters = self.build_filters(filters=filters)

        try:
            objects = self.apply_filters(bundle.request, applicable_filters)
            return self.authorized_read_list(objects, bundle)
        except ValueError:
            return BadRequest("Invalid resource lookup data provided (mismatched type).")

    def dehydrate(self, bundle):
        print bundle
        print bundle.obj.actions
        bundle.actions = bundle.obj.actions
        bundle.data['actions'] = bundle.obj.actions
        return bundle

    def obj_create(self, bundle, request=None, **kwargs):
        pass

  # not relevant?
    def obj_update(self, bundle, request=None, **kwargs):
        pass

  # not relevant?
    def obj_delete_list(self, request=None, **kwargs):
        pass

  # not relevant?
    def obj_delete(self, request=None, **kwargs):
        pass

  # not relevant?
    def rollback(self, bundles):
        pass  # not relevant?

    # will become prepend_urls on upgrade to 0.9.12 (is deprecated at that point)
    def prepend_urls(self):
        return [url(r"^(?P<resource_name>%s)/create/(?P<pk>\w[\w/-]*)/auv%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('auv_create'), name="api_auv_create")]

    def auv_create(self, request, **kwargs):
        return self.dispatch("auv_create", request, **kwargs)

    def post_auv_create(self, request, **kwargs):
        # should extract and validate the form...
        form = staging_forms.ApiDeploymentForm(request.POST)
        if form.is_valid():
            print "Validated"
            # extract the path we are working with
            base = staging_settings.STAGING_IMPORT_DIR
            path = os.path.join(base, kwargs['pk'].decode('hex'))

            # now we create the deployment
            created_deployment = AUVDeployment()

            data = form.cleaned_data

            created_deployment.short_name = data['short_name']
            created_deployment.campaign = data['campaign']
            created_deployment.license = data['license']
            created_deployment.descriptive_leywords = data['descriptive_keywords']

            print "passing to function to process"
            # now pass to the parsing function
            try:
                AUVImporter.import_path(created_deployment, path)
            except Exception:
                logger.exception("Unable to import deployment.")

            print "Exiting!"

            # then return the new deployment
            return self.create_response(request, created_deployment)

        # on failure... not sure what to do yet
        # probably just return the form
        # or call the original view that should have created it?
        print "Invalid"
