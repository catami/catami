from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from dajaxice.utils import deserialize_form
from dajax.core import Dajax
import guardian
from webinterface.forms import CreateCollectionForm, CreateWorksetForm
from collection.models import Collection, CollectionManager

@dajaxice_register
def send_workset_form(request, form, form_id):
    dajax = Dajax()
    form = CreateWorksetForm(deserialize_form(form))

    user = request.user
    if request.user.is_anonymous():
        user = guardian.utils.get_anonymous_user()

    if form.is_valid():  # All validation rules pass
        dajax.remove_css_class(form_id+' input', 'error')
        dajax.script('form_errors(false,"{0}");'.format(form_id))

        wsid, msg = CollectionManager().workset_from_collection(
            user,
            form.cleaned_data.get('name'),
            form.cleaned_data.get('description'),
            form.cleaned_data.get('ispublic') == "true",
            int(form.cleaned_data.get('c_id')),
            int(form.cleaned_data.get('n')),
            form.cleaned_data.get('method')
        )

        if wsid is None: wsid = "null"
        dajax.script('refresh_worksets({0},"{1}");'.format(wsid,msg))

    else:
        dajax.remove_css_class(form_id+' input', 'error')
        dajax.script('form_errors(true,"{0}");'.format(form_id))
        for error in form.errors:
            dajax.add_css_class(form_id+' #id_%s' % error, 'error')

    return dajax.json()
