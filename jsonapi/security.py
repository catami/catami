from tastypie.authentication import Authentication
from tastypie.authorization import Authorization

from django.db.models import Q

def is_reading(request):
    if request.method in ('GET', 'OPTIONS', 'HEAD'):
        return True

class CollectionAuthorization(Authorization):
    def is_authorized(self, request, object=None):
        print request.method
        if object:
            if object.is_public:
                if is_reading(request):
                    return True
                else:
                    return False
            else:
                if not hasattr(request, 'user'):
                    return False

                if request.user == owner:
                    return True
        else:
            return True

    def read_list(self, object_list, bundle):
        request = bundle.request
        if hasattr(request, 'user'):
            return object_list.filter(Q(owner=request.user) | Q(is_public=True))
        else:
            return object_list.filter(is_public=True)
