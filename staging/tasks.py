"""Tasks that are used to import data to the database."""

__author__ = "Lachlan Toohey"

from urllib2 import urlopen, HTTPError

import json
import datetime
import tempfile
import os.path

from django.db import transaction, IntegrityError
from django.core import serializers
from django.template.defaultfilters import slugify

from .extras import update_progress
from .annotations import CPCFileParser
import metadata

from dateutil.tz import tzutc

import catamidb.models

import logging

logger = logging.getLogger(__name__)


def json_sload(json_string):
    """Load the json string into the database."""
    # now load into the database
    json_real_load(json_string)


def json_fload(file_name):
    """Load the json in file 'file_name' in to the database."""
    # now load into the database
    json_file = open(file_name, 'r')
    json_real_load(json_file)


def json_real_load(data):
    """The function that does the real load of json into the database.

    This data can be either a string or file-like object from which data
    can be read.

    Objects in the file have to be from catamidb.models else the whole contents
    will be rejected. This is a security issue.
    """
    with transaction.commit_manually():
        try:
            for obj in serializers.deserialize('json', data):
                # check if the class is in catamidb
                if obj.object.__class__.__module__ == "catamidb.models":
                    obj.save()
                else:
                    raise ValueError('Object does not come from target Module.', obj.object)
        except:
            transaction.rollback()
            # reraise the same error
            raise
        else:
            transaction.commit()


def metadata_type(metadata_file):
    base, extension = os.path.splitext(metadata_file)

    file_type = extension.lower()
    logger.debug("metadata_type: file extension (normalised) is {0}.".format(file_type))

    if file_type == ".xls":
        logger.debug("metadata_type: file is xls format.")
        return "xls"
    elif file_type == ".xlsx":
        logger.debug("metadata_type: file is xlsx format.")
        return "xlsx"
    else:
        logger.debug("metadata_type: file is unknown format.")
        return ""


def metadata_sheet_names(metadata_file):
    """Return a list of sheet names in the file."""
    logger.debug("metadata_sheet_names: getting sheet names.")

    structure = metadata_outline(metadata_file)

    return structure.keys()


def metadata_sheet_name_deslug(metadata_file, slugged_name):
    """Get the deslugged version of the sheet name."""
    sheet_names = metadata_sheet_names(metadata_file)

    for sheet_name in sheet_names:
        if slugify(sheet_name) == slugged_name:
            return sheet_name

    return None


def metadata_outline(metadata_file, *args, **kwargs):
    """Get an outline of the metadata file structure."""
    logger.debug("metadata_outline: getting file outline: {0}".format(metadata_file))
    data_type = metadata_type(metadata_file)

    if data_type == "xls":
        return metadata.xls_outline(metadata_file, *args, **kwargs)
    elif data_type == "xlsx":
        return metadata.xlsx_outline(metadata_file, *args, **kwargs)
    else:
        logger.warning("metadata_outline: cannot handle extension '{0}'".format(data_type))
        return None


def metadata_transform(metadata_file, *args, **kwargs):
    """Transform the and extract data from the metadata file."""
    logger.debug("metadata_transform: transforming file data.")
    data_type = metadata_type(metadata_file)

    if data_type == "xls":
        return metadata.xls_transform(metadata_file, *args, **kwargs)
    elif data_type == "xlsx":
        return metadata.xlsx_transform(metadata_file, *args, **kwargs)
    else:
        logger.warning("metadata_outline: cannot handle extension '{0}'".format(data_type))
        return None


def metadata_import(model_class, fields_list, field_mappings):
    """Import metadata into the database.

    - model_class is the django model.Model being imported
    - field_mappings are the objects that maps rows of data to fields
    - fields_list is the raw data that is being imported
    """
    # we are going to make some checks/assumptions here
    # first is that we *always* inherit from Deployment.
    # second (that possibly will get removed) is that the levels
    # are only one deep (ie AUV -> Deployment, not A -> B -> Deployment)

    base_model = catamidb.models.Deployment

    if len(model_class._meta.parents) != 1:
        raise Exception("Model to import to has multiple parents!")

    if model_class._meta.parents.keys()[0] != base_model:
        raise Exception("Model must directly inherit from Deployment")

    subclass_fields = model_class._meta.local_fields
    subclass_field_names = [f.name for f in subclass_fields]
    subclass_name = "{0}.{1}".format(model_class._meta.app_label,
                                     model_class._meta.object_name)

    base_fields = base_model._meta.local_fields
    base_field_names = [f.name for f in base_fields]
    base_name = "{0}.{1}".format(base_model._meta.app_label,
                                 base_model._meta.object_name)

    # only commit changes if no errors
    # there are going to be metadata errors...
    with transaction.commit_manually():
        try:
            # this is where all the magic happens
            for row in fields_list:
                # map to db fields
                outfields = {}
                try:
                    for field_name, extractor in field_mappings.iteritems():
                        outfields[field_name] = extractor.get_data(row)
                except Exception as exc:  # ValidationError as exc:
                    # do nothing, just drop row and continue to
                    # next
                    logger.warning("Validation failed on row.")
                    logger.warning("Error: " + str(exc))
                    continue

                # this gets fields and maps to the correct (sub)model
                # still probably doesn't work well with natural key/pk
                # and relationship fields
                # mainly thinking of campaigns... but others may arise

                # split to parent
                base_fields = {field: value for field, value in outfields.iteritems() if field in base_field_names}

                # and child
                subclass_fields = {field: value for field, value in outfields.iteritems() if field in subclass_field_names}

                # create data structures
                # HACK: if creating like this create the model directly
                #base_instance = base_model(**base_fields)
                #base_instance.save()
                # a little to hardcoded for my liking...
                #subclass_fields['deployment_ptr'] = base_instance
                #subclass_instance = model_class(**subclass_fields)
                subclass_instance = model_class(**base_fields)

                # save to the database
                try:
                    subclass_instance.save()
                except IntegrityError as exc:
                    logger.warning("IntegrityError: " + exc)
                    continue
        except:
            logger.debug("Rolling back")
            transaction.rollback()
            raise
        else:
            transaction.commit()
            logger.debug("Commiting")


def annotation_cpc_import(user, deployment, cpc_file_handles):
    """Import CPC annotations into the database.

    This is currently targetted at AUV dives. Not sure if used
    beyond that realm.
    """
    # deployment is used to reduce the search space/chance of collision with images
    # still also need mapping of local ids to catami users

    subset = catamidb.models.Image.objects.filter(deployment=deployment)

    # we are assuming AUV naming conventions for the image...

    # get the date time to look the image reference up from the
    # name of the file... this will assume AUV imagery.
    # Videos probably come from some other idea anyway...

    for cpc_handle in cpc_file_handles:
        annotations = CPCFileParser(cpc_handle)

        image_name = annotations.image_file_name

        # extract the timing info from the file name
        image_datetime = datetime.datetime.strptime(image_name, "PR_%Y%m%d_%H%M%S_%f_LC16")
        image_datetime = image_datetime.replace(tz=utc)
        # now look it up... hopefully the timestamp will match something in the database

        image = subset.get(date_time=image_datetime)

        for a in annotations:
            an = catamidb.models.Annotation()
            an.image_reference = image
            an.method = "50 Point CPC"
            an.code = a['label']
            an.point = "POINT({0} {1})".format(a['x'], a['y'])
            an.comments = a['notes']
            an.user_who_annotated = user

            an.save()

    # annotations are done!
