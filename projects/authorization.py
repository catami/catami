import logging
from django.contrib.auth.models import Group
from django.dispatch import receiver
import guardian
from guardian.models import UserObjectPermission
from guardian.shortcuts import assign_perm
from userena.signals import signup_complete

logger = logging.getLogger(__name__)


# default permissions for project objects
def apply_project_permissions(user, project):
    #assign all permissions view, add, change, delete
    logger.debug("Applying owner permissions to project: " + project.name + " " + project.id.__str__())

    assign_perm('view_project', user, project)
    assign_perm('add_project', user, project)
    assign_perm('change_project', user, project)
    assign_perm('delete_project', user, project)

    #assign view permissions to the Anonymous user
    logger.debug("Making project public: " + project.name)

    public_group, created = Group.objects.get_or_create(name='Public')
    assign_perm('view_project', public_group, project)


def apply_annotation_set_permissions(user, annotation_set):
    #assign all permissions view, add, change, delete
    logger.debug("Applying owner permissions to annotation set: " + annotation_set.name)

    assign_perm('view_annotationset', user, annotation_set)
    assign_perm('add_annotationset', user, annotation_set)
    assign_perm('change_annotationset', user, annotation_set)
    assign_perm('delete_annotationset', user, annotation_set)

    #assign view permissions to the Anonymous user
    logger.debug("Making annotation set public: " + annotation_set.name)

    public_group, created = Group.objects.get_or_create(name='Public')
    assign_perm('view_annotationset', public_group, annotation_set)