"""Forms for the staging application.

This includes AUVImportForm and FileImportForm.
"""
from django import forms
from django.contrib.gis.forms import fields as gisfields
from django.db import models
from Force.models import Campaign, Deployment, User

from .models import MetadataFile

from .widgets import PointField, MultiSourceField
from .fields import MultiFileField

import logging

logger = logging.getLogger(__name__)


class CampaignCreateForm(forms.ModelForm):
    class Meta:
        model = Campaign


class AUVImportForm(forms.Form):
    """Form to handle importing AUV data from the data fabric."""
    # widget format adjusting
    attrs = {'class': 'span12'}
    campaign_widget = forms.Select(attrs=attrs)
    url_widget = forms.TextInput(attrs=attrs)

    # the options for the campaign model choice field
    campaign_options = {}
    campaign_options['widget'] = campaign_widget
    campaign_options['queryset'] = Campaign.objects.all()
    campaign_options['empty_label'] = None

    # auv import base
    import_base = 'http://df.arcs.org.au/ARCS/projects/IMOS/public/AUV'

    # the fields themselves
    campaign_name = forms.ModelChoiceField(**campaign_options)
    mission_name = forms.CharField(widget=url_widget, max_length=100)
    base_url = forms.URLField(widget=url_widget, initial=import_base)

    # help strings for the fields
    campaign_name.help_text = "Campaign to add deployment to."
    mission_name.help_text = "Short Name/Folder Name of the mission to import."
    base_url.help_text = "Base URL to import from."
    # extra validation/clearning

    def clean_mission_name(self):
        """Function to validate the mission_name."""
        # check the mission doesn't exist
        # auv missions are all unique in short name (as start time
        # is included)
        mission_name = self.cleaned_data['mission_name']
        logger.debug("clean_mission_name: cleaning name {0}".format(mission_name))

        # split into date/name parts
        mission_name_parts = mission_name.split('_', 2)

        # check that it has the correct number of parts
        if len(mission_name_parts) < 3:
            logger.debug("AUVImportForm.clean_mission_name: name doesn't match pattern.")
            raise forms.ValidationError("Mission Name does not match expected pattern 'rYYYYmmdd_HHMMSS_<mission_description>'.")

        mission_text = mission_name_parts[2]

        try:
            Deployment.objects.get(short_name=mission_text)
        except Deployment.DoesNotExist:
            # doesn't exist, so all good
            logger.debug("AUVImportForm.clean_mission_name: valid name.")
            return mission_name
        else:
            logger.debug("AUVImportForm.clean_mission_name: name already exists.")
            raise forms.ValidationError('Mission Name already exists.')


class AUVManualImportForm(AUVImportForm):
    """Form to enable manual specification of Metadata Files."""
    attrs = {'class': 'span12'}
    track_widget = forms.TextInput(attrs=attrs)
    netcdf_widget = forms.TextInput(attrs=attrs)

    trackfile_url = forms.URLField(widget=track_widget)
    netcdffile_url = forms.URLField(widget=netcdf_widget)


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
            logger.debug("ModelImportForm getting all fields of {0}".format(model))
            all_model_fields = model._meta.fields
            # this is a list of fields
            # each field has:
            # - name
            # - model (class of actual model it is declared in)
            # - formfield() constructs a matching form.field

            for model_field in all_model_fields:
                # create the default form field for that type
                form_field = model_field.formfield(required=False)
                logger.debug('ModelImportForm model field {0} has form field {1}'.format(model_field, form_field))
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
                    self.fields[model_field.name] = MultiSourceField(base_field=form_field, columns=columns, required=False)

        else:
            # wrong type of class
            raise TypeError("Expected subclass of django.db.models.Model")


class AnnotationCPCImportForm(forms.Form):
    """Form to enable importing of multiple CPC files for a deployment."""
    cpc_files = MultiFileField()
    deployment = forms.ModelChoiceField(queryset=Deployment.objects.all())
    user = forms.ModelChoiceField(queryset=User.objects.all())
