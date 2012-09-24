from django import forms
from Force.models import Campaign

class AUVImportForm(forms.Form):
    Campaign.objects.update()
    choices = tuple([(c.short_name, "{0} {1}".format(c.date_start, c.short_name))  for c in Campaign.objects.all()])
    campaign_name = forms.ChoiceField(choices=choices)
    mission_name = forms.CharField(max_length=100)
    base_url = forms.URLField(initial='http://df.arcs.org.au/ARCS/projects/IMOS/public/AUV/')

