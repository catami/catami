from django import forms



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


#class CreateWorksetForm(forms.Form):
#    name = forms.CharField(label=u'Name', widget=forms.TextInput(attrs={'placeholder': 'Enter a descriptive name'}))
#    #ispublic = forms.BooleanField(label=u'Make public?', required=False)
#    n = forms.IntegerField(label=u'N', widget=forms.TextInput(attrs={'placeholder': 'Numeric input'}))
#    description = forms.CharField(label=u'Description', required=False, widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Longer description (optional)'}))
#    method = forms.CharField(widget=forms.HiddenInput())
#    c_id = forms.IntegerField(widget=forms.HiddenInput())
