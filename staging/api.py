from tastypie import fields
from tastypie.resources import ModelResource, Resource, Bundle
from tastypie.exceptions import NotFound, BadRequest

import staging.settings as staging_settings

from django.core.urlresolvers import reverse

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


class FilesystemToOne(fields.RelatedField):
    def dehydrate(self, bundle):
        try:
            foreign_obj = getattr(bundle.obj, self.attribute)
        except ObjectDoesNotExist:
            foreign_obj = None

        if not foreign_obj:
            if not self.null:
                raise ApiFieldError("The model '%r' has an empty attribute and doesn't allow a null value." % (bundle.obj, self.attribute))
            return None

        fk_resource = self.get_related_resource(foreign_obj)
        fk_bundle = Bundle(obj=foreign_obj, request=bundle.request)
        return self.dehydrate_related(fk_bundle, fk_resource)


class FilesystemToMany(fields.RelatedField):
    def dehydrate(self, bundle):
        if not bundle.obj or not bundle.obj.pk:
            if not self.null:
                raise ApiFieldError("The model '%r' does not have a primary key and can not be used in a ToMany context." % (bundle.obj))
            return []

        the_m2ms = None
        if isinstance(self.attribute, basestring):
            the_m2ms = getattr(bundle.obj, self.attribute)
        elif callable(self.attribute):
            the_m2ms = self.attribute(bundle)

        if not the_m2ms:
            if not self.null:
                raise ApiFieldError("The model '%r' has an empty attribute and doesn't allow a null value." % (bundle.obj, self.attribute))
            return []

        m2m_resources = []
        m2m_dehydrated = []

        for m2m in the_m2ms:
            m2m_resource = self.get_related_resource(m2m)
            m2m_bundle = Bundle(obj=m2m, request=bundle.request)
            m2m_resources.append(m2m_resource)
            m2m_dehydrated.append(self.dehydrate_related(m2m_bundle, m2m_resource))

        return m2m_dehydrated

class StagingFilesResource(Resource):
    """Read only resource that allows exploration of the staging area."""
    pk = fields.CharField(attribute='pk')
    path = fields.CharField(attribute='path')
    name = fields.CharField(attribute='name')
    is_dir = fields.BooleanField(attribute='is_dir')

#    children = FilesystemToMany('staging.api.StagingFilesResource', attribute='children', related_name="parent", null=True, full=False)
    parent = fields.CharField(attribute='parent')   #FilesystemToOne('staging.api.StagingFilesResource', attribute='parent')

    class Meta:
        resource_name = 'stagingfiles'
        object_class = StagingFileObject

    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.path.encode('hex')
        else:
            kwargs['pk'] = bundle_or_obj.path.encode('hex')

        return kwargs

    def get_object_list(self, request):
        pass

    def get_resource_uri(self, bundle_or_obj):
        """Get the API address of this URI."""

        # these are both needed...
        kwargs = {'api_name': self._meta.api_name,
            'resource_name': self._meta.resource_name,
            }

        # get the objects pk/lookup
        if isinstance(bundle_or_obj, Bundle):
            pk = bundle_or_obj.obj.pk
        else:
            pk = bundle_or_obj.pk

        # add it in
        kwargs['pk'] = pk

        # and get the reverse url from django
        return reverse("api_dispatch_detail", kwargs=kwargs)

    def obj_get(self, request=None, **kwargs):
        # get the system dir and list child folders
        base = staging_settings.STAGING_IMPORT_DIR
        path = kwargs['pk'].decode('hex')
        system_dir = os.path.join(base, path)
        print system_dir

        # don't think I use this anymore...
        if False:
        #if os.path.isdir(system_dir):
            child_files = []
            for name in os.listdir(system_dir):
                system_name = os.path.join(system_dir, name)
                relative_name = os.path.join(path, name)

                if os.path.isdir(system_name):
                    is_dir = True
                elif os.path.isfile(system_name):
                    is_dir = False
                else:
                    # not a file or dir? skip on
                    continue

                # now create the StagingFileObject
                data = {}
                data['path'] = relative_name
                data['pk'] = relative_name.encode('hex')
                data['name'] = name
                data['is_dir'] = is_dir
                child_files.append(StagingFileObject(initial=data))
        else:
            child_files = []

        parent = {}
        parent_path = os.path.dirname(path)
        if parent_path == "":
            parent_path = "./"
        parent['pk'] = parent_path.encode('hex')

        parent_obj = StagingFileObject(initial=parent)

        data = {}
        data['path'] = path
        data['pk'] = path.encode('hex')
        data['parent'] = parent['pk'] # the straight key is more useful   parent_obj
        data['name'] = os.path.basename(path)
        data['is_dir'] = os.path.isdir(system_dir)

        return StagingFileObject(initial=data)

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
                children.append(StagingFileObject(initial=data))
        else:
            children = []

        return children


    def obj_get_list(self, request=None, **kwargs):
        # this is where filtering normally happens...
        if hasattr(request, 'GET'):
            filters = request.GET.copy()

        filters.update(kwargs)

        # skip this?
        applicable_filters = self.build_filters(filters=filters)

        try:
            base_object_list = self.apply_filters(request, applicable_filters)
            return self.apply_authorization_limits(request, base_object_list)
        except ValueError:
            return BadRequest("Invalid resource lookup data provided (mismatched type).")

    def obj_create(self, bundle, request=None, **kwargs):
        pass # not relevant?
    def obj_update(self, bundle, request=None, **kwargs):
        pass  # not relevant?
    def obj_delete_list(self, request=None, **kwargs):
        pass  # not relevant?
    def obj_delete(self, request=None, **kwargs):
        pass  # not relevant?
    def rollback(self, bundles):
        pass  # not relevant?
