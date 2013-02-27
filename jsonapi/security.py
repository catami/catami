from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized

from django.db.models import Q


class CollectionAuthorization(Authorization):
    """Implements authorization for collections.

    Restricts access to reading, deleting and updating of details,
    and to only reading of lists.
    """

    def read_list(self, object_list, bundle):
        """Restrict the list to only show public/user owned collections."""
        request = bundle.request
        if hasattr(request, 'user') and request.user.is_authenticated():
            return object_list.filter(Q(owner=request.user) | Q(is_public=True))
        else:
            return object_list.filter(is_public=True)

    def read_detail(self, object_list, bundle):
        """Restrict detail of collections to owner unless is_public."""
        if bundle.obj.owner == bundle.request.user or bundle.obj.is_public:
            return True
        else:
            raise Unauthorized("You do not have permission to see this collection.")

    def delete_detail(self, object_list, bundle):
        #TODO: extend to check for dependant collections and annotation sets
        # basically anything that looks at this and expects it to exist
        # for now just prevent deletion
        if False:  # bundle.obj.owner == bundle.request.user:
            return True
        else:
            raise Unauthorized("You do not have permission to see this collection.")

    def update_detail(self, object_list, bundle):
        """Restrict access to updating a collection.

        Restricted to requests where the user is the owner and the collection
        is unlocked.
        """
        # get the original object (this is needed in case we are locking it)
        # bundle.obj is the modified value
        # the original can be found in object_list
        original = object_list.get(id=bundle.obj.id)
        if not original.owner == bundle.request.user:
            raise Unauthorized("You do not own this collection so can't modify it.")
        elif original.is_locked:
            raise Unauthorized("This collection is locked and cannot be unlocked or modified.")
        else:
            return True
