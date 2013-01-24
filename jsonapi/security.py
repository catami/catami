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
            print "No Object!"
            return True

    def apply_limits(self, request, object_list):
        print "Filtering collection list"
        if request and hasattr(request, 'user'):
            return object_list.filter(Q(owner=request.user) | Q(is_public=True))
        else:
            return object_list.filter(is_public=True)
