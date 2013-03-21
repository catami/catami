
import logging
from django.contrib.auth.models import Group
from django.dispatch import receiver
import guardian
from guardian.shortcuts import assign_perm
from userena.signals import signup_complete

logger = logging.getLogger(__name__)


# default permissions for collection objects
def apply_collection_permissions(user, collection):
    #assign all permissions view, add, change, delete
    logger.debug("Applying owner permissions to campaign: " + collection.name)

    assign_perm('view_collection', user, collection)
    assign_perm('add_collection', user, collection)
    assign_perm('change_collection', user, collection)
    assign_perm('delete_collection', user, collection)

    #assign view permissions to the Anonymous user
    logger.debug("Making campaign public: " + collection.name)

    public_group, created = Group.objects.get_or_create(name='Public')
    assign_perm('view_collection', public_group, collection)