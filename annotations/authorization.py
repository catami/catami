
import logging
from django.contrib.auth.models import Group
from django.dispatch import receiver
import guardian
from guardian.shortcuts import assign
from userena.signals import signup_complete

logger = logging.getLogger(__name__)


# default permissions for collection objects
def apply_pointannotationset_permissions(user, point_annotation_set):
    #assign all permissions view, add, change, delete
    logger.debug("Applying owner permissions to point annotation set: " + point_annotation_set.name)

    assign('view_pointannotationset', user, point_annotation_set)
    assign('add_pointannotationset', user, point_annotation_set)
    assign('change_pointannotationset', user, point_annotation_set)
    assign('delete_pointannotationset', user, point_annotation_set)

    #assign view permissions to the Anonymous user
    logger.debug("Making point annotation set public: " + point_annotation_set.name)

    public_group, created = Group.objects.get_or_create(name='Public')
    assign('view_pointannotationset', public_group, point_annotation_set)