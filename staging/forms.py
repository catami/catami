"""Forms for the staging application.

This includes AUVImportForm and FileImportForm.
"""
from django import forms

from django.contrib.gis.forms import fields as gisfields
from django.db import models
from catamidb.models import Campaign, Deployment

from .models import MetadataFile

from .widgets import PointField, MultiSourceField
from .fields import MultiFileField

import logging

logger = logging.getLogger(__name__)


class CampaignCreateForm(forms.ModelForm):
    class Meta:
        model = Campaign


class FileImportForm(forms.Form):
    """Form to assist with uploading a json file.

    Particularly targetted at files to directly deserialize.
    """
    upload_file = forms.FileField()

    upload_file.help_text = "JSON file in import format."


class MetadataStagingForm(forms.ModelForm):
    """Form to upload generic files that will need processing.
    """

    class Meta:
        model = MetadataFile
        exclude = ('owner', )


class ModelImportForm(forms.Form):
    """Form to handle general importing of data to deployments.

    This takes data from existing structures and helps create
    a mapping.

    Internally it mimics a lot of code from django/forms/models.py
    with regards to model introspection to get a list of fields.
    """

    def __init__(self, *args, **kwargs):
        """Create the ModelImportForm from a model.

        This creates all the fields 'on the fly' from the model enabling
        it to adapt to any models given to it.
        """
        columns = kwargs.pop('columns')
        model = kwargs.pop('model')

        logger.debug("ModelImportForm init'ing parent")

        # init the form
        super(ModelImportForm, self).__init__(*args, **kwargs)

        # get the model fields (the dbmodel)
        # and add the form fields to match
        if issubclass(model, models.Model):
            # get the fields
            logger.debug(
                "ModelImportForm getting all fields of {0}".format(model))
            all_model_fields = model._meta.fields
            # this is a list of fields
            # each field has:
            # - name
            # - model (class of actual model it is declared in)
            # - formfield() constructs a matching form.field

            for model_field in all_model_fields:
                # create the default form field for that type
                form_field = model_field.formfield(required=False)
                logger.debug(
                    'ModelImportForm model field {0} has form field {1}'.format(
                        model_field, form_field))
                if form_field:
                    # as long as there is a corresponding form field
                    # (autofield - pk does not have one)

                    # make a split date time, or use lat lon/not the geometry
                    # field
                    if type(form_field) == forms.DateTimeField:
                        form_field = forms.SplitDateTimeField(required=False)
                    elif type(form_field) == gisfields.GeometryField:
                        form_field = PointField(required=False)

                    # a little bit improper but required=False prevents it
                    # check all the sub fields. The compress phase does
                    # actually check that it has a valid value
                    # and ignores this required flag against convention.
                    self.fields[model_field.name] = MultiSourceField(
                        base_field=form_field, columns=columns,
                        required=False)

        else:
            # wrong type of class
            raise TypeError("Expected subclass of django.db.models.Model")


class ApiDeploymentForm(forms.Form):
    short_name = forms.CharField()
    campaign = forms.ModelChoiceField(queryset=Campaign.objects.all())
    license = forms.CharField(max_length=500)
    descriptive_keywords = forms.CharField(max_length=500)
