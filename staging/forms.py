from django import forms
from Force.models import Campaign, Deployment

import logging

logger = logging.getLogger(__name__)

class AUVImportForm(forms.Form):
    # get the available campaigns
    Campaign.objects.update()

    choices = tuple([(c.short_name, "{0} {1}".format(c.date_start, c.short_name))  for c in Campaign.objects.all()])

    # widget format adjusting
    attrs={'class': 'span12'}
    campaign_widget = forms.Select(attrs=attrs)
    url_widget = forms.TextInput(attrs=attrs)


    # the fields themselves
    campaign_name = forms.ModelChoiceField(widget=campaign_widget, queryset=Campaign.objects.all(), empty_label=None)
    mission_name = forms.CharField(widget=url_widget, max_length=100)
    base_url = forms.URLField(widget=url_widget, initial='http://df.arcs.org.au/ARCS/projects/IMOS/public/AUV/')

    # help strings for the fields
    campaign_name.help_text="""Campaign to add deployment to."""
    mission_name.help_text="""Short Name/Folder Name of the mission to import."""
    base_url.help_text="""Base URL to import from."""

    # extra validation/clearning

    def clean_mission_name(self):
        # check the mission doesn't exist
        # auv missions are all unique in short name (as start time
        # is included)
        mission_name = self.cleaned_data['mission_name']
        logger.debug("clean_mission_name: cleaning name {0}".format(mission_name))

        # split into date/name parts
        mission_name_parts = mission_name.split('_', 2)
        if len(mission_name_parts) < 3:
            logger.debug("AUVImportForm.clean_mission_name: name doesn't match pattern.")
            raise forms.ValidationError("Mission Name does not match expected pattern 'rYYYYmmdd_HHMMSS_<mission_description>'.")

        mission_text = mission_name_parts[2]

        try:
            existing = Deployment.objects.get(short_name=mission_text)
        except Deployment.DoesNotExist:
            # doesn't exist, so all good
            logger.debug("AUVImportForm.clean_mission_name: valid name.")
            return mission_name
        else:
            logger.debug("AUVImportForm.clean_mission_name: name already exists.")
            raise forms.ValidationError('Mission Name already exists.')


class FileImportForm(forms.Form):
    upload_file = forms.FileField()

    upload_file.help_text="""JSON file in import format."""
