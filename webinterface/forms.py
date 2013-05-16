from django import forms
from annotations.models import POINT_METHODOLOGIES
from annotations.models import PointAnnotationSet

class CreateCollectionForm(forms.Form):
    deployment_ids = forms.CharField()
    collection_name = forms.CharField()

class CreateCollectionExploreForm(forms.Form):
    deployment_ids = forms.CharField()
    collection_name = forms.CharField()
    depth__gte = forms.CharField()
    depth__lte = forms.CharField()
    temperature__gte = forms.CharField()
    temperature__lte = forms.CharField()
    salinity__gte = forms.CharField()
    salinity__lte = forms.CharField()
    altitude__gte = forms.CharField()
    altitude__lte = forms.CharField()

#class CreateWorksetForm(forms.Form):
#    name = forms.CharField()
#    description = forms.CharField(required=False)
#    ispublic = forms.BooleanField(required=False)
#    c_id = forms.IntegerField()
#    n = forms.IntegerField()

class CreateWorksetForm(forms.Form):
    name = forms.CharField(label=u'Name', widget=forms.TextInput(attrs={'placeholder': 'Enter a descriptive name'}))
    #ispublic = forms.BooleanField(label=u'Make public?', required=False)
    n = forms.IntegerField(label=u'N', min_value=1)
    description = forms.CharField(label=u'Description', required=False, widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Longer description (optional)'}))
    method = forms.CharField(widget=forms.HiddenInput())
    c_id = forms.IntegerField(widget=forms.HiddenInput())


class CreatePointAnnotationSet (forms.Form):
    collection = forms.IntegerField(widget=forms.HiddenInput())
    owner = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(label=u'Name', widget=forms.TextInput(attrs={'placeholder': 'Enter a descriptive name'}))
    methodology = forms.ChoiceField(label=u'Methodology', choices=POINT_METHODOLOGIES, initial=0)
    count = forms.IntegerField(label=u'N', min_value=1)


#class CreatePointAnnotationSet (forms.ModelForm):
#    class Meta:
#        model = PointAnnotationSet