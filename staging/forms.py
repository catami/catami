"""Forms for the staging application.

This includes AUVImportForm and FileImportForm.
"""
from django import forms
from Force.models import Campaign, Deployment

from .models import MetadataFile

import logging

logger = logging.getLogger(__name__)

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
    import_base = 'http://df.arcs.org.au/ARCS/projects/IMOS/public/AUV/'

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
        exclude = ('owner',)

