from django import forms
from Force.models import Campaign

class AUVImportForm(forms.Form):
    # get the available campaigns
    choices = tuple([(c.short_name, "{0} {1}".format(c.date_start, c.short_name))  for c in Campaign.objects.all()])

    # widget format adjusting
    attrs={'class': 'span12'}
    campaign_widget = forms.Select(attrs=attrs)
    url_widget = forms.TextInput(attrs=attrs)


    # the fields themselves
    campaign_name = forms.ChoiceField(widget=campaign_widget, choices=choices)
    mission_name = forms.CharField(widget=url_widget, max_length=100)
    base_url = forms.URLField(widget=url_widget, initial='http://df.arcs.org.au/ARCS/projects/IMOS/public/AUV/')

    # help strings for the fields
    campaign_name.help_text="""Campaign to add deployment to."""
    mission_name.help_text="""Short Name/Folder Name of the mission to import."""
    base_url.help_text="""Base URL to import from."""

class FileImportForm(forms.Form):
    upload_file = forms.FileField()
